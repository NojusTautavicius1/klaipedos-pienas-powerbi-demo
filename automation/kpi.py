# Mėnesio rodikliai vadovybės komentarui. Tos pačios formulės kaip Power BI matuose (_Matai):
# Pajamos, Marža %, pelno skaidymas (kiekis / mix / kaina / žaliavos) produkto × kliento lygiu,
# užsakymų įvykdymas, plano įvykdymas, prastovos, sąnaudos vs biudžetas, skundai, DI sąskaitos.
import pandas as pd

import data


def _r(x: float, digits: int = 0) -> float:
    return round(float(x), digits) if digits else int(round(float(x)))


def _pct(x: float) -> float:
    return round(float(x) * 100, 1)


def profit_bridge(cur: pd.DataFrame, prev: pd.DataFrame) -> dict:
    """Pelno pokyčio skaidymas kaip matuose „Kiekio efektas“, „Mix efektas“, „Kainos ir nuolaidų efektas“,
    „Žaliavų kainų efektas“. Grąžina eurus."""
    keys = ["PREKES_KODAS", "KLIENTO_KODAS"]
    cols = ["PRISTATYTA_VNT", "PAJAMOS", "SAVIKAINA"]
    a = prev.groupby(keys)[cols].sum()
    b = cur.groupby(keys)[cols].sum()
    j = a.add_suffix("_PY").join(b, how="outer").fillna(0.0)
    q, q_py = j["PRISTATYTA_VNT"], j["PRISTATYTA_VNT_PY"]
    gp, gp_py = j["PAJAMOS"] - j["SAVIKAINA"], j["PAJAMOS_PY"] - j["SAVIKAINA_PY"]
    total_q_py = q_py.sum()
    avg_gp_py = gp_py.sum() / total_q_py
    volume = (q.sum() - total_q_py) * avg_gp_py
    at_py_margin = (q * (gp_py / q_py.where(q_py > 0))).where(q_py > 0, gp).sum()
    mix = at_py_margin - q.sum() * avg_gp_py
    both = (q > 0) & (q_py > 0)
    price = (q * (j["PAJAMOS"] / q.where(both) - j["PAJAMOS_PY"] / q_py.where(both))).where(both, 0).sum()
    materials = (-q * (j["SAVIKAINA"] / q.where(both) - j["SAVIKAINA_PY"] / q_py.where(both))).where(both, 0).sum()
    total = gp.sum() - gp_py.sum()
    return {"kiekis_eur": _r(volume), "mix_eur": _r(mix), "kaina_ir_nuolaidos_eur": _r(price),
            "zaliavu_kainos_eur": _r(materials), "is_viso_eur": _r(total),
            "nepaaiskinta_eur": _r(total - volume - mix - price - materials)}


def _sales_block(s: pd.DataFrame) -> dict:
    rev, cost = s["PAJAMOS"].sum(), s["SAVIKAINA"].sum()
    return {"pajamos_eur": _r(rev), "bendrasis_pelnas_eur": _r(rev - cost),
            "marza_proc": _pct(1 - cost / rev) if rev else None,
            "parduota_vnt": _r(s["PRISTATYTA_VNT"].sum()),
            "uzsakymu_ivykdymas_proc": _pct(s["PRISTATYTA_VNT"].sum() / s["UZSAKYTA_VNT"].sum()),
            "prarastos_pajamos_eur": _r(s["PRARASTOS_PAJAMOS"].sum()),
            "uzsakymu_savaiciu_sk": int(s["DATA"].nunique())}


def month_facts(month: str) -> dict:
    """Visi faktai vienam mėnesiui (pvz. '2026-10'), palyginti su praėjusiu mėnesiu ir pernai."""
    m = pd.Period(month, "M")
    py, pm = m - 12, m - 1
    s = data.sales()
    cur, prev_year, prev_month = s[s["YM"] == m], s[s["YM"] == py], s[s["YM"] == pm]
    if cur.empty:
        raise ValueError(f"{month}: pardavimų duomenų nėra")

    facts: dict = {"menuo": str(m), "palyginimas_pernai": str(py), "praejes_menuo": str(pm)}
    facts["pardavimai"] = _sales_block(cur)
    facts["pardavimai_pernai"] = _sales_block(prev_year)
    facts["pardavimai_praejusi_menesi"] = _sales_block(prev_month)
    c, p = facts["pardavimai"], facts["pardavimai_pernai"]
    facts["pokyciai"] = {
        "pajamos_yoy_proc": _pct(c["pajamos_eur"] / p["pajamos_eur"] - 1),
        "pajamos_mom_proc": _pct(c["pajamos_eur"] / facts["pardavimai_praejusi_menesi"]["pajamos_eur"] - 1),
        "marzos_pokytis_pp": round(c["marza_proc"] - p["marza_proc"], 1),
        "parduota_vnt_yoy_proc": _pct(c["parduota_vnt"] / p["parduota_vnt"] - 1),
        # ERP užsakymai fiksuojami kartą per savaitę (antradienį): mėnuo gali turėti 4 arba 5 užsakymų savaites.
        "pajamos_savaitei_yoy_proc": _pct((c["pajamos_eur"] / c["uzsakymu_savaiciu_sk"])
                                          / (p["pajamos_eur"] / p["uzsakymu_savaiciu_sk"]) - 1),
    }
    facts["pelno_skaidymas_vs_pernai"] = profit_bridge(cur, prev_year)

    ytd = s[(s["DATA"].dt.year == m.year) & (s["DATA"].dt.month <= m.month)]
    ytd_py = s[(s["DATA"].dt.year == py.year) & (s["DATA"].dt.month <= m.month)]
    facts["metai_iki_siol"] = {"laikotarpis": f"{m.year}-01 – {m}", **_sales_block(ytd),
                               "pajamos_pernai_eur": _r(ytd_py["PAJAMOS"].sum()),
                               "marza_pernai_proc": _pct(1 - ytd_py["SAVIKAINA"].sum() / ytd_py["PAJAMOS"].sum())}

    by_market = []
    for market, g in cur.groupby("RINKA"):
        g_py = prev_year[prev_year["RINKA"] == market]
        by_market.append({"rinka": market, "pajamos_eur": _r(g["PAJAMOS"].sum()),
                          "yoy_proc": _pct(g["PAJAMOS"].sum() / g_py["PAJAMOS"].sum() - 1) if len(g_py) else None,
                          "marza_proc": _pct(1 - g["SAVIKAINA"].sum() / g["PAJAMOS"].sum())})
    facts["rinkos"] = sorted(by_market, key=lambda r: -r["pajamos_eur"])

    by_cat = []
    for cat, g in cur.groupby("KATEGORIJA"):
        g_py = prev_year[prev_year["KATEGORIJA"] == cat]
        by_cat.append({"kategorija": cat, "pajamos_eur": _r(g["PAJAMOS"].sum()),
                       "yoy_proc": _pct(g["PAJAMOS"].sum() / g_py["PAJAMOS"].sum() - 1) if len(g_py) else None,
                       "uzsakymu_ivykdymas_proc": _pct(g["PRISTATYTA_VNT"].sum() / g["UZSAKYTA_VNT"].sum())})
    facts["kategorijos"] = sorted(by_cat, key=lambda r: -r["pajamos_eur"])

    customers = []
    for name, g in cur.groupby("PAVADINIMAS"):
        g_py = prev_year[prev_year["PAVADINIMAS"] == name]
        customers.append({"klientas": name, "pajamos_eur": _r(g["PAJAMOS"].sum()),
                          "pokytis_eur": _r(g["PAJAMOS"].sum() - g_py["PAJAMOS"].sum())})
    customers.sort(key=lambda r: r["pokytis_eur"])
    facts["klientai_maziausias_pokytis"] = customers[:2]
    facts["klientai_didziausias_augimas"] = customers[-2:][::-1]

    facts["gamyba"] = _production(m)
    facts["zaliavos"] = _materials(m)
    facts["sanaudos"] = _costs(m)
    facts["kokybe"] = _quality(m)
    facts["di_saskaitos"] = _invoices(m)
    facts["prognoze_ir_orai"] = _forecast(m)
    return facts


def _production(m: pd.Period) -> dict:
    prod = data.production()
    prod = prod[prod["YM"] == m]
    plan = data.plan()
    plan = plan[(plan["Savaitės pradžia"] + pd.Timedelta(days=4)).dt.to_period("M") == m]
    lines = data.lines().set_index("LINIJOS_KODAS")
    dt = data.downtime()
    dt = dt[(dt["SAVAITES_PRADZIA"] + pd.Timedelta(days=3)).dt.to_period("M") == m]
    rows = []
    for code, g in prod.groupby("LINIJA"):
        planned = plan.loc[plan["Linija"] == code, "VNT"].sum()
        line_dt = dt[dt["LINIJA"] == code].groupby("PRIEZASTIS")["PRASTOVOS_MIN"].sum().sort_values(ascending=False)
        rows.append({"linija": f"{code} {lines.loc[code, 'PAVADINIMAS']} ({lines.loc[code, 'GAMYKLA']})",
                     "plano_ivykdymas_proc": _pct(g["PAGAMINTA_VNT"].sum() / planned) if planned else None,
                     "brokas_proc": _pct(g["BROKAS_VNT"].sum() / g["PAGAMINTA_VNT"].sum())
                     if g["PAGAMINTA_VNT"].sum() else None,
                     "prastovos_min": _r(line_dt.sum()),
                     "prastovos_pagal_priezasti_min": {k: _r(v) for k, v in line_dt.items()}})
    weeks = dt["SAVAITES_PRADZIA"].nunique() or 1
    reasons = dt.groupby("PRIEZASTIS")["PRASTOVOS_MIN"].sum().sort_values(ascending=False)
    total = prod["PAGAMINTA_VNT"].sum()
    return {"pagaminta_vnt": _r(total), "plano_ivykdymas_proc": _pct(total / plan["VNT"].sum()),
            "linijos": rows, "prastovos_min": _r(dt["PRASTOVOS_MIN"].sum()),
            "prastovu_dalis_proc": _pct(dt["PRASTOVOS_MIN"].sum() / (weeks * lines["MINUTES_PER_SAVAITE"].sum())),
            "pagrindine_prastovu_priezastis": reasons.index[0] if len(reasons) else None,
            "pagrindines_priezasties_min": _r(reasons.iloc[0]) if len(reasons) else 0}


def _materials(m: pd.Period) -> list[dict]:
    p = data.purchases()
    p = p[p["ZALIAVOS_KODAS"] != "TRANSP"]
    out = []
    for code, g in p.groupby("ZALIAVOS_KODAS"):
        def price(period):
            x = g[g["YM"] == period]
            return x["SUMA_BE_PVM_EUR"].sum() / x["KIEKIS"].sum() if x["KIEKIS"].sum() else None
        now, year_ago = price(m), price(m - 12)
        if now and year_ago:
            out.append({"zaliava": g["APRASYMAS"].iloc[0], "kaina_eur": round(now, 3),
                        "kaina_pernai_eur": round(year_ago, 3), "pokytis_proc": _pct(now / year_ago - 1)})
    return sorted(out, key=lambda r: -abs(r["pokytis_proc"]))[:4]


def _costs(m: pd.Period) -> dict:
    actual, budget = data.finance()
    a = actual[actual["YM"] == m].groupby("STRAIPSNIS")["SUMA_EUR"].sum()
    b = budget[budget["YM"] == m].set_index("STRAIPSNIS")["SUMA_EUR"]
    items = [{"straipsnis": k, "faktas_eur": _r(v), "biudzetas_eur": _r(b[k]), "nuokrypis_eur": _r(v - b[k])}
             for k, v in a.items() if k in b.index]
    items.sort(key=lambda r: -abs(r["nuokrypis_eur"]))
    revenue_budget = b.get("Pajamos")
    return {"sanaudos_eur": _r(a.sum()), "sanaudu_biudzetas_eur": _r(sum(i["biudzetas_eur"] for i in items)),
            "didziausi_nuokrypiai": items[:3],
            "pajamu_biudzetas_eur": _r(revenue_budget) if revenue_budget is not None else None}


def _quality(m: pd.Period) -> dict:
    c = data.complaints()
    cur = c[c["YM"] == m]
    monthly = c.groupby("YM").size()
    return {"skundu_sk": int(len(cur)), "vid_skundu_per_men": round(float(monthly.mean()), 1),
            "tipai": cur["Tipas"].value_counts().to_dict(),
            "atviri_skundai": int((c["Būsena"] != "Uždarytas").sum())}


def _invoices(m: pd.Period) -> dict:
    log = data.ai_log()  # DI kol kas nuskaito tik spalio sąskaitas (iki rugsėjo jos jau buvo ERP)
    approved = int((log["STATUSAS"] == "Patvirtinta").sum())
    return {"apdorota": int(len(log)), "patvirtinta_automatiskai": approved,
            "atiduota_perziurai": int(len(log) - approved),
            "perziuros_priezastys": sorted({p for p in log["PRIEZASTYS"].dropna() if p}),
            "kaina_usd": round(float(log["KAINA_USD"].sum()), 2),
            "sutaupyta_val": round((len(log) * 4 - log["TRUKME_S"].sum() / 60) / 60, 1)}


def _forecast(m: pd.Period) -> dict:
    f = data.forecast()
    f = f[(f["Savaitės pradžia"] + pd.Timedelta(days=1)).dt.to_period("M") == m]
    s = data.sales()
    s = s[s["YM"] == m]
    ordered = s.groupby([s["DATA"] - pd.Timedelta(days=1), "SALIS", "PREKES_KODAS"])["UZSAKYTA_VNT"].sum()
    fc = f.groupby(["Savaitės pradžia", "Šalis", "PREKES_KODAS"])["VNT"].sum()
    j = pd.concat([ordered.rename("u"), fc.rename("f")], axis=1).fillna(0)
    accuracy = 1 - (j["u"] - j["f"]).abs().sum() / j["f"].sum()
    an = data.weekly_anomaly()
    an = an[(an["SAVAITE"] + pd.Timedelta(days=3)).dt.to_period("M") == m]
    return {"prognozes_tikslumas_proc": _pct(accuracy),
            "uzsakyta_vs_prognoze_proc": _pct(j["u"].sum() / j["f"].sum() - 1),
            "oru_nukrypimas_c": round(float(an["NUKRYPIMAS"].mean()), 1)}
