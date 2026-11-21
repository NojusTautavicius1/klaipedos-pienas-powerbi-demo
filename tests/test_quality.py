import csv
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data_gen"))

from quality import allocate_shipments, lab_batch_code  # noqa: E402

W1 = date(2025, 1, 6)
W2 = W1 + timedelta(weeks=1)


def batch(nr, week, produced, scrap=0):
    return {"batch": nr, "week": week, "sku": "100101", "produced": produced, "scrap": scrap,
            "erp_date": week + timedelta(days=4)}


def sale(week, customer, delivered):
    return {"week": week, "date": week + timedelta(days=1), "customer": customer, "sku": "100101",
            "delivered": delivered}


def test_fifo_uses_opening_stock_first_then_oldest_batch():
    batches = [batch("P25-000001", W1, 100, 10), batch("P25-000002", W2, 100)]
    # Pradinis likutis 50: stock po 1 sav. = 50 + 100 - 10 - 120 = 20
    sales = [sale(W1, "C01", 120), sale(W2, "C01", 60)]
    stock = [{"week": W1, "sku": "100101", "stock": 20}]
    shipments, shipped = allocate_shipments(batches, sales, stock)

    first_week = [(s["batch"]["batch"] if s["batch"] else None, s["qty"]) for s in shipments if s["sale"]["week"] == W1]
    assert first_week == [(None, 50), ("P25-000001", 70)]
    assert shipped == {"P25-000001": 90, "P25-000002": 40}


def test_fifo_never_ships_more_than_batch_has():
    rng = np.random.default_rng(1)
    batches = [batch(f"P25-{i:06d}", W1 + timedelta(weeks=i), int(rng.integers(50, 150)), 5) for i in range(10)]
    sales = [sale(b["week"], "C01", b["produced"] - 5) for b in batches]
    stock = [{"week": W1, "sku": "100101", "stock": 0}]
    _, shipped = allocate_shipments(batches, sales, stock)
    for b in batches:
        assert shipped[b["batch"]] <= b["produced"] - b["scrap"]


def normalise(code: str) -> str:
    """Ta pati taisyklė kaip Power Query lentelėje „Lab tyrimai“."""
    t = code.replace("/", "-").strip().upper()
    prefix, number = t.split("-")
    return f"{prefix}-{number.zfill(6)}"


def test_lab_codes_normalise_back_to_erp_format():
    rng = np.random.default_rng(3)
    codes = {lab_batch_code("P26-000370", rng) for _ in range(2000)}
    assert {"P26-000370", "P26/000370", "p26-000370", "P26-370"} <= codes
    assert {normalise(c) for c in codes} == {"P26-000370"}


def test_generated_lab_rows_all_match_erp_batches():
    lab = ROOT / "data" / "raw" / "laboratorija" / "tyrimai.csv"
    erp = ROOT / "data" / "raw" / "erp" / "gamyba.csv"
    with erp.open(encoding="utf-8-sig") as f:
        batches = {r["PARTIJOS_NR"] for r in csv.DictReader(f, delimiter=";")}
    with lab.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert rows and all(normalise(r["Batch"]) in batches for r in rows)


def test_generated_shipments_respect_mass_balance():
    with (ROOT / "data" / "raw" / "erp" / "gamyba.csv").open(encoding="utf-8-sig") as f:
        made = {r["PARTIJOS_NR"]: int(r["PAGAMINTA_VNT"]) - int(r["BROKAS_VNT"]) for r in csv.DictReader(f, delimiter=";")}
    shipped = defaultdict(int)
    with (ROOT / "data" / "raw" / "sandelis" / "siuntos.csv").open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if r["PARTIJOS_NR"]:
                shipped[r["PARTIJOS_NR"]] += int(r["KIEKIS_VNT"])
    assert all(qty <= made[nr] for nr, qty in shipped.items())
