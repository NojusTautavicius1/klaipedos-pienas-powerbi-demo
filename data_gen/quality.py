# Kokybė ir atsekamumas (RVASVT / BRC): kiekviena savaitinė gamybos partija gauna
#   - kelią per gamybos etapus su kontrolės parametrais (linijų apskaita, data/raw/linijos/partiju_etapai.csv);
#   - laboratorinius tyrimus (laboratorijos sistema, kitas CSV formatas, data/raw/laboratorija/tyrimai.csv);
#   - siuntas klientams pagal FIFO (sandėlio sistema, data/raw/sandelis/siuntos.csv);
#   - žaliavų sunaudojimą su tiekėjo sąskaita (ERP, data/raw/erp/zaliavu_sunaudojimas.csv);
#   - skundus ir partijų sprendimus (kokybės skyriaus Excel ir CSV, data/raw/kokybe/).
# Etapai yra tipinė ledų gamybos technologija, ne patvirtinta konkrečios gamyklos informacija.
# 3 istorijos tęsinys: kol KRE-L2 kompresorius genda (KRE_L2_DOWNTIME), grūdinimo tunelis nepasiekia -35 °C,
# ledai grūdinami per šiltai, juose susidaro ledo kristalai ir po kelių savaičių ateina klientų skundai.
# Naudoja atskirą atsitiktinių skaičių srautą, todėl kiti duomenys nuo šio modulio nesikeičia.
import csv
from collections import defaultdict, deque
from datetime import date, datetime, time, timedelta
from pathlib import Path

import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font

from catalog import CUSTOMERS, Product
from simulate import END, KRE_L2_DOWNTIME

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

# Užšaldymo ir fasavimo greitis, vnt./min.
LINE_RATE = {"KLA-L1": 50, "KLA-L2": 40, "KLA-L3": 14, "KRE-L1": 50, "KRE-L2": 60, "GAR-L1": 9}
LINE_MINUTES = 4800

# kategorija: (riebalai %: tikslas, min, max), (purumas %: tikslas, min, max)
SPECS = {
    "Plombyras puodelyje": ((12.5, 12.0, 14.0), (70, 60, 90)),
    "Ledai ant pagaliuko": ((10.5, 10.0, 12.0), (80, 70, 100)),
    "Ledai su vafliu": ((10.5, 10.0, 12.0), (85, 70, 100)),
    "Šeimos pakuotė": ((10.5, 10.0, 12.0), (90, 80, 110)),
    "Vaikiški ledai": ((6.5, 6.0, 8.0), (70, 60, 90)),
    "Šerbetas": ((0.4, 0.0, 1.0), (30, 20, 45)),
    "Ledų tortas": ((12.5, 12.0, 14.0), (80, 70, 100)),
}

COMPLAINT_TYPES = [
    # tipas, svoris, aprašymas, korekcinis veiksmas
    ("Pažeista pakuotė", 0.40, "Įplyšusi ar suspausta pakuotė", "Patikrintas pakavimo įrenginys ir dėžių krovimas"),
    ("Etiketė / alergenų informacija", 0.10, "Neįskaitomas galiojimo terminas ar partijos kodas",
     "Patikrintas etikečių spausdintuvas, papildyta pamainos patikra"),
    ("Skonis / kvapas", 0.15, "Pirkėjui neįprastas skonis", "Patikrinti žaliavų sertifikatai ir mišinio receptūra"),
    ("Temperatūra pristatant", 0.15, "Ledai pristatyti aptirpę", "Patikrinti vežėjo temperatūros įrašai"),
    ("Tekstūra (ledo kristalai)", 0.15, "Ledai su ledo kristalais, smėlėta tekstūra",
     "Patikrinta grūdinimo ir sandėliavimo temperatūra"),
    ("Svetimkūnis", 0.05, "Pirkėjas rado plastiko dalelę", "Patikrintos fasavimo įrangos tarpinės ir sietai"),
]
KRE_L2_ACTION = ("Pakeistas tunelio šaldymo kompresorius, įdiegta signalizacija, kai tunelyje šilčiau nei -35 °C; "
                 "paveiktos partijos peržiūrėtos")


def batch_numbers(production: list[dict]) -> list[dict]:
    """Tie patys partijų numeriai ir datos kaip export.export_production (gamyba.csv)."""
    batches = []
    for i, p in enumerate(production, start=1):
        d = p["week"] + timedelta(days=4)
        batches.append(p | {"batch": f"P{d.strftime('%y')}-{i:06d}", "erp_date": d})
    return batches


def write_csv(path: Path, header: list[str], rows: list[list], delimiter: str = ";") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(header)
        writer.writerows(rows)


def lt(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def stamp(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")


def compromised(b: dict) -> bool:
    return b["line"] == "KRE-L2" and b["week"] in KRE_L2_DOWNTIME and KRE_L2_DOWNTIME[b["week"]] < 0.75


# ---------- Siuntos (FIFO) ----------

def allocate_shipments(batches: list[dict], sales: list[dict], stock: list[dict]) -> tuple[list[dict], dict]:
    """Kiekvieną pristatymą paskirsto partijoms FIFO. Eilės priekyje 2024 m. likutis (partija nežinoma)."""
    first_week = min(b["week"] for b in batches)
    delivered0 = defaultdict(int)
    for s in sales:
        if s["week"] == first_week:
            delivered0[s["sku"]] += s["delivered"]
    queues = defaultdict(deque)
    for st in stock:
        if st["week"] == first_week:
            b0 = next(b for b in batches if b["sku"] == st["sku"] and b["week"] == first_week)
            opening = st["stock"] - b0["produced"] + b0["scrap"] + delivered0[st["sku"]]
            queues[st["sku"]].append([None, max(0, opening)])
    for b in sorted(batches, key=lambda x: x["week"]):
        queues[b["sku"]].append([b, b["produced"] - b["scrap"]])

    shipments, shipped = [], defaultdict(int)
    for s in sorted(sales, key=lambda r: (r["sku"], r["week"], r["customer"])):
        qty = s["delivered"]
        q = queues[s["sku"]]
        while qty > 0 and q:
            b, left = q[0]
            take = min(qty, left)
            if take > 0:
                shipments.append({"sale": s, "batch": b, "qty": take})
                if b is not None:
                    shipped[b["batch"]] += take
            qty -= take
            q[0][1] -= take
            if q[0][1] <= 0:
                q.popleft()
        if qty > 0:  # neturėtų nutikti (apvalinimas); jei nutiktų, matosi kaip siunta be partijos
            shipments.append({"sale": s, "batch": None, "qty": qty})
    return shipments, shipped


# ---------- Gamybos etapai ----------

def build_steps(products: dict[str, Product], batches: list[dict], rng: np.random.Generator) -> tuple[list, dict]:
    by_line_week = defaultdict(list)
    for b in batches:
        by_line_week[(b["line"], b["week"])].append(b)
    rows, deviations, timeline = [], defaultdict(list), {}
    for (line, week), group in sorted(by_line_week.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        eff = group[0]["efficiency"]
        freeze_minutes = {b["batch"]: b["produced"] / LINE_RATE[line] / max(eff, 0.3) for b in group}
        utilisation = sum(freeze_minutes.values()) / LINE_MINUTES
        group = sorted(group, key=lambda b: b["sku"])
        for k, b in enumerate(group):
            start = datetime.combine(week, time(6, 0)) + timedelta(days=5 * k / len(group),
                                                                  minutes=float(rng.uniform(0, 40)))
            bad_tunnel = compromised(b)
            steps = []
            t = start

            def step(name, minutes, control, value, lo, hi, ccp, wait=0.0):
                nonlocal t
                t += timedelta(minutes=wait)
                begin = t
                t += timedelta(minutes=minutes)
                steps.append([name, begin, t, control, value, lo, hi, ccp])

            step("Mišinio ruošimas", rng.uniform(90, 120), "Mišinio temperatūra, °C", rng.normal(65, 1.5), 60, 70, "N")
            past = rng.normal(85.0, 0.6) if rng.random() > 0.002 else rng.uniform(78.0, 79.6)
            step("Pasterizacija", 30, "Pasterizacijos temperatūra, °C", past, 80, None, "T", wait=rng.uniform(5, 15))
            step("Homogenizavimas ir aušinimas", rng.uniform(30, 45), "Mišinio temperatūra po aušinimo, °C",
                 rng.normal(3.5, 0.5), None, 5, "N", wait=rng.uniform(0, 10))
            ageing = rng.uniform(240, 300)
            step("Brandinimas", ageing, "Brandinimo trukmė, h", ageing / 60, 4, None, "N", wait=rng.uniform(0, 10))
            queue = rng.uniform(15, 60) + max(0.0, utilisation - 0.5) * 1400
            step("Šaldymas ir fasavimas", freeze_minutes[b["batch"]], "Mišinio išeigos temperatūra, °C",
                 rng.normal(-5.8, 0.22), None, -5, "N", wait=queue)
            detector_ok = rng.random() > 0.002
            step("Metalo detektorius", 5, "Etalonų patikra (1 = aptikti visi)", 1 if detector_ok else 0, 1, None, "T")
            tunnel = rng.uniform(-31, -27) if bad_tunnel else rng.normal(-38, 0.8)
            step("Grūdinimas tunelyje", rng.uniform(120, 180), "Tunelio oro temperatūra, °C", tunnel, None, -35, "N",
                 wait=rng.uniform(5, 20))
            step("Sandėliavimas", 0, "Sandėlio temperatūra, °C", rng.normal(-25, 0.6), None, -22, "N",
                 wait=rng.uniform(5, 20))
            timeline[b["batch"]] = {"freeze_day": steps[4][1].date(), "stored": steps[7][1]}
            for nr, (name, begin, end, control, value, lo, hi, ccp) in enumerate(steps, start=1):
                ok = (lo is None or value >= lo) and (hi is None or value <= hi)
                if not ok:
                    deviations[b["batch"]].append(name)
                rows.append([b["batch"], nr, name, stamp(begin), "" if name == "Sandėliavimas" else stamp(end), control,
                             lt(value, 1), "" if lo is None else lt(lo, 1), "" if hi is None else lt(hi, 1), ccp])
    return rows, deviations, timeline


# ---------- Laboratorija ----------

def lab_batch_code(batch: str, rng: np.random.Generator) -> str:
    """Laborantas partijos numerį įveda rankomis: kartais kitu formatu."""
    r = rng.random()
    if r < 0.02:
        return batch.replace("-", "/")
    if r < 0.03:
        return batch.lower()
    if r < 0.04:
        prefix, number = batch.split("-")
        return f"{prefix}-{int(number)}"
    return batch


def build_lab(products: dict[str, Product], batches: list[dict], timeline: dict, rng: np.random.Generator):
    rows, failed = [], defaultdict(list)
    for b in batches:
        p = products[b["sku"]]
        (fat_t, fat_lo, fat_hi), (ov_t, ov_lo, ov_hi) = SPECS[p.category]
        bad = compromised(b)
        tests = [
            ("Riebalai", "%", rng.normal(fat_t, 0.22), fat_lo, fat_hi),
            ("Purumas (overrun)", "%", rng.normal(ov_t, 4.5), ov_lo, ov_hi),
            ("Produkto temperatūra po grūdinimo", "°C", rng.uniform(-16.5, -12.0) if bad else rng.normal(-22, 1.1),
             None, -18),
            ("Juslinis įvertinimas", "balai", rng.choice([2, 3]) if bad else (rng.choice([4, 5], p=[0.3, 0.7])
                                                                              if rng.random() > 0.005 else 3), 4, None),
            ("Bendras mikroorganizmų skaičius", "KSV/g", float(rng.lognormal(np.log(3000), 0.9)), None, 100000),
            ("Enterobakterijos", "KSV/g", float(rng.choice([0, rng.integers(10, 90), rng.integers(110, 300)],
                                                           p=[0.85, 0.147, 0.003])), None, 100),
            ("Listeria monocytogenes", "aptikta 25 g", 0.0, None, 0),
        ]
        day = timeline[b["batch"]]["freeze_day"] + timedelta(days=1)
        code = lab_batch_code(b["batch"], rng)
        for name, unit, value, lo, hi in tests:
            value = round(float(value), 2 if unit == "%" else 1)
            if (lo is not None and value < lo) or (hi is not None and value > hi):
                failed[b["batch"]].append(name)
            rows.append([code, day.strftime("%d.%m.%Y"), name, f"{value}", unit,
                         "" if lo is None else f"{lo}", "" if hi is None else f"{hi}"])
    return rows, failed


# ---------- Žaliavų sunaudojimas ----------

def build_consumption(products: dict[str, Product], batches: list[dict], invoices: list[dict], timeline: dict):
    deliveries = defaultdict(list)  # žaliava -> [(data, sąskaitos nr, tiekėjas)]
    for inv in invoices:
        for line in inv["lines"]:
            deliveries[line["material"]].append((inv["date"], inv["number"], inv["supplier"]))
    for v in deliveries.values():
        v.sort()
    rows = []
    for b in batches:
        mix_day = timeline[b["batch"]]["freeze_day"]
        for material, qty in products[b["sku"]].recipe.items():
            candidates = [d for d in deliveries[material] if d[0] <= mix_day]
            delivery = candidates[-1] if candidates else deliveries[material][0]
            rows.append([b["batch"], material, lt(b["produced"] * qty, 3), delivery[2], delivery[1]])
    return rows


# ---------- Skundai ir sprendimai ----------

def build_complaints(shipments: list[dict], rng: np.random.Generator) -> list[list]:
    names = {c[0]: c[1] for c in CUSTOMERS}
    weights = np.array([t[1] for t in COMPLAINT_TYPES])
    rows = []
    for sh in shipments:
        b, s = sh["batch"], sh["sale"]
        if b is None:
            continue
        ship_day = max(s["date"], b["erp_date"] + timedelta(days=1))
        expected = sh["qty"] / 450_000
        if compromised(b):
            expected += sh["qty"] / 25_000
        for _ in range(rng.poisson(expected)):
            if compromised(b) and rng.random() < 0.9:
                kind = COMPLAINT_TYPES[4]
                action = KRE_L2_ACTION
            else:
                kind = COMPLAINT_TYPES[int(rng.choice(len(COMPLAINT_TYPES), p=weights / weights.sum()))]
                action = kind[3]
            received = ship_day + timedelta(days=int(rng.integers(3, 35)))
            if received > END:
                continue
            code = b["batch"] if rng.random() > 0.1 else f" {b['batch'].lower()}"
            status = "Uždarytas" if received < END - timedelta(days=14) else "Tiriamas"
            rows.append([received, names[s["customer"]], s["sku"], code, kind[0], kind[2], status,
                         action if status == "Uždarytas" else ""])
    rows.sort(key=lambda r: r[0])
    return [[f"SK-{r[0]:%y}-{i:04d}"] + r for i, r in enumerate(rows, start=1)]


def build_decisions(batches: list[dict], deviations: dict, failed: dict, timeline: dict) -> list[list]:
    rows = []
    for b in batches:
        problems = deviations.get(b["batch"], []) + failed.get(b["batch"], [])
        if not problems:
            continue
        if compromised(b):
            decision = "Išleista, dalis sunaikinta"
        elif "Pasterizacija" in problems:
            decision = "Mišinys pakartotinai pasterizuotas, išleista"
        elif any(p in problems for p in ("Bendras mikroorganizmų skaičius", "Enterobakterijos", "Metalo detektorius")):
            decision = "Sulaikyta, išleista po pakartotinio tyrimo"
        else:
            decision = "Išleista su nuokrypiu (neturi įtakos saugai)"
        day = timeline[b["batch"]]["freeze_day"] + timedelta(days=2)
        rows.append([b["batch"], decision, day.isoformat(), "; ".join(dict.fromkeys(problems)),
                     "Kokybės užtikrinimo specialistas"])
    return rows


# ---------- Eksportas ----------

def export_quality(products_list: list[Product], sim: dict, invoices: list[dict], rng: np.random.Generator) -> dict:
    products = {p.sku: p for p in products_list}
    all_batches = batch_numbers(sim["production"])
    batches = [b for b in all_batches if b["produced"] > 0]  # 0 vnt. „partijos“ ERP yra, bet realiai nebuvo gaminta
    steps, deviations, timeline = build_steps(products, batches, rng)
    lab, failed = build_lab(products, batches, timeline, rng)
    shipments, _ = allocate_shipments(all_batches, sim["sales"], sim["stock"])
    consumption = build_consumption(products, batches, invoices, timeline)
    complaints = build_complaints(shipments, rng)
    decisions = build_decisions(batches, deviations, failed, timeline)

    write_csv(RAW / "linijos" / "partiju_etapai.csv",
              ["PARTIJOS_NR", "ETAPO_NR", "ETAPAS", "PRADZIA", "PABAIGA", "KONTROLE", "REIKSME", "RIBA_MIN",
               "RIBA_MAX", "KVT"], steps)
    # Laboratorijos sistema eksportuoja kitaip: kablelis skiria laukus, taškas dešimtainėms, data dd.MM.yyyy.
    write_csv(RAW / "laboratorija" / "tyrimai.csv",
              ["Batch", "SampleDate", "Test", "Result", "Unit", "LimitMin", "LimitMax"], lab, delimiter=",")
    ship_rows, counters = [], defaultdict(int)
    for sh in sorted(shipments, key=lambda x: (x["sale"]["date"], x["sale"]["customer"], x["sale"]["sku"])):
        s, b = sh["sale"], sh["batch"]
        day = s["date"] if b is None else max(s["date"], b["erp_date"] + timedelta(days=1))
        counters[day.year] += 1
        ship_rows.append([f"S{day:%y}-{counters[day.year]:06d}", day.isoformat(), s["customer"], s["sku"],
                          "" if b is None else b["batch"], sh["qty"]])
    write_csv(RAW / "sandelis" / "siuntos.csv",
              ["SIUNTOS_NR", "DATA", "KLIENTO_KODAS", "PREKES_KODAS", "PARTIJOS_NR", "KIEKIS_VNT"], ship_rows)
    write_csv(RAW / "erp" / "zaliavu_sunaudojimas.csv",
              ["PARTIJOS_NR", "ZALIAVOS_KODAS", "KIEKIS", "TIEKEJO_KODAS", "TIEKEJO_SASKAITA"], consumption)
    write_csv(RAW / "kokybe" / "partiju_sprendimai.csv",
              ["PARTIJOS_NR", "SPRENDIMAS", "SPRENDIMO_DATA", "PRIEZASTYS", "ATSAKINGAS"], decisions)

    wb = Workbook()
    ws = wb.active
    ws.title = "Skundai"
    ws.append(["Nr.", "Gauta", "Klientas", "Prekės kodas", "Partija", "Tipas", "Aprašymas", "Būsena",
               "Korekcinis veiksmas"])
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for r in complaints:
        ws.append(r)
    for col, width in zip("ABCDEFGHI", (12, 12, 26, 12, 14, 28, 44, 12, 60)):
        ws.column_dimensions[col].width = width
    (RAW / "kokybe").mkdir(parents=True, exist_ok=True)
    wb.save(RAW / "kokybe" / "skundu_registras.xlsx")

    return {
        "partijos": len(batches),
        "etapu_eiluciu": len(steps),
        "lab_eiluciu": len(lab),
        "lab_kitu_formatu": sum(1 for r in lab if "/" in r[0] or r[0] != r[0].upper() or len(r[0]) < 10),
        "siuntu": len(ship_rows),
        "siuntu_be_partijos": sum(1 for r in ship_rows if not r[4]),
        "skundu": len(complaints),
        "kre_l2_kristalu_skundai": sum(1 for r in complaints if r[5] == "Tekstūra (ledo kristalai)"),
        "sprendimu": len(decisions),
    }
