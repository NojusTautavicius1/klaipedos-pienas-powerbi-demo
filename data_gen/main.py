# Paleidimas: python data_gen/main.py
# Sugeneruoja visus „ERP“ eksportus, Excel planą ir spalio sąskaitų tiesą (PDF generuoja invoices/make_pdfs.py).
from collections import defaultdict
from datetime import date

import numpy as np

import export
import quality
import simulate
from catalog import CUSTOMERS, build_products
from finance import build_finance
from purchasing import build_invoices, material_prices, unit_costs

SEED = 20261121
TARGET_REVENUE_2025 = 14_000_000


def net_revenue(rows: list[dict], year: int) -> float:
    return sum(r["delivered"] * r["list_price"] * (1 - r["customer_discount"]) * (0.8 if r["promo"] else 1.0)
               for r in rows if r["date"].year == year)


def run(scale: float):
    simulate.DEMAND_SCALE = scale
    rng = np.random.default_rng(SEED)
    products = build_products()
    sim = simulate.simulate(products, rng)
    prices = material_prices(rng)
    costs = unit_costs(products, prices)
    return rng, products, sim, prices, costs


def story_checks(sim: dict, costs: dict, prices: dict) -> None:
    country_of = {c[0]: c[2] for c in CUSTOMERS}
    print("\n--- Istorijų patikra ---")
    for year in (2025, 2026):
        rev = net_revenue(sim["sales"], year)
        cogs = sum(r["delivered"] * costs[(r["sku"], (r["date"].year, r["date"].month))]
                   for r in sim["sales"] if r["date"].year == year)
        print(f"{year}: pajamos {rev / 1e6:.2f} mln. €, žaliavų marža {(1 - cogs / rev) * 100:.1f} %")

    margin = defaultdict(lambda: [0.0, 0.0])
    for r in sim["sales"]:
        ym = (r["date"].year, r["date"].month)
        net = r["delivered"] * r["list_price"] * (1 - r["customer_discount"]) * (0.8 if r["promo"] else 1.0)
        margin[ym][0] += net
        margin[ym][1] += r["delivered"] * costs[(r["sku"], ym)]
    print("Marža %: mėn. 2025 -> 2026")
    for m in range(4, 10):
        a, b = margin[(2025, m)], margin[(2026, m)]
        print(f"  {m:02d}: {(1 - a[1] / a[0]) * 100:.1f} -> {(1 - b[1] / b[0]) * 100:.1f}")

    print(f"Grietinėlė €/kg: 2026-03 {prices[('Z-GRIE', (2026, 3))]}, 2026-04 {prices[('Z-GRIE', (2026, 4))]}")

    line_of = {p["sku"]: p["line"] for p in sim["production"]}
    fill = defaultdict(lambda: [0, 0])
    for r in sim["sales"]:
        if r["date"].year in (2025, 2026) and 5 <= r["date"].month <= 8:
            k = (line_of[r["sku"]], r["date"].year, r["date"].month)
            fill[k][0] += r["delivered"]
            fill[k][1] += r["ordered"]
    print("Pristatyta / užsakyta % (gegužė–rugpjūtis):")
    for line in sorted({k[0] for k in fill}):
        cells = [f"{y}-{m:02d} {fill[(line, y, m)][0] / fill[(line, y, m)][1] * 100:3.0f}"
                 for y in (2025, 2026) for m in range(5, 9)]
        print(f"  {line}: " + " | ".join(cells))
    lost = defaultdict(float)
    for r in sim["sales"]:
        if r["date"].year == 2026 and r["date"].month in (6, 7, 8):
            lost["Lidl" if r["customer"] in ("C01", "C02", "C03") else "kiti"] += r["ordered"] - r["delivered"]
    print("Prarasti vnt. 2026 VI–VIII:", {k: f"{v:,.0f}" for k, v in lost.items()})

    for ym in ((2026, 6), (2026, 7)):
        rows = [p for p in sim["production"] if p["line"] == "KRE-L2" and (p["week"].year, p["week"].month) == ym]
        print(f"KRE-L2 {ym[0]}-{ym[1]:02d}: planas {sum(p['planned'] for p in rows):,}, "
              f"pagaminta {sum(p['produced'] for p in rows):,}")

    print("Užsakyta / prognozė pagal šalį, 2026-06-22 savaitė ir VI–VIII:")
    for country in sorted({f["country"] for f in sim["forecast"]}):
        for label, weeks in (("06-22", {date(2026, 6, 22)}),
                             ("VI-VIII", {w for w in {f["week"] for f in sim["forecast"]} if w.year == 2026 and 6 <= w.month <= 8})):
            fc = sum(f["forecast"] for f in sim["forecast"] if f["country"] == country and f["week"] in weeks)
            od = sum(r["ordered"] for r in sim["sales"] if r["week"] in weeks and country_of[r["customer"]] == country)
            print(f"  {country} {label}: {od / fc * 100:5.1f} %  (anomalija {sim['anomaly'][(country, date(2026, 6, 22))]:+.1f} °C)"
                  if label == "06-22" else f"  {country} {label}: {od / fc * 100:5.1f} %")


def main() -> None:
    _, _, sim, _, _ = run(1.0)
    scale = TARGET_REVENUE_2025 / net_revenue(sim["sales"], 2025)
    rng, products, sim, prices, costs = run(scale)
    invoices = build_invoices(products, sim["production"], prices, rng)
    actuals, budget = build_finance(sim["sales"], sim["promos"], costs, rng)

    export.export_dimensions(products)
    dq = export.export_sales(sim["sales"], costs, rng)
    export.export_production(sim["production"], sim["eff"], rng)
    export.export_plan_excel(sim["production"], sim["forecast"], rng)
    export.export_stock(sim["stock"])
    october = export.export_purchases(invoices)
    export.export_finance(actuals, budget)
    export.write_truth("dq_tiesa.json", dq)
    export.write_truth("spalio_saskaitos.json", october)
    q = quality.export_quality(products, sim, invoices, np.random.default_rng(SEED + 1))
    export.write_truth("kokybe_tiesa.json", q)

    print(f"Mastelis {scale:.3f}; pardavimų eilučių {len(sim['sales']):,}; sąskaitų {len(invoices)}, "
          f"iš jų spalio (PDF) {len(october)}")
    print("DQ:", dq)
    print("Kokybė:", q)
    story_checks(sim, costs, prices)


if __name__ == "__main__":
    main()
