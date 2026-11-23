"""Sugeneruoja Power BI ataskaitos puslapius (PBIR formatu) iš aprašo šiame faile.

Kiekvienas vizualas yra vienas JSON failas KlaipedosPienas.Report/definition/pages/<puslapis>/visuals/.
Paleisti, kai Power BI Desktop uždarytas:  python powerbi/kurti_ataskaita.py
Skriptas perrašo visus puslapius, todėl rankiniai pakeitimai Desktop'e dingtų.
Jei ataskaitą toliau tvarkai ranka, šio skripto nebeleisk.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

REPORT = Path(__file__).parent / "KlaipedosPienas.Report" / "definition"
SCH = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"
W, H = 1280, 720
FOOTER = "Sintetiniai duomenys · mokomasis pavyzdys, ne tikri AB „Klaipėdos pienas“ skaičiai · Orai: Open-Meteo"
GREY = "#9AA0A6"
DARK = "#0B0B0B"
MUTED = "#5F6368"


# ---------- pagalbinės funkcijos ----------

def lit(v):
    if isinstance(v, bool):
        s = "true" if v else "false"
    elif isinstance(v, int):
        s = f"{v}L"
    elif isinstance(v, float):
        s = f"{v}D"
    else:
        s = "'" + str(v).replace("'", "''") + "'"
    return {"expr": {"Literal": {"Value": s}}}


def color(c):
    return {"solid": {"color": lit(c)}}


def table_of(ref: str) -> tuple[str, str, bool]:
    """'_Matai[Pajamos]' -> (lentelė, laukas, ar matas). Matai prasideda 'M:'."""
    measure = ref.startswith("M:")
    ref = ref[2:] if measure else ref
    t, f = ref.split("[", 1)
    return t, f.rstrip("]"), measure


def field(ref: str):
    t, f, m = table_of(ref)
    kind = "Measure" if m else "Column"
    return {kind: {"Expression": {"SourceRef": {"Entity": t}}, "Property": f}}


def proj(ref: str, display: str | None = None):
    t, f, _ = table_of(ref)
    p = {"field": field(ref), "queryRef": f"{t}.{f}", "nativeQueryRef": f}
    if display is not None:
        p["displayName"] = display
    return p


def M(name: str) -> str:
    return f"M:_Matai[{name}]"


def in_filter(ref: str, values: list, name: str):
    t, f, _ = table_of(ref)
    return {
        "name": name,
        "field": field(ref),
        "type": "Categorical",
        "filter": {
            "Version": 2,
            "From": [{"Name": "t", "Entity": t, "Type": 0}],
            "Where": [{"Condition": {"In": {
                "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": f}}],
                "Values": [[lit(v)["expr"]] for v in values],
            }}}],
        },
    }


def week_filter(day: str, name: str):
    """Categorical filtras vienai savaitei: Data[Savaitės pradžia] = datetime literalas."""
    return {
        "name": name,
        "field": field("Data[Savaitės pradžia]"),
        "type": "Categorical",
        "filter": {
            "Version": 2,
            "From": [{"Name": "d", "Entity": "Data", "Type": 0}],
            "Where": [{"Condition": {"In": {
                "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": "Savaitės pradžia"}}],
                "Values": [[{"Literal": {"Value": f"datetime'{day}T00:00:00'"}}]],
            }}}],
        },
    }


def slicer_selection(ref: str, values: list):
    t, f, _ = table_of(ref)
    return {"filter": {
        "Version": 2,
        "From": [{"Name": "t", "Entity": t, "Type": 0}],
        "Where": [{"Condition": {"In": {
            "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": f}}],
            "Values": [[lit(v)["expr"]] for v in values],
        }}}],
    }}


class Page:
    def __init__(self, key: str, title: str, subtitle: str | None = None):
        self.key, self.title = key, title
        self.name = hashlib.md5(key.encode()).hexdigest()[:20]
        self.visuals: list[dict] = []
        self.interactions: list[dict] = []
        self.filters: list[dict] = []
        self.z = 0
        self.text(title, 16, 0, 900, 54, size=18, bold=True)
        if subtitle:
            self.text(subtitle, 16, 40, 960, 40, size=10, col=MUTED)
        self.text(FOOTER, 24, 692, 1000, 22, size=8, col=GREY)

    def _vid(self):
        return f"{self.name[:8]}v{len(self.visuals):02d}"

    def add(self, vtype, x, y, w, h, roles=None, title=None, objects=None, vco=None,
            filters=None, sort=None, name=None):
        vid = name or self._vid()
        visual = {"visualType": vtype, "drillFilterOtherVisuals": True}
        if roles:
            qs = {}
            for role, refs in roles.items():
                qs[role] = {"projections": [r if isinstance(r, dict) else proj(r) for r in refs]}
            visual["query"] = {"queryState": qs}
            if sort:
                ref, direction = sort
                visual["query"]["sortDefinition"] = {"sort": [{"field": field(ref), "direction": direction}],
                                                     "isDefaultSort": False}
        if objects:
            visual["objects"] = objects
        vco = dict(vco or {})
        if title is not None:
            vco["title"] = [{"properties": {"show": lit(bool(title)), **({"text": lit(title)} if title else {})}}]
        if vtype not in ("textbox", "actionButton"):
            # Naujas Power BI automatiškai rodo angliškas paantraštes („X by Y“): išjungiame.
            vco.setdefault("subTitle", [{"properties": {"show": lit(False)}}])
        if vco:
            visual["visualContainerObjects"] = vco
        cont = {
            "$schema": f"{SCH}/visualContainer/2.4.0/schema.json",
            "name": vid,
            "position": {"x": x, "y": y, "z": self.z, "width": w, "height": h, "tabOrder": self.z},
            "visual": visual,
        }
        if filters:
            cont["filterConfig"] = {"filters": filters}
        self.z += 1000
        self.visuals.append(cont)
        return vid

    # --- dažni vizualai ---
    def text(self, txt, x, y, w, h, size=11, bold=False, col=DARK):
        paragraphs = []
        for line in txt.split("\n"):
            style = {"fontSize": f"{size}pt", "color": col}
            if bold:
                style["fontWeight"] = "bold"
            paragraphs.append({"textRuns": [{"value": line, "textStyle": style}]})
        return self.add("textbox", x, y, w, h, objects={"general": [{"properties": {"paragraphs": paragraphs}}]},
                        vco={"background": [{"properties": {"show": lit(False)}}],
                             "border": [{"properties": {"show": lit(False)}}]})

    def card(self, measure, x, y, w, h, label=None, size=22, wrap=False):
        hide = label == ""
        objs = {"labels": [{"properties": {"fontSize": lit(float(size))}}],
                "categoryLabels": [{"properties": {"show": lit(not hide), "fontSize": lit(9.0)}}]}
        if wrap:
            objs["wordWrap"] = [{"properties": {"show": lit(True)}}]
        return self.add("card", x, y, w, h, roles={"Values": [proj(M(measure), None if hide else label)]}, objects=objs)

    def slicer(self, ref, x, y, w, h, title, mode="Dropdown", single=False, select=None, search=False):
        objs = {"data": [{"properties": {"mode": lit(mode)}}]}
        if title:
            # Pavadinimas jau rodomas vizualo antraštėje, slicerio galvutė tik užima vietą.
            objs["header"] = [{"properties": {"show": lit(False)}}]
        if single:
            objs["selection"] = [{"properties": {"singleSelect": lit(True), "strictSingleSelect": lit(True)}}]
        general = {}
        if select:
            general["filter"] = slicer_selection(ref, select)
        if search:
            general["selfFilterEnabled"] = lit(True)
        if general:
            objs["general"] = [{"properties": general}]
        return self.add("slicer", x, y, w, h, roles={"Values": [ref]}, title=title, objects=objs)

    def button(self, label, x, y, w, h, target: "Page", fill="#2A78D6", fcol="#FFFFFF"):
        objs = {
            "icon": [{"properties": {"show": lit(False)}}],
            "text": [{"properties": {"show": lit(True), "text": lit(label), "fontColor": color(fcol),
                                     "fontSize": lit(12.0), "bold": lit(True)}}],
            "fill": [{"properties": {"show": lit(True), "fillColor": color(fill), "transparency": lit(0.0)}}],
            "outline": [{"properties": {"show": lit(False)}}],
        }
        vco = {"visualLink": [{"properties": {"show": lit(True), "type": lit("PageNavigation"),
                                              "navigationSection": lit(target.name)}}]}
        return self.add("actionButton", x, y, w, h, objects=objs, vco=vco, title=False)

    def no_filter(self, source, targets):
        for t in targets:
            self.interactions.append({"source": source, "target": t, "type": "NoFilter"})


def series_colors(mapping: dict[str, str]):
    return {"dataPoint": [{"properties": {"fill": color(c)}, "selector": {"metadata": ref}}
                          for ref, c in mapping.items()]}


def table_obj(font=10, wrap=True, widths: dict[str, float] | None = None, totals=False):
    o = {
        "values": [{"properties": {"fontSize": lit(float(font)), "wordWrap": lit(wrap)}}],
        "columnHeaders": [{"properties": {"fontSize": lit(float(font)), "wordWrap": lit(True)}}],
        "total": [{"properties": {"totals": lit(totals)}}],
    }
    if widths:
        o["columnWidth"] = [{"properties": {"value": lit(float(v))}, "selector": {"metadata": k}}
                            for k, v in widths.items()]
    return o


# ---------- puslapiai ----------

def build() -> list[Page]:
    P = {}
    order = ["virselis", "klausk", "apzvalga", "kodel", "planavimas", "gamyba", "procesas",
             "kokybe", "atsaukimas", "pardavimai", "di"]
    titles = {
        "virselis": ("Klaipėdos pienas · ledų gamyba", None),
        "klausk": ("Klausk duomenų", "Pasirink klausimą. Atsakymą DAX suskaičiuoja iš to paties modelio, todėl skaičiai visada sutampa su ataskaita."),
        "apzvalga": ("Apžvalga", "Pagrindiniai rodikliai ir automatiniai įspėjimai pasirinktam laikotarpiui"),
        "kodel": ("Kodėl?", None),
        "planavimas": ("Planavimas: orai ir prognozė", "Kiek orai keičia užsakymus ir kiek pataisyti prognozę"),
        "gamyba": ("Gamyba", "Planas ir faktas, prastovos ir brokas pagal liniją"),
        "procesas": ("Procesas: nuo žaliavos iki lentynos", "Kur partija praleidžia laiką ir kur kontrolės taškai neatitinka ribų"),
        "kokybe": ("Kokybė", "Pirmo karto atitiktis, skundai ir partijų sprendimai"),
        "atsaukimas": ("Atšaukimo simuliacija", "Pasirink partiją: kam išsiųsta, iš ko pagaminta, ką rodė kontrolė"),
        "pardavimai": ("Pardavimai", "Rinkos, klientai, kategorijos ir sezoniškumas"),
        "di": ("Duomenų kokybė ir DI", "Ką patikros rado duomenyse ir kaip DI apdoroja tiekėjų sąskaitas"),
    }
    names = {"virselis": "Viršelis", "klausk": "Klausk", "apzvalga": "Apžvalga", "kodel": "Kodėl?",
             "planavimas": "Planavimas", "gamyba": "Gamyba", "procesas": "Procesas", "kokybe": "Kokybė",
             "atsaukimas": "Atšaukimas", "pardavimai": "Pardavimai", "di": "Duomenų kokybė ir DI"}
    for k in order:
        P[k] = Page(k, *titles[k])
        P[k].display = names[k]

    month = "Data[Metai-mėnuo]"

    # --- Viršelis ---
    p = P["virselis"]
    p.visuals = p.visuals[:0]  # be standartinės antraštės
    p.z = 0
    p.text("Klaipėdos pienas · ledų gamyba", 60, 70, 1100, 60, size=32, bold=True)
    p.text("Power BI + DI pavyzdys · 2025-01 – 2026-10 · ERP, planuotojo Excel, laboratorija, sandėlis, skundai, DI nuskaitytos sąskaitos ir tikri orai viename modelyje",
           60, 135, 1100, 50, size=12, col=MUTED)
    p.text("Sintetiniai duomenys. Mokomasis pavyzdys, nesusijęs su AB „Klaipėdos pienas“. Tiekėjai išgalvoti, orai tikri (Open-Meteo).",
           60, 190, 1100, 30, size=10, col="#B3261E")
    p.card("Pajamos", 60, 240, 260, 110)
    p.card("Marža %", 340, 240, 260, 110)
    p.card("Užsakymų įvykdymas %", 620, 240, 260, 110)
    p.card("Pirmo karto atitiktis %", 900, 240, 260, 110)
    p.text("Trys istorijos duomenyse", 60, 380, 600, 34, size=16, bold=True)
    p.button("1 · Karščio banga", 60, 420, 260, 56, P["planavimas"])
    p.button("2 · Linija sugedo", 340, 420, 260, 56, P["gamyba"])
    p.button("3 · Kodėl krito marža", 620, 420, 260, 56, P["kodel"])
    p.button("Atšaukimas pagal partiją", 900, 420, 260, 56, P["atsaukimas"])
    p.text("Arba paklausk", 60, 500, 600, 34, size=16, bold=True)
    p.button("Klausk duomenų →", 60, 540, 540, 64, P["klausk"], fill="#0B0B0B")
    p.button("Apžvalga →", 620, 540, 540, 64, P["apzvalga"], fill="#FFFFFF", fcol="#2A78D6")
    p.text(FOOTER, 24, 692, 1000, 22, size=8, col=GREY)

    # --- Klausk ---
    p = P["klausk"]
    p.slicer("Atsakymai[Klausimas]", 24, 80, 400, 380, "Klausimas", mode="Basic", single=True,
             select=["Kodėl 2026 m. birželį trūko puodelių?"])
    p.slicer("Oro scenarijus[Nukrypimas °C]", 24, 470, 400, 90, "4 klausimui: kiek šilčiau nei įprasta? (°C)",
             mode="Dropdown", single=True, select=[6])
    p.slicer("Partija[Partija paieškai]", 24, 570, 400, 90, "7 klausimui: partija", single=True, search=True,
             select=["P26-001885 · KAR KAR šerbetas mangų 500 ml · 2026-07-17"])
    p.card("Pasirinktas klausimas", 440, 80, 816, 70, label="", size=16, wrap=True)
    p.add("tableEx", 440, 160, 816, 440,
          roles={"Values": [proj("Atsakymai[Eilutė]", " "), proj(M("Atsakymas"), "Atsakymas")]},
          sort=("Atsakymai[Eilutė]", "Ascending"),
          objects=table_obj(font=12, widths={"Atsakymai.Eilutė": 110.0, "_Matai.Atsakymas": 680.0}),
          title=False)
    p.text("Atsakymus skaičiuoja DAX matas [Atsakymas] tiesiai iš modelio, be interneto ir be DI. "
           "Laisvus klausimus galima užduoti Claude (Claude Code + Power BI Modeling MCP, skilas /klausk-duomenu).",
           440, 610, 816, 60, size=9, col=MUTED)

    # --- Apžvalga ---
    p = P["apzvalga"]
    s = p.slicer(month, 1000, 4, 256, 72, "Mėnuo")
    for i, (m, lbl) in enumerate([("Pajamos", None), ("Marža %", None), ("Užsakymų įvykdymas %", None),
                                  ("Pirmo karto atitiktis %", None)]):
        p.card(m, 24 + i * 310, 80, 298, 100, label=lbl)
    for i, m in enumerate(["Įspėjimas: trūkumai", "Įspėjimas: marža", "Įspėjimas: prognozė", "Įspėjimas: kokybė"]):
        p.card(m, 24 + i * 310, 190, 298, 90, label="", size=11, wrap=True)
    p.add("clusteredColumnChart", 24, 290, 610, 395, roles={"Category": [month], "Y": [M("Pajamos")],
          "Tooltips": [M("Pajamos YoY %"), M("Marža %")]}, title="Pajamos pagal mėnesį")
    p.add("lineChart", 646, 290, 610, 395, roles={"Category": [month], "Y": [M("Marža %"), M("Marža % PY")]},
          title="Marža %: šie metai ir pernai", objects=series_colors({"_Matai.Marža % PY": GREY, "_Matai.Marža %": "#2A78D6"}))

    # --- Kodėl? ---
    p = P["kodel"]
    sel = ["2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09"]
    s = p.slicer(month, 1000, 4, 256, 72, "Laikotarpis", select=sel)
    p.card("Antraštė: kodėl", 24, 80, 960, 40, label="", size=14, wrap=True)
    p.add("waterfallChart", 24, 125, 600, 300,
          roles={"Category": ["Maržos veiksniai[Veiksnys]"], "Y": [M("Veiksnio poveikis")]},
          title="Bendrojo pelno pokytis vs pernai: kas jį lėmė", sort=("Maržos veiksniai[Veiksnys]", "Ascending"),
          objects={"legend": [{"properties": {"show": lit(False)}}]})
    # Skaidymo medis PBIR faile neišsaugo išskleidimo, todėl vietoj jo du aiškūs skaidymai.
    p.add("clusteredBarChart", 640, 125, 616, 270,
          roles={"Category": ["Klientas[Rinka]"], "Y": [M("Pelno pokyčis vs PY")]},
          title="Pelno pokytis vs pernai pagal rinką (spustelėk, kad filtruotum)",
          sort=(M("Pelno pokyčis vs PY"), "Descending"))
    p.add("clusteredBarChart", 640, 405, 616, 280,
          roles={"Category": ["Produktas[Kategorija]"], "Y": [M("Pelno pokyčis vs PY")]},
          title="Pelno pokytis vs pernai pagal kategoriją",
          sort=(M("Pelno pokyčis vs PY"), "Descending"))
    g = p.add("lineChart", 24, 435, 300, 250, roles={"Category": [month], "Y": [M("Vid. pirkimo kaina")]},
              title="Grietinėlės 35 % kaina, €/kg",
              filters=[in_filter("Žaliava[Žaliava]", ["Grietinėlė 35 %"], "fGriet")])
    b = p.add("clusteredBarChart", 334, 435, 290, 250,
              roles={"Category": ["Žaliava[Žaliava]"], "Y": [M("Žaliavų kainų indeksas")]},
              title="Žaliavų kainų indeksas", sort=(M("Žaliavų kainų indeksas"), "Descending"))
    p.no_filter(s, [g])

    # --- Planavimas ---
    p = P["planavimas"]
    summer = in_filter("Data[Mėnesio nr]", [5, 6, 7, 8, 9], "fVasara")
    p.add("scatterChart", 24, 80, 620, 370,
          roles={"Category": ["Data[Savaitės pradžia]"], "X": [M("Nukrypimas nuo normos °C")],
                 "Y": [M("Prognozės nuokrypis %")]},
          title="Kiekviena vasaros savaitė: oras vs prognozės klaida",
          objects={"trend": [{"properties": {"show": lit(True)}}]}, filters=[summer])
    p.card("Paklausos jautrumas 1 °C", 660, 80, 192, 100, label="+1 °C virš normos")
    p.add("card", 862, 80, 192, 100, roles={"Values": [proj(M("Prognozės tikslumas %"), "Tikslumas 2025 VI–VIII")]},
          objects={"labels": [{"properties": {"fontSize": lit(22.0)}}]},
          filters=[in_filter("Data[Metai]", [2025], "f25"), in_filter("Data[Mėnesio nr]", [6, 7, 8], "f25m")])
    p.add("card", 1064, 80, 192, 100, roles={"Values": [proj(M("Prognozės tikslumas %"), "Tikslumas 2026 VI–VIII")]},
          objects={"labels": [{"properties": {"fontSize": lit(22.0)}}]},
          filters=[in_filter("Data[Metai]", [2026], "f26"), in_filter("Data[Mėnesio nr]", [6, 7, 8], "f26m")])
    p.slicer("Oro scenarijus[Nukrypimas °C]", 660, 190, 300, 90, "Kiek šilčiau nei įprasta? (°C)",
             mode="Dropdown", single=True, select=[6])
    p.card("Rekomenduojamas prognozės pokytis %", 970, 190, 140, 90, label="Prognozę keisti", size=16)
    p.add("card", 1116, 190, 140, 90, roles={"Values": [proj(M("Papildomai reikia vnt"), "Papildomai 06-22 sav., vnt.")]},
          objects={"labels": [{"properties": {"fontSize": lit(16.0)}}]}, filters=[week_filter("2026-06-22", "fSavK")])
    p.text("Karščio savaitė 2026-06-22 (+6 °C): ar orų pataisa būtų padėjusi?", 660, 282, 596, 48, size=11, bold=True)
    for i, (m, lbl) in enumerate([("Prognozė vnt", "Planuotojo prognozė, vnt."),
                                  ("Prognozė su orais vnt", "Su orų pataisa, vnt."),
                                  ("Užsakyta vnt", "Iš tikrųjų užsakyta, vnt.")]):
        p.add("card", 660 + i * 202, 330, 192, 120, roles={"Values": [proj(M(m), lbl)]},
              objects={"labels": [{"properties": {"fontSize": lit(20.0)}}]},
              filters=[week_filter("2026-06-22", f"fSav{i}")])
    p.add("lineChart", 24, 460, 616, 225, roles={"Category": ["Data[Savaitės pradžia]"], "Y": [M("Nukrypimas nuo normos °C")]},
          title="Oras: nukrypimas nuo normos, °C", filters=[in_filter("Data[Metai]", [2026], "fL1")])
    p.add("lineChart", 650, 460, 606, 225, roles={"Category": ["Data[Savaitės pradžia]"], "Y": [M("Prognozės nuokrypis %")]},
          title="Užsakymai vs prognozė, %", objects=series_colors({"_Matai.Prognozės nuokrypis %": "#EB6834"}),
          filters=[in_filter("Data[Metai]", [2026], "fL2")])

    # --- Gamyba ---
    p = P["gamyba"]
    # Numatytai VI–VII, kad iš karto matytųsi KRE-L2 gedimas (istorija 2).
    s = p.slicer(month, 1000, 4, 256, 72, "Mėnuo", select=["2026-06", "2026-07"])
    p.add("lineChart", 24, 80, 820, 300, roles={"Category": ["Data[Savaitės pradžia]"], "Y": [M("Planas vnt"), M("Pagaminta vnt")]},
          title="Planas ir pagaminta per savaitę", objects=series_colors({"_Matai.Planas vnt": GREY, "_Matai.Pagaminta vnt": "#2A78D6"}))
    p.card("Plano įvykdymas %", 860, 80, 396, 92)
    p.card("Prastovų dalis %", 860, 184, 396, 92)
    p.card("Brokas %", 860, 288, 396, 92)
    p.add("clusteredColumnChart", 24, 390, 500, 295, roles={"Category": ["Linija[Linija]"], "Y": [M("Plano įvykdymas %")]},
          title="Plano įvykdymas pagal liniją", sort=(M("Plano įvykdymas %"), "Ascending"))
    p.add("barChart", 540, 390, 440, 295, roles={"Category": ["Prastovos[Priežastis]"], "Y": [M("Prastovos min")]},
          title="Prastovos pagal priežastį, min", sort=(M("Prastovos min"), "Descending"))
    p.slicer("Linija[Linija]", 996, 390, 260, 295, "Linija", mode="Basic")

    # --- Procesas ---
    p = P["procesas"]
    s = p.slicer(month, 1000, 4, 256, 72, "Mėnuo")
    p.add("barChart", 24, 80, 640, 320,
          roles={"Category": ["Partijų etapai[Etapas]"], "Y": [M("Vid. etapo trukmė h"), M("Vid. laukimas prieš etapą h")]},
          title="Etapo trukmė ir laukimas prieš etapą, h", sort=("Partijų etapai[Etapas]", "Ascending"),
          objects=series_colors({"_Matai.Vid. etapo trukmė h": "#2A78D6", "_Matai.Vid. laukimas prieš etapą h": "#EB6834"}))
    l = p.add("lineChart", 680, 80, 576, 320, roles={"Category": [month], "Y": [M("Laukimas prieš šaldymą h")]},
              title="Laukimas prieš šaldymą: vasarą eilė prie frizerio",
              objects=series_colors({"_Matai.Laukimas prieš šaldymą h": "#EB6834"}))
    p.card("Vid. gamybos ciklas h", 24, 410, 205, 90)
    p.card("Laukimo dalis %", 241, 410, 205, 90)
    p.card("KVT nukrypimai", 458, 410, 206, 90)
    p.text("Etapai yra tipinė ledų gamybos technologija. Tikroje įmonėje jie būtų paimti iš linijų SCADA/MES sistemos. "
           "KVT = kritinis valdymo taškas (RVASVT): pasterizacija ≥ 80 °C, metalo detektorius, grūdinimas ≤ −35 °C.",
           24, 510, 640, 80, size=10, col=MUTED)
    p.add("tableEx", 680, 410, 576, 275,
          roles={"Values": ["Partijų etapai[Partijos nr]", "Partijų etapai[Etapas]", "Partijų etapai[Kontrolė]",
                            "Partijų etapai[Reikšmė]", "Partijų etapai[Riba min]", "Partijų etapai[Riba max]"]},
          title="Kontrolės taškai, kurie neatitiko ribų", objects=table_obj(font=9),
          filters=[in_filter("Partijų etapai[Atitinka]", ["Ne"], "fNe")])
    p.no_filter(s, [l])

    # --- Kokybė ---
    p = P["kokybe"]
    s = p.slicer(month, 1000, 4, 256, 72, "Partijos gamybos mėnuo")
    for i, m in enumerate(["Pirmo karto atitiktis %", "Skundai 1 mln. vnt.", "Grūdinimo nukrypimai", "Laboratorijos neatitiktys"]):
        p.card(m, 24 + i * 310, 80, 298, 90)
    p.add("columnChart", 24, 180, 740, 280,
          roles={"Category": ["Skundai[Gavimo mėnuo]"], "Series": ["Skundai[Tipas]"], "Y": [M("Skundų sk.")]},
          title="Skundai pagal gavimo mėnesį ir tipą", sort=("Skundai[Gavimo mėnuo]", "Ascending"))
    p.add("clusteredBarChart", 780, 180, 476, 280, roles={"Category": ["Partija[Būsena]"], "Y": [M("Partijų sk.")]},
          title="Partijos pagal sprendimą", sort=(M("Partijų sk."), "Descending"))
    p.add("tableEx", 24, 470, 1232, 215,
          roles={"Values": ["Skundai[Skundo nr]", "Skundai[Gauta]", "Skundai[Klientas]", "Skundai[Partijos nr]",
                            "Skundai[Tipas]", "Skundai[Būsena]", "Skundai[Korekcinis veiksmas]"]},
          title="Skundų registras", objects=table_obj(font=9), sort=("Skundai[Gauta]", "Descending"))

    # --- Atšaukimas ---
    p = P["atsaukimas"]
    p.slicer("Partija[Partija paieškai]", 24, 76, 520, 68, "Partija (įvesk numerį)", single=True, search=True,
             select=["P26-001885 · KAR KAR šerbetas mangų 500 ml · 2026-07-17"])
    p.card("Antraštė: partija", 560, 76, 696, 62, label="", size=13, wrap=True)
    for i, (m, lbl) in enumerate([("Atšaukimas: klientų sk.", "Klientų"), ("Išsiųsta vnt", "Išsiųsta, vnt."),
                                  ("Atšaukimas: likutis sandėlyje vnt", "Likutis sandėlyje, vnt."),
                                  ("Atšaukimas: atsekta %", "Atsekta"), ("Atšaukimas: tiekėjų sąskaitų sk.", "Tiekėjų sąskaitų")]):
        p.card(m, 24 + i * 248, 148, 236, 80, label=lbl, size=18)
    p.add("tableEx", 24, 238, 610, 215,
          roles={"Values": ["Klientas[Klientas]", "Siuntos[Siuntos nr]", "Siuntos[Siuntos data]", M("Išsiųsta vnt")]},
          title="Kam išsiųsta", objects=table_obj(font=10))
    p.add("tableEx", 646, 238, 610, 215,
          roles={"Values": ["Žaliava[Žaliava]", "Tiekėjas[Tiekėjas]", "Žaliavų sunaudojimas[Tiekėjo sąskaita]",
                            "Žaliavų sunaudojimas[Sunaudota]"]},
          title="Iš ko pagaminta", objects=table_obj(font=10))
    p.add("tableEx", 24, 463, 610, 222,
          roles={"Values": ["Partijų etapai[Etapas]", "Partijų etapai[Pradžia]", "Partijų etapai[Kontrolė]",
                            "Partijų etapai[Reikšmė]", "Partijų etapai[Atitinka]"]},
          title="Gamybos kelias", objects=table_obj(font=9), sort=("Partijų etapai[Etapas]", "Ascending"))
    p.add("tableEx", 646, 463, 610, 222,
          roles={"Values": ["Lab tyrimai[Rodiklis]", "Lab tyrimai[Rezultatas]", "Lab tyrimai[Matas]",
                            "Lab tyrimai[Riba min]", "Lab tyrimai[Riba max]", "Lab tyrimai[Atitinka]"]},
          title="Laboratorija", objects=table_obj(font=9))

    # --- Pardavimai ---
    p = P["pardavimai"]
    s = p.slicer(month, 1000, 4, 256, 72, "Mėnuo")
    p.add("pivotTable", 24, 80, 640, 605,
          roles={"Rows": ["Klientas[Rinka]", "Klientas[Klientas]"],
                 "Values": [M("Pajamos"), M("Pajamos YoY %"), M("Marža %"), M("Akcijų pajamų dalis %"), M("Užsakymų įvykdymas %")]},
          title="Rinkos ir klientai", objects=table_obj(font=10, totals=True))
    p.add("clusteredBarChart", 680, 80, 576, 290, roles={"Category": ["Produktas[Kategorija]"], "Y": [M("Pajamos")],
          "Tooltips": [M("Marža %")]}, title="Pajamos pagal kategoriją", sort=(M("Pajamos"), "Descending"))
    p.add("clusteredColumnChart", 680, 380, 576, 305,
          roles={"Category": ["Data[Mėnuo]"], "Series": ["Data[Metai]"], "Y": [M("Parduota vnt")]},
          title="Sezoniškumas: parduota vnt. pagal mėnesį", sort=("Data[Mėnuo]", "Ascending"))

    # --- DI ---
    p = P["di"]
    p.add("tableEx", 24, 80, 740, 350,
          roles={"Values": ["Kokybės patikros[Sritis]", "Kokybės patikros[Patikra]", M("Rasta atvejų"),
                            "Kokybės patikros[Kas daroma]"]},
          title="Duomenų kokybės patikros", objects=table_obj(font=9))
    p.card("DI apdorota sąskaitų", 780, 80, 233, 85)
    p.card("DI automatizavimo lygis %", 1023, 80, 233, 85)
    p.card("DI kaina USD", 780, 175, 233, 85)
    p.card("Sutaupyta laiko min", 1023, 175, 233, 85)
    p.text("PDF sąskaita → Claude (struktūruotas JSON pagal schemą) → taisyklės: eilučių suma, PVM, tiekėjas žinomas, "
           "ne dublikatas, valiuta EUR → ERP importo failas.\nAbejotinos sąskaitos keliauja žmogui (lentelė apačioje).\n"
           "Patikra su žinomais atsakymais: 378 iš 378 laukų teisingi.", 780, 270, 476, 160, size=10, col=MUTED)
    p.add("tableEx", 24, 440, 610, 245,
          roles={"Values": ["Peržiūra[Failas]", "Peržiūra[Tiekėjas]", "Peržiūra[Suma]", "Peržiūra[Priežastys]",
                            "Peržiūra[Įtartinas turinys]"]},
          title="Atiduota žmogui peržiūrėti", objects=table_obj(font=9))
    p.add("tableEx", 646, 440, 610, 245,
          roles={"Values": ["DI žurnalas[Failas]", "DI žurnalas[Statusas]", "DI žurnalas[Kaina USD]", "DI žurnalas[Trukmė s]"]},
          title="DI žurnalas", objects=table_obj(font=9))

    return [P[k] for k in order]


def write(pages: list[Page]) -> None:
    pdir = REPORT / "pages"
    if pdir.exists():
        shutil.rmtree(pdir)
    pdir.mkdir(parents=True)
    for p in pages:
        d = pdir / p.name
        (d / "visuals").mkdir(parents=True)
        page = {"$schema": f"{SCH}/page/2.1.0/schema.json", "name": p.name, "displayName": p.display,
                "displayOption": "FitToPage", "height": H, "width": W}
        if p.interactions:
            page["visualInteractions"] = p.interactions
        (d / "page.json").write_text(json.dumps(page, ensure_ascii=False, indent=2), encoding="utf-8")
        for v in p.visuals:
            vd = d / "visuals" / v["name"]
            vd.mkdir()
            (vd / "visual.json").write_text(json.dumps(v, ensure_ascii=False, indent=2), encoding="utf-8")
    meta = {"$schema": f"{SCH}/pagesMetadata/1.1.0/schema.json", "pageOrder": [p.name for p in pages],
            "activePageName": pages[0].name}
    (pdir / "pages.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(pages)} puslapiai, {sum(len(p.visuals) for p in pages)} vizualai")


if __name__ == "__main__":
    write(build())
