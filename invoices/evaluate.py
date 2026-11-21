# Paleidimas: python invoices/evaluate.py (po run.py)
# Lygina DI rezultatą su tiesa (PDF generavome patys, todėl žinome teisingus atsakymus) ir rašo docs/di_tikslumas.md.
import csv
import json
from pathlib import Path

from validate import normalize_number

ROOT = Path(__file__).resolve().parent.parent
MANUAL_MINUTES_PER_INVOICE = 4  # prielaida: rankinis vienos sąskaitos suvedimas ir patikra


def same(a, b) -> bool:
    if isinstance(b, float) or isinstance(a, float):
        return abs(float(a) - float(b)) <= 0.005
    return a == b


def compare(truth: dict, got: dict) -> dict[str, bool]:
    checks = {
        "tiekėjo PVM kodas": got["supplier_vat_code"] == truth["supplier_vat"],
        "sąskaitos numeris": normalize_number(got["invoice_number"]) == normalize_number(truth["number"]),
        "data": got["invoice_date"] == truth["date"],
        "valiuta": got["currency"] == truth["currency"],
        "atvirkštinis PVM": got["reverse_charge"] == truth["reverse_charge"],
        "suma be PVM": same(got["net_total"], truth["net"]),
        "PVM suma": same(got["vat_amount"], truth["vat"]),
        "suma su PVM": same(got["gross_total"], truth["gross_printed"]),
        "eilučių skaičius": len(got["lines"]) == len(truth["lines"]),
    }
    pairs = list(zip(truth["lines"], got["lines"]))
    for field, key in (("kiekis", "qty"), ("kaina", "unit_price"), ("nuolaida", "discount_pct"),
                       ("eilutės suma", "net")):
        got_key = {"qty": "quantity", "net": "line_net"}.get(key, key)
        checks[f"eilutė: {field}"] = all(same(g[got_key], t[key]) for t, g in pairs)
    checks["eilutė: žaliavos kodas"] = all(g["material_code"] == t["material"] for t, g in pairs)
    return checks


def main() -> None:
    truth = json.loads((ROOT / "data" / "truth" / "pdf_tiesa.json").read_text(encoding="utf-8"))
    with (ROOT / "data" / "clean" / "di_zurnalas.csv").open(encoding="utf-8-sig") as f:
        log = {r["FAILAS"]: r for r in csv.DictReader(f, delimiter=";")}

    field_ok, rows, errors = {}, [], []
    cost = seconds = 0.0
    for t in truth:
        cached = json.loads((ROOT / "data" / "clean" / "di_cache" / f"{Path(t['file']).stem}.json")
                            .read_text(encoding="utf-8"))
        checks = compare(t, cached["invoice"])
        for name, ok in checks.items():
            field_ok.setdefault(name, []).append(ok)
            if not ok:
                errors.append(f"{t['file']}: {name}")
        entry = log[t["file"]]
        status_ok = entry["STATUSAS"] == t["expected_status"]
        reasons_ok = set(filter(None, entry["PRIEZASTYS"].split(","))) == set(t["expected_reasons"])
        rows.append((t["file"], t["trap"] or "", t["expected_status"], entry["STATUSAS"], status_ok and reasons_ok))
        cost += cached["usage"]["cost_usd"]
        seconds += cached["seconds"]

    total_fields = sum(len(v) for v in field_ok.values())
    correct_fields = sum(sum(v) for v in field_ok.values())
    decisions_ok = sum(r[4] for r in rows)
    n = len(truth)
    lines = [
        "# DI sąskaitų nuskaitymo tikslumas",
        "",
        "Sintetinės sąskaitos (PAVYZDYS). Teisingi atsakymai žinomi, nes PDF sugeneruoti iš tų pačių duomenų.",
        "",
        f"- Sąskaitų: **{n}** (iš jų {sum(1 for t in truth if t['trap'])} su specialiais „spąstais“)",
        f"- Laukų tikslumas: **{correct_fields}/{total_fields} ({correct_fields / total_fields * 100:.1f} %)**",
        f"- Teisingas sprendimas (patvirtinti / į peržiūrą su teisinga priežastimi): **{decisions_ok}/{n}**",
        f"- Kaina: **{cost:.2f} $** iš viso, {cost / n:.3f} $ už sąskaitą (Claude Opus 5.5)",
        f"- Laikas: {seconds / 60:.1f} min. DI vs ~{n * MANUAL_MINUTES_PER_INVOICE} min. rankomis "
        f"(prielaida: {MANUAL_MINUTES_PER_INVOICE} min. sąskaitai)",
        "",
        "## Laukai",
        "",
        "| Laukas | Teisingai |",
        "|---|---|",
        *[f"| {name} | {sum(v)}/{len(v)} |" for name, v in field_ok.items()],
        "",
        "## Spąstai ir sprendimai",
        "",
        "| Failas | Spąstai | Tikėtasi | Gauta | OK |",
        "|---|---|---|---|---|",
        *[f"| {f} | {trap} | {exp} | {got} | {'✅' if ok else '❌'} |" for f, trap, exp, got, ok in rows if trap],
        "",
        "## Klaidos",
        "",
        *([f"- {e}" for e in errors] or ["Nėra."]),
    ]
    out = ROOT / "docs" / "di_tikslumas.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[4:9]))
    print("Klaidos:", errors or "nėra")


if __name__ == "__main__":
    main()
