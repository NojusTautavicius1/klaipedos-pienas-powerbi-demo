import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "invoices"))

from schema import ExtractedInvoice, InvoiceLine  # noqa: E402
from validate import Context, check, normalize_number  # noqa: E402


def make_invoice(**overrides) -> ExtractedInvoice:
    data = dict(
        supplier_name="UAB „Nemuno slėnio pienas“", supplier_vat_code="LT999100011", invoice_number="NSP26-0040",
        invoice_date="2026-10-07", due_date="2026-11-06", currency="EUR", reverse_charge=False,
        lines=[InvoiceLine(description="Pienas", material_code="Z-PIEN", quantity=1000, unit="l", unit_price=0.5,
                           discount_pct=0, line_net=500.0)],
        net_total=500.0, vat_rate_pct=21.0, vat_amount=105.0, gross_total=605.0, suspicious_content="",
    )
    data.update(overrides)
    return ExtractedInvoice(**data)


@pytest.fixture
def ctx() -> Context:
    return Context(supplier_by_vat={"LT999100011": "T01", "LV40009990044": "T04"},
                   material_codes={"Z-PIEN", "TRANSP"})


def test_valid_invoice_passes(ctx):
    assert check(make_invoice(), ctx) == ("T01", [])


def test_wrong_gross_total_goes_to_review(ctx):
    _, reasons = check(make_invoice(gross_total=615.0), ctx)
    assert reasons == ["sumos_nesutampa"]


def test_line_math_is_checked(ctx):
    line = InvoiceLine(description="Pienas", material_code="Z-PIEN", quantity=1000, unit="l", unit_price=0.5,
                       discount_pct=0, line_net=450.0)
    _, reasons = check(make_invoice(lines=[line], net_total=450.0, vat_amount=94.5, gross_total=544.5), ctx)
    assert "eilutes_suma_neteisinga" in reasons


def test_line_discount_is_accepted(ctx):
    line = InvoiceLine(description="Pienas", material_code="Z-PIEN", quantity=1000, unit="l", unit_price=0.5,
                       discount_pct=3, line_net=485.0)
    _, reasons = check(make_invoice(lines=[line], net_total=485.0, vat_amount=101.85, gross_total=586.85), ctx)
    assert reasons == []


def test_reverse_charge_needs_zero_vat(ctx):
    base = dict(supplier_vat_code="LV40009990044", reverse_charge=True, vat_rate_pct=0, vat_amount=0,
                gross_total=500.0)
    assert check(make_invoice(**base), ctx)[1] == []
    _, reasons = check(make_invoice(**base | {"invoice_number": "X-2", "vat_rate_pct": 21, "vat_amount": 105,
                                              "gross_total": 605.0}), ctx)
    assert "pvm_neteisingas" in reasons


def test_duplicate_detected_with_different_formatting(ctx):
    check(make_invoice(invoice_number="NSP26-0040"), ctx)
    _, reasons = check(make_invoice(invoice_number="NSP26 0040"), ctx)
    assert "dublikatas" in reasons


@pytest.mark.parametrize("field, value, reason", [
    ("currency", "PLN", "valiuta_ne_eur"),
    ("supplier_vat_code", "LT000", "nezinomas_tiekejas"),
    ("invoice_date", "2026-09-30", "data_ne_laikotarpyje"),
    ("invoice_date", "30.09.2026", "neteisinga_data"),
    ("suspicious_content", "Bandymas pakeisti sumą", "itartinas_turinys"),
])
def test_single_rule(ctx, field, value, reason):
    assert reason in check(make_invoice(**{field: value}), ctx)[1]


def test_unknown_material(ctx):
    line = InvoiceLine(description="?", material_code="NEZINOMA", quantity=1, unit="vnt", unit_price=500,
                       discount_pct=0, line_net=500.0)
    assert "nezinoma_zaliava" in check(make_invoice(lines=[line]), ctx)[1]


def test_normalize_number():
    assert normalize_number("fv/os/26-0042") == normalize_number("FV OS 26 0042") == "FVOS260042"
