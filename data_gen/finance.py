# Mėnesio veiklos sąnaudos pagal kaštų centrus ir biudžetas.
from collections import defaultdict
from datetime import date, timedelta

import numpy as np

from purchasing import months
from simulate import SEASON

COST_CENTRES = {
    "Energija": "Gamyba",
    "Darbo užmokestis": "Gamyba",
    "Remontas ir priežiūra": "Gamyba",
    "Logistika": "Pardavimai",
    "Marketingas": "Pardavimai",
    "Administracija": "Administracija",
}
KRE_L2_REPAIR = 42000.0  # 3 istorija: Kretingos linijos remontas 2026 m. birželį


def planned_cost(item: str, year: int, month: int, units: float, promo_weeks: int) -> float:
    season = SEASON["vasara"][month - 1]
    y26 = year >= 2026
    if item == "Energija":
        return 70000 * (0.7 + 0.3 * season) * (1.08 if y26 else 1.0)
    if item == "Darbo užmokestis":
        return 230000 * (1.07 if y26 else 1.0) + 40000 * season
    if item == "Remontas ir priežiūra":
        return 18000.0
    if item == "Logistika":
        return 0.03 * units
    if item == "Marketingas":
        return 30000 + 8000 * promo_weeks
    return 55000 * (1.04 if y26 else 1.0)


def build_finance(sales: list[dict], promos: set, unit_cost: dict, rng: np.random.Generator):
    units = defaultdict(float)
    revenue = defaultdict(float)
    cogs = defaultdict(float)
    for row in sales:
        ym = (row["date"].year, row["date"].month)
        net_price = row["list_price"] * (1 - row["customer_discount"]) * (0.8 if row["promo"] else 1.0)
        units[ym] += row["delivered"]
        revenue[ym] += row["delivered"] * net_price
        cogs[ym] += row["delivered"] * unit_cost[(row["sku"], ym)]
    promo_weeks = defaultdict(int)
    for week, _category in promos:
        promo_weeks[(week.year, week.month)] += 1

    actuals, budget = [], []
    for y, m in months():
        month_end = date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)
        for item, centre in COST_CENTRES.items():
            value = planned_cost(item, y, m, units[(y, m)], promo_weeks[(y, m)])
            actual = value * rng.normal(1.0, 0.03)
            if item == "Remontas ir priežiūra" and (y, m) == (2026, 6):
                actual += KRE_L2_REPAIR
            actuals.append({"date": month_end, "centre": centre, "item": item, "amount": round(actual, 2)})
            budget.append({"year": y, "month": m, "item": item, "amount": round(value, 2)})

        prev = (y - 1, m)
        if y == 2025:
            rev_budget = revenue[(y, m)] * rng.normal(1.0, 0.03)
            margin = 1 - cogs[(y, m)] / revenue[(y, m)]
        else:
            rev_budget = revenue[prev] * 1.06 * 1.03
            margin = 1 - cogs[prev] / revenue[prev]
        budget.append({"year": y, "month": m, "item": "Pajamos", "amount": round(rev_budget, 2)})
        budget.append({"year": y, "month": m, "item": "Bendrasis pelnas", "amount": round(rev_budget * margin, 2)})
    return actuals, budget
