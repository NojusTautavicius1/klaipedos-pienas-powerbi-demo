import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "automation"))

import data_dictionary  # noqa: E402
import kpi  # noqa: E402
import planner_weather  # noqa: E402
from monthly_commentary import Action, Commentary, Number, matches, parse_lt_number, resolve, verify  # noqa: E402


# ---------- Mėnesio komentaro skaičių patikra ----------

FACTS = {"pardavimai": {"pajamos_eur": 851687, "marza_proc": 60.9},
         "pokyciai": {"marzos_pokytis_pp": -1.9},
         "rinkos": [{"rinka": "A", "yoy_proc": 7.9}, {"rinka": "B", "yoy_proc": 12.0}]}


def commentary(text: str, numbers: list[tuple[str, str]]) -> Commentary:
    return Commentary(antraste=text, santrauka=[], kodel="", rizikos=[], veiksmai=[],
                      skaiciai=[Number(tekste=t, kelias=k) for t, k in numbers])


def test_parse_lt_number_handles_thousands_and_signs():
    assert parse_lt_number("851,7 tūkst. €") == pytest.approx(851_700)
    assert parse_lt_number("−1,9 p. p.") == pytest.approx(-1.9)
    assert parse_lt_number("1,2 mln. €") == pytest.approx(1_200_000)
    assert parse_lt_number("2 440,8 tūkst. €") == pytest.approx(2_440_800)


def test_resolve_list_paths():
    assert resolve(FACTS, "rinkos[1].yoy_proc") == 12.0


def test_matches_allows_rounding_only():
    assert matches(851_700, 851_687)
    assert matches(1.9, -1.9)  # „krito 1,9 p. p.“
    assert not matches(861_700, 851_687)


def test_verify_accepts_correct_text():
    c = commentary("Pajamos 851,7 tūkst. €, marža 60,9 % (−1,9 p. p.), B rinka +12,0 %.",
                   [("851,7 tūkst. €", "pardavimai.pajamos_eur"), ("60,9 %", "pardavimai.marza_proc"),
                    ("−1,9 p. p.", "pokyciai.marzos_pokytis_pp"), ("+12,0 %", "rinkos[1].yoy_proc")])
    assert verify(c, FACTS) == []


def test_verify_catches_wrong_number_wrong_path_and_unlisted_number():
    c = commentary("Pajamos 900,0 tūkst. €, o pelnas 123,4 tūkst. €.",
                   [("900,0 tūkst. €", "pardavimai.pajamos_eur"), ("60,9 %", "pardavimai.nera")])
    problems = verify(c, FACTS)
    assert any("nesutampa" in p for p in problems)
    assert any("faktuose nėra" in p for p in problems)
    assert any("123,4" in p for p in problems)


def test_verify_ignores_years_and_small_counts():
    c = commentary("2026-10 mėn. trys veiksmai per 2 savaites.", [])
    assert verify(c, FACTS) == []


# ---------- KPI sutampa su Power BI modeliu ----------

def test_profit_bridge_effects_sum_to_total():
    s = __import__("data").sales()
    cur = s[(s["DATA"].dt.year == 2026) & s["DATA"].dt.month.between(4, 9)]
    prev = s[(s["DATA"].dt.year == 2025) & s["DATA"].dt.month.between(4, 9)]
    b = kpi.profit_bridge(cur, prev)
    assert abs(b["nepaaiskinta_eur"]) <= 2
    # Tas pats skaičius kaip Power BI mate „Pelno pokyčis vs PY“ (IV–IX, PLANAS.md): +268 tūkst. €
    assert b["is_viso_eur"] == pytest.approx(267_649, abs=5)
    assert b["zaliavu_kainos_eur"] < 0


def test_sales_cleaning_matches_dq_truth():
    s = __import__("data").sales()
    assert (s["KLIENTO_KODAS"] == "NEŽINOMAS").sum() == 28  # data/truth/dq_tiesa.json: truksta_kliento
    assert not s.duplicated(subset=[c for c in s.columns if c not in ("YM",)]).any()


def test_month_facts_counts_order_weeks():
    f = kpi.month_facts("2026-06")
    assert f["pardavimai"]["uzsakymu_savaiciu_sk"] == 5
    assert f["pardavimai_pernai"]["uzsakymu_savaiciu_sk"] == 4
    assert f["pokyciai"]["pajamos_savaitei_yoy_proc"] < f["pokyciai"]["pajamos_yoy_proc"]


# ---------- Orų pataisa planuotojui ----------

def test_sensitivity_recovers_seasonal_pattern():
    sens = planner_weather.sensitivity(planner_weather.demand_vs_forecast())
    # Šerbetas jautriausias, tortai beveik nejautrūs; žiemą jautrumas mažesnis nei vasarą
    assert sens[("Šerbetas", True)] > sens[("Plombyras puodelyje", True)] > sens[("Ledų tortas", True)]
    assert sens[("Plombyras puodelyje", False)] < sens[("Plombyras puodelyje", True)]


def test_adjustment_is_capped():
    assert planner_weather.adjustment(0.05, 30) == pytest.approx(0.60)
    assert planner_weather.adjustment(0.05, 0) == 0


def test_backtest_improves_out_of_sample_accuracy():
    r = planner_weather.backtest()
    assert r["su_orais_tikslumas_proc"] > r["planuotojo_tikslumas_proc"] + 3
    heat = r["karscio_savaite_2026_06_22"]
    assert abs(heat["su_orais_paklaida_proc"]) < abs(heat["planuotojo_paklaida_proc"])


def test_heatwave_week_excel_has_planner_format(tmp_path):
    week = pd.Timestamp("2026-06-22").date()
    sens = planner_weather.sensitivity(planner_weather.demand_vs_forecast())
    weather = planner_weather.observed_weather(week)
    rec, source = planner_weather.recommend(week, weather, sens)
    result = planner_weather.write_excel(tmp_path / "x.xlsx", week, weather, rec, source, "test", sens)
    assert result["pokytis_proc"] > 20
    plan = pd.read_excel(tmp_path / "x.xlsx", sheet_name="Planas", header=2)
    assert list(plan.columns[:5]) == ["Savaitė", "Savaitės pradžia", "Linija", "Produktas", "Planas, vnt"]
    assert (plan["Planas, vnt"] % 500 == 0).all()


# ---------- Duomenų žodynas iš TMDL ----------

def test_data_dictionary_covers_all_measures():
    text = data_dictionary.build(ROOT / "powerbi" / "modelio_kopija_tmdl")
    tmdl_measures = sum(p.read_text(encoding="utf-8-sig").count("\tmeasure ")
                        for p in (ROOT / "powerbi" / "modelio_kopija_tmdl" / "tables").glob("*.tmdl"))
    assert text.count("```dax") == tmdl_measures
    assert "Kiekio efektas" in text and "Eksporto vadybininkas (UK)" in text
