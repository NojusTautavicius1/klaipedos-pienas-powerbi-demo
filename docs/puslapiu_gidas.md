# Power BI puslapių kūrimo gidas

Modelis jau paruoštas: 31 lentelė, 39 ryšiai, 116 matų. Šiame gide aprašyta, kaip sudėti vizualus. Visi matai yra lentelėje **`_Matai`**, suskirstyti į aplankus. Laukai nurodyti formatu `Lentelė[Stulpelis]`, o matai `[Mato pavadinimas]`.

Kaip atrodo galutinis variantas, matyti peržiūroje: https://claude.ai/artifact/Urh4D3uQkD4VUUGevxcFix (tie patys skaičiai iš modelio).

Laiko sąnaudos: ~1 val. paruošimas ir 1–3 puslapiai, po to ~30 min. kiekvienam kitam puslapiui.

---

## 0. Paruošimas (vieną kartą)

1. **Išsaugok kaip .pbip:** File → Save as → tipas „Power BI project files (*.pbip)“ → `powerbi\KlaipedosPienas.pbip`.
2. **Tema:** View → Themes → Browse for themes → `powerbi\tema_klaipedos_pienas.json`. Gausi spalvas, šriftus, kortelių rėmelius ir šviesiai melsvą puslapio foną.
3. **Lietuviški skaičiai:** File → Options and settings → Options → Global → Regional settings → pasirink lietuvių (Lietuva) lokalę, tada perkrauk Desktop. Skaičiai bus „1 234,5“.
4. **Puslapio dydis:** Format → Canvas settings → 16:9 (1280 × 720).
5. **Bendras šablonas puslapiui** (padaryk pirmame puslapyje, tada Duplicate page):
   - Viršuje teksto laukas su puslapio pavadinimu, 18 pt, Segoe UI Semibold.
   - Viršuje dešinėje: Insert → Buttons → Navigator → **Page navigator**.
   - Kairėje viršuje pjaustyklė (Slicer) `Data[Metai-mėnuo]`, stilius „Dropdown“.
   - Apačioje teksto laukas 8 pt, pilka spalva: *„Sintetiniai duomenys · mokomasis pavyzdys, ne tikri AB „Klaipėdos pienas“ skaičiai · Orai: Open-Meteo“*.
6. **Pjaustyklių sinchronizavimas:** View → Sync slicers → `Data[Metai-mėnuo]` pažymėk visuose puslapiuose.

**Spalvų taisyklės** (tema jas jau nustato, tik nekeisk):
- Viena serija = mėlyna. Lyginant su planu ar pernai, planas/pernai yra pilka, o faktas mėlynas.
- Teigiamas pokytis mėlynas, neigiamas oranžinis.
- Žalia ir raudona naudojamos **tik** būsenai (gerai/blogai), ne serijoms.
- **Niekada nedėk dviejų Y ašių.** Du skirtingus matus rodyk dviejose diagramose vieną po kita.
- Jei diagramoje naudojama 3–5 spalva (žalsvai mėlyna, geltona ar rožinė), įjunk **Data labels**: šviesiame fone jų kontrastas mažas.

---

## 1. Viršelis

| Vizualas | Laukai / nustatymai |
|---|---|
| Teksto laukas | „Klaipėdos pienas · ledų gamyba“ (32 pt) ir eilutė „Power BI + DI pavyzdys, 2025-01 – 2026-10“ |
| Teksto laukas | Įspėjimas: „Sintetiniai duomenys. Mokomasis pavyzdys, nesusijęs su AB „Klaipėdos pienas“.“ |
| 3 mygtukai (Insert → Buttons → Blank) | „Karščio banga“, „Linija sugedo“, „Kodėl krito marža“. Action → Bookmark (žr. 11 skyrių) |
| Mygtukas „Visi puslapiai“ | Action → Page navigation → Apžvalga |

---

## 2. Apžvalga

| Vizualas | Laukai | Pastabos |
|---|---|---|
| 4 kortelės (Card, new) | `[Pajamos]`, `[Marža %]`, `[Užsakymų įvykdymas %]`, `[Pirmo karto atitiktis %]` | Prie kiekvienos kortelės pridėk Reference label: `[Pajamos YoY %]`, `[Maržos pokytis p. p.]`, `[Prarastos pajamos]`, `[Skundai 1 mln. vnt.]` |
| 4 kortelės su įspėjimais | `[Įspėjimas: trūkumai]`, `[Įspėjimas: marža]`, `[Įspėjimas: prognozė]`, `[Įspėjimas: kokybė]` | Card → Callout value 11 pt, kairėje. Tekstą su ⚠ ar ✓ sugeneruoja pats matas |
| Stulpelinė (Clustered column) | X: `Data[Metai-mėnuo]`, Y: `[Pajamos]` | Tooltip: `[Pajamos YoY %]`, `[Marža %]` |
| Linijinė (Line) | X: `Data[Metai-mėnuo]`, Y: `[Marža %]`, `[Marža % PY]` | `[Marža % PY]` pilka spalva |

**Mobilus vaizdas:** View → Mobile layout. Ištempk 4 korteles ir 4 įspėjimus vieną po kitu, o apačioje pajamų diagramą.

---

## 3. Pardavimai

| Vizualas | Laukai |
|---|---|
| Matrica (Matrix) | Eilutės: `Klientas[Rinka]` → `Klientas[Klientas]`; Stulpeliai: nieko; Reikšmės: `[Pajamos]`, `[Pajamos YoY %]`, `[Marža %]`, `[Akcijų pajamų dalis %]`, `[Užsakymų įvykdymas %]` |
| Juostinė (Clustered bar) | Y: `Produktas[Kategorija]`, X: `[Pajamos]`, Tooltip: `[Marža %]` |
| Stulpelinė | X: `Data[Mėnuo]` (rūšiuojama pagal mėnesio nr.), Legend: `Data[Metai]`, Y: `[Parduota vnt]`. Matosi sezoniškumas ir abeji metai |
| Pjaustyklės | `Šalis[Šalis]`, `Produktas[Prekės ženklas]` |

Sąlyginis formatavimas: `[Pajamos YoY %]` → Font color → Rules (< 0 oranžinė, ≥ 0 mėlyna).

---

## 4. Planavimas: orai ir prognozė ⭐

Šitas puslapis planuotojui pats įdomiausias.

| Vizualas | Laukai | Pastabos |
|---|---|---|
| Taškinė (Scatter) | Values (Details): `Data[Savaitės pradžia]`, `Šalis[Šalies kodas]`; X: `[Nukrypimas nuo normos °C]`; Y: `[Prognozės nuokrypis %]` | Filtras šiam vizualui: `Data[Mėnesio nr]` 5–9. Analytics → **Trend line** įjungta. Visi taškai viena spalva |
| Kortelė | `[Paklausos jautrumas 1 °C]` | Antraštė: „+1 °C virš normos = … užsakymų“ |
| Kortelės | `[Prognozės tikslumas %]` 2025 ir 2026 vasarai | Du vizualai su filtrais `Data[Metai]` |
| Pjaustyklė (Slider) | `Oro scenarijus[Nukrypimas °C]` | Single value. Pavadinimas: „Kiek šilčiau nei įprasta bus kitą savaitę?“ |
| Kortelės | `[Rekomenduojamas prognozės pokytis %]`, `[Papildomai reikia vnt]` | Keičiasi kartu su slankikliu |
| Grupuota juostinė | Y: `Šalis[Šalis]`, X: `[Prognozė vnt]`, `[Prognozė su orais vnt]`, `[Užsakyta vnt]` | Prognozė pilka, su orais mėlyna, užsakyta oranžinė |
| Linijinė (2 vizualai vienas po kitu) | X: `Data[Savaitės pradžia]`; viršuje Y: `[Nukrypimas nuo normos °C]`, apačioje Y: `[Prognozės nuokrypis %]` | **Ne dviguba ašis**, o dvi atskiros diagramos su ta pačia X ašimi |

**Demonstracija pokalbyje:** pjaustyklėje pasirink savaitę 2026-06-22, slankiklį pastumk ant +6 ir parodyk, kad „su orais“ ≈ „užsakyta“.

---

## 5. Gamyba

| Vizualas | Laukai |
|---|---|
| Linijinė | X: `Data[Savaitės pradžia]`, Y: `[Planas vnt]` (pilka), `[Pagaminta vnt]` (mėlyna) |
| Stulpelinė | X: `Linija[Linija]`, Y: `[Plano įvykdymas %]`; pridėk Constant line ties 0,95 |
| Sukrautoji juostinė (Stacked bar) | Y: `Prastovos[Priežastis]`, X: `[Prastovos min]`, rūšiuota mažėjančiai |
| Kortelės | `[Prastovų dalis %]`, `[Brokas %]` |
| Pjaustyklė | `Linija[Gamykla]`, `Linija[Linija]` |

Su `Linija[Linija]` = „Puodelių linija“ ir laikotarpiu 2026-06–07 matosi gedimas: kompresorius → dalių laukimas → remontas.

---

## 6. Procesas: nuo žaliavos iki lentynos

| Vizualas | Laukai | Pastabos |
|---|---|---|
| Sukrautoji juostinė | Y: `Partijų etapai[Etapas]` (rūšiuok pagal `Etapo nr`), X: `[Vid. etapo trukmė h]`, `[Vid. laukimas prieš etapą h]` | Trukmė mėlyna, laukimas oranžinis. Taip matosi, kur partija tiesiog stovi |
| Linijinė | X: `Data[Metai-mėnuo]`, Y: `[Laukimas prieš šaldymą h]` | Vasarą eilė prie frizerio |
| Kortelės | `[Vid. gamybos ciklas h]`, `[Laukimo dalis %]`, `[KVT nukrypimai]` | |
| Lentelė | `Partijų etapai[Etapas]`, `[Kontrolė]`, `[Reikšmė]`, `[Riba min]`, `[Riba max]`, `[KVT]`, `[Atitinka]` | Sąlyginis formatavimas `Atitinka` = „Ne“ → raudonas fonas |
| Teksto laukas | „Etapai yra tipinė ledų gamybos technologija. Tikrame projekte jie būtų paimti iš linijų SCADA/MES.“ | |

---

## 7. Kodėl? ⭐

| Vizualas | Laukai | Pastabos |
|---|---|---|
| Teksto laukas su dinamine antrašte | Antraštė: fx → `[Antraštė: kodėl]` | |
| **Krioklio diagrama (Waterfall)** | Category: `Maržos veiksniai[Veiksnys]`, Y: `[Veiksnio poveikis]` | Total = pelno pokytis. Spalvas nustato tema |
| **Skaidymo medis (Decomposition tree)** | Analyze: `[Pelno pokytis vs PY]`; Explain by: `Klientas[Rinka]`, `Klientas[Klientas]`, `Produktas[Kategorija]`, `Produktas[Produktas]` | Įjunk „AI splits“ |
| Linijinė | X: `Data[Metai-mėnuo]`, Y: `[Vid. pirkimo kaina]`, filtras `Žaliava[Žaliava]` = „Grietinėlė 35 %“ | |
| Juostinė | Y: `Žaliava[Žaliava]`, X: `[Žaliavų kainų indeksas]` | |

Pjaustyklė: pasirink 2026-04 – 2026-09.

---

## 8. Kokybė

| Vizualas | Laukai |
|---|---|
| Kortelės | `[Pirmo karto atitiktis %]`, `[Skundai 1 mln. vnt.]`, `[Grūdinimo nukrypimai]`, `[Laboratorijos neatitiktys]` |
| Sukrautoji stulpelinė | X: `Skundai[Gavimo mėnuo]`, Y: `[Skundų sk.]`, Legend: `Skundai[Tipas]` |
| Juostinė | Y: `Partija[Būsena]`, X: `[Partijų sk.]` |
| Lentelė | `Skundai[Skundo nr]`, `[Gauta]`, `Klientas[Klientas]`, `Partija[Partijos nr]`, `[Tipas]`, `[Būsena]`, `[Korekcinis veiksmas]` |

Pastaba: `Data` pjaustyklė čia filtruoja pagal **partijos gamybos** datą, o stulpelinė diagrama rodo skundus pagal gavimo mėnesį.

---

## 9. Atšaukimo simuliacija (drill-through) ⭐

1. Naujas puslapis „Atšaukimas“. Format → Page information → Page type: **Drill through**, Drill through from: `Partija[Partijos nr]`.
2. Pjaustyklė su paieška: `Partija[Partija paieškai]`, stilius Dropdown, įjungtas Search.
3. Vizualai:

| Vizualas | Laukai |
|---|---|
| Teksto laukas, fx antraštė | `[Antraštė: partija]` |
| Kortelės | `[Atšaukimas: klientų sk.]`, `[Išsiųsta vnt]`, `[Atšaukimas: likutis sandėlyje vnt]`, `[Atšaukimas: atsekta %]`, `[Atšaukimas: tiekėjų sąskaitų sk.]` |
| Lentelė „Kam išsiųsta“ | `Klientas[Klientas]`, `Siuntos[Siuntos nr]`, `[Siuntos data]`, `[Išsiųsta vnt]` |
| Lentelė „Iš ko pagaminta“ | `Žaliava[Žaliava]`, `Tiekėjas[Tiekėjas]`, `Žaliavų sunaudojimas[Tiekėjo sąskaita]`, `[Sunaudota]` |
| Lentelė „Gamybos kelias“ | `Partijų etapai[Etapas]`, `[Pradžia]`, `[Pabaiga]`, `[Kontrolė]`, `[Reikšmė]`, `[Atitinka]` |
| Lentelė „Laboratorija“ | `Lab tyrimai[Rodiklis]`, `[Rezultatas]`, `[Matas]`, `[Riba min]`, `[Riba max]`, `[Atitinka]` |

**Demonstracija:** įvesk `P26-001885` (skundas dėl svetimkūnio iš Costco UK) arba bet kurią KRE-L2 partiją 2026-06-22–07-12. Kitame puslapyje, pvz. „Kokybė“ lentelėje, dešinis pelės mygtukas ant partijos → Drill through → Atšaukimas.

---

## 10. Duomenų kokybė ir DI

| Vizualas | Laukai |
|---|---|
| Lentelė | `Kokybės patikros[Sritis]`, `[Patikra]`, `[Rasta atvejų]`, `[Kas daroma]` |
| Kortelės | `[DI apdorota sąskaitų]`, `[DI automatizavimo lygis %]`, `[DI kaina USD]`, `[Sutaupyta laiko min]` |
| Lentelė | `Peržiūra[Failas]`, `[Tiekėjas]`, `[Suma]`, `[Priežastys]`, `[Įtartinas turinys]` |
| Lentelė | `DI žurnalas[Failas]`, `[Statusas]`, `[Kaina USD]`, `[Trukmė s]` |

Teksto laukas: „PDF → Claude (struktūrizuotas JSON) → taisyklės (sumos, PVM, tiekėjas, dublikatai) → ERP importo failas. 378/378 laukų teisingai.“

---

## 11. Istorijų režimas (Bookmarks)

View → Bookmarks. Kiekvienai istorijai nustatyk puslapį ir filtrus, tada Add bookmark:

| Žymelė | Puslapis | Būsena |
|---|---|---|
| 1 Karščio banga | Planavimas | Savaitė 2026-06-22, slankiklis +6 |
| 2 Linija sugedo | Gamyba | Linija = Puodelių linija, 2026-06 – 2026-07 |
| 3 Kokybės pasekmės | Kokybė | 2026-06 – 2026-08, Tipas = Tekstūra (ledo kristalai) |
| 4 Kodėl krito marža | Kodėl? | 2026-04 – 2026-09 |
| 5 Atšaukimas | Atšaukimas | Partija P26-001885 |

Tada Insert → Buttons → Navigator → **Bookmark navigator**: jį įdėk į viršelį ir į kiekvieną istorijos puslapį, kad būtų galima spausti „toliau“.

---

## 12. Tooltip puslapis „Savaitė“

1. Naujas puslapis „Tooltip savaitė“. Page information → **Allow use as tooltip**: On, Canvas settings → Type: Tooltip.
2. Kortelės: `[Temperatūra °C]`, `[Nukrypimas nuo normos °C]`, `[Prognozės nuokrypis %]`, `[Užsakymų įvykdymas %]`, `[Prastovos min]`.
3. Paslėpk puslapį (dešinis pelės mygtukas → Hide page).
4. Savaitinėse diagramose (Planavimas, Gamyba): Format → General → Tooltips → Type: Report page → „Tooltip savaitė“.

---

## 13. Prieš ekrano nuotraukas

- [ ] Kiekviename puslapyje yra užrašas „Sintetiniai duomenys“.
- [ ] Nėra tuščių vizualų ar „(Blank)“ (jei yra, pridėk filtrą „is not blank“).
- [ ] Pjaustyklės išvalytos, jei kuriamas bendras vaizdas.
- [ ] Mobilus vaizdas sutvarkytas bent Apžvalgos puslapyje.
- [ ] File → Save (.pbip), tada commit.
