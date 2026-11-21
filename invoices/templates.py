# Trys sąskaitų maketai: A (LT klasikinis), B (LT modernus, sumos viršuje), C (užsienio tiekėjas, EN).
from datetime import date

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", "C:/Windows/Fonts/arialbd.ttf"))

BUYER = ["AB „Klaipėdos pienas“", "Įm. kodas 000000000 (pavyzdys)", "PVM kodas LT000000000 (pavyzdys)"]
LT_MONTHS = ["sausio", "vasario", "kovo", "balandžio", "gegužės", "birželio", "liepos", "rugpjūčio", "rugsėjo",
             "spalio", "lapkričio", "gruodžio"]
W, H = A4


def lt_num(v: float, digits: int = 2) -> str:
    return f"{v:,.{digits}f}".replace(",", " ").replace(".", ",")


def en_num(v: float, digits: int = 2) -> str:
    return f"{v:,.{digits}f}"


def lt_date(d: date) -> str:
    return f"{d.year} m. {LT_MONTHS[d.month - 1]} {d.day} d."


def watermark(c: Canvas) -> None:
    c.saveState()
    c.setFillColor(Color(0.8, 0.8, 0.8, alpha=0.35))
    c.setFont("Arial-Bold", 44)
    c.translate(W / 2, H / 2)
    c.rotate(35)
    c.drawCentredString(0, 0, "PAVYZDYS")
    c.setFont("Arial", 14)
    c.drawCentredString(0, -26, "sintetiniai duomenys, ne tikras dokumentas")
    c.restoreState()


def hidden_text(c: Canvas, text: str) -> None:
    """Saugumo testas: baltas mažas tekstas, žmogus jo nemato, modelis gali perskaityti."""
    c.saveState()
    c.setFillColor(white)
    c.setFont("Arial", 4)
    c.drawString(40, 120, text)
    c.restoreState()


def table(c: Canvas, x: float, y: float, cols: list[tuple[str, float, str]], rows: list[list[str]]) -> float:
    c.setFont("Arial-Bold", 8.5)
    cx = x
    for title, width, align in cols:
        c.drawRightString(cx + width - 4, y, title) if align == "r" else c.drawString(cx + 2, y, title)
        cx += width
    c.line(x, y - 4, cx, y - 4)
    c.setFont("Arial", 8.5)
    for row in rows:
        y -= 15
        cx = x
        for (title, width, align), value in zip(cols, row):
            c.drawRightString(cx + width - 4, y, value) if align == "r" else c.drawString(cx + 2, y, value)
            cx += width
    c.line(x, y - 6, cx, y - 6)
    return y - 6


def template_a(c: Canvas, inv: dict, supplier: dict) -> None:
    c.setFont("Arial-Bold", 15)
    c.drawCentredString(W / 2, H - 60, "PVM SĄSKAITA FAKTŪRA")
    serija, nr = inv["number"][:-5], inv["number"][-4:]
    c.setFont("Arial", 10)
    c.drawCentredString(W / 2, H - 78, f"Serija {serija} Nr. {nr}")
    c.drawCentredString(W / 2, H - 92, lt_date(inv["date"]))
    c.setFont("Arial-Bold", 9)
    c.drawString(40, H - 130, "Pardavėjas")
    c.drawString(320, H - 130, "Pirkėjas")
    c.setFont("Arial", 9)
    for i, text in enumerate([supplier["name"], f"PVM mokėtojo kodas {supplier['vat']}", "Pavyzdžio g. 1, Lietuva"]):
        c.drawString(40, H - 144 - i * 12, text)
    for i, text in enumerate(BUYER):
        c.drawString(320, H - 144 - i * 12, text)
    cols = [("Nr.", 25, "l"), ("Pavadinimas", 185, "l"), ("Mato vnt.", 55, "l"), ("Kiekis", 70, "r"),
            ("Kaina, EUR", 75, "r"), ("Suma, EUR", 105, "r")]
    rows = [[str(i), ln["description"], ln["unit"], lt_num(ln["qty"], 0), lt_num(ln["unit_price"], 4), lt_num(ln["net"])]
            for i, ln in enumerate(inv["lines"], start=1)]
    y = table(c, 40, H - 210, cols, rows)
    c.setFont("Arial", 9.5)
    for i, (label, value) in enumerate([("Suma be PVM:", inv["net"]), ("PVM 21 %:", inv["vat"]),
                                        ("Iš viso su PVM:", inv["gross_printed"])]):
        c.drawRightString(430, y - 20 - i * 14, label)
        c.drawRightString(555, y - 20 - i * 14, lt_num(value))
    c.drawString(40, y - 80, f"Apmokėti iki {inv['due'].isoformat()}. Bankas: LT00 0000 0000 0000 0000 (pavyzdys)")


def template_b(c: Canvas, inv: dict, supplier: dict) -> None:
    c.setFillColor(HexColor("#1F4E79"))
    c.rect(0, H - 70, W, 70, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Arial-Bold", 18)
    c.drawString(40, H - 45, supplier["name"])
    c.setFillColor(HexColor("#000000"))
    c.setFont("Arial-Bold", 12)
    c.drawString(40, H - 100, f"Sąskaita faktūra {inv['number']}")
    c.setFont("Arial", 9)
    c.drawString(40, H - 116, f"Išrašymo data: {inv['date'].isoformat()}    Apmokėjimo terminas: {inv['due'].isoformat()}")
    c.drawString(40, H - 130, f"Tiekėjo PVM kodas: {supplier['vat']}")
    c.drawString(40, H - 144, "Klientas: " + ", ".join(BUYER[:1]))
    c.roundRect(370, H - 150, 185, 62, 6)
    c.setFont("Arial", 9)
    c.drawString(380, H - 104, f"Be PVM: {lt_num(inv['net'])} €")
    c.drawString(380, H - 118, f"PVM (21 %): {lt_num(inv['vat'])} €")
    c.setFont("Arial-Bold", 11)
    c.drawString(380, H - 138, f"MOKĖTI: {lt_num(inv['gross_printed'])} €")
    has_discount = any(ln["discount_pct"] for ln in inv["lines"])
    cols = [("Prekė / paslauga", 190, "l"), ("Kaina €", 70, "r"), ("Kiekis", 70, "r"), ("Vnt.", 40, "l")]
    if has_discount:
        cols.append(("Nuolaida", 50, "r"))
    cols.append(("Suma €", 95, "r"))
    rows = []
    for ln in inv["lines"]:
        row = [ln["description"], lt_num(ln["unit_price"], 4), lt_num(ln["qty"], 0), ln["unit"]]
        if has_discount:
            row.append(f"{lt_num(ln['discount_pct'], 0)} %")
        rows.append(row + [lt_num(ln["net"])])
    table(c, 40, H - 190, cols, rows)


def template_c(c: Canvas, inv: dict, supplier: dict) -> None:
    title = "INVOICE / RĒĶINS" if supplier["country"] == "LV" else "FAKTURA VAT / INVOICE"
    cur = inv["currency"]
    c.setFont("Arial-Bold", 16)
    c.drawString(40, H - 60, title)
    c.setFont("Arial", 9)
    c.drawRightString(555, H - 50, f"No. {inv['number']}")
    c.drawRightString(555, H - 64, f"Date: {inv['date'].strftime('%d.%m.%Y')}")
    c.drawRightString(555, H - 78, f"Due: {inv['due'].strftime('%d.%m.%Y')}")
    c.drawString(40, H - 100, f"Seller: {supplier['name']}, VAT No. {supplier['vat']}")
    c.drawString(40, H - 114, f"Buyer: {BUYER[0]}, VAT No. LT000000000")
    cols = [("Description", 200, "l"), ("Qty", 70, "r"), ("Unit", 40, "l"), (f"Unit price {cur}", 85, "r"),
            (f"Amount {cur}", 100, "r")]
    rows = [[ln["description"], en_num(ln["qty"], 0), ln["unit"], en_num(ln["unit_price"], 4), en_num(ln["net"])]
            for ln in inv["lines"]]
    y = table(c, 40, H - 150, cols, rows)
    c.setFont("Arial", 9.5)
    c.drawRightString(430, y - 20, f"Net total ({cur}):")
    c.drawRightString(555, y - 20, en_num(inv["net"]))
    c.drawRightString(430, y - 34, "VAT 0 %:")
    c.drawRightString(555, y - 34, en_num(0))
    c.setFont("Arial-Bold", 10)
    c.drawRightString(430, y - 50, f"TOTAL ({cur}):")
    c.drawRightString(555, y - 50, en_num(inv["gross_printed"]))
    c.setFont("Arial", 8.5)
    c.drawString(40, y - 80, "Reverse charge – VAT to be accounted for by the recipient (Art. 196 Directive 2006/112/EC).")


TEMPLATES = {"A": template_a, "B": template_b, "C": template_c}
TEMPLATE_BY_SUPPLIER = {"T01": "A", "T02": "A", "T03": "A", "T04": "C", "T05": "B", "T06": "C", "T07": "B"}
