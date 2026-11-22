# Bendras duomenų įkėlimas automatizavimo skriptams.
# Valo taip pat, kaip Power Query modelyje (powerbi/modelio_kopija_tmdl), todėl skaičiai sutampa su ataskaita:
#   - pardavimų dublikatai (identiškos eilutės) pašalinami;
#   - kliento kodas Trim + Upper, tuščias = NEŽINOMAS;
#   - plano kodai Trim (planuotojo Excel kartais turi tarpą gale).
from functools import lru_cache
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
ERP = RAW / "erp"
CLEAN = ROOT / "data" / "clean"
OUT = ROOT / "data" / "out"


def _csv(path: Path, **kwargs) -> pd.DataFrame:
    return pd.read_csv(path, sep=";", decimal=",", encoding="utf-8-sig", dtype={"PREKES_KODAS": str}, **kwargs)


@lru_cache
def products() -> pd.DataFrame:
    return _csv(ERP / "produktai.csv")


@lru_cache
def customers() -> pd.DataFrame:
    return _csv(ERP / "klientai.csv")


@lru_cache
def lines() -> pd.DataFrame:
    return _csv(ERP / "linijos.csv")


@lru_cache
def sales() -> pd.DataFrame:
    frames = [_csv(f, keep_default_na=False, na_values=[""]) for f in sorted((ERP / "pardavimai").glob("*.csv"))]
    df = pd.concat(frames, ignore_index=True)
    df = df.drop_duplicates().copy()
    code = df["KLIENTO_KODAS"].fillna("").astype(str).str.strip().str.upper()
    df["KLIENTO_KODAS"] = code.where(code != "", "NEŽINOMAS")
    df["DATA"] = pd.to_datetime(df["DATA"])
    net = df["KAINA_EUR"] * (1 - df["NUOLAIDA_PROC"] / 100)
    df["PAJAMOS"] = df["PRISTATYTA_VNT"] * net
    df["SAVIKAINA"] = df["PRISTATYTA_VNT"] * df["SAVIKAINA_VNT_EUR"]
    df["PRARASTA_VNT"] = df["UZSAKYTA_VNT"] - df["PRISTATYTA_VNT"]
    df["PRARASTOS_PAJAMOS"] = df["PRARASTA_VNT"] * net
    df["YM"] = df["DATA"].dt.to_period("M")
    df = df.merge(products()[["PREKES_KODAS", "KATEGORIJA", "PREKES_ZENKLAS", "LINIJA", "PLANO_KODAS"]],
                  on="PREKES_KODAS", how="left")
    df = df.merge(customers()[["KLIENTO_KODAS", "PAVADINIMAS", "SALIS", "RINKA"]], on="KLIENTO_KODAS", how="left")
    return df


@lru_cache
def production() -> pd.DataFrame:
    df = _csv(ERP / "gamyba.csv")
    df["DATA"] = pd.to_datetime(df["DATA"])
    df["SAVAITE"] = df["DATA"] - pd.to_timedelta(df["DATA"].dt.day_of_week, unit="D")
    df["YM"] = df["DATA"].dt.to_period("M")
    return df


def _plan_sheet(sheet: str, value: str) -> pd.DataFrame:
    df = pd.read_excel(RAW / "excel" / "gamybos_planas.xlsx", sheet_name=sheet, header=2)
    df["Produktas"] = df["Produktas"].astype(str).str.strip()
    df["Savaitės pradžia"] = pd.to_datetime(df["Savaitės pradžia"])
    return df.rename(columns={value: "VNT"})


@lru_cache
def plan() -> pd.DataFrame:
    df = pd.concat([_plan_sheet(s, "Planas, vnt") for s in ("2025", "2026")], ignore_index=True)
    return df


@lru_cache
def forecast() -> pd.DataFrame:
    df = _plan_sheet("Prognozė", "Prognozė, vnt")
    return df.merge(products()[["PLANO_KODAS", "PREKES_KODAS", "KATEGORIJA", "LINIJA"]],
                    left_on="Produktas", right_on="PLANO_KODAS", how="left")


@lru_cache
def weather() -> pd.DataFrame:
    df = _csv(RAW / "orai" / "orai.csv")
    df["DATA"] = pd.to_datetime(df["DATA"])
    return df


@lru_cache
def downtime() -> pd.DataFrame:
    df = _csv(ERP / "prastovos.csv")
    df["SAVAITES_PRADZIA"] = pd.to_datetime(df["SAVAITES_PRADZIA"])
    return df


@lru_cache
def purchases() -> pd.DataFrame:
    df = _csv(ERP / "pirkimai.csv")
    di = _csv(CLEAN / "pirkimai_di.csv")
    df = pd.concat([df, di], ignore_index=True)
    df["DATA"] = pd.to_datetime(df["DATA"])
    df["YM"] = df["DATA"].dt.to_period("M")
    return df


@lru_cache
def finance() -> tuple[pd.DataFrame, pd.DataFrame]:
    actual = _csv(ERP / "finansai_sanaudos.csv")
    actual["YM"] = pd.to_datetime(actual["DATA"]).dt.to_period("M")
    budget = _csv(ERP / "biudzetas.csv")
    budget["YM"] = pd.PeriodIndex.from_fields(year=budget["METAI"], month=budget["MENUO"], freq="M")
    return actual, budget


@lru_cache
def complaints() -> pd.DataFrame:
    df = pd.read_excel(RAW / "kokybe" / "skundu_registras.xlsx")
    df["Gauta"] = pd.to_datetime(df["Gauta"])
    df["YM"] = df["Gauta"].dt.to_period("M")
    return df


@lru_cache
def ai_log() -> pd.DataFrame:
    return _csv(CLEAN / "di_zurnalas.csv")


def weekly_anomaly() -> pd.DataFrame:
    """Savaitė (pirmadienis) × šalis -> vidutinis nukrypimas nuo normos, °C."""
    w = weather().copy()
    w["SAVAITE"] = w["DATA"] - pd.to_timedelta(w["DATA"].dt.day_of_week, unit="D")
    w["NUKRYPIMAS"] = w["TMAX_C"] - w["NORMA_C"]
    return w.groupby(["SAVAITE", "SALIS"], as_index=False)["NUKRYPIMAS"].mean()
