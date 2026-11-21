# Rašo failus taip, kaip juos išduotų savos gamybos ERP ir planuotojo Excel:
# CSV su ';', dešimtainis kablelis, pardavimai po failą per mėnesį, kelios tyčinės kokybės klaidos.
import csv
import json
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font

from catalog import CUSTOMERS, LINES, MATERIALS, SUPPLIERS, Product

ROOT = Path(__file__).resolve().parent.parent
ERP = ROOT / "data" / "raw" / "erp"
EXCEL = ROOT / "data" / "raw" / "excel"
TRUTH = ROOT / "data" / "truth"
ERP_PURCHASES_UNTIL = date(2026, 9, 30)  # spalio sąskaitos dar neįvestos: jas suves DI

DOWNTIME_REASONS = ["Planinis valymas", "Produkto keitimas (derinimas)", "Pakavimo įrangos gedimas",
                    "Žaliavų trūkumas", "Elektros sutrikimas"]
KRE_L2_REASONS = ["Šaldymo kompresoriaus gedimas", "Laukiama atsarginių dalių", "Šaldymo tunelio remontas",
                  "Paleidimas po remonto"]


def num(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)
        writer.writerows(rows)


def export_dimensions(products: list[Product]) -> None:
    write_csv(ERP / "produktai.csv",
              ["PREKES_KODAS", "PAVADINIMAS", "PREKES_ZENKLAS", "KATEGORIJA", "TURIS_ML", "LINIJA", "PLANO_KODAS",
               "BAZINE_KAINA_EUR"],
              [[p.sku, p.name, p.brand, p.category, p.volume_ml, p.line, p.plan_code, num(p.list_price, 4)]
               for p in products])
    write_csv(ERP / "receptai.csv", ["PREKES_KODAS", "ZALIAVOS_KODAS", "KIEKIS_VNT"],
              [[p.sku, m, num(q, 5)] for p in products for m, q in p.recipe.items()])
    write_csv(ERP / "klientai.csv", ["KLIENTO_KODAS", "PAVADINIMAS", "SALIS", "RINKA", "VADYBININKAS"],
              [[c[0], c[1], c[2], c[3], c[4]] for c in CUSTOMERS])
    write_csv(ERP / "tiekejai.csv", ["TIEKEJO_KODAS", "PAVADINIMAS", "SALIS", "PVM_KODAS", "VALIUTA"],
              [[s[0], s[1], s[2], s[3], s[4]] for s in SUPPLIERS])
    write_csv(ERP / "zaliavos.csv", ["ZALIAVOS_KODAS", "PAVADINIMAS", "MATAS", "TIEKEJO_KODAS"],
              [[m[0], m[1], m[2], m[4]] for m in MATERIALS] + [["TRANSP", "Transportavimo paslauga", "vnt", ""]])
    write_csv(ERP / "linijos.csv", ["LINIJOS_KODAS", "GAMYKLA", "PAVADINIMAS", "MINUTES_PER_SAVAITE"],
              [list(line) for line in LINES])


def export_sales(sales: list[dict], unit_cost: dict, rng: np.random.Generator) -> dict:
    invoice_no = {}
    by_month = defaultdict(list)
    dq = {"dublikatai": 0, "nesutvarkyti_kliento_kodai": 0, "truksta_kliento": 0}
    for row in sales:
        d = row["date"]
        key = (row["week"], row["customer"])
        if key not in invoice_no:
            invoice_no[key] = f"PS{d.strftime('%y')}-{len(invoice_no) + 1:06d}"
        discount = 1 - (1 - row["customer_discount"]) * (1 - (0.2 if row["promo"] else 0.0))
        customer = row["customer"]
        r = rng.random()
        if r < 0.001:
            customer, dq["truksta_kliento"] = "", dq["truksta_kliento"] + 1
        elif r < 0.006:
            customer, dq["nesutvarkyti_kliento_kodai"] = f" {customer.lower()} ", dq["nesutvarkyti_kliento_kodai"] + 1
        line = [invoice_no[key], d.isoformat(), customer, row["sku"], row["ordered"], row["delivered"],
                num(row["list_price"], 4), num(discount * 100, 1), "T" if row["promo"] else "N",
                num(unit_cost[(row["sku"], (d.year, d.month))], 4)]
        by_month[(d.year, d.month)].append(line)
        if rng.random() < 0.003:
            by_month[(d.year, d.month)].append(line)
            dq["dublikatai"] += 1
    header = ["SASKAITOS_NR", "DATA", "KLIENTO_KODAS", "PREKES_KODAS", "UZSAKYTA_VNT", "PRISTATYTA_VNT",
              "KAINA_EUR", "NUOLAIDA_PROC", "AKCIJA", "SAVIKAINA_VNT_EUR"]
    for (y, m), rows in sorted(by_month.items()):
        write_csv(ERP / "pardavimai" / f"pardavimai_{y}-{m:02d}.csv", header, rows)
    return dq


def export_production(production: list[dict], eff: dict, rng: np.random.Generator) -> None:
    rows = []
    for i, p in enumerate(production, start=1):
        d = p["week"] + timedelta(days=4)
        rows.append([f"P{d.strftime('%y')}-{i:06d}", d.isoformat(), p["line"], p["sku"], p["produced"], p["scrap"]])
    write_csv(ERP / "gamyba.csv", ["PARTIJOS_NR", "DATA", "LINIJA", "PREKES_KODAS", "PAGAMINTA_VNT", "BROKAS_VNT"],
              rows)

    downtime = []
    minutes = {code: m for code, _, _, m in LINES}
    for (line, week), e in sorted(eff.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        total = round((1 - e) * minutes[line] * 0.9 + rng.uniform(0, 20))
        if total < 30:
            continue
        if line == "KRE-L2" and e < 0.75:
            reason = KRE_L2_REASONS[min(len(KRE_L2_REASONS) - 1, (week.day - 1) // 7)]
        else:
            reason = DOWNTIME_REASONS[int(rng.integers(len(DOWNTIME_REASONS)))]
        downtime.append([week.isoformat(), line, total, reason])
    write_csv(ERP / "prastovos.csv", ["SAVAITES_PRADZIA", "LINIJA", "PRASTOVOS_MIN", "PRIEZASTIS"], downtime)


def export_plan_excel(production: list[dict], rng: np.random.Generator) -> None:
    """Planuotojo Excel: pavadinimo eilutė virš lentelės, plano kodai (ne ERP kodai), kartais tarpai."""
    wb = Workbook()
    wb.remove(wb.active)
    for year in (2025, 2026):
        ws = wb.create_sheet(str(year))
        ws.append([f"GAMYBOS PLANAS {year} (v3 galutinis)"])
        ws["A1"].font = Font(bold=True, size=14)
        ws.append([])
        ws.append(["Savaitė", "Savaitės pradžia", "Linija", "Produktas", "Planas, vnt"])
        for p in (r for r in production if r["week"].year == year):
            iso = p["week"].isocalendar()
            code = p["plan_code"] + (" " if rng.random() < 0.02 else "")
            ws.append([f"{iso.year}-W{iso.week:02d}", p["week"], p["line"], code, p["planned"]])
        for col, width in zip("ABCDE", (10, 16, 10, 20, 12)):
            ws.column_dimensions[col].width = width
    EXCEL.mkdir(parents=True, exist_ok=True)
    wb.save(EXCEL / "gamybos_planas.xlsx")


def export_stock(stock: list[dict]) -> None:
    plant = {code: name for code, name, _, _ in LINES}
    write_csv(ERP / "atsargos.csv", ["DATA", "PREKES_KODAS", "SANDELIS", "LIKUTIS_VNT"],
              [[(s["week"] + timedelta(days=6)).isoformat(), s["sku"], plant[s["line"]], s["stock"]] for s in stock])


def export_purchases(invoices: list[dict]) -> list[dict]:
    rows, october = [], []
    for inv in invoices:
        if inv["date"] > ERP_PURCHASES_UNTIL:
            october.append(inv)
            continue
        for line in inv["lines"]:
            rows.append([inv["number"], inv["date"].isoformat(), inv["supplier"], line["material"],
                         line["description"], num(line["qty"], 3), line["unit"], num(line["unit_price"], 4),
                         num(line["discount_pct"], 1), num(line["net"]), num(inv["vat_rate"] * 100, 0),
                         inv["currency"], "ERP"])
    write_csv(ERP / "pirkimai.csv",
              ["SASKAITOS_NR", "DATA", "TIEKEJO_KODAS", "ZALIAVOS_KODAS", "APRASYMAS", "KIEKIS", "MATAS",
               "KAINA_EUR", "NUOLAIDA_PROC", "SUMA_BE_PVM_EUR", "PVM_PROC", "VALIUTA", "SALTINIS"], rows)
    return october


def export_finance(actuals: list[dict], budget: list[dict]) -> None:
    write_csv(ERP / "finansai_sanaudos.csv", ["DATA", "KASTU_CENTRAS", "STRAIPSNIS", "SUMA_EUR"],
              [[a["date"].isoformat(), a["centre"], a["item"], num(a["amount"])] for a in actuals])
    write_csv(ERP / "biudzetas.csv", ["METAI", "MENUO", "STRAIPSNIS", "SUMA_EUR"],
              [[b["year"], b["month"], b["item"], num(b["amount"])] for b in budget])


def write_truth(name: str, payload) -> None:
    TRUTH.mkdir(parents=True, exist_ok=True)
    (TRUTH / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
