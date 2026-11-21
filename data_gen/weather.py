# Tikri orai iš Open-Meteo archyvo (nemokamas, be rakto): dienos maksimali temperatūra kiekvienos rinkos mieste.
# Norma = 2015–2024 m. vidurkis tą pačią metų dieną (±7 d. langas). Paklausą lemia nukrypimas nuo normos:
# planuotojas planuoja pagal įprastą sezoną, o pirkėjai perka pagal tai, koks oras iš tikrųjų.
# Atsisiunčiama vieną kartą į data/raw/orai/orai.csv, vėliau skaitoma iš disko.
import csv
import json
import urllib.request
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "raw" / "orai" / "orai.csv"
API = "https://archive-api.open-meteo.com/v1/archive"
NORM_YEARS = (2015, 2024)
FIRST_DAY, LAST_DAY = date(2025, 1, 1), date(2026, 10, 31)

# šalis -> (miestas, platuma, ilguma)
CITIES = {
    "LT": ("Klaipėda", 55.71, 21.13),
    "LV": ("Ryga", 56.95, 24.11),
    "EE": ("Talinas", 59.44, 24.75),
    "PL": ("Varšuva", 52.23, 21.01),
    "DE": ("Berlynas", 52.52, 13.40),
    "GB": ("Londonas", 51.51, -0.13),
}


def _fetch(lat: float, lon: float) -> dict[date, float]:
    url = (f"{API}?latitude={lat}&longitude={lon}&start_date={NORM_YEARS[0]}-01-01&end_date={LAST_DAY.isoformat()}"
           "&daily=temperature_2m_max&timezone=Europe%2FVilnius")
    with urllib.request.urlopen(url, timeout=60) as response:
        daily = json.load(response)["daily"]
    return {date.fromisoformat(d): t for d, t in zip(daily["time"], daily["temperature_2m_max"]) if t is not None}


def _norms(series: dict[date, float]) -> dict[int, float]:
    """Metų dienos (1..366) norma: 2015–2024 vidurkis ±7 dienų lange."""
    by_doy = defaultdict(list)
    for d, t in series.items():
        if NORM_YEARS[0] <= d.year <= NORM_YEARS[1]:
            by_doy[d.timetuple().tm_yday].append(t)
    norms = {}
    for doy in range(1, 367):
        window = [t for k in range(doy - 7, doy + 8) for t in by_doy[(k - 1) % 366 + 1]]
        norms[doy] = round(sum(window) / len(window), 2)
    return norms


def download() -> None:
    rows = []
    for country, (city, lat, lon) in CITIES.items():
        series = _fetch(lat, lon)
        norms = _norms(series)
        day = FIRST_DAY
        while day <= LAST_DAY:
            rows.append([day.isoformat(), country, city, f"{series[day]:.1f}".replace(".", ","),
                         f"{norms[day.timetuple().tm_yday]:.1f}".replace(".", ",")])
            day += timedelta(days=1)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    with CACHE.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["DATA", "SALIS", "MIESTAS", "TMAX_C", "NORMA_C"])
        writer.writerows(rows)


def load() -> dict[tuple[str, date], tuple[float, float]]:
    """(šalis, data) -> (tikra maks. temperatūra, norma)."""
    if not CACHE.exists():
        download()
    with CACHE.open(encoding="utf-8-sig") as f:
        return {(r["SALIS"], date.fromisoformat(r["DATA"])):
                (float(r["TMAX_C"].replace(",", ".")), float(r["NORMA_C"].replace(",", ".")))
                for r in csv.DictReader(f, delimiter=";")}


def weekly_anomaly(weather: dict, country: str, week: date) -> float:
    """Savaitės (pirm.–sekm.) vidutinis nukrypimas nuo normos, °C."""
    days = [weather[(country, week + timedelta(days=i))] for i in range(7) if (country, week + timedelta(days=i)) in weather]
    return sum(t - n for t, n in days) / len(days) if days else 0.0


if __name__ == "__main__":
    download()
    print(f"Išsaugota: {CACHE}")
