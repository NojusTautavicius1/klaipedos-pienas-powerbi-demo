# Žaliavų kainos, tiekėjų sąskaitos ir produktų savikaina.
# 2 istorija: grietinėlės (Z-GRIE, tiekėjas T02) kaina nuo 2026-04-01 pakyla ~18 %.
import math
from collections import defaultdict
from datetime import date, timedelta

import numpy as np

from catalog import MATERIALS, SUPPLIERS, Product
from simulate import WEEKS

CREAM_RISE_FROM = date(2026, 4, 1)
CREAM_RISE = 1.18
VAT_LT = 0.21
TRANSPORT_FEE = {"T01": 45.0, "T06": 180.0}
INVOICE_PREFIX = {"T01": "NSP", "T02": "KG", "T03": "CT", "T04": "RK", "T05": "VM", "T06": "FV/OS/", "T07": "SP"}


def month_key(d: date) -> tuple[int, int]:
    return (d.year, d.month)


def months() -> list[tuple[int, int]]:
    keys = []
    for w in WEEKS:
        for day in (w, w + timedelta(days=6)):
            if month_key(day) not in keys and day <= date(2026, 10, 31):
                keys.append(month_key(day))
    return keys


def material_prices(rng: np.random.Generator) -> dict[tuple[str, tuple[int, int]], float]:
    prices = {}
    for code, _, _, base, _, _ in MATERIALS:
        for i, (y, m) in enumerate(months()):
            factor = 1 + rng.normal(0, 0.01)
            if code == "Z-PIEN":
                factor *= 1 + 0.05 * math.cos((m - 1) / 12 * 2 * math.pi)
                factor *= 1.03 if y >= 2026 else 1.0
            elif code == "Z-GRIE" and date(y, m, 1) >= CREAM_RISE_FROM:
                factor *= CREAM_RISE
            elif code == "Z-KAKA":
                factor *= 1 + 0.01 * min(i, 12)
            elif code == "Z-SOKO":
                factor *= 1 + 0.005 * i
            prices[(code, (y, m))] = round(base * factor, 4)
    return prices


def unit_costs(products: list[Product], prices: dict) -> dict[tuple[str, tuple[int, int]], float]:
    """ERP savikaina vienetui: recepto kiekiai x mėnesio žaliavų kaina."""
    return {
        (p.sku, ym): round(sum(q * prices[(m, ym)] for m, q in p.recipe.items()), 4)
        for p in products for ym in months()
    }


def consumption_by_week(products: list[Product], production: list[dict]) -> dict:
    recipe = {p.sku: p.recipe for p in products}
    usage = defaultdict(float)
    for row in production:
        for material, qty in recipe[row["sku"]].items():
            usage[(row["week"], material)] += row["produced"] * qty
    return usage


def build_invoices(products, production, prices, rng: np.random.Generator) -> list[dict]:
    """Viena sąskaita tiekėjui per pristatymą. T04 pristato kas 2 savaites."""
    usage = consumption_by_week(products, production)
    materials_by_supplier = defaultdict(list)
    for code, name, unit, _, supplier, pack in MATERIALS:
        materials_by_supplier[supplier].append((code, name, unit, pack))

    invoices = []
    counters = defaultdict(int)
    for wi, w in enumerate(WEEKS):
        delivery = w + timedelta(days=2)
        for s_code, s_name, country, vat_code, currency, every in SUPPLIERS:
            if wi % every:
                continue
            lines = []
            for m_code, m_name, unit, pack in materials_by_supplier[s_code]:
                need = sum(usage[(WEEKS[j], m_code)] for j in range(wi, min(wi + every, len(WEEKS))))
                qty = math.ceil(need * rng.uniform(1.0, 1.04) / pack) * pack
                if qty <= 0:
                    continue
                price = round(prices[(m_code, month_key(delivery))] * (1 + rng.normal(0, 0.005)), 4)
                lines.append({"material": m_code, "description": m_name, "unit": unit, "qty": qty,
                              "unit_price": price, "discount_pct": 0.0})
            if s_code in TRANSPORT_FEE and lines:
                lines.append({"material": "TRANSP", "description": "Transportavimo paslauga", "unit": "vnt",
                              "qty": 1, "unit_price": TRANSPORT_FEE[s_code], "discount_pct": 0.0})
            if not lines:
                continue
            counters[(s_code, delivery.year)] += 1
            reverse_charge = country != "LT"
            for line in lines:
                line["net"] = round(line["qty"] * line["unit_price"] * (1 - line["discount_pct"] / 100), 2)
            net = round(sum(line["net"] for line in lines), 2)
            vat_rate = 0.0 if reverse_charge else VAT_LT
            vat = round(net * vat_rate, 2)
            invoices.append({
                "supplier": s_code, "supplier_name": s_name, "supplier_vat": vat_code, "country": country,
                "number": f"{INVOICE_PREFIX[s_code]}{delivery.strftime('%y')}-{counters[(s_code, delivery.year)]:04d}",
                "date": delivery, "due": delivery + timedelta(days=30), "currency": currency,
                "reverse_charge": reverse_charge, "lines": lines,
                "net": net, "vat_rate": vat_rate, "vat": vat, "gross": round(net + vat, 2),
            })
    return invoices
