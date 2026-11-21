# Paleidimas: python invoices/run.py [--limit N]
# PDF -> Claude -> taisyklės -> pirkimai_di.csv (Power BI), erp_importas.csv (ERP), perziura.csv (žmogui), di_zurnalas.csv
import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from extract import MODEL, build_client, extract
from schema import ExtractedInvoice
from validate import Context, check, normalize_number

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)
        writer.writerows(rows)


def num(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def build_context() -> tuple[Context, str]:
    suppliers = read_csv(RAW / "erp" / "tiekejai.csv")
    materials = read_csv(RAW / "erp" / "zaliavos.csv")
    history = {(r["TIEKEJO_KODAS"], normalize_number(r["SASKAITOS_NR"])) for r in read_csv(RAW / "erp" / "pirkimai.csv")}
    ctx = Context(
        supplier_by_vat={s["PVM_KODAS"]: s["TIEKEJO_KODAS"] for s in suppliers},
        material_codes={m["ZALIAVOS_KODAS"] for m in materials},
        known_numbers=history,
    )
    material_list = "\n".join(f"- {m['ZALIAVOS_KODAS']}: {m['PAVADINIMAS']} ({m['MATAS']})" for m in materials)
    return ctx, material_list


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="apdoroti tik N failų (bandymui)")
    args = parser.parse_args()
    load_dotenv(ROOT / ".env")

    ctx, material_list = build_context()
    client = build_client()
    pdfs = sorted((RAW / "saskaitos_pdf").glob("*.pdf"), key=lambda p: (p.name.startswith("skenuota"), p.name))
    if args.limit:
        pdfs = pdfs[: args.limit]

    approved, erp_import, review, log = [], [], [], []
    for pdf in pdfs:
        result = extract(client, pdf, material_list, CLEAN / "di_cache")
        inv = ExtractedInvoice.model_validate(result["invoice"])
        supplier, reasons = check(inv, ctx)
        status = "Patvirtinta" if not reasons else "Peržiūrai"
        usage = result["usage"]
        log.append([pdf.name, status, ",".join(reasons), usage["model"], usage["input_tokens"],
                    usage["output_tokens"], num(usage["cost_usd"], 4), num(result["seconds"], 1),
                    datetime.now().isoformat(timespec="seconds")])
        print(f"{status:12} {pdf.name:42} {', '.join(reasons)}{' (talpykla)' if result['cached'] else ''}")
        if reasons:
            review.append([pdf.name, supplier or "", inv.supplier_name, inv.invoice_number, inv.invoice_date,
                           inv.currency, num(inv.gross_total), ", ".join(reasons), inv.suspicious_content])
            continue
        vat_pct = num(inv.vat_rate_pct, 0)
        for line in inv.lines:
            approved.append([inv.invoice_number, inv.invoice_date, supplier, line.material_code, line.description,
                             num(line.quantity, 3), line.unit, num(line.unit_price, 4), num(line.discount_pct, 1),
                             num(line.line_net), vat_pct, inv.currency, "DI"])
            erp_import.append(["PIRK_SF", supplier, inv.invoice_number, inv.invoice_date, inv.due_date,
                               line.material_code, num(line.quantity, 3), num(line.unit_price, 4),
                               num(line.discount_pct, 1), num(line.line_net), vat_pct, f"DI ({MODEL}) + taisyklės"])

    write_csv(CLEAN / "pirkimai_di.csv",
              ["SASKAITOS_NR", "DATA", "TIEKEJO_KODAS", "ZALIAVOS_KODAS", "APRASYMAS", "KIEKIS", "MATAS",
               "KAINA_EUR", "NUOLAIDA_PROC", "SUMA_BE_PVM_EUR", "PVM_PROC", "VALIUTA", "SALTINIS"], approved)
    write_csv(CLEAN / "erp_importas.csv",
              ["DOK_TIPAS", "TIEKEJO_KODAS", "SF_NR", "SF_DATA", "APMOKETI_IKI", "ZALIAVOS_KODAS", "KIEKIS", "KAINA",
               "NUOLAIDA_PROC", "SUMA_BE_PVM", "PVM_PROC", "PATVIRTINO"], erp_import)
    write_csv(CLEAN / "perziura.csv",
              ["FAILAS", "TIEKEJO_KODAS", "TIEKEJAS", "SF_NR", "DATA", "VALIUTA", "SUMA", "PRIEZASTYS",
               "ITARTINAS_TURINYS"], review)
    write_csv(CLEAN / "di_zurnalas.csv",
              ["FAILAS", "STATUSAS", "PRIEZASTYS", "MODELIS", "IVESTIES_TOKENAI", "ISVESTIES_TOKENAI", "KAINA_USD",
               "TRUKME_S", "APDOROTA"], log)
    print(f"\nPatvirtinta {len(pdfs) - len(review)}, peržiūrai {len(review)}. Failai: {CLEAN}")


if __name__ == "__main__":
    sys.exit(main())
