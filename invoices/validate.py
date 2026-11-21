# Taisyklės, kurios tikrina DI rezultatą. Modeliu nepasitikime aklai: viskas, kas nepraeina, keliauja žmogui.
import re
from dataclasses import dataclass, field
from datetime import date

from schema import ExtractedInvoice

TOLERANCE = 0.02
VAT_LT = 21.0


@dataclass
class Context:
    supplier_by_vat: dict[str, str]  # PVM kodas -> tiekėjo kodas
    material_codes: set[str]
    known_numbers: set[tuple[str, str]] = field(default_factory=set)  # (tiekėjas, normalizuotas numeris)
    period: tuple[date, date] = (date(2026, 10, 1), date(2026, 10, 31))


def normalize_number(number: str) -> str:
    return re.sub(r"[^0-9A-Z]", "", number.upper())


def close(a: float, b: float, tolerance: float = TOLERANCE) -> bool:
    return abs(a - b) <= tolerance


def check(inv: ExtractedInvoice, ctx: Context) -> tuple[str | None, list[str]]:
    """Grąžina (tiekėjo kodas, priežasčių sąrašas). Tuščias sąrašas reiškia, kad sąskaita patvirtinta."""
    reasons = []
    supplier = ctx.supplier_by_vat.get(inv.supplier_vat_code.replace(" ", "").upper())
    if supplier is None:
        reasons.append("nezinomas_tiekejas")
    if inv.currency.upper() != "EUR":
        reasons.append("valiuta_ne_eur")
    try:
        issued = date.fromisoformat(inv.invoice_date)
        if not ctx.period[0] <= issued <= ctx.period[1]:
            reasons.append("data_ne_laikotarpyje")
    except ValueError:
        reasons.append("neteisinga_data")

    if not inv.lines:
        reasons.append("nera_eiluciu")
    for line in inv.lines:
        expected = line.quantity * line.unit_price * (1 - line.discount_pct / 100)
        if not close(expected, line.line_net, max(TOLERANCE, 0.001 * abs(line.line_net))):
            reasons.append("eilutes_suma_neteisinga")
            break
    if any(line.material_code not in ctx.material_codes for line in inv.lines):
        reasons.append("nezinoma_zaliava")

    lines_total = sum(line.line_net for line in inv.lines)
    if not close(lines_total, inv.net_total) or not close(inv.net_total + inv.vat_amount, inv.gross_total):
        reasons.append("sumos_nesutampa")
    if inv.reverse_charge:
        vat_ok = inv.vat_rate_pct == 0 and close(inv.vat_amount, 0)
    else:
        vat_ok = inv.vat_rate_pct == VAT_LT and close(inv.net_total * VAT_LT / 100, inv.vat_amount)
    if not vat_ok:
        reasons.append("pvm_neteisingas")

    key = (supplier or inv.supplier_vat_code, normalize_number(inv.invoice_number))
    if key in ctx.known_numbers:
        reasons.append("dublikatas")
    ctx.known_numbers.add(key)

    if inv.suspicious_content.strip():
        reasons.append("itartinas_turinys")
    return supplier, reasons
