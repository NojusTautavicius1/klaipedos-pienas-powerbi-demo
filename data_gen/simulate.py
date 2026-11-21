# Savaitinė simuliacija: paklausa -> planas -> gamyba -> atsargos -> pristatymai.
# Paslėptos istorijos:
#   1) 2026 m. liepos karščiai: paklausa ~+35 %, planuotojas to nežino.
#   3) Kretingos puodelių linija (KRE-L2) 2026 m. birželį dirba ~55 % efektyvumu.
#   Kartu jos sukelia trūkumus Lidl liepą. 2 istorija (grietinėlė) yra purchasing.py.
import math
from datetime import date, timedelta

import numpy as np

from catalog import CUSTOMERS, LINES, Product

START = date(2025, 1, 6)
END = date(2026, 10, 31)
WEEKS = [START + timedelta(weeks=i) for i in range(200) if START + timedelta(weeks=i) + timedelta(days=1) <= END]

SEASON = {
    "vasara": [0.40, 0.45, 0.60, 0.80, 1.10, 1.45, 1.70, 1.55, 0.95, 0.65, 0.50, 0.60],
    "sventes": [0.60, 0.70, 0.80, 0.90, 1.00, 1.10, 1.10, 1.00, 0.80, 0.80, 1.00, 2.20],
}
HEATWAVE = (date(2026, 6, 29), date(2026, 8, 2))
KRE_L2_DOWNTIME = {date(2026, 6, 1): 0.62, date(2026, 6, 8): 0.48, date(2026, 6, 15): 0.55, date(2026, 6, 22): 0.70}
PRICE_RISE_2026 = 1.03
PROMO_DISCOUNT = 0.20
PROMO_LIFT = 1.6
DEMAND_SCALE = 1.0  # derinama main.py, kad metinės pajamos būtų ~14 mln. €
CAPACITY_HEADROOM = 1.08  # linijos pajėgumas virš didžiausios savaitės prognozės
SAFETY_COVER = 0.5  # kiek kitos savaitės prognozės laikoma atsargose


def season_factor(week: date, profile: str) -> float:
    thursday = week + timedelta(days=3)
    return SEASON[profile][thursday.month - 1]


def growth(week: date) -> float:
    return 1.06 if week.year >= 2026 else 1.0


def heat(week: date, category: str) -> float:
    if HEATWAVE[0] <= week <= HEATWAVE[1]:
        return 1.10 if category == "Ledų tortas" else 1.35
    return 1.0


def list_price(product: Product, week: date) -> float:
    return round(product.list_price * (PRICE_RISE_2026 if week.year >= 2026 else 1.0), 4)


def build_listing(products: list[Product], rng: np.random.Generator) -> dict[tuple[str, str], bool]:
    """Kurie klientai prekiauja kuriais SKU. Lidl LT, vietiniai ir HoReCa turi viską."""
    listing = {}
    top_by_category = {}
    for p in products:
        if p.category not in top_by_category or p.base_weekly > top_by_category[p.category].base_weekly:
            top_by_category[p.category] = p
    for c in CUSTOMERS:
        code, country = c[0], c[2]
        for p in products:
            if code in ("C01", "C08", "C09"):
                listed = True
            elif p.category == "Ledų tortas":
                listed = country in ("LT", "LV", "EE")
            elif top_by_category[p.category].sku == p.sku:
                listed = True
            else:
                listed = rng.random() < 0.65
            listing[(code, p.sku)] = listed
    return listing


def build_promos(products: list[Product], rng: np.random.Generator) -> set[tuple[date, str]]:
    """Lidl akcijų savaitės pagal kategoriją. 2026 vasarą akcijų daugiau (2 istorijos dalis)."""
    promos = set()
    categories = sorted({p.category for p in products})
    for year, summer_count in ((2025, 5), (2026, 9)):
        year_weeks = [w for w in WEEKS if w.year == year]
        summer = [w for w in year_weeks if 4 <= w.month <= 9]
        other = [w for w in year_weeks if not 4 <= w.month <= 9]
        for category in categories:
            for w in rng.choice(summer, size=min(summer_count, len(summer)), replace=False):
                promos.add((w, category))
            for w in rng.choice(other, size=min(2, len(other)), replace=False):
                promos.add((w, category))
    return promos


def line_efficiency(rng: np.random.Generator) -> dict[tuple[str, date], float]:
    eff = {}
    for code, *_ in LINES:
        for w in WEEKS:
            value = float(np.clip(rng.normal(0.975, 0.02), 0.90, 1.0))
            if rng.random() < 0.03:
                value = float(rng.uniform(0.78, 0.88))
            if code == "KRE-L2" and w in KRE_L2_DOWNTIME:
                value = KRE_L2_DOWNTIME[w]
            eff[(code, w)] = value
    return eff


def simulate(products: list[Product], rng: np.random.Generator) -> dict:
    listing = build_listing(products, rng)
    promos = build_promos(products, rng)
    eff = line_efficiency(rng)
    promo_customers = {c[0] for c in CUSTOMERS if c[7]}

    sales, production, stock = [], [], []
    for p in products:
        expected = np.zeros((len(WEEKS), len(CUSTOMERS)))
        actual = np.zeros_like(expected)
        promo_flags = np.zeros_like(expected, dtype=bool)
        for wi, w in enumerate(WEEKS):
            base = p.base_weekly * DEMAND_SCALE * season_factor(w, p.season) * growth(w)
            for ci, c in enumerate(CUSTOMERS):
                if not listing[(c[0], p.sku)]:
                    continue
                is_promo = c[0] in promo_customers and (w, p.category) in promos
                lift = PROMO_LIFT if is_promo else 1.0
                expected[wi, ci] = base * c[5] * lift
                actual[wi, ci] = expected[wi, ci] * heat(w, p.category) * rng.lognormal(0, 0.12)
                promo_flags[wi, ci] = is_promo

        forecast = expected.sum(axis=1) * rng.normal(1.0, 0.04, size=len(WEEKS))
        capacity = CAPACITY_HEADROOM * forecast.max()
        inventory = 1.5 * forecast[0]
        for wi, w in enumerate(WEEKS):
            next_fc = forecast[wi + 1] if wi + 1 < len(WEEKS) else forecast[wi]
            plan = float(np.clip(forecast[wi] + SAFETY_COVER * next_fc - inventory, 0, capacity))
            plan = math.ceil(plan / 500) * 500
            e = eff[(p.line, w)]
            produced = round(plan * e)
            scrap_rate = 0.012 + abs(rng.normal(0, 0.004)) + (0.02 if e < 0.75 else 0.0)
            scrap = round(produced * scrap_rate)
            available = inventory + produced - scrap
            demand_total = actual[wi].sum()
            ratio = min(1.0, available / demand_total) if demand_total > 0 else 1.0
            delivered_total = 0
            for ci, c in enumerate(CUSTOMERS):
                ordered = round(actual[wi, ci])
                if ordered <= 0:
                    continue
                delivered = math.floor(ordered * ratio)
                delivered_total += delivered
                sales.append({
                    "week": w, "date": w + timedelta(days=1), "customer": c[0], "sku": p.sku, "ordered": ordered, "delivered": delivered,
                    "list_price": list_price(p, w), "customer_discount": c[6],
                    "promo": bool(promo_flags[wi, ci]),
                })
            inventory = available - delivered_total
            production.append({
                "week": w, "sku": p.sku, "line": p.line, "plan_code": p.plan_code, "planned": plan,
                "produced": produced, "scrap": scrap, "efficiency": e,
            })
            stock.append({"week": w, "sku": p.sku, "line": p.line, "stock": round(inventory)})
    return {"sales": sales, "production": production, "stock": stock, "promos": promos, "eff": eff}
