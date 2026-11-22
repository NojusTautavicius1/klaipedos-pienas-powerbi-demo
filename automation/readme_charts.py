# Paleidimas: python automation/readme_charts.py
# README iliustracijos iš tų pačių duomenų ir formulių kaip Power BI (spalvos iš powerbi/tema_klaipedos_pienas.json).
# Tai ne Power BI ekrano nuotraukos: jos atsiras, kai ataskaitos puslapiai bus sudėti GUI (docs/puslapiu_gidas.md).
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import data  # noqa: E402
import kpi  # noqa: E402
import planner_weather  # noqa: E402

IMG = data.ROOT / "docs" / "img"
BLUE, ORANGE, GRAY = "#2A78D6", "#EB6834", "#898781"
INK, INK2, GRID, BG = "#0B0B0B", "#52514E", "#E1E0D9", "#FCFCFB"

plt.rcParams.update({
    "font.family": "Segoe UI", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG, "figure.dpi": 150,
})


def lt(x: float, digits: int = 0) -> str:
    return f"{x:,.{digits}f}".replace(",", " ").replace(".", ",")


def finish(fig, ax, title: str, subtitle: str, name: str) -> None:
    ax.set_title(title, loc="left", fontsize=13, color=INK, fontweight="semibold", pad=24)
    ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=9.5, color=INK2, va="bottom")
    fig.text(0.01, 0.01, "Sintetiniai duomenys, mokomasis pavyzdys · orai: Open-Meteo", fontsize=7.5, color=GRAY)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    IMG.mkdir(parents=True, exist_ok=True)
    fig.savefig(IMG / name)
    plt.close(fig)
    print("Išsaugota:", IMG / name)


def weather_scatter() -> None:
    h = planner_weather.demand_vs_forecast()
    h = h[h["VASARA"]]
    g = h.groupby(["SAVAITE", "SALIS"]).agg(UZSAKYTA=("UZSAKYTA", "sum"), PROGNOZE=("PROGNOZE", "sum"),
                                             ANOMALIJA=("ANOMALIJA", "first")).reset_index()
    g["NUOKRYPIS"] = g["UZSAKYTA"] / g["PROGNOZE"] - 1
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.scatter(g["ANOMALIJA"], g["NUOKRYPIS"] * 100, s=22, color=BLUE, alpha=0.55, edgecolor=BG, linewidth=0.8)
    b = np.polyfit(g["ANOMALIJA"], np.log(g["UZSAKYTA"] / g["PROGNOZE"]), 1)
    xs = np.linspace(g["ANOMALIJA"].min(), g["ANOMALIJA"].max(), 50)
    ax.plot(xs, (np.exp(b[1] + b[0] * xs) - 1) * 100, color=INK2, linewidth=2)
    heat = g[g["SAVAITE"] == pd.Timestamp("2026-06-22")]
    ax.scatter(heat["ANOMALIJA"], heat["NUOKRYPIS"] * 100, s=60, color=ORANGE, edgecolor=BG, linewidth=1.5, zorder=3)
    for _, r in heat.iterrows():
        if r["SALIS"] in ("GB", "DE", "LT"):
            ax.annotate(f"{r['SALIS']} 06-22", (r["ANOMALIJA"], r["NUOKRYPIS"] * 100), xytext=(6, 4),
                        textcoords="offset points", fontsize=8.5, color=INK)
    ax.axhline(0, color=GRAY, linewidth=0.8)
    ax.set_xlabel("Savaitės maks. temperatūra − norma, °C")
    ax.set_ylabel("Užsakyta vs prognozė, %")
    finish(fig, ax, f"+1 °C virš normos ≈ +{lt((math.exp(b[0]) - 1) * 100, 1)} % užsakymų",
           "Vasaros savaitės (V–IX) × 6 rinkos, 2025–2026. Oranžinė: 2026-06-22 karščio banga.", "orai_vs_prognoze.png")


def profit_waterfall() -> None:
    s = data.sales()
    cur = s[(s["DATA"].dt.year == 2026) & s["DATA"].dt.month.between(4, 9)]
    prev = s[(s["DATA"].dt.year == 2025) & s["DATA"].dt.month.between(4, 9)]
    b = kpi.profit_bridge(cur, prev)
    steps = [("Kiekis", b["kiekis_eur"]), ("Produktų ir\nklientų mix", b["mix_eur"]),
             ("Kainos ir\nnuolaidos", b["kaina_ir_nuolaidos_eur"]), ("Žaliavų kainos\n(grietinėlė)", b["zaliavu_kainos_eur"])]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    running = 0.0
    for i, (label, v) in enumerate(steps):
        bottom = running if v >= 0 else running + v
        ax.bar(i, abs(v) / 1000, bottom=bottom / 1000, color=BLUE if v >= 0 else ORANGE, width=0.6, edgecolor=BG,
               linewidth=2)
        ax.text(i, (running + max(v, 0)) / 1000 + 12, ("+" if v >= 0 else "−") + lt(abs(v) / 1000) + " tūkst. €",
                ha="center", fontsize=9, color=INK)
        running += v
    ax.bar(len(steps), running / 1000, color=INK2, width=0.6, edgecolor=BG, linewidth=2)
    ax.text(len(steps), running / 1000 + 12, "+" + lt(running / 1000) + " tūkst. €", ha="center", fontsize=9,
            color=INK, fontweight="semibold")
    ax.set_xticks(range(len(steps) + 1), [l for l, _ in steps] + ["Pelno\npokytis"])
    ax.set_ylabel("tūkst. €")
    ax.axhline(0, color=GRAY, linewidth=0.8)
    ax.grid(axis="x", visible=False)
    m_now = 1 - cur["SAVIKAINA"].sum() / cur["PAJAMOS"].sum()
    m_py = 1 - prev["SAVIKAINA"].sum() / prev["PAJAMOS"].sum()
    finish(fig, ax, "Kodėl marža krito, nors pelnas augo",
           f"Bendrojo pelno pokytis 2026 IV–IX vs 2025 IV–IX. Marža {lt(m_py * 100, 1)} % → {lt(m_now * 100, 1)} %.",
           "pelno_skaidymas.png")


def kre_l2() -> None:
    p = data.production()
    plan = data.plan()
    weeks = pd.date_range("2026-04-06", "2026-09-28", freq="7D")
    prod = p[p["LINIJA"] == "KRE-L2"].groupby("SAVAITE")["PAGAMINTA_VNT"].sum().reindex(weeks, fill_value=0)
    pl = plan[plan["Linija"] == "KRE-L2"].groupby("Savaitės pradžia")["VNT"].sum().reindex(weeks, fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.plot(weeks, pl / 1000, color=GRAY, linewidth=2, label="Planas (Excel)")
    ax.plot(weeks, prod / 1000, color=BLUE, linewidth=2, label="Pagaminta (ERP)")
    ax.axvspan(pd.Timestamp("2026-06-22"), pd.Timestamp("2026-07-19"), color=ORANGE, alpha=0.12, linewidth=0)
    top = max(pl.max(), prod.max()) / 1000
    ax.set_ylim(0, top * 1.25)
    ax.text(pd.Timestamp("2026-06-24"), top * 1.23, "Kompresoriaus gedimas →\ndalys → remontas →\npaleidimas",
            fontsize=8.5, color=INK, va="top")
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    ax.set_ylabel("tūkst. vnt. per savaitę")
    ax.set_xlim(weeks[0], weeks[-1])
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    finish(fig, ax, "Kretingos puodelių linija (KRE-L2): 4 savaitės pačiame sezone",
           "Gamybos planas ir faktas, 2026 IV–IX. Birželį pristatyta tik 77 % puodelių užsakymų.", "kre_l2.png")


def weather_backtest() -> None:
    h = planner_weather.demand_vs_forecast()
    sens = planner_weather.sensitivity(h[h["SAVAITE"].dt.year == 2025])
    t = h[(h["SAVAITE"].dt.year == 2026) & h["VASARA"]].copy()
    t["SU_ORAIS"] = t["PROGNOZE"] * (1 + np.array([planner_weather.adjustment(sens.get((c, True), 0.0), a)
                                                    for c, a in zip(t["KATEGORIJA"], t["ANOMALIJA"])]))
    w = t.groupby("SAVAITE")[["UZSAKYTA", "PROGNOZE", "SU_ORAIS"]].sum() / 1000
    r = planner_weather.backtest()
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.plot(w.index, w["PROGNOZE"], color=GRAY, linewidth=2, label="Planuotojo prognozė (be orų)")
    ax.plot(w.index, w["SU_ORAIS"], color=BLUE, linewidth=2, label="Prognozė su orų pataisa")
    ax.plot(w.index, w["UZSAKYTA"], color=ORANGE, linewidth=2, linestyle=(0, (4, 2)), label="Užsakyta iš tikrųjų")
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    ax.set_ylabel("tūkst. vnt. per savaitę")
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    finish(fig, ax, f"Orų pataisa: prognozės tikslumas {lt(r['planuotojo_tikslumas_proc'], 1)} % → "
           f"{lt(r['su_orais_tikslumas_proc'], 1)} %",
           "2026 m. V–IX. Jautrumas apskaičiuotas tik iš 2025 m., todėl 2026 m. modeliui yra nauji duomenys.",
           "oru_pataisa.png")


if __name__ == "__main__":
    weather_scatter()
    profit_waterfall()
    kre_l2()
    weather_backtest()
