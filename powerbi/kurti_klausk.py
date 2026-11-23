"""Įdeda į modelį (TMDL) puslapio „Klausk“ lentelę ir atsakymų matus.

Atsakymai skaičiuojami DAX'u iš to paties modelio, todėl skaičiai visada sutampa
su ataskaita ir veikia be interneto ar DI (užtenka nemokamo Power BI Desktop).

Paleisti, kai Power BI Desktop uždarytas:  python powerbi/kurti_klausk.py
Skriptą galima leisti pakartotinai: senus „Klausk“ objektus jis pakeičia naujais.
"""
from __future__ import annotations

import re
import uuid
from pathlib import Path

DEF = Path(__file__).parent / "KlaipedosPienas.SemanticModel" / "definition"
FOLDER = "11 Klausk"

KLAUSIMAI = [
    (1, "Kaip sekasi šiais metais, palyginti su pernai?", "metai"),
    (2, "Kodėl 2026 m. birželį trūko puodelių?", "trūkumai"),
    (3, "Kodėl krito marža, nors pardavimai augo?", "marža"),
    (4, "Kiek daugiau gaminti, jei kitą savaitę bus karšta?", "karštis"),
    (5, "Ar linijos gedimas paveikė kokybę?", "kokybė"),
    (6, "Kur gamyboje partija stovi ilgiausiai?", "procesas"),
    (7, "Kas gavo partiją ir iš ko ji pagaminta?", "partija"),
    (8, "Kiek laiko ir pinigų sutaupo DI sąskaitoms?", "DI"),
    (9, "Ar galima pasitikėti šiais duomenimis?", "duomenys"),
]
EILUTES = [(1, "Atsakymas"), (2, "①"), (3, "②"), (4, "③"), (5, "④"), (6, "Ką daryti"), (7, "Kur žiūrėti")]

# Pagalbinės formatavimo išraiškos (lietuviški skaičiai)
def n(x):  # sveikas skaičius
    return f'FORMAT({x}, "#,0", "lt-LT")'

def eur(x):
    return f'FORMAT({x}, "#,0 €", "lt-LT")'

def seur(x):  # su ženklu
    return f'FORMAT({x}, "+#,0 €;-#,0 €", "lt-LT")'

def pct(x, d=1):
    z = "0" + ("." + "0" * d if d else "")
    return f'FORMAT({x}, "{z} %", "lt-LT")'

def spct(x, d=1):
    z = "0" + ("." + "0" * d if d else "")
    return f'FORMAT({x}, "+{z} %;-{z} %", "lt-LT")'

def dec(x, d=1, sign=False):
    z = "0" + ("." + "0" * d if d else "")
    f = f"+{z};-{z}" if sign else z
    return f'FORMAT({x}, "{f}", "lt-LT")'


ATSAKYMAI = {}

ATSAKYMAI["metai"] = f"""
VAR e = SELECTEDVALUE(Atsakymai[Eilė])
VAR P26 = DATESBETWEEN(Data[Data], DATE(2026, 1, 1), DATE(2026, 10, 31))
VAR P25 = DATESBETWEEN(Data[Data], DATE(2025, 1, 1), DATE(2025, 10, 31))
VAR Paj26 = CALCULATE([Pajamos], P26)
VAR Paj25 = CALCULATE([Pajamos], P25)
VAR Pel26 = CALCULATE([Bendrasis pelnas], P26)
VAR Pel25 = CALCULATE([Bendrasis pelnas], P25)
VAR M26 = CALCULATE([Marža %], P26)
VAR M25 = CALCULATE([Marža %], P25)
VAR Iv = CALCULATE([Užsakymų įvykdymas %], P26)
VAR Pr = CALCULATE([Prarastos pajamos], P26)
VAR Rinkos =
    ADDCOLUMNS(
        FILTER(VALUES(Klientas[Rinka]), NOT ISBLANK(Klientas[Rinka]) && Klientas[Rinka] <> "(nenurodyta)"),
        "@g", DIVIDE(CALCULATE([Pajamos], P26), CALCULATE([Pajamos], P25)) - 1
    )
VAR Geriausia = TOPN(1, Rinkos, [@g], DESC)
RETURN
    SWITCH(
        e,
        1, "Pajamos ir pelnas auga, bet marža mažesnė nei pernai, o vasarą dalies užsakymų nespėta įvykdyti.",
        2, "2026 m. sausis–spalis: pajamos " & {eur("Paj26")} & " (" & {spct("DIVIDE(Paj26, Paj25) - 1")} & " vs pernai).",
        3, "Bendrasis pelnas " & {eur("Pel26")} & " (" & {seur("Pel26 - Pel25")} & "), marža " & {pct("M26")} & " (" & {dec("(M26 - M25) * 100", 1, True)} & " p. p.).",
        4, "Užsakymų įvykdyta " & {pct("Iv")} & ", dėl trūkumų prarasta " & {eur("Pr")} & " pajamų.",
        5, "Sparčiausiai augo rinka „" & MAXX(Geriausia, Klientas[Rinka]) & "“: " & {spct("MAXX(Geriausia, [@g])")} & ".",
        6, "Daugiausia dėmesio reikia dviem dalykams: grietinėlės kainai (ji mažina maržą) ir pasiruošimui karščio savaitėms (dėl jų trūksta prekių).",
        7, "Puslapis „Apžvalga“."
    )
"""

ATSAKYMAI["trūkumai"] = f"""
VAR e = SELECTEDVALUE(Atsakymai[Eilė])
VAR Bir = DATESBETWEEN(Data[Data], DATE(2026, 6, 1), DATE(2026, 6, 30))
VAR VIVII = DATESBETWEEN(Data[Data], DATE(2026, 6, 1), DATE(2026, 7, 31))
VAR Karstis = DATESBETWEEN(Data[Data], DATE(2026, 6, 22), DATE(2026, 6, 28))
VAR Puod = CALCULATE([Užsakymų įvykdymas %], Bir, Produktas[Kategorija] = "Plombyras puodelyje")
VAR Kitos = CALCULATE([Užsakymų įvykdymas %], Bir, Produktas[Kategorija] <> "Plombyras puodelyje")
VAR Nuokr = CALCULATE([Nukrypimas nuo normos °C], Karstis)
VAR Lond = CALCULATE([Nukrypimas nuo normos °C], Karstis, 'Šalis'[Šalies kodas] = "GB")
VAR Planas = CALCULATE([Plano įvykdymas %], VIVII, Linija[Linijos kodas] = "KRE-L2")
VAR Prast = CALCULATE([Prastovos min], VIVII, Linija[Linijos kodas] = "KRE-L2")
VAR PrarV = CALCULATE([Prarasta vnt], VIVII, Produktas[Kategorija] = "Plombyras puodelyje")
VAR PrarE = CALCULATE([Prarastos pajamos], VIVII, Produktas[Kategorija] = "Plombyras puodelyje")
RETURN
    SWITCH(
        e,
        1, "Sutapo dvi priežastys: karščio banga ir sugedusi Kretingos puodelių linija (KRE-L2).",
        2, "Birželį pristatyta tik " & {pct("Puod")} & " puodelių užsakymų, kitų kategorijų " & {pct("Kitos")} & ". Problema yra vienos linijos.",
        3, "2026-06-22 savaitę Europoje buvo karščio banga: rinkose vidutiniškai " & {dec("Nuokr", 1, True)} & " °C virš normos, Londone " & {dec("Lond", 1, True)} & " °C. Užsakymai viršijo prognozę.",
        4, "Tą pačią savaitę KRE-L2 sugedo šaldymo kompresorius. Per VI–VII linija pagamino " & {pct("Planas", 0)} & " plano, prastovos " & {n("Prast")} & " min.",
        5, "Per VI–VII prarasta " & {n("PrarV")} & " vnt. puodelių ir " & {eur("PrarE")} & " pajamų.",
        6, "Šaldymo įrangai daryti prevencinę priežiūrą prieš sezoną (gegužę), atsargines kompresoriaus dalis laikyti vietoje, o planuojant atsižvelgti į orų prognozę.",
        7, "Puslapiai „Gamyba“ ir „Planavimas“."
    )
"""

ATSAKYMAI["marža"] = f"""
VAR e = SELECTEDVALUE(Atsakymai[Eilė])
VAR P26 = DATESBETWEEN(Data[Data], DATE(2026, 4, 1), DATE(2026, 9, 30))
VAR P25 = DATESBETWEEN(Data[Data], DATE(2025, 4, 1), DATE(2025, 9, 30))
VAR Paj26 = CALCULATE([Pajamos], P26)
VAR Paj25 = CALCULATE([Pajamos], P25)
VAR M26 = CALCULATE([Marža %], P26)
VAR M25 = CALCULATE([Marža %], P25)
VAR Pok = CALCULATE([Pelno pokyčis vs PY], P26)
VAR Kiek = CALCULATE([Kiekio efektas], P26)
VAR Mix = CALCULATE([Mix efektas], P26)
VAR Kain = CALCULATE([Kainos ir nuolaidų efektas], P26)
VAR Zal = CALCULATE([Žaliavų kainų efektas], P26)
VAR G1 = CALCULATE([Vid. pirkimo kaina], DATESBETWEEN(Data[Data], DATE(2026, 1, 1), DATE(2026, 3, 31)), 'Žaliava'[Žaliava] = "Grietinėlė 35 %")
VAR G2 = CALCULATE([Vid. pirkimo kaina], P26, 'Žaliava'[Žaliava] = "Grietinėlė 35 %")
RETURN
    SWITCH(
        e,
        1, "Pelnas augo, bet lėčiau nei pajamos, nes nuo balandžio pabrango grietinėlė.",
        2, "2026 m. IV–IX pajamos " & {spct("DIVIDE(Paj26, Paj25) - 1")} & " (" & {dec("Paj25 / 1000000", 2)} & " → " & {dec("Paj26 / 1000000", 2)} & " mln. €), o žaliavų marža " & {pct("M25")} & " → " & {pct("M26")} & ".",
        3, "Bendrasis pelnas vis tiek " & {seur("Pok")} & ": kiekis " & {seur("Kiek")} & ", kainos ir nuolaidos " & {seur("Kain")} & ", mix " & {seur("Mix")} & ", žaliavų kainos " & {seur("Zal")} & ".",
        4, "Grietinėlė 35 %: I–III vidutiniškai " & {dec("G1", 2)} & " €/kg, IV–IX " & {dec("G2", 2)} & " €/kg (" & {spct("DIVIDE(G2, G1) - 1")} & ").",
        6, "Derėtis su grietinėlės tiekėju arba ieškoti antro. Peržiūrėti kainas produktų, kuriuose daugiausia grietinėlės (plombyras, tortai).",
        7, "Puslapis „Kodėl?“ (krioklio diagrama ir pokytis pagal rinką bei kategoriją)."
    )
"""

ATSAKYMAI["karštis"] = f"""
VAR e = SELECTEDVALUE(Atsakymai[Eilė])
VAR J = CALCULATE([Paklausos jautrumas 1 °C], REMOVEFILTERS(Data))
VAR N = [Pasirinktas nukrypimas °C]
VAR R = [Rekomenduojamas prognozės pokytis %]
VAR Sav = TREATAS({{DATE(2026, 6, 22)}}, Data[Savaitės pradžia])
VAR Pr = CALCULATE([Prognozė vnt], Sav)
VAR PrO = CALCULATE([Prognozė su orais vnt], Sav, 'Oro scenarijus'[Nukrypimas °C] = 6)
VAR Uz = CALCULATE([Užsakyta vnt], Sav)
RETURN
    SWITCH(
        e,
        1, "Iš istorijos matyti: +1 °C virš normos ≈ " & {spct("J")} & " užsakymų (gegužė–rugsėjis, visos rinkos).",
        2, IF(N = 0, "Slankikliu dešinėje pasirink, kiek šilčiau nei įprasta bus kitą savaitę.", "Jei bus " & {dec("N", 0, True)} & " °C virš normos, prognozę reikia keisti " & {spct("R")} & "."),
        3, "Patikra su tikra karščio savaite 2026-06-22 (+6 °C): planuotojo prognozė " & {n("Pr")} & " vnt., su orų pataisa " & {n("PrO")} & " vnt., iš tikrųjų užsakyta " & {n("Uz")} & " vnt.",
        6, "Kas savaitę į planą įtraukti 16 dienų orų prognozę. Skriptas planner_weather.py ją paima automatiškai ir įrašo į planuotojo Excel.",
        7, "Puslapis „Planavimas“."
    )
"""

ATSAKYMAI["kokybė"] = f"""
VAR e = SELECTEDVALUE(Atsakymai[Eilė])
VAR Kris = CALCULATE(COUNTROWS(Skundai), Skundai[Tipas] = "Tekstūra (ledo kristalai)", Skundai[Gavimo mėnuo] IN {{"2026-07", "2026-08"}})
VAR KrisKiti = CALCULATE(COUNTROWS(Skundai), Skundai[Tipas] = "Tekstūra (ledo kristalai)", NOT Skundai[Gavimo mėnuo] IN {{"2026-07", "2026-08"}})
VAR Menesiu = CALCULATE(DISTINCTCOUNT(Skundai[Gavimo mėnuo]), NOT Skundai[Gavimo mėnuo] IN {{"2026-07", "2026-08"}})
VAR Gedimas = DATESBETWEEN(Data[Data], DATE(2026, 6, 22), DATE(2026, 7, 12))
VAR SkG = CALCULATE([Skundai 1 mln. vnt.], Gedimas, Linija[Linijos kodas] = "KRE-L2")
VAR SkV = [Skundai 1 mln. vnt.]
VAR FtaV = [Pirmo karto atitiktis %]
VAR FtaG = CALCULATE([Pirmo karto atitiktis %], Gedimas, Linija[Linijos kodas] = "KRE-L2")
RETURN
    SWITCH(
        e,
        1, "Taip. Kol KRE-L2 kompresorius neveikė, šaldymo tunelis nepasiekė −35 °C, ir ledai buvo grūdinami per šiltai.",
        2, "Liepą–rugpjūtį gauta " & {n("Kris")} & " skundų dėl ledo kristalų, kai kitais mėnesiais vidutiniškai " & {dec("DIVIDE(KrisKiti, Menesiu)")} & " per mėnesį.",
        3, "Gedimo metu (06-22–07-12) pagamintų KRE-L2 partijų skundai: " & {dec("SkG", 0)} & " milijonui vienetų, kai vidutiniškai " & {dec("SkV")} & ".",
        4, "Pirmo karto atitiktis: visų partijų " & {pct("FtaV")} & ", gedimo laikotarpio KRE-L2 partijų " & {pct("FtaG", 0)} & ".",
        6, "Grūdinimo temperatūrą stebėti realiu laiku ir partiją sulaikyti automatiškai, kai riba viršijama, o ne laukti skundų.",
        7, "Puslapiai „Kokybė“ ir „Procesas“."
    )
"""

ATSAKYMAI["procesas"] = f"""
VAR e = SELECTEDVALUE(Atsakymai[Eilė])
VAR Et = TOPN(1, VALUES('Partijų etapai'[Etapas]), [Vid. laukimas prieš etapą h], DESC)
VAR EtP = MAXX(Et, 'Partijų etapai'[Etapas])
VAR EtH = MAXX(Et, [Vid. laukimas prieš etapą h])
VAR Cik = [Vid. gamybos ciklas h]
VAR LD = [Laukimo dalis %]
VAR Sau = CALCULATE([Laukimas prieš šaldymą h], DATESBETWEEN(Data[Data], DATE(2026, 1, 1), DATE(2026, 1, 31)))
VAR Lie = CALCULATE([Laukimas prieš šaldymą h], DATESBETWEEN(Data[Data], DATE(2026, 7, 1), DATE(2026, 7, 31)))
RETURN
    SWITCH(
        e,
        1, "Ilgiausiai partija laukia prieš etapą „" & EtP & "“: vidutiniškai " & {dec("EtH")} & " h.",
        2, "Vidutinis gamybos ciklas " & {dec("Cik")} & " h, iš jo " & {pct("LD", 0)} & " laiko partija tiesiog laukia eilėje.",
        3, "Laukimas prieš šaldymą: 2026 m. sausį " & {dec("Sau")} & " h, liepą " & {dec("Lie")} & " h, nes vasarą frizeriai perkrauti.",
        6, "Vasarai planuoti papildomą pamainą prie frizerių arba dalį produkcijos pagaminti iš anksto, kol sezonas neprasidėjo.",
        7, "Puslapis „Procesas“."
    )
"""

ATSAKYMAI["partija"] = f"""
VAR e = SELECTEDVALUE(Atsakymai[Eilė])
VAR Pav = SELECTEDVALUE(Partija[Partija paieškai])
VAR Pag = SUM(Partija[Pagaminta vnt])
VAR Br = SUM(Partija[Brokas vnt])
VAR Isv = [Išsiųsta vnt]
VAR Lik = [Atšaukimas: likutis sandėlyje vnt]
VAR Ats = [Atšaukimas: atsekta %]
VAR KlSk = [Atšaukimas: klientų sk.]
VAR Kl =
    CONCATENATEX(
        FILTER(VALUES(Klientas[Klientas]), [Išsiųsta vnt] > 0),
        Klientas[Klientas] & " " & {n("[Išsiųsta vnt]")},
        ", ",
        [Išsiųsta vnt], DESC
    )
VAR Tsk = [Atšaukimas: tiekėjų sąskaitų sk.]
VAR Sas =
    CONCATENATEX(
        SUMMARIZE('Žaliavų sunaudojimas', 'Žaliavų sunaudojimas'[Tiekėjo sąskaita], 'Žaliava'[Žaliava]),
        'Žaliavų sunaudojimas'[Tiekėjo sąskaita] & " (" & 'Žaliava'[Žaliava] & ")",
        ", "
    )
VAR Sk = [Skundų sk.]
VAR SkT = CONCATENATEX(VALUES(Skundai[Tipas]), Skundai[Tipas], ", ")
RETURN
    IF(
        NOT HASONEVALUE(Partija[Partijos nr]),
        IF(e = 1, "Pasirink vieną partiją paieškos laukelyje dešinėje (pvz. P26-001885)."),
        SWITCH(
            e,
            1, "Partija " & Pav & " atsekta " & {pct("Ats", 0)} & ".",
            2, "Pagaminta " & {n("Pag")} & " vnt., brokas " & {n("Br")} & ", išsiųsta " & {n("Isv")} & ", sandėlyje liko " & {n("Lik")} & " vnt.",
            3, "Gavo " & KlSk & " klientai: " & Kl & ".",
            4, "Žaliavos iš " & Tsk & " tiekėjų sąskaitų: " & Sas & ".",
            5, IF(Sk > 0, "Šiai partijai užregistruota skundų: " & Sk & " (" & SkT & ").", "Skundų šiai partijai neužregistruota."),
            6, "Jei reikia atšaukti, informuoti šiuos klientus ir paprašyti tiekėjų partijų sertifikatų. Visa informacija gaunama iš karto, nereikia ieškoti penkiose sistemose.",
            7, "Puslapis „Atšaukimas“."
        )
    )
"""

ATSAKYMAI["DI"] = f"""
VAR e = SELECTEDVALUE(Atsakymai[Eilė])
VAR N = [DI apdorota sąskaitų]
VAR A = [DI automatizavimo lygis %]
VAR P = [DI atiduota peržiūrai]
VAR T = [DI laikas min]
VAR R = [Rankinio darbo laikas min]
VAR K = [DI kaina USD]
RETURN
    SWITCH(
        e,
        1, "DI apdorotos tiekėjų sąskaitos: " & {n("N")} & ". Automatiškai patvirtinta " & {pct("A", 0)} & ", žmogui patikrinti nukreipta: " & {n("P")} & ".",
        2, "Laikas: " & {dec("T")} & " min. su DI vietoje maždaug " & {n("R")} & " min. rankomis.",
        3, "Kaina: " & {dec("K", 2)} & " $, t. y. apie " & {dec("DIVIDE(K, N)", 2)} & " $ už sąskaitą.",
        4, "Patikra su žinomais atsakymais: 378 iš 378 laukų teisingi, pagauti visi 6 „spąstai“ (nuolaida eilutėje, skenuota kopija, kita valiuta, dublikatas, nesutampanti suma, paslėpta instrukcija DI).",
        6, "Pradėti nuo vieno tiekėjo: pirmą mėnesį DI dirba lygiagrečiai su žmogumi, ir rezultatai lyginami.",
        7, "Puslapis „Duomenų kokybė ir DI“."
    )
"""

ATSAKYMAI["duomenys"] = f"""
VAR e = SELECTEDVALUE(Atsakymai[Eilė])
VAR Np = COUNTROWS('Kokybės patikros')
VAR Dub = [Pašalinta dublikatų]
VAR Kk = [Sutvarkyta kliento kodų]
VAR Bk = [Be kliento kodo]
VAR Pk = [Sutvarkyta plano kodų]
VAR Nk = [Nerasta plano kodų]
VAR Lab = [Lab nr. kitu formatu]
VAR SkN = [Skundo nr. kitu formatu]
RETURN
    SWITCH(
        e,
        1, "Taip, nes prieš patenkant į ataskaitą duomenys patikrinami " & Np & " taisyklėmis.",
        2, "Pašalinta dublikatų: " & {n("Dub")} & ". Sutvarkyta kliento kodų: " & {n("Kk")} & ", plano kodų: " & {n("Pk")} & " (ERP ir planuotojo Excel kodai skiriasi).",
        3, "Partijos numeris įvestas kitu formatu: laboratorijoje " & {n("Lab")} & " k., skundų registre " & {n("SkN")} & " k. Sutvarkyta automatiškai.",
        4, "Automatiškai nesutvarkyta: eilutės be kliento kodo (" & {n("Bk")} & ") ir nerasti plano kodai (" & {n("Nk")} & "). Jos rodomos atskirai, kad žmogus patikrintų.",
        6, "Tikroje įmonėje pirmiausia sulyginti ataskaitos sumas su finansų skyriaus skaičiais ir tik tada rodyti vadovams.",
        7, "Puslapis „Duomenų kokybė ir DI“."
    )
"""


def dispatcher() -> str:
    lines = ["VAR q = SELECTEDVALUE(Atsakymai[Nr])", "RETURN", "    SWITCH(", "        q,"]
    for i, (nr, _, key) in enumerate(KLAUSIMAI):
        keep = {"karštis": "REMOVEFILTERS(Data), REMOVEFILTERS(Partija)",
                "partija": "REMOVEFILTERS(Data), REMOVEFILTERS('Oro scenarijus')"}.get(
            key, "REMOVEFILTERS(Data), REMOVEFILTERS(Partija), REMOVEFILTERS('Oro scenarijus')")
        lines.append(f"        {nr}, CALCULATE([Atsakymas: {key}], {keep}),")
    lines[-1] = lines[-1].rstrip(",")
    lines.append("    )")
    return "\n".join(lines)


def q(name: str) -> str:
    return name if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) else "'" + name.replace("'", "''") + "'"


def measure_tmdl(name: str, expr: str, hidden: bool, desc: str | None = None, fmt: str | None = None) -> str:
    body = "\n".join("\t\t\t" + l if l.strip() else "" for l in expr.strip("\n").splitlines())
    body = "\n".join(l for l in body.splitlines() if l)  # be tuščių eilučių
    out = []
    if desc:
        out.append(f"\t/// {desc}")
    out.append(f"\tmeasure {q(name)} =")
    out.append(body)
    if fmt:
        out.append(f"\t\tformatString: {fmt}")
    if hidden:
        out.append("\t\tisHidden")
    out.append(f"\t\tdisplayFolder: {FOLDER}")
    out.append(f"\t\tlineageTag: {uuid.uuid4()}")
    return "\n".join(out) + "\n"


def table_tmdl() -> str:
    k = ",\n".join(f'\t\t\t\t        {{{nr}, "{txt}"}}' for nr, txt, _ in KLAUSIMAI)
    e = ",\n".join(f'\t\t\t\t        {{{nr}, "{txt}"}}' for nr, txt in EILUTES)
    return f"""/// Puslapio „Klausk“ klausimai ir atsakymo eilutės. Atsakymus skaičiuoja matas [Atsakymas] (aplankas „{FOLDER}“).
table Atsakymai
	lineageTag: {uuid.uuid4()}

	column Nr
		isHidden
		formatString: 0
		lineageTag: {uuid.uuid4()}
		summarizeBy: none
		isNameInferred
		sourceColumn: [Nr]

	column Klausimas
		lineageTag: {uuid.uuid4()}
		summarizeBy: none
		isNameInferred
		sourceColumn: [Klausimas]
		sortByColumn: Nr

	column Eilė
		isHidden
		formatString: 0
		lineageTag: {uuid.uuid4()}
		summarizeBy: none
		isNameInferred
		sourceColumn: [Eilė]

	column Eilutė
		lineageTag: {uuid.uuid4()}
		summarizeBy: none
		isNameInferred
		sourceColumn: [Eilutė]
		sortByColumn: Eilė

	partition Atsakymai = calculated
		mode: import
		source =
				VAR K =
				    DATATABLE(
				        "Nr", INTEGER, "Klausimas", STRING,
				        {{
{k}
				        }}
				    )
				VAR E =
				    DATATABLE(
				        "Eilė", INTEGER, "Eilutė", STRING,
				        {{
{e}
				        }}
				    )
				RETURN
				    CROSSJOIN(K, E)

"""


def main() -> None:
    tables = DEF / "tables"
    (tables / "Atsakymai.tmdl").write_text(table_tmdl(), encoding="utf-8")

    model = DEF / "model.tmdl"
    mt = model.read_text(encoding="utf-8")
    if "ref table Atsakymai" not in mt:
        mt = mt.replace("ref table 'Partijų sprendimai'\n", "ref table 'Partijų sprendimai'\nref table Atsakymai\n")
        model.write_text(mt, encoding="utf-8")

    matai = tables / "_Matai.tmdl"
    t = matai.read_text(encoding="utf-8")
    # išmesti senus „Klausk“ matus (jei skriptas leidžiamas pakartotinai)
    blocks = re.split(r"(?=^\t(?:/// .*\n\t)?measure |^\tcolumn )", t, flags=re.M)
    blocks = [b for b in blocks if f"displayFolder: {FOLDER}\n" not in b]
    t = "".join(blocks)

    new = []
    new.append(measure_tmdl("Atsakymas", dispatcher(), False,
                            "Atsakymas į pasirinktą klausimą (Atsakymai[Klausimas]) pagal eilutę (Atsakymai[Eilutė])."))
    new.append(measure_tmdl("Pasirinktas klausimas", 'SELECTEDVALUE(Atsakymai[Klausimas], "Pasirink klausimą kairėje")', False))
    for _, _, key in KLAUSIMAI:
        new.append(measure_tmdl(f"Atsakymas: {key}", ATSAKYMAI[key], True))
    insert = "\n".join(new) + "\n"
    pos = t.index("\tcolumn Pagalbinis")
    t = t[:pos] + insert + t[pos:]
    matai.write_text(t, encoding="utf-8")
    print(f"Atsakymai.tmdl + {len(new)} matai aplanke „{FOLDER}“")


if __name__ == "__main__":
    main()
