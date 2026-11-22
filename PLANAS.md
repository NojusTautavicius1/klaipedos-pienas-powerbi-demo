# Power BI + DI pavyzdys AB „Klaipėdos pienas“ skelbimui

Skelbimas: „Duomenų analitikos ir procesų automatizavimo specialistas (-ė)“, CVbankas 1-14146220.
Terminas: apie **2026-11-26** (11-21 rodė „Liko 5 dienos“). 49 kandidatai, CV jau peržiūrinėja.
Tikslas: iki **11-24** turėti viešą, veikiantį pavyzdį ir kandidatuoti su tekstu „išmokau Power BI, kurdamas tokį pavyzdį jūsų tipo įmonei“.

---

## 1. Ką sužinojau (tyrimas)

**Ko nori skelbimas (5 pareigos → ką pavyzdys turi parodyti):**

| Pareiga skelbime | Kaip parodysime pavyzdyje |
|---|---|
| Sujungti ERP ir kitų sistemų duomenis į vieną modelį, automatizuoti surinkimą | „ERP eksportai“ (CSV) + Excel gamybos planas + DI nuskaitytos sąskaitos → vienas žvaigždės modelis, Power Query, atnaujinimas vienu mygtuku |
| Power BI: pardavimai, finansai, gamyba, pirkimai, atsargos; interaktyvios ataskaitos, rodančios **ne tik rezultatus, bet ir procesą** (įžangoje: „ir juos lemiančias priežastis“) | Puslapis „Procesas: nuo žaliavos iki lentynos“ (pirkimas → gamyba → sandėlis → pardavimas, kur stringa) + „Kodėl?“ puslapis (maržos pokyčio skaidymas, decomposition tree) |
| DI ir automatizavimas: dokumentų apdorojimas, duomenų suvedimas, **ataskaitų rengimas**, **informacijos perdavimas tarp sistemų** | Python + Claude: PDF sąskaitos → patikrinta lentelė → ERP importo failas ir Power BI; „Mėnesio komentaras“: Claude pats parašo vadovybei, kas pasikeitė ir kodėl |
| Efektyvumas, išmatuojama nauda | Skaičius README: „40 sąskaitų rankomis ≈ X val., su DI ≈ Y min., tikslumas Z %“ |
| Duomenų kokybė, prieigos, dokumentacija, mokymai | Duomenų kokybės puslapis, RLS rolė (vadybininkas mato tik savo tinklą), duomenų žodynas, trumpas „kaip naudotis“ gidas |

**Apie įmonę (iš skelbimų):**
- Ledų gamintoja, „Žemaitijos pieno“ grupė, apie 140 darbuotojų, 10–20 mln. € pajamų. Prekės ženklai DIONE ir KAR KAR, pirkėjai Lidl, Kaufland, Tesco, Costco.
- Darbo vietos: Klaipėda, Kretinga, Gargždai.
- **ERP savos gamybos**: programuotojo skelbime PHP + SQL/Oracle, „VVS/ERP“, daug integracijų tarp sistemų. Taigi duomenys ateis kaip SQL lentelės arba eksportai, ne kaip gražus SAP.
- **Gamybos planavimas daromas Excel'yje** (planuotojo skelbime reikalaujama tik MS Excel). Planuotojas analizuoja nukrypimų priežastis, sezoniškumą ir atsargas. Tai tiesiogiai tinka Power BI.
- Ledams labai svarbus **sezoniškumas** (vasaros pikas).

**Įrankiai (patikrinta šiame kompiuteryje):**
- Power BI Desktop neįdiegtas. Yra Microsoft Store (`winget install 9NTXR16HNW1T`), nemokamas.
- Python 3.14, Node 24, .NET 10, git: yra.
- **Power BI Modeling MCP** (oficialus Microsoft, `@microsoft/powerbi-modeling-mcp`, preview). Leidžia man per Claude Code kurti lenteles, Power Query skaidinius, ryšius, DAX matus, RLS roles ir vykdyti DAX užklausas atidarytame Power BI Desktop faile arba PBIP aplanke. **Vizualų ir puslapių jis nekuria.** Prieš naudojant reikia priimti EULA (tavo sutikimu).
- **PBIP formatas** (modelis kaip TMDL tekstas, ataskaita kaip PBIR JSON): tinka git'ui ir GitHub, matosi visas DAX kodas.
- **Publish to web** nemokamai neveiks (reikia Pro/PPU ir darbo paskyros). Todėl rodome per GitHub: ekrano nuotraukos, GIF/video, .pbix atsisiuntimui.
- Claude API: `claude-opus-5-5`, PDF kaip `document` blokas, `messages.parse()` su Pydantic schema (garantuotas JSON). Raktas jau yra `idea-radar/.env`, perkelsime į šio projekto `.env` (gitignore). 40 sąskaitų kainuos mažiau nei 1 €.

**Panaudoti skillai:** system-design, core-dev, execution-operator (AI-Brain), claude-api. Vėliau: lt-rasymas (motyvacinis tekstas), dataviz (ataskaitos spalvos ir vizualai).

---

## 2. Pagrindinė idėja: „ataskaita, kuri atsako kodėl“

Sintetiniuose duomenyse **specialiai paslėpsime 3 istorijas**, kurias ataskaita turi rasti:

Paklausą lemia **tikri orai** (Open-Meteo, 6 rinkų miestai, nukrypimas nuo 2015–2024 m. normos). Planuotojas prognozuoja pagal įprastą sezoną, todėl karštą savaitę užsakymai viršija prognozę. Iš duomenų atkuriamas jautrumas: **+1 °C virš normos ≈ +4,5 % užsakymų** (šerbetas 5,8 %, tortai 0,9 %).

1. **2026-06-22 savaitės karščio banga Europoje** (tikri orai: Londonas +10,0 °C, Berlynas +8,8, Varšuva +6,2, Klaipėda +3,6 virš normos) ir karšta JK vasara. Tą savaitę užsakymai viršijo prognozę JK +63 %, Lietuvoje +15 %. Prognozės tikslumas VI–VIII: 2025 m. 86 %, 2026 m. 85 %. Prarasta 411 tūkst. vnt. (VI–VIII).
2. **Grietinėlės kaina +18 % nuo 2026 m. balandžio** (3,10 → 3,65 €/kg, tiekėjas T02): žaliavų marža IV–IX krito 62,8 % → 60,2 %, nors pardavimai augo.
3. **Tą pačią savaitę neatlaiko Kretingos puodelių linijos (KRE-L2) šaldymo kompresorius**: 4 savaitės sumažinto pajėgumo (gedimas → dalių laukimas → tunelio remontas → paleidimas), VI–VII pagaminta 79 % plano, 7 765 min. prastovų, +42 tūkst. € remontas liepą. Puodelių pristatyta tik 77 % užsakymų birželį ir 90 % liepą; kitos linijos karštį atlaikė (94–100 %).

**Padaryta 11-21:** generatorius (`data_gen/`, orai `data_gen/weather.py`), 27 PDF sąskaitos su 6 spąstais, Claude ištraukėjas + taisyklės + ERP importas (`invoices/`), tikslumas 378/378 laukų, 27/27 sprendimų, 0,60 $ (`docs/di_tikslumas.md`), 13 testų. Power BI modelis per MCP: 31 lentelė, 39 ryšiai, 116 matų, RLS, orų what-if, automatiniai įspėjimai.

**Kokybė ir atsekamumas (RVASVT / BRC, `data_gen/quality.py`):** kiekviena partija turi duomenis iš 5 „sistemų“:
- linijų apskaitos (8 etapai su laikais ir kontrole, KVT: pasterizacija ≥ 80 °C, metalo detektorius);
- laboratorijos (kitas CSV formatas, 4 % partijos nr. įvesta rankomis kitaip);
- sandėlio siuntų (FIFO);
- ERP žaliavų sunaudojimo (partija → tiekėjo sąskaita);
- kokybės skyriaus Excel skundų registro ir partijų sprendimų.

3 istorijos tęsinys: kol KRE-L2 kompresorius sugedęs, tunelis pasiekia tik −27…−31 °C (riba −35 °C), ledai grūdinami per šiltai, ir liepą–rugpjūtį ateina 18 skundų dėl ledo kristalų (įprastai ~1 per mėn.). Skundų iš tų partijų tenka 43 milijonui vienetų, kai vidutiniškai 2,5 (17 kartų daugiau). Pirmo karto atitiktis iš viso 95,8 %, gedimo partijų 0 %. Laukimas prieš šaldymą sausį 0,6 h, 2026 m. liepą 6,5 h (linija apkrauta). Atšaukimo simuliacija: partija → klientai, kiekiai, likutis sandėlyje, tiekėjų sąskaitos, masės balansas 100 %. Etapai yra tipinė ledų technologija (pokalbyje paklausti, kaip pas juos).

Pokalbyje galėsi parodyti: „Marža krito 2,6 p. p. Paspaudžiu „Kodėl?“: IV–IX bendrasis pelnas vis tiek +268 tūkst. €, nes kiekis +417 tūkst., kainos +136 tūkst., mix +47 tūkst., o žaliavos (grietinėlė) atėmė −333 tūkst. €.“ Ir: „Jei planuotojas būtų žiūrėjęs orų prognozę (+8 °C JK), modelis būtų rekomendavęs +45 % prognozės.“

---

**Padaryta 11-22 (`automation/`, 32 testai):**
- **Mėnesio komentaras** (`monthly_commentary.py` + `kpi.py`): faktai tomis pačiomis formulėmis kaip DAX matai (IV–IX pelno pokytis +267 649 € sutampa su modeliu), Claude rašo, skriptas tikrina kiekvieną skaičių pagal nurodytą fakto kelią ir regex'u ieško skaičių be šaltinio. Rezultatai: `docs/menesio_komentaras_2026-10.md`, `docs/menesio_komentaras_2026-06.md` (~0,2 $ vienas). Rastas kalendoriaus spąstas: 2026-06 turi 5 užsakymų antradienius, 2025-06 tik 4, todėl +48,7 % → vienai savaitei +18,9 %. Tai įrašyta į faktus ir instrukciją. **Šiuo pavyzdžiu verta pasigirti pokalbyje.**
- **Orų pataisa planuotojui** (`planner_weather.py`): jautrumas iš istorijos pagal kategoriją ir sezoną, tikra Open-Meteo 16 d. prognozė, Excel planuotojo formatu (`data/out/planuotojui_*.xlsx`) su linijų apkrova ir patarimu gaminti iš anksto. Patikra su nematytais duomenimis (mokyta 2025, tikrinta 2026 V–IX): tikslumas 88,1 % → 94,8 %, karščio savaitės paklaida −22 % → +0,8 %. Sintetiniuose duomenyse ryšys įdėtas sąmoningai, README tai pasakyta.
- **Duomenų žodynas** iš TMDL (`data_dictionary.py` → `docs/duomenu_zodynas.md`): 30 lentelių, 39 ryšiai, 116 matų su DAX, 3 RLS rolės.
- **README** su architektūra (mermaid), lentele „skelbimas → projektas“, 4 diagramomis (`docs/img/`, `readme_charts.py`) ir EN santrauka. **90 dienų planas**: `docs/pirmos_90_dienu.md` (pradžia ne sezono metu, sulyginimas su finansais, DI pilotas lygiagrečiai su žmogumi, BRCGS atsekamumo testas, mokymai pagal skyrius).
- **Motyvacinis tekstas**: `IT\CV\juodrastis\klaipedos_pienas_motyvacinis.md` (ne repozitorijoje).

**Liko tau (Nojau) iki 11-24:**
1. Atidaryti Power BI Desktop, modelį išsaugoti kaip `powerbi\KlaipedosPienas.pbip` (README jau rodo šį kelią) ir sudėti puslapius pagal `docs/puslapiu_gidas.md`.
2. Padaryti 2–3 ekrano nuotraukas („Kodėl?“, „Planavimas“, „Atšaukimas“), įdėti į `docs/img/` ir README skyrių „Trys istorijos“.
3. README skyriuje „Kas ką darė“ parašyta, kad vizualus sudėjai pats. Tai turi būti tiesa prieš darant repozitoriją viešą.
4. Padaryti repozitoriją viešą, perskaityti ir patvirtinti motyvacinį tekstą, kandidatuoti CVbankas formoje.
5. Neprivaloma: įrašyti „Klausk duomenų“ video (`docs/video_scenarijus.md`).

## 3. Duomenų modelis (žvaigždės schema)

Laikotarpis: 2025-01-01 – 2026-10-31 (22 mėn., matosi sezoniškumas ir YoY).

**Dimensijos**
- `Data` (kalendorius, LT mėnesiai, savaitės, sezonas)
- `Produktas` (~40 SKU: prekės ženklas, kategorija: plombyras / pieniški / šerbetas / su vafliu / tortai, pakuotė, savikainos receptas)
- `Klientas` (prekybos tinklai ir šalys: LT, LV, EE, UK, …)
- `Gamykla_Linija` (Klaipėda, Kretinga, Gargždai; 2–3 linijos)
- `Žaliava` (pienas, grietinėlė, cukrus, kakava, vafliai, pakuotės)
- `Tiekėjas`

**Faktai**
- `Pardavimai` (sąskaitų eilutės: kiekis, kaina, nuolaida, akcija taip/ne)
- `Gamyba` (partijos: planas iš Excel ir faktas, prastovos min., brokas %)
- `Pirkimai` (iš DI nuskaitytų PDF sąskaitų + ERP istorija)
- `Atsargos` (savaitiniai likučiai: gatava produkcija ir žaliavos)
- `Finansai` (mėnesio sąnaudos pagal kaštų centrą + biudžetas)

**Tyčia „nešvarūs“ duomenys**, kad matytųsi duomenų kokybės darbas: dublikatai, kablelis vietoj taško, skirtingi SKU kodai ERP ir Excel plane, trūkstami klientų ID. Viskas valoma Power Query, o „Duomenų kokybės“ puslapis rodo, kiek ko rasta.

**Pagrindiniai DAX matai:** Pajamos, Bendrasis pelnas, Marža %, MoM %, YoY %, Planas vs faktas, Prarasti pardavimai, Atsargų dienos (days of cover), Žaliavų kainos indeksas, Gamybos plano įvykdymas %, **Kaina / kiekis / mix skaidymas** (waterfall).

---

## 4. Ataskaitos puslapiai

1. **Apžvalga**: KPI kortelės (pajamos, pelnas, marža, plano įvykdymas) + tendencija + 3 automatiniai „įspėjimai“.
2. **Pardavimai**: tinklai, prekės ženklai, šalys, sezoniškumas, akcijų poveikis.
3. **Gamyba**: planas ir faktas pagal liniją, prastovos, brokas.
4. **Pirkimai ir žaliavos**: kainų indeksas, tiekėjai, DI nuskaitytos sąskaitos.
5. **Atsargos**: likučiai, atsargų dienos, trūkumai.
6. **Procesas: nuo žaliavos iki lentynos**: viena grandinė per mėnesį: žaliavų pirkimas → gamybos planas ir faktas → sandėlis → pardavimai ir trūkumai. Matosi, kur grandinė stringa (pvz. birželio prastovos → liepos trūkumai Lidl).
7. **Kodėl?**: maržos pokyčio waterfall (kaina / kiekis / mix / savikaina) + decomposition tree + drill-through iki SKU.
8. **Duomenų kokybė ir DI**: kiek sąskaitų apdorota, kiek atmesta validacijos, kiek laiko sutaupyta.

Bendra: vienodas filtrų skydelis (laikotarpis, gamykla, tinklas), drill-through, tooltip'ai, LT kalba, ramios spalvos (dataviz skillas).

---

## 5. DI dalis: PDF sąskaitų nuskaitymas

```
sugeneruoti PDF (3 tiekėjų maketai, LT „PVM sąskaita faktūra“)
   → Claude (claude-opus-5-5, messages.parse + Pydantic schema)
   → validacija: eilučių suma = viso, PVM 21 %, tiekėjas žinomas, data intervale, ne dublikatas
   → geros eilutės → pirkimai_di.csv → Power BI
                   → erp_importas.csv (formatas, kurį „ERP“ priimtų: perdavimas tarp sistemų be rankinio suvedimo)
   → klaidingos → perziura.csv (žmogus patikrina)
   → tikslumo ataskaita: lyginame su tikrais duomenimis (žinome, nes PDF generavome patys)
```

- ~40 sąskaitų, dalis su „spąstais“: kita valiuta, nuolaida eilutėje, pasuktas skenas, trūkstamas laukas. Tai parodo, kad validacija ir „žmogus cikle“ veikia.
- README skaičiai: tikslumas laukų lygiu, kaina už sąskaitą, laikas.
- Tai ta pati „tikrink modelio atsakymą“ idėja kaip idea-radar.
- **„Mėnesio komentaras“ (ataskaitų rengimo automatizavimas):** skriptas per MCP/DAX paima mėnesio rodiklius, Claude parašo 5–7 sakinius vadovybei (kas pasikeitė, kodėl, ką daryti). Rezultatas: `docs/menesio-komentaras-2026-10.md` + nuotrauka README. Skelbime tai įvardyta tiesiai, todėl tai nebe „jei liks laiko“.

---

## 6. Kas ką daro

| Darbas | Kas |
|---|---|
| Duomenų generatorius (Python), PDF sąskaitos, Claude ištraukėjas, testai | Claude |
| Power BI Desktop įdiegimas, EULA sutikimas MCP | Tu |
| Modelis per MCP: Power Query užklausos, ryšiai, DAX matai, RLS, aprašymai | Claude (tu stebi ir klausi) |
| **Vizualai ir puslapiai GUI** pagal mano žingsnių gidą | **Tu**: pokalbyje turėsi paaiškinti ir parodyti patirtį, tai svarbiausia dalis tavo mokymuisi |
| Tikrinimas DAX užklausomis (ar istorijos „randamos“) | Claude |
| README, ekrano nuotraukos, GIF, motyvacinis tekstas (lt-rasymas) | Claude, tu patvirtini |
| Kandidatavimas CVbankas formoje | Tu |

---

## 7. Projekto struktūra

```
pienines_cv/
  data_gen/          sintetinių duomenų generatorius (seed, 3 istorijos)
  invoices/          PDF generatorius + Claude ištraukėjas + validacija + testai
  data/              raw/ (ERP eksportai, Excel planas, PDF), clean/ (DI rezultatai)
  powerbi/           PBIP projektas (TMDL modelis + PBIR ataskaita)
  docs/              duomenų žodynas, matų aprašai, naudotojo gidas, nuotraukos
  README.md          istorija, nuotraukos, kaip paleisti, skaičiai
```

---

## 8. Laiko planas

| Diena | Darbai | Rezultatas |
|---|---|---|
| **Šešt. 11-21** | Power BI įdiegimas; projekto struktūra; duomenų generatorius; PDF sąskaitos; Claude ištraukėjas + validacija | Visi duomenys diske, DI dalis veikia, tikslumo skaičius |
| **Sekm. 11-22** | Modelis per MCP (Power Query, ryšiai, matai, RLS); tu kuri puslapius 1–4 | Veikiantis modelis, pirmi puslapiai |
| **Pirm. 11-23** | Puslapiai 5–8 („Procesas“ ir „Kodėl?“ svarbiausi); „Mėnesio komentaras“; patikra, ar randamos 3 istorijos; dokumentacija | Užbaigta ataskaita |
| **Antr. 11-24** | README, nuotraukos, GIF; GitHub; projektas portfolio (ntdev.lt); motyvacinis tekstas; **kandidatavimas** | Išsiųsta |
| Treč. 11-25 | Atsarga | |

Jei vėluojame: pirmiausia atsisakome RLS, tada 8 puslapio, tada sujungiame 2–5 puslapius į mažiau. Neatsisakome: „Procesas“, „Kodėl?“, DI sąskaitų ir „Mėnesio komentaro“, nes jie tiesiogiai atitinka skelbimo žodžius.

---

## 9. Rizikos

- **MCP preview gali neprisijungti prie Desktop.** Atsarginis kelias: aš rašau TMDL failus PBIP aplanke tiesiogiai, tu atidarai.
- **Power BI mokymosi kreivė.** Puslapių gidas bus žingsnis po žingsnio; pradėsime nuo paprasčiausių vizualų.
- **Sintetiniai duomenys su tikrais pavadinimais.** Kad niekas nepalaikytų jų tikrais, aiškiai žymime visur (žr. 10 skyrių).
- **Terminas.** Skelbimas gali užsidaryti anksčiau. Kandidatuojame 11-24, ne paskutinę dieną.

---

## 10. Priimti sprendimai (2026-11-21)

1. **Kalba: lietuvių** (ataskaita, matai, README; README gale trumpa EN santrauka).
2. **Pavadinimai tikri** (Klaipėdos pienas, DIONE, KAR KAR, Lidl, Kaufland, Tesco, Costco), bet visur aiškiai parašyta, kad tai išgalvotas pavyzdys:
   - README viršuje: „Tai mokomasis pavyzdys. Visi skaičiai sugeneruoti, tai ne tikri AB „Klaipėdos pienas“ duomenys, ir projektas nesusijęs su įmone.“
   - Ataskaitos titulinis puslapis + mažas užrašas kiekvieno puslapio apačioje: „Sintetiniai duomenys“.
   - PDF sąskaitose vandens ženklas „PAVYZDYS“.
   - Tiekėjai išgalvoti (ne tikros įmonės).
3. **Vizualus kuri tu GUI** pagal mano žingsnių gidą. Modelį ir DAX darau aš per MCP.
4. **Claude raktas**: kopijuojamas iš `idea-radar/.env` į šio projekto `.env` (gitignore).
