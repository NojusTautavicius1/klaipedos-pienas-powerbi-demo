# Paleidimas:
#   python automation/planner_weather.py                         # kita savaitė, tikra Open-Meteo 16 d. orų prognozė
#   python automation/planner_weather.py --savaite 2026-06-22    # „kas būtų, jei“: istorinė savaitė, tikri tos savaitės orai
#   python automation/planner_weather.py --patikra               # kiek orų pataisa pagerintų 2026 m. vasaros prognozę
#
# Planuotojas planuoja Excel'yje pagal įprastą sezoną. Šis skriptas:
#   1) iš istorijos (2025 m.) apskaičiuoja, kiek kiekviena kategorija jautri orams (+1 °C virš normos = +x % užsakymų);
#   2) paima orų prognozę 6 rinkų miestams ir palygina su norma (2015–2024 m. vidurkis);
#   3) pakoreguoja planuotojo prognozę ir įrašo Excel failą TOKIU PAT formatu kaip gamybos planas
#      (Savaitė / Savaitės pradžia / Linija / Produktas / Planas), su papildomais stulpeliais ir linijų apkrovos patikra.
# Tai „informacijos perdavimas tarp sistemų“ atgal į planuotojo įrankį: jam nereikia atidaryti Power BI.
import argparse
import json
import math
import time
import urllib.request
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

import data

FORECAST_API = "https://api.open-meteo.com/v1/forecast"
CITIES = {"LT": ("Klaipėda", 55.71, 21.13), "LV": ("Ryga", 56.95, 24.11), "EE": ("Talinas", 59.44, 24.75),
          "PL": ("Varšuva", 52.23, 21.01), "DE": ("Berlynas", 52.52, 13.40), "GB": ("Londonas", 51.51, -0.13)}
SUMMER_MONTHS = range(5, 10)
MAX_ADJUSTMENT = 0.60  # daugiau nei +60 % prognozės automatiškai nesiūlome: tai jau žmogaus sprendimas


def monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


# ---------- 1. Jautrumas orams iš istorijos ----------

def demand_vs_forecast() -> pd.DataFrame:
    """Savaitė × šalis × kategorija: užsakyta, prognozė, orų nukrypimas."""
    s = data.sales()
    s = s.assign(SAVAITE=s["DATA"] - pd.Timedelta(days=1))
    ordered = s.groupby(["SAVAITE", "SALIS", "KATEGORIJA"])["UZSAKYTA_VNT"].sum().rename("UZSAKYTA")
    f = data.forecast()
    fc = f.groupby(["Savaitės pradžia", "Šalis", "KATEGORIJA"])["VNT"].sum().rename("PROGNOZE")
    fc.index.names = ["SAVAITE", "SALIS", "KATEGORIJA"]
    j = pd.concat([ordered, fc], axis=1).dropna().reset_index()
    j = j[(j["UZSAKYTA"] > 0) & (j["PROGNOZE"] > 0)]
    an = data.weekly_anomaly().rename(columns={"NUKRYPIMAS": "ANOMALIJA"})
    j = j.merge(an, on=["SAVAITE", "SALIS"], how="left").dropna(subset=["ANOMALIJA"])
    j["MENUO"] = (j["SAVAITE"] + pd.Timedelta(days=3)).dt.month
    j["VASARA"] = j["MENUO"].isin(SUMMER_MONTHS)
    return j


def sensitivity(history: pd.DataFrame) -> dict[tuple[str, bool], float]:
    """(kategorija, vasara?) -> nuolydis: ln(užsakyta/prognozė) = a + b · anomalija. Grąžina b (log vienetais)."""
    out = {}
    for (cat, summer), g in history.groupby(["KATEGORIJA", "VASARA"]):
        if len(g) < 20:
            continue
        x, y = g["ANOMALIJA"].to_numpy(), np.log(g["UZSAKYTA"] / g["PROGNOZE"]).to_numpy()
        b = np.polyfit(x, y, 1)[0]
        out[(cat, bool(summer))] = float(max(b, 0.0))  # neigiamas jautrumas būtų triukšmas: nesiūlome mažinti dėl šilumos
    return out


def adjustment(b: float, anomaly: float) -> float:
    return float(np.clip(math.exp(b * anomaly) - 1, -MAX_ADJUSTMENT, MAX_ADJUSTMENT))


# ---------- 2. Orai ----------

def norms_for(week: date) -> dict[str, float]:
    """Savaitės norma kiekvienai šaliai iš orai.csv (ta pati metų diena, NORMA_C stulpelis)."""
    w = data.weather()
    days = {(week + timedelta(days=i)).strftime("%m-%d") for i in range(7)}
    sel = w[w["DATA"].dt.strftime("%m-%d").isin(days)]
    return sel.groupby("SALIS")["NORMA_C"].mean().to_dict()


def forecast_weather(week: date) -> dict[str, dict]:
    """Tikra Open-Meteo prognozė savaitei (maks. temperatūrų vidurkis) ir nukrypimas nuo normos."""
    norms = norms_for(week)
    out = {}
    for country, (city, lat, lon) in CITIES.items():
        url = (f"{FORECAST_API}?latitude={lat}&longitude={lon}&daily=temperature_2m_max"
               f"&start_date={week}&end_date={week + timedelta(days=6)}&timezone=Europe%2FVilnius")
        for attempt in range(3):
            try:
                with urllib.request.urlopen(url, timeout=30) as response:
                    temps = [t for t in json.load(response)["daily"]["temperature_2m_max"] if t is not None]
                break
            except OSError:
                if attempt == 2:
                    raise
                time.sleep(3)
        tmax = sum(temps) / len(temps)
        out[country] = {"miestas": city, "tmax": round(tmax, 1), "norma": round(norms[country], 1),
                        "nukrypimas": round(tmax - norms[country], 1), "dienu": len(temps)}
    return out


def observed_weather(week: date) -> dict[str, dict]:
    w = data.weather()
    sel = w[(w["DATA"] >= pd.Timestamp(week)) & (w["DATA"] < pd.Timestamp(week + timedelta(days=7)))]
    out = {}
    for country, g in sel.groupby("SALIS"):
        out[country] = {"miestas": g["MIESTAS"].iloc[0], "tmax": round(g["TMAX_C"].mean(), 1),
                        "norma": round(g["NORMA_C"].mean(), 1),
                        "nukrypimas": round((g["TMAX_C"] - g["NORMA_C"]).mean(), 1), "dienu": len(g)}
    return out


# ---------- 3. Bazinė prognozė ----------

def base_forecast(week: date) -> tuple[pd.DataFrame, str]:
    """Planuotojo prognozė (šalis × produktas). Jei savaitės dar nėra Excel'yje, imama pernai tos pačios ISO
    savaitės prognozė × metinis augimas (tikrame darbe skriptas skaitytų planuotojo einamąjį failą)."""
    f = data.forecast()
    rows = f[f["Savaitės pradžia"] == pd.Timestamp(week)]
    if len(rows):
        return rows[["Šalis", "PREKES_KODAS", "Produktas", "KATEGORIJA", "LINIJA", "VNT"]].copy(), \
            "planuotojo prognozė iš gamybos_planas.xlsx (lapas „Prognozė“)"
    iso = week.isocalendar()
    last_year = date.fromisocalendar(iso.year - 1, iso.week, 1)
    rows = f[f["Savaitės pradžia"] == pd.Timestamp(last_year)].copy()
    s = data.sales()
    last_month = s["DATA"].max().month
    cur = s[(s["DATA"].dt.year == iso.year) & (s["DATA"].dt.month <= last_month)]["UZSAKYTA_VNT"].sum()
    prev = s[(s["DATA"].dt.year == iso.year - 1) & (s["DATA"].dt.month <= last_month)]["UZSAKYTA_VNT"].sum()
    growth = cur / prev
    rows["VNT"] = (rows["VNT"] * growth).round()
    return rows[["Šalis", "PREKES_KODAS", "Produktas", "KATEGORIJA", "LINIJA", "VNT"]], \
        f"pernai {last_year} savaitės planuotojo prognozė × metų augimas {growth:.3f} (einamosios savaitės Excel'yje dar nėra)"


def line_capacity() -> dict[str, float]:
    """Įrodytas linijos pajėgumas: didžiausia per savaitę pagaminta produkcija istorijoje."""
    p = data.production()
    weekly = p.groupby(["LINIJA", "SAVAITE"])["PAGAMINTA_VNT"].sum()
    return weekly.groupby("LINIJA").max().to_dict()


def recommend(week: date, weather: dict[str, dict], sens: dict) -> tuple[pd.DataFrame, str]:
    base, source = base_forecast(week)
    summer = (week + timedelta(days=3)).month in SUMMER_MONTHS
    base["NUKRYPIMAS"] = base["Šalis"].map(lambda c: weather[c]["nukrypimas"])
    base["JAUTRUMAS"] = base["KATEGORIJA"].map(lambda c: sens.get((c, summer), 0.0))
    base["PATAISA"] = [adjustment(b, a) for b, a in zip(base["JAUTRUMAS"], base["NUKRYPIMAS"])]
    base["SU_ORAIS"] = (base["VNT"] * (1 + base["PATAISA"])).round()
    return base, source


# ---------- 4. Excel planuotojui ----------

HEADER = Font(bold=True, color="FFFFFF")
HEADER_FILL = PatternFill("solid", fgColor="1F5A96")
WARN_FILL = PatternFill("solid", fgColor="FCE4D6")
OK_FILL = PatternFill("solid", fgColor="E2EFDA")


def _header(ws, row: int, values: list[str]) -> None:
    ws.append(values) if row is None else None
    for col, _ in enumerate(values, start=1):
        cell = ws.cell(row=ws.max_row, column=col)
        cell.font, cell.fill = HEADER, HEADER_FILL
        cell.alignment = Alignment(wrap_text=True, vertical="center")


def write_excel(path: Path, week: date, weather: dict, rec: pd.DataFrame, source: str, mode: str,
                sens: dict) -> dict:
    iso = week.isocalendar()
    label = f"{iso.year}-W{iso.week:02d}"
    capacity = line_capacity()
    lines = data.lines().set_index("LINIJOS_KODAS")
    by_sku = rec.groupby(["LINIJA", "Produktas", "KATEGORIJA"], as_index=False)[["VNT", "SU_ORAIS"]].sum()
    by_line = by_sku.groupby("LINIJA")[["VNT", "SU_ORAIS"]].sum()

    wb = Workbook()
    ws = wb.active
    ws.title = "Santrauka"
    ws.append([f"ORŲ PATAISA GAMYBOS PLANUI · {label} (nuo {week})"])
    ws["A1"].font = Font(bold=True, size=14)
    ws.append([f"Orai: {mode}. Bazinė prognozė: {source}."])
    ws.append(["Sintetiniai duomenys, mokomasis pavyzdys. Orai tikri (Open-Meteo)."])
    ws.append([])
    _header(ws, None, ["Šalis", "Miestas", "Maks. t° (vid.)", "Norma", "Nukrypimas °C", "Bazinė prognozė, vnt",
                       "Su orais, vnt", "Pokytis %"])
    for country in sorted(weather):
        r = rec[rec["Šalis"] == country]
        b, a = r["VNT"].sum(), r["SU_ORAIS"].sum()
        w = weather[country]
        ws.append([country, w["miestas"], w["tmax"], w["norma"], w["nukrypimas"], int(b), int(a),
                   (a / b - 1) if b else 0])
    total_b, total_a = rec["VNT"].sum(), rec["SU_ORAIS"].sum()
    ws.append(["Iš viso", "", "", "", "", int(total_b), int(total_a), (total_a / total_b - 1) if total_b else 0])
    ws.cell(row=ws.max_row, column=1).font = Font(bold=True)
    for row in ws.iter_rows(min_row=6, max_row=ws.max_row):
        row[7].number_format = "+0.0%;-0.0%;0.0%"
        row[5].number_format = row[6].number_format = "# ##0"

    ws.append([])
    ws.append(["Linijų apkrova"])
    ws.cell(row=ws.max_row, column=1).font = Font(bold=True, size=12)
    _header(ws, None, ["Linija", "Pavadinimas", "Gamykla", "Bazinis kiekis, vnt", "Su orais, vnt",
                       "Įrodytas pajėgumas, vnt/sav.", "Apkrova %", "Ką daryti"])
    warnings = []
    for code, row in by_line.iterrows():
        load = row["SU_ORAIS"] / capacity[code]
        action = ("Viršija pajėgumą: dalį gaminti savaite anksčiau į šaldytą sandėlį arba planuoti papildomą pamainą"
                  if load > 1.0 else "Artėja prie ribos: suderinti pamainas" if load > 0.9 else "Telpa")
        if load > 0.9:
            warnings.append(f"{code} {lines.loc[code, 'PAVADINIMAS']}: apkrova {load:.0%}")
        ws.append([code, lines.loc[code, "PAVADINIMAS"], lines.loc[code, "GAMYKLA"], int(row["VNT"]),
                   int(row["SU_ORAIS"]), int(capacity[code]), load, action])
        ws.cell(row=ws.max_row, column=7).number_format = "0%"
        ws.cell(row=ws.max_row, column=8).fill = WARN_FILL if load > 0.9 else OK_FILL
    for col, width in zip("ABCDEFGH", (10, 26, 14, 16, 14, 18, 11, 70)):
        ws.column_dimensions[col].width = width

    # Planas tuo pačiu formatu kaip planuotojo Excel (galima kopijuoti tiesiai į jo failą)
    ws2 = wb.create_sheet("Planas")
    ws2.append([f"GAMYBOS PLANO PASIŪLYMAS SU ORAIS {label}"])
    ws2["A1"].font = Font(bold=True, size=14)
    ws2.append([])
    _header(ws2, None, ["Savaitė", "Savaitės pradžia", "Linija", "Produktas", "Planas, vnt",
                        "Bazinė prognozė, vnt", "Orų pataisa %", "Skirtumas, vnt", "Kategorija"])
    for _, r in by_sku.sort_values(["LINIJA", "Produktas"]).iterrows():
        rounded = int(math.ceil(r["SU_ORAIS"] / 500) * 500)  # planuotojas planuoja 500 vnt. žingsniu
        ws2.append([label, week, r["LINIJA"], r["Produktas"], rounded, int(r["VNT"]),
                    (r["SU_ORAIS"] / r["VNT"] - 1) if r["VNT"] else 0, rounded - int(r["VNT"]), r["KATEGORIJA"]])
        ws2.cell(row=ws2.max_row, column=2).number_format = "yyyy-mm-dd"
        ws2.cell(row=ws2.max_row, column=7).number_format = "+0.0%;-0.0%;0.0%"
    last = ws2.max_row
    ws2.conditional_formatting.add(f"G4:G{last}", CellIsRule(operator="greaterThan", formula=["0.1"], fill=WARN_FILL))
    for col, width in zip("ABCDEFGHI", (10, 16, 10, 20, 12, 18, 14, 14, 22)):
        ws2.column_dimensions[col].width = width
    ws2.freeze_panes = "A4"

    ws3 = wb.create_sheet("Kaip skaičiuota")
    summer = (week + timedelta(days=3)).month in SUMMER_MONTHS
    ws3.append(["Kaip skaičiuota"])
    ws3["A1"].font = Font(bold=True, size=14)
    for line in [
        "1. Jautrumas orams apskaičiuotas iš visos istorijos (2025-01 – 2026-10): kiekvienai kategorijai regresija",
        "   ln(užsakyta / prognozė) = a + b × (savaitės maks. temperatūra − norma), savaitė × šalis.",
        "   Vasaros (V–IX) ir ne sezono savaitės vertinamos atskirai: žiemą oras paklausą veikia silpniau.",
        "2. Norma = 2015–2024 m. tos pačios dienos vidurkis (Open-Meteo archyvas).",
        "3. Pataisa = e^(b × nukrypimas) − 1, ribojama ±60 %. Didesnius pokyčius sprendžia planuotojas.",
        "4. Linijos pajėgumas = didžiausia savaitės gamyba istorijoje. Jei apkrova > 100 %, siūloma gaminti anksčiau:",
        "   ledai laikomi −25 °C sandėlyje, todėl dalį karštos savaitės paklausos galima pagaminti iš anksto.",
        "5. Planas suapvalintas iki 500 vnt., kaip daro planuotojas.",
        "",
        f"Šiai savaitei naudojamas {'vasaros' if summer else 'ne sezono'} jautrumas:",
    ]:
        ws3.append([line])
    ws3.append(["Kategorija", "+1 °C virš normos = užsakymų pokytis"])
    for cat in sorted({k[0] for k in sens}):
        ws3.append([cat, math.exp(sens.get((cat, summer), 0.0)) - 1])
        ws3.cell(row=ws3.max_row, column=2).number_format = "+0.0%"
    ws3.column_dimensions["A"].width = 100
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return {"failas": str(path), "savaite": label, "bazine_vnt": int(total_b), "su_orais_vnt": int(total_a),
            "pokytis_proc": round((total_a / total_b - 1) * 100, 1) if total_b else 0, "ispejimai": warnings}


# ---------- 5. Patikra: ar orų pataisa būtų pagerinusi 2026 m. vasaros prognozę ----------

def backtest() -> dict:
    """Jautrumas skaičiuojamas TIK iš 2025 m., tikrinama su 2026 m. V–IX (duomenys, kurių modelis nematė).
    Orai: tikri tos savaitės orai, t. y. „tobula“ orų prognozė. Tikra 5–7 d. prognozė klysta ±1–2 °C,
    todėl realus pagerėjimas bus kiek mažesnis."""
    h = demand_vs_forecast()
    sens = sensitivity(h[h["SAVAITE"].dt.year == 2025])
    test = h[(h["SAVAITE"].dt.year == 2026) & h["VASARA"]].copy()
    test["PATAISA"] = [adjustment(sens.get((c, True), 0.0), a) for c, a in zip(test["KATEGORIJA"], test["ANOMALIJA"])]
    test["SU_ORAIS"] = test["PROGNOZE"] * (1 + test["PATAISA"])

    def accuracy(df, col):
        return 1 - (df["UZSAKYTA"] - df[col]).abs().sum() / df[col].sum()

    heat = test[test["SAVAITE"] == pd.Timestamp("2026-06-22")]
    return {
        "laikotarpis": "2026 m. V–IX, savaitė × šalis × kategorija",
        "planuotojo_tikslumas_proc": round(accuracy(test, "PROGNOZE") * 100, 1),
        "su_orais_tikslumas_proc": round(accuracy(test, "SU_ORAIS") * 100, 1),
        "karscio_savaite_2026_06_22": {
            "uzsakyta_vnt": int(heat["UZSAKYTA"].sum()), "planuotojo_prognoze_vnt": int(heat["PROGNOZE"].sum()),
            "su_orais_vnt": int(heat["SU_ORAIS"].sum()),
            "planuotojo_paklaida_proc": round((heat["PROGNOZE"].sum() / heat["UZSAKYTA"].sum() - 1) * 100, 1),
            "su_orais_paklaida_proc": round((heat["SU_ORAIS"].sum() / heat["UZSAKYTA"].sum() - 1) * 100, 1),
        },
        "jautrumas_vasara_proc": {c: round((math.exp(b) - 1) * 100, 1) for (c, s), b in sorted(sens.items()) if s},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--savaite", help="savaitės pirmadienis YYYY-MM-DD (istorinė savaitė su tikrais orais)")
    parser.add_argument("--patikra", action="store_true")
    args = parser.parse_args()

    if args.patikra:
        result = backtest()
        out = data.OUT / "oru_pataisos_patikra.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    sens = sensitivity(demand_vs_forecast())
    if args.savaite:
        week = monday(date.fromisoformat(args.savaite))
        weather, mode = observed_weather(week), "tikri tos savaitės orai (istorinė savaitė)"
    else:
        week = monday(date.today()) + timedelta(days=7)
        weather, mode = forecast_weather(week), f"Open-Meteo prognozė, gauta {date.today()}"
    rec, source = recommend(week, weather, sens)
    iso = week.isocalendar()
    result = write_excel(data.OUT / f"planuotojui_{iso.year}-W{iso.week:02d}.xlsx", week, weather, rec, source, mode,
                         sens)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
