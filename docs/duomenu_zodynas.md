# Duomenų žodynas

> Sugeneruota automatiškai iš Power BI modelio (`automation/data_dictionary.py`, šaltinis `powerbi/modelio_kopija_tmdl`). Rankomis neredaguoti: pakeisk modelį ir paleisk skriptą iš naujo.
> Sintetiniai duomenys, mokomasis pavyzdys.

Modelyje: **30 lentelės**, **39 ryšiai**, **116 matai**, **3 RLS rolės**.

## Turinys

- [Lentelės](#lentelės)
- [Ryšiai](#ryšiai)
- [Prieigos rolės (RLS)](#prieigos-rolės-rls)
- [Matai pagal aplanką](#matai-pagal-aplanką)

## Lentelės

| Lentelė | Tipas | Stulpelių | Aprašymas |
|---|---|---:|---|
| **Atsargos** | Power Query | 1 | Savaitiniai gatavos produkcijos likučiai sekmadienį (atsargos.csv). Likučiai nesumuojami per laiką: naudok matą Likutis vnt. |
| **Biudžetas** | Power Query | 0 | Mėnesio biudžetas pagal straipsnį, įskaitant Pajamas ir Bendrąjį pelną (biudzetas.csv). Data = mėnesio pabaiga. |
| **DI žurnalas** | Power Query | 9 | Kiekviena DI nuskaityta PDF sąskaita: statusas, priežastys, modelis, tokenai, kaina ir trukmė (di_zurnalas.csv). |
| **Data** | DAX (skaičiuojama) | 7 | Kalendorius 2025-01-01 – 2026-10-31. Pažymėtas kaip datų lentelė. |
| **Finansai** | Power Query | 1 | Mėnesio sąnaudos pagal kaštų centrą ir straipsnį (finansai_sanaudos.csv). |
| **Gamyba** | Power Query | 2 | Gamybos partijos (gamyba.csv). Savaitės pradžia sieja su planu ir prastovomis. |
| **Gamybos planas** | Power Query | 1 | Planuotojo Excel (gamybos_planas.xlsx, lapai 2025 ir 2026). Praleidžiamos eilutės iki antraštės, plano kodas Trim. Su produktu sieja Plano kodas. |
| **Klientas** | Power Query | 4 | Prekybos tinklai ir šalys (klientai.csv) + eilutė NEŽINOMAS pardavimams be kliento kodo. |
| **Kokybės patikros** | DAX (skaičiuojama) | 4 | Duomenų kokybės patikrų sąrašas. Naudok su matu Rasta atvejų. |
| **Lab tyrimai** | Power Query | 8 | Laboratorijos sistemos eksportas (tyrimai.csv): kitas formatas (skirtukas kablelis, dešimtainės taškas, data dd.MM.yyyy), partijos nr. kartais įvestas rankomis kitaip. Power Query sutvarko. |
| **Linija** | Power Query | 4 | Gamybos linijos ir gamyklos (linijos.csv). |
| **Maržos veiksniai** | DAX (skaičiuojama) | 1 | Ašis krioklio (waterfall) diagramai puslapyje Kodėl?. Naudok su matu Veiksnio poveikis. |
| **Orai** | Power Query | 1 | Tikri orai iš Open-Meteo archyvo: dienos maksimali temperatūra kiekvienos rinkos mieste ir 2015–2024 m. norma tą pačią metų dieną (data/raw/orai/orai.csv). |
| **Oro scenarijus** | DAX (skaičiuojama) | 1 | What-if parametras planuotojui: kiek °C šiltesnė už normą bus savaitė. Naudok kaip pjaustyklę su matu Pasirinktas nukrypimas °C. |
| **Pardavimai** | Power Query | 7 | Pardavimų sąskaitų eilutės iš 22 mėnesinių ERP eksportų. Valymas: pašalinti dublikatai (ERP eilučių > 1), kliento kodas Trim + Upper, tuščias kodas = NEŽINOMAS. |
| **Partija** | Power Query | 11 | Gamybos partijos (ERP gamyba.csv, tik pagaminta > 0). Atsekamumo centras: į ją rodo etapai, tyrimai, siuntos, žaliavos ir skundai. |
| **Partijų etapai** | Power Query | 12 | Partijos kelias per gamybos etapus iš linijų apskaitos (partiju_etapai.csv): laikai ir kontrolės parametrai. KVT = kritinis valdymo taškas (RVASVT). Etapai yra tipinė ledų technologija. |
| **Partijų sprendimai** | Power Query | 4 | Kokybės specialisto sprendimai partijoms su nuokrypiais (partiju_sprendimai.csv). |
| **Peržiūra** | Power Query | 9 | Sąskaitos, kurių DI nepatvirtino ir atidavė žmogui (perziura.csv): priežastis ir, jei buvo, įtartinas turinys. |
| **Pirkimai** | Power Query | 8 | Žaliavų pirkimų sąskaitų eilutės: ERP istorija iki 2026-09 + spalio sąskaitos, kurias nuskaitė DI (pirkimai_di.csv). Šaltinis = ERP arba DI. |
| **Prastovos** | Power Query | 1 | Savaitinės linijų prastovos su priežastimi (prastovos.csv). |
| **Produktas** | Power Query | 10 | Produktų katalogas iš ERP (produktai.csv). Plano kodas sieja su planuotojo Excel. |
| **Prognozė** | Power Query | 1 | Planuotojo paklausos prognozė pagal savaitę, produktą ir šalį (Excel lapas Prognozė). Orai čia neįskaičiuoti. |
| **Siuntos** | Power Query | 2 | Sandėlio siuntos klientams su partija (siuntos.csv, FIFO). Siuntos be partijos = 2024 m. likutis. |
| **Skundai** | Power Query | 7 | Kokybės skyriaus skundų registras (Excel skundu_registras.xlsx). Klientas įrašytas pavadinimu, partija kartais su tarpais ar mažosiomis. |
| **Straipsnis** | DAX (skaičiuojama) | 3 | Finansų ir biudžeto straipsniai. Tipas skiria rezultatus nuo sąnaudų. |
| **Tiekėjas** | Power Query | 5 | Žaliavų tiekėjai (tiekejai.csv). Tiekėjai išgalvoti. |
| **Šalis** | DAX (skaičiuojama) | 4 | Rinkos šalys ir miestas, kurio orai naudojami. Filtruoja klientus, orus ir prognozę kartu. |
| **Žaliava** | Power Query | 4 | Žaliavų sąrašas (zaliavos.csv). |
| **Žaliavų sunaudojimas** | Power Query | 2 | ERP: kiek kokios žaliavos sunaudota partijai ir iš kurios tiekėjo sąskaitos (atgalinis atsekamumas). |

### Atsargos

Savaitiniai gatavos produkcijos likučiai sekmadienį (atsargos.csv). Likučiai nesumuojami per laiką: naudok matą Likutis vnt.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Sandėlis | string |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Data, Prekės kodas, Likutis vnt.

### Biudžetas

Mėnesio biudžetas pagal straipsnį, įskaitant Pajamas ir Bendrąjį pelną (biudzetas.csv). Data = mėnesio pabaiga.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|

Paslėpti techniniai stulpeliai (raktai ryšiams): Metai, Mėnuo, Straipsnis, Suma, Data.

### DI žurnalas

Kiekviena DI nuskaityta PDF sąskaita: statusas, priežastys, modelis, tokenai, kaina ir trukmė (di_zurnalas.csv).

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Failas | string |  |
| Statusas | string |  |
| Priežastys | string |  |
| Modelis | string |  |
| Įvesties tokenai | int64 |  |
| Išvesties tokenai | int64 |  |
| Kaina USD | double |  |
| Trukmė s | double |  |
| Apdorota | dateTime |  |

### Data

Kalendorius 2025-01-01 – 2026-10-31. Pažymėtas kaip datų lentelė.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Data |  |  |
| Metai |  |  |
| Mėnuo |  |  |
| Metai-mėnuo |  |  |
| Ketvirtis |  |  |
| Savaitės pradžia |  |  |
| Sezonas |  |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Mėnesio nr, Metai-mėnuo nr, Savaitės dienos nr, Mėnesio pabaiga.

### Finansai

Mėnesio sąnaudos pagal kaštų centrą ir straipsnį (finansai_sanaudos.csv).

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Kaštų centras | string |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Data, Straipsnis, Suma.

### Gamyba

Gamybos partijos (gamyba.csv). Savaitės pradžia sieja su planu ir prastovomis.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Partijos nr | string |  |
| Data | dateTime |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Linijos kodas, Prekės kodas, Pagaminta vnt, Brokas vnt, Savaitės pradžia.

### Gamybos planas

Planuotojo Excel (gamybos_planas.xlsx, lapai 2025 ir 2026). Praleidžiamos eilutės iki antraštės, plano kodas Trim. Su produktu sieja Plano kodas.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| ISO savaitė | string |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Savaitės pradžia, Linijos kodas, Plano kodas (Excel), Planas vnt, Plano kodas, Kodas taisytas.

### Klientas

Prekybos tinklai ir šalys (klientai.csv) + eilutė NEŽINOMAS pardavimams be kliento kodo.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Kliento kodas | string |  |
| Klientas | string |  |
| Rinka | string |  |
| Vadybininkas | string |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Šalis.

### Kokybės patikros

Duomenų kokybės patikrų sąrašas. Naudok su matu Rasta atvejų.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Nr |  |  |
| Sritis |  |  |
| Patikra |  |  |
| Kas daroma |  |  |

### Lab tyrimai

Laboratorijos sistemos eksportas (tyrimai.csv): kitas formatas (skirtukas kablelis, dešimtainės taškas, data dd.MM.yyyy), partijos nr. kartais įvestas rankomis kitaip. Power Query sutvarko.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Partijos nr (laboratorijoje) | string |  |
| Mėginio data | dateTime |  |
| Rodiklis | string |  |
| Rezultatas | double |  |
| Matas | string |  |
| Riba min | double |  |
| Riba max | double |  |
| Atitinka | string |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Partijos nr, Nr. taisytas.

### Linija

Gamybos linijos ir gamyklos (linijos.csv).

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Linijos kodas | string |  |
| Gamykla | string |  |
| Linija | string |  |
| Minutės per savaitę | int64 |  |

### Maržos veiksniai

Ašis krioklio (waterfall) diagramai puslapyje Kodėl?. Naudok su matu Veiksnio poveikis.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Veiksnys |  |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Eilė.

### Orai

Tikri orai iš Open-Meteo archyvo: dienos maksimali temperatūra kiekvienos rinkos mieste ir 2015–2024 m. norma tą pačią metų dieną (data/raw/orai/orai.csv).

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Miestas | string |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Data, Šalies kodas, Maks. temperatūra, Norma.

### Oro scenarijus

What-if parametras planuotojui: kiek °C šiltesnė už normą bus savaitė. Naudok kaip pjaustyklę su matu Pasirinktas nukrypimas °C.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Nukrypimas °C |  |  |

### Pardavimai

Pardavimų sąskaitų eilutės iš 22 mėnesinių ERP eksportų. Valymas: pašalinti dublikatai (ERP eilučių > 1), kliento kodas Trim + Upper, tuščias kodas = NEŽINOMAS.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Sąskaitos nr | string |  |
| Užsakyta vnt | int64 |  |
| Pristatyta vnt | int64 |  |
| Kainoraščio kaina | double |  |
| Nuolaida % | double |  |
| Akcija | string |  |
| Savikaina vnt | double |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Data, Kliento kodas (ERP), Prekės kodas, ERP eilučių, Kliento kodas, Pajamos, Pajamos be nuolaidų, Žaliavų savikaina, Prarasta vnt, Prarastos pajamos, Kodas taisytas.

### Partija

Gamybos partijos (ERP gamyba.csv, tik pagaminta > 0). Atsekamumo centras: į ją rodo etapai, tyrimai, siuntos, žaliavos ir skundai.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Partijos nr | string |  |
| ERP data | dateTime |  |
| Pagaminta vnt | int64 |  |
| Brokas vnt | int64 |  |
| Būsena | string (skaičiuojamas) | Kokybės sprendimas; jei nuokrypių nebuvo: Išleista. |
| Neatitikčių | int64 (skaičiuojamas) | Laboratorijos ir gamybos kontrolės rezultatų už ribų skaičius. |
| Gamybos ciklas h | double (skaičiuojamas) | Nuo mišinio ruošimo pradžios iki padėjimo į sandėlį. |
| Laukimas h | double (skaičiuojamas) | Kiek iš gamybos ciklo partija tiesiog laukia tarp etapų. |
| Išsiųsta vnt | int64 (skaičiuojamas) |  |
| Likutis vnt | int64 (skaičiuojamas) | Dar sandėlyje: pagaminta − brokas − išsiųsta. Atšaukimo atveju šiuos vienetus galima blokuoti vietoje. |
| Partija paieškai | string (skaičiuojamas) | Partijos nr ir produktas: patogu pjaustyklėje su paieška. |

Paslėpti techniniai stulpeliai (raktai ryšiams): Linijos kodas, Prekės kodas, Savaitės pradžia.

### Partijų etapai

Partijos kelias per gamybos etapus iš linijų apskaitos (partiju_etapai.csv): laikai ir kontrolės parametrai. KVT = kritinis valdymo taškas (RVASVT). Etapai yra tipinė ledų technologija.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Etapo nr | int64 |  |
| Etapas | string |  |
| Pradžia | dateTime |  |
| Pabaiga | dateTime |  |
| Kontrolė | string |  |
| Reikšmė | double |  |
| Riba min | double |  |
| Riba max | double |  |
| KVT | string |  |
| Atitinka | string |  |
| Trukmė min | double |  |
| Laukimas min | double (skaičiuojamas) | Kiek partija laukia tarp ankstesnio etapo pabaigos ir šio etapo pradžios. |

Paslėpti techniniai stulpeliai (raktai ryšiams): Partijos nr.

### Partijų sprendimai

Kokybės specialisto sprendimai partijoms su nuokrypiais (partiju_sprendimai.csv).

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Sprendimas | string |  |
| Sprendimo data | dateTime |  |
| Nuokrypiai | string |  |
| Atsakingas | string |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Partijos nr.

### Peržiūra

Sąskaitos, kurių DI nepatvirtino ir atidavė žmogui (perziura.csv): priežastis ir, jei buvo, įtartinas turinys.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Failas | string |  |
| Tiekėjo kodas | string |  |
| Tiekėjas | string |  |
| Sąskaitos nr | string |  |
| Data | dateTime |  |
| Valiuta | string |  |
| Suma | double |  |
| Priežastys | string |  |
| Įtartinas turinys | string |  |

### Pirkimai

Žaliavų pirkimų sąskaitų eilutės: ERP istorija iki 2026-09 + spalio sąskaitos, kurias nuskaitė DI (pirkimai_di.csv). Šaltinis = ERP arba DI.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Sąskaitos nr | string |  |
| Aprašymas | string |  |
| Matas | string |  |
| Kaina | double |  |
| Nuolaida % | double |  |
| PVM % | double |  |
| Valiuta | string |  |
| Šaltinis | string |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Data, Tiekėjo kodas, Žaliavos kodas, Kiekis, Suma be PVM.

### Prastovos

Savaitinės linijų prastovos su priežastimi (prastovos.csv).

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Priežastis | string |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Savaitės pradžia, Linijos kodas, Prastovos min.

### Produktas

Produktų katalogas iš ERP (produktai.csv). Plano kodas sieja su planuotojo Excel.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Prekės kodas | string |  |
| Produktas | string |  |
| Prekės ženklas | string |  |
| Kategorija | string |  |
| Tūris, ml | int64 |  |
| Linijos kodas | string |  |
| Plano kodas | string |  |
| Bazinė kaina | double |  |
| Gamykla | string (skaičiuojamas) | Gamykla, kurioje gaminamas produktas (pagal liniją). |
| Linija | string (skaičiuojamas) | Gamybos linijos pavadinimas. |

### Prognozė

Planuotojo paklausos prognozė pagal savaitę, produktą ir šalį (Excel lapas Prognozė). Orai čia neįskaičiuoti.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| ISO savaitė | string |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Savaitės pradžia, Šalies kodas, Plano kodas, Prognozė vnt, Užsakymų diena.

### Siuntos

Sandėlio siuntos klientams su partija (siuntos.csv, FIFO). Siuntos be partijos = 2024 m. likutis.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Siuntos nr | string |  |
| Siuntos data | dateTime |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Kliento kodas, Prekės kodas, Partijos nr, Kiekis vnt.

### Skundai

Kokybės skyriaus skundų registras (Excel skundu_registras.xlsx). Klientas įrašytas pavadinimu, partija kartais su tarpais ar mažosiomis.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Skundo nr | string |  |
| Gauta | dateTime |  |
| Tipas | string |  |
| Aprašymas | string |  |
| Būsena | string |  |
| Korekcinis veiksmas | string |  |
| Gavimo mėnuo | string |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Klientas, Prekės kodas, Partija (registre), Partijos nr, Nr. taisytas.

### Straipsnis

Finansų ir biudžeto straipsniai. Tipas skiria rezultatus nuo sąnaudų.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Straipsnis |  |  |
| Kaštų centras |  |  |
| Tipas |  |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Eilė.

### Tiekėjas

Žaliavų tiekėjai (tiekejai.csv). Tiekėjai išgalvoti.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Tiekėjo kodas | string |  |
| Tiekėjas | string |  |
| Šalis | string |  |
| PVM kodas | string |  |
| Valiuta | string |  |

### Šalis

Rinkos šalys ir miestas, kurio orai naudojami. Filtruoja klientus, orus ir prognozę kartu.

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Šalies kodas |  |  |
| Šalis |  |  |
| Orų miestas |  |  |
| Rinka |  |  |

### Žaliava

Žaliavų sąrašas (zaliavos.csv).

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Žaliavos kodas | string |  |
| Žaliava | string |  |
| Matas | string |  |
| Pagrindinio tiekėjo kodas | string |  |

### Žaliavų sunaudojimas

ERP: kiek kokios žaliavos sunaudota partijai ir iš kurios tiekėjo sąskaitos (atgalinis atsekamumas).

| Stulpelis | Tipas | Aprašymas |
|---|---|---|
| Sunaudota | double |  |
| Tiekėjo sąskaita | string |  |

Paslėpti techniniai stulpeliai (raktai ryšiams): Partijos nr, Žaliavos kodas, Tiekėjo kodas.

## Ryšiai

Visi ryšiai „daug su vienu“ (faktų lentelė → dimensija).

| Iš (faktai) | Į (dimensija) | Pastaba |
|---|---|---|
| Pardavimai[Data] | Data[Data] |  |
| Pardavimai[Kliento kodas] | Klientas[Kliento kodas] |  |
| Pardavimai[Prekės kodas] | Produktas[Prekės kodas] |  |
| Gamyba[Savaitės pradžia] | Data[Data] |  |
| Gamyba[Prekės kodas] | Produktas[Prekės kodas] |  |
| Gamyba[Linijos kodas] | Linija[Linijos kodas] |  |
| Gamybos planas[Savaitės pradžia] | Data[Data] |  |
| Gamybos planas[Plano kodas] | Produktas[Plano kodas] |  |
| Gamybos planas[Linijos kodas] | Linija[Linijos kodas] |  |
| Prastovos[Savaitės pradžia] | Data[Data] |  |
| Prastovos[Linijos kodas] | Linija[Linijos kodas] |  |
| Atsargos[Data] | Data[Data] |  |
| Atsargos[Prekės kodas] | Produktas[Prekės kodas] |  |
| Pirkimai[Data] | Data[Data] |  |
| Pirkimai[Tiekėjo kodas] | Tiekėjas[Tiekėjo kodas] |  |
| Pirkimai[Žaliavos kodas] | Žaliava[Žaliavos kodas] |  |
| Finansai[Data] | Data[Data] |  |
| Finansai[Straipsnis] | Straipsnis[Straipsnis] |  |
| Biudžetas[Data] | Data[Data] |  |
| Biudžetas[Straipsnis] | Straipsnis[Straipsnis] |  |
| Klientas[Šalis] | Šalis[Šalies kodas] |  |
| Orai[Data] | Data[Data] |  |
| Orai[Šalies kodas] | Šalis[Šalies kodas] |  |
| Prognozė[Plano kodas] | Produktas[Plano kodas] |  |
| Prognozė[Šalies kodas] | Šalis[Šalies kodas] |  |
| Partija[Savaitės pradžia] | Data[Data] |  |
| Partija[Prekės kodas] | Produktas[Prekės kodas] |  |
| Partija[Linijos kodas] | Linija[Linijos kodas] |  |
| Partijų etapai[Partijos nr] | Partija[Partijos nr] |  |
| Lab tyrimai[Partijos nr] | Partija[Partijos nr] |  |
| Siuntos[Partijos nr] | Partija[Partijos nr] |  |
| Siuntos[Kliento kodas] | Klientas[Kliento kodas] |  |
| Žaliavų sunaudojimas[Partijos nr] | Partija[Partijos nr] |  |
| Žaliavų sunaudojimas[Žaliavos kodas] | Žaliava[Žaliavos kodas] |  |
| Žaliavų sunaudojimas[Tiekėjo kodas] | Tiekėjas[Tiekėjo kodas] |  |
| Skundai[Partijos nr] | Partija[Partijos nr] |  |
| Skundai[Klientas] | Klientas[Klientas] |  |
| Partijų sprendimai[Partijos nr] | Partija[Partijos nr] |  |
| Prognozė[Užsakymų diena] | Data[Data] |  |

## Prieigos rolės (RLS)

| Rolė | Ką mato | Filtras |
|---|---|---|
| Baltijos šalių vadybininkas | Mato tik Lidl LT/LV/EE, vietinius tinklus ir HoReCa. | `Klientas = Klientas[Vadybininkas] = "Baltijos šalių vadybininkas"` |
| Eksporto vadybininkas (DE/PL) | Mato tik Kaufland Polska ir Deutschland. | `Klientas = Klientas[Vadybininkas] = "Eksporto vadybininkas (DE/PL)"` |
| Eksporto vadybininkas (UK) | Mato tik Tesco UK ir Costco UK. | `Klientas = Klientas[Vadybininkas] = "Eksporto vadybininkas (UK)"` |

## Matai pagal aplanką

### 0 Apžvalga ir antraštės

| Matas | Formatas | Aprašymas |
|---|---|---|
| `Įspėjimas: trūkumai` | | Automatinis įspėjimas apžvalgai: blogiausiai įvykdyta kategorija pasirinktu laikotarpiu. |
| `Įspėjimas: marža` | |  |
| `Įspėjimas: kokybė` | | Skundai pagal partijų gamybos laikotarpį, palyginti su visos istorijos vidurkiu. |
| `Įspėjimas: prognozė` | |  |
| `Antraštė: laikotarpis` | |  |
| `Antraštė: kodėl` | |  |
| `Antraštė: partija` | |  |

<details><summary>DAX kodas</summary>

**Įspėjimas: trūkumai**

```dax
VAR Kategorijos = FILTER(VALUES(Produktas[Kategorija]), [Užsakyta vnt] > 0)
VAR Blogiausia = TOPN(1, Kategorijos, [Užsakymų įvykdymas %], ASC)
VAR Pavadinimas = MAXX(Blogiausia, Produktas[Kategorija])
VAR Ivykdymas = MINX(Blogiausia, [Užsakymų įvykdymas %])
VAR Prarasta = CALCULATE([Prarastos pajamos], TREATAS({Pavadinimas}, Produktas[Kategorija]))
RETURN
    IF(
        Ivykdymas < 0.97,
        "⚠ " & Pavadinimas & ": pristatyta tik " & FORMAT(Ivykdymas, "0.0 %", "lt-LT") & " užsakymų, prarasta " & FORMAT(Prarasta, "#,0 €", "lt-LT"),
        "✓ Visų kategorijų užsakymai įvykdyti bent 97 %"
    )
```

**Įspėjimas: marža**

```dax
VAR Pokytis = [Maržos pokyčis p. p.]
VAR Tekstas = "Marža " & FORMAT([Marža %], "0.0 %", "lt-LT") & " (" & FORMAT(Pokytis, "+0.0;-0.0", "lt-LT") & " p. p. vs pernai)"
RETURN
    SWITCH(
        TRUE(),
        ISBLANK(Pokytis), "Palyginimo su pernai nėra",
        Pokytis <= -1, "⚠ " & Tekstas & ". Priežastys: puslapis „Kodėl?“",
        "✓ " & Tekstas
    )
```

**Įspėjimas: kokybė**

```dax
VAR Dabar = [Skundai 1 mln. vnt.]
VAR Iprasta = CALCULATE([Skundai 1 mln. vnt.], REMOVEFILTERS(Data))
RETURN
    SWITCH(
        TRUE(),
        ISBLANK(Dabar), "✓ Skundų nėra",
        Dabar > 2 * Iprasta, "⚠ " & FORMAT(Dabar, "0.0", "lt-LT") & " skundo milijonui vnt. (įprastai " & FORMAT(Iprasta, "0.0", "lt-LT") & "). Puslapis „Kokybė“",
        "✓ Skundų lygis įprastas: " & FORMAT(Dabar, "0.0", "lt-LT") & " milijonui vnt."
    )
```

**Įspėjimas: prognozė**

```dax
VAR Nuokrypis = [Prognozės nuokrypis %]
VAR Orai = [Nukrypimas nuo normos °C]
RETURN
    IF(
        ABS(Nuokrypis) >= 0.1,
        "⚠ Užsakymai " & FORMAT(Nuokrypis, "+0 %;-0 %", "lt-LT") & " nuo prognozės, orai " & FORMAT(Orai, "+0.0;-0.0", "lt-LT") & " °C nuo normos. Puslapis „Planavimas“",
        "✓ Užsakymai atitinka prognozę (" & FORMAT(Nuokrypis, "+0 %;-0 %", "lt-LT") & ")"
    )
```

**Antraštė: laikotarpis**

```dax
FORMAT(MIN(Data[Data]), "yyyy-MM-dd") & " – " & FORMAT(MAX(Data[Data]), "yyyy-MM-dd")
```

**Antraštė: kodėl**

```dax
VAR Pokytis = [Pelno pokyčis vs PY]
RETURN
    IF(
        ISBLANK(Pokytis),
        "Pasirink laikotarpį, kuris turi palyginimą su pernai",
        "Bendrasis pelnas " & FORMAT(Pokytis, "+#,0 €;-#,0 €", "lt-LT") & " vs pernai, marža " & FORMAT([Maržos pokyčis p. p.], "+0.0;-0.0", "lt-LT") & " p. p. Kas tai lėmė?"
    )
```

**Antraštė: partija**

```dax
IF(HASONEVALUE(Partija[Partijos nr]), "Partija " & SELECTEDVALUE(Partija[Partija paieškai]) & " · " & SELECTEDVALUE(Partija[Būsena]), "Pasirink vieną partiją (paieška viršuje arba dešiniu pelės mygtuku → Drill through)")
```

</details>

### 1 Pardavimai

| Matas | Formatas | Aprašymas |
|---|---|---|
| `Pajamos` | `#,0" €"` | Pajamos po nuolaidų: pristatytas kiekis × kainoraščio kaina × (1 − nuolaida). |
| `Pajamos be nuolaidų` | `#,0" €"` |  |
| `Nuolaidos` | `#,0" €"` | Klientų nuolaidos ir akcijų nuolaidos kartu. |
| `Nuolaidų dalis %` | `0.0%` |  |
| `Žaliavų savikaina` | `#,0" €"` | Parduotų produktų žaliavų savikaina pagal receptą ir tų mėnesių žaliavų kainas. |
| `Bendrasis pelnas` | `#,0" €"` | Pajamos minus žaliavų savikaina (darbo, energijos ir kitos sąnaudos čia neįskaičiuotos, jos yra Finansuose). |
| `Marža %` | `0.0%` | Bendrasis pelnas / Pajamos (marža po žaliavų). |
| `Parduota vnt` | `#,0` |  |
| `Užsakyta vnt` | `#,0` |  |
| `Prarasta vnt` | `#,0` | Užsakyta, bet nepristatyta (trūkumas sandėlyje). |
| `Prarastos pajamos` | `#,0" €"` | Kiek būtų uždirbta, jei būtų pristatytas visas užsakymas. |
| `Užsakymų įvykdymas %` | `0.0%` | Fill rate: pristatyta / užsakyta. |
| `Akcijų pajamų dalis %` | `0.0%` |  |
| `Vid. kaina vnt` | `0.000" €"` |  |

<details><summary>DAX kodas</summary>

**Pajamos**

```dax
SUM(Pardavimai[Pajamos])
```

**Pajamos be nuolaidų**

```dax
SUM(Pardavimai[Pajamos be nuolaidų])
```

**Nuolaidos**

```dax
[Pajamos be nuolaidų] - [Pajamos]
```

**Nuolaidų dalis %**

```dax
DIVIDE([Nuolaidos], [Pajamos be nuolaidų])
```

**Žaliavų savikaina**

```dax
SUM(Pardavimai[Žaliavų savikaina])
```

**Bendrasis pelnas**

```dax
[Pajamos] - [Žaliavų savikaina]
```

**Marža %**

```dax
DIVIDE([Bendrasis pelnas], [Pajamos])
```

**Parduota vnt**

```dax
SUM(Pardavimai[Pristatyta vnt])
```

**Užsakyta vnt**

```dax
SUM(Pardavimai[Užsakyta vnt])
```

**Prarasta vnt**

```dax
SUM(Pardavimai[Prarasta vnt])
```

**Prarastos pajamos**

```dax
SUM(Pardavimai[Prarastos pajamos])
```

**Užsakymų įvykdymas %**

```dax
DIVIDE([Parduota vnt], [Užsakyta vnt])
```

**Akcijų pajamų dalis %**

```dax
DIVIDE(CALCULATE([Pajamos], Pardavimai[Akcija] = "Taip"), [Pajamos])
```

**Vid. kaina vnt**

```dax
DIVIDE([Pajamos], [Parduota vnt])
```

</details>

### 10 Kokybė ir atsekamumas

| Matas | Formatas | Aprašymas |
|---|---|---|
| `Partijų sk.` | `#,0` |  |
| `Partijų su nuokrypiu` | `#,0` |  |
| `Pirmo karto atitiktis %` | `0.0%` | Right first time: dalis partijų, kurių visi laboratorijos ir gamybos kontrolės rezultatai buvo ribose. |
| `KVT nukrypimai` | `#,0` | Kritinių valdymo taškų (pasterizacija, metalo detektorius) nukrypimai. |
| `Laboratorijos neatitiktys` | `#,0` |  |
| `Grūdinimo nukrypimai` | `#,0` | Partijos, kurias tunelis grūdino šiltesniu nei -35 °C oru. |
| `Skundų sk.` | `#,0` | Pagal partijos gamybos datą. Tendencijai pagal gavimo mėnesį naudok Skundai[Gavimo mėnuo]. |
| `Išsiųsta vnt` | `#,0` |  |
| `Skundai 1 mln. vnt.` | `0.0` | Skundų skaičius milijonui išsiųstų vienetų (tos pačios partijos). |
| `Vid. gamybos ciklas h` | `0.0" h"` |  |
| `Laukimo dalis %` | `0.0%` | Kiek gamybos ciklo partija tiesiog laukia (dažniausiai prieš šaldymą, kai linija užimta). |
| `Vid. etapo trukmė h` | `0.0" h"` |  |
| `Vid. laukimas prieš etapą h` | `0.0" h"` |  |
| `Laukimas prieš šaldymą h` | `0.0" h"` | Brandąs mišinys laukia laisvo frizerio. Didžiausias kamštis sezono piko metu. |
| `Atšaukimas: klientų sk.` | `#,0` | Kiek klientų gavo pasirinktų partijų produkcijos. |
| `Atšaukimas: siuntų sk.` | `#,0` |  |
| `Atšaukimas: likutis sandėlyje vnt` | `#,0` | Vienetai, kuriuos galima tuoj pat blokuoti sandėlyje. |
| `Atšaukimas: atsekta %` | `0.0%` | Masės balansas (BRC): kiek pagamintų vienetų rasta siuntose, broke ir sandėlyje. |
| `Atšaukimas: tiekėjų sąskaitų sk.` | `#,0` | Iš kiek tiekėjų sąskaitų (žaliavų partijų) pagaminta. |

<details><summary>DAX kodas</summary>

**Partijų sk.**

```dax
COUNTROWS(Partija)
```

**Partijų su nuokrypiu**

```dax
CALCULATE(COUNTROWS(Partija), Partija[Neatitikčių] > 0) + 0
```

**Pirmo karto atitiktis %**

```dax
1 - DIVIDE([Partijų su nuokrypiu], [Partijų sk.])
```

**KVT nukrypimai**

```dax
CALCULATE(COUNTROWS('Partijų etapai'), 'Partijų etapai'[KVT] = "Taip", 'Partijų etapai'[Atitinka] = "Ne") + 0
```

**Laboratorijos neatitiktys**

```dax
CALCULATE(COUNTROWS('Lab tyrimai'), 'Lab tyrimai'[Atitinka] = "Ne") + 0
```

**Grūdinimo nukrypimai**

```dax
CALCULATE(COUNTROWS('Partijų etapai'), 'Partijų etapai'[Etapas] = "Grūdinimas tunelyje", 'Partijų etapai'[Atitinka] = "Ne") + 0
```

**Skundų sk.**

```dax
COUNTROWS(Skundai) + 0
```

**Išsiųsta vnt**

```dax
SUM(Siuntos[Kiekis vnt])
```

**Skundai 1 mln. vnt.**

```dax
DIVIDE([Skundų sk.], [Išsiųsta vnt]) * 1000000
```

**Vid. gamybos ciklas h**

```dax
AVERAGE(Partija[Gamybos ciklas h])
```

**Laukimo dalis %**

```dax
DIVIDE(SUM(Partija[Laukimas h]), SUM(Partija[Gamybos ciklas h]))
```

**Vid. etapo trukmė h**

```dax
DIVIDE(AVERAGE('Partijų etapai'[Trukmė min]), 60)
```

**Vid. laukimas prieš etapą h**

```dax
DIVIDE(AVERAGE('Partijų etapai'[Laukimas min]), 60)
```

**Laukimas prieš šaldymą h**

```dax
CALCULATE([Vid. laukimas prieš etapą h], 'Partijų etapai'[Etapas] = "Šaldymas ir fasavimas")
```

**Atšaukimas: klientų sk.**

```dax
DISTINCTCOUNT(Siuntos[Kliento kodas])
```

**Atšaukimas: siuntų sk.**

```dax
COUNTROWS(Siuntos)
```

**Atšaukimas: likutis sandėlyje vnt**

```dax
SUM(Partija[Likutis vnt])
```

**Atšaukimas: atsekta %**

```dax
DIVIDE(SUM(Partija[Išsiųsta vnt]) + SUM(Partija[Brokas vnt]) + [Atšaukimas: likutis sandėlyje vnt], SUM(Partija[Pagaminta vnt]))
```

**Atšaukimas: tiekėjų sąskaitų sk.**

```dax
DISTINCTCOUNT('Žaliavų sunaudojimas'[Tiekėjo sąskaita])
```

</details>

### 2 Palyginimai

| Matas | Formatas | Aprašymas |
|---|---|---|
| `Pajamos PM` | `#,0" €"` | Praeito mėnesio pajamos. |
| `Pajamos MoM %` | `+0.0%;-0.0%;0.0%` |  |
| `Pajamos PY` | `#,0" €"` | Tas pats laikotarpis prieš metus. |
| `Pajamos YoY %` | `+0.0%;-0.0%;0.0%` |  |
| `Parduota vnt PY` | `#,0` |  |
| `Parduota vnt YoY %` | `+0.0%;-0.0%;0.0%` |  |
| `Žaliavų savikaina PY` | `#,0" €"` |  |
| `Bendrasis pelnas PY` | `#,0" €"` |  |
| `Marža % PY` | `0.0%` |  |
| `Maržos pokyčis p. p.` | `+0.0" p. p.";-0.0" p. p.";0.0" p. p."` | Maržos pokyčis procentiniais punktais, palyginti su tuo pačiu laikotarpiu prieš metus. |
| `Pajamos YTD` | `#,0" €"` |  |
| `Pajamos YTD PY` | `#,0" €"` |  |

<details><summary>DAX kodas</summary>

**Pajamos PM**

```dax
CALCULATE([Pajamos], DATEADD(Data[Data], -1, MONTH))
```

**Pajamos MoM %**

```dax
IF(NOT ISBLANK([Pajamos PM]), DIVIDE([Pajamos] - [Pajamos PM], [Pajamos PM]))
```

**Pajamos PY**

```dax
CALCULATE([Pajamos], SAMEPERIODLASTYEAR(Data[Data]))
```

**Pajamos YoY %**

```dax
IF(NOT ISBLANK([Pajamos PY]), DIVIDE([Pajamos] - [Pajamos PY], [Pajamos PY]))
```

**Parduota vnt PY**

```dax
CALCULATE([Parduota vnt], SAMEPERIODLASTYEAR(Data[Data]))
```

**Parduota vnt YoY %**

```dax
IF(NOT ISBLANK([Parduota vnt PY]), DIVIDE([Parduota vnt] - [Parduota vnt PY], [Parduota vnt PY]))
```

**Žaliavų savikaina PY**

```dax
CALCULATE([Žaliavų savikaina], SAMEPERIODLASTYEAR(Data[Data]))
```

**Bendrasis pelnas PY**

```dax
CALCULATE([Bendrasis pelnas], SAMEPERIODLASTYEAR(Data[Data]))
```

**Marža % PY**

```dax
CALCULATE([Marža %], SAMEPERIODLASTYEAR(Data[Data]))
```

**Maržos pokyčis p. p.**

```dax
IF(NOT ISBLANK([Marža % PY]) && NOT ISBLANK([Marža %]), ([Marža %] - [Marža % PY]) * 100)
```

**Pajamos YTD**

```dax
TOTALYTD([Pajamos], Data[Data])
```

**Pajamos YTD PY**

```dax
CALCULATE([Pajamos YTD], SAMEPERIODLASTYEAR(Data[Data]))
```

</details>

### 3 Kodėl? (pelno skaidymas)

| Matas | Formatas | Aprašymas |
|---|---|---|
| `Pelno pokyčis vs PY` | `+#,0" €";-#,0" €";0" €"` | Bendrojo pelno pokyčis, palyginti su tuo pačiu laikotarpiu prieš metus. Lygus keturių efektų sumai. |
| `Kiekio efektas` | `+#,0" €";-#,0" €";0" €"` | Kiek pelno pokyčio lėmė parduotas kiekis, jei vidutinis pelnas vienetui būtų kaip pernai. |
| `Mix efektas` | `+#,0" €";-#,0" €";0" €"` | Kiek lėmė pasikeitusi pardavimų struktūra (kurie produktai ir kuriems klientams). Skaičiuojama produkto × kliento lygiu. |
| `Kainos ir nuolaidų efektas` | `+#,0" €";-#,0" €";0" €"` | Kiek lėmė grynosios kainos vienetui pokyčis (kainoraštis, klientų ir akcijų nuolaidos). |
| `Žaliavų kainų efektas` | `+#,0" €";-#,0" €";0" €"` | Kiek lėmė žaliavų savikainos vienetui pokyčis (pvz. grietinėlės kaina). Neigiamas = savikaina išaugo. |
| `Veiksnio poveikis` | `+#,0" €";-#,0" €";0" €"` | Krioklio diagramai: ašis = Maržos veiksniai[Veiksnys], reikšmė = šis matas. |

<details><summary>DAX kodas</summary>

**Pelno pokyčis vs PY**

```dax
IF(NOT ISBLANK([Bendrasis pelnas PY]), [Bendrasis pelnas] - [Bendrasis pelnas PY])
```

**Kiekio efektas**

```dax
VAR KiekisPY = [Parduota vnt PY]
RETURN
    IF(KiekisPY > 0, ([Parduota vnt] - KiekisPY) * DIVIDE([Bendrasis pelnas PY], KiekisPY))
```

**Mix efektas**

```dax
VAR KiekisPY = [Parduota vnt PY]
VAR VidPelnasPY = DIVIDE([Bendrasis pelnas PY], KiekisPY)
VAR PagalPernaiPelna =
    SUMX(
        CROSSJOIN(VALUES(Produktas[Prekės kodas]), VALUES(Klientas[Kliento kodas])),
        VAR q = [Parduota vnt]
        VAR qPY = [Parduota vnt PY]
        RETURN IF(qPY > 0, q * DIVIDE([Bendrasis pelnas PY], qPY), [Bendrasis pelnas])
    )
RETURN
    IF(KiekisPY > 0, PagalPernaiPelna - [Parduota vnt] * VidPelnasPY)
```

**Kainos ir nuolaidų efektas**

```dax
VAR KiekisPY = [Parduota vnt PY]
RETURN
    IF(
        KiekisPY > 0,
        SUMX(
            CROSSJOIN(VALUES(Produktas[Prekės kodas]), VALUES(Klientas[Kliento kodas])),
            VAR q = [Parduota vnt]
            VAR qPY = [Parduota vnt PY]
            RETURN IF(q > 0 && qPY > 0, q * (DIVIDE([Pajamos], q) - DIVIDE([Pajamos PY], qPY)))
        )
    )
```

**Žaliavų kainų efektas**

```dax
VAR KiekisPY = [Parduota vnt PY]
RETURN
    IF(
        KiekisPY > 0,
        SUMX(
            CROSSJOIN(VALUES(Produktas[Prekės kodas]), VALUES(Klientas[Kliento kodas])),
            VAR q = [Parduota vnt]
            VAR qPY = [Parduota vnt PY]
            RETURN IF(q > 0 && qPY > 0, -q * (DIVIDE([Žaliavų savikaina], q) - DIVIDE([Žaliavų savikaina PY], qPY)))
        )
    )
```

**Veiksnio poveikis**

```dax
SWITCH(
    SELECTEDVALUE('Maržos veiksniai'[Veiksnys]),
    "Kiekis", [Kiekio efektas],
    "Produktų ir klientų mix", [Mix efektas],
    "Kaina ir nuolaidos", [Kainos ir nuolaidų efektas],
    "Žaliavų kainos", [Žaliavų kainų efektas],
    [Pelno pokyčis vs PY]
)
```

</details>

### 4 Gamyba

| Matas | Formatas | Aprašymas |
|---|---|---|
| `Pagaminta vnt` | `#,0` |  |
| `Brokas vnt` | `#,0` |  |
| `Brokas %` | `0.0%` |  |
| `Planas vnt` | `#,0` | Planuotojo Excel planas. |
| `Plano įvykdymas %` | `0.0%` |  |
| `Plano nuokrypis vnt` | `+#,0;-#,0;0` |  |
| `Prastovos min` | `#,0` |  |
| `Galimos minutės` | `#,0` | Linijų darbo minutės per savaitę × savaičių (pirmadienių) skaičius laikotarpyje. |
| `Prastovų dalis %` | `0.0%` |  |

<details><summary>DAX kodas</summary>

**Pagaminta vnt**

```dax
SUM(Gamyba[Pagaminta vnt])
```

**Brokas vnt**

```dax
SUM(Gamyba[Brokas vnt])
```

**Brokas %**

```dax
DIVIDE([Brokas vnt], [Pagaminta vnt])
```

**Planas vnt**

```dax
SUM('Gamybos planas'[Planas vnt])
```

**Plano įvykdymas %**

```dax
DIVIDE([Pagaminta vnt], [Planas vnt])
```

**Plano nuokrypis vnt**

```dax
[Pagaminta vnt] - [Planas vnt]
```

**Prastovos min**

```dax
SUM(Prastovos[Prastovos min])
```

**Galimos minutės**

```dax
SUMX(VALUES(Linija[Linijos kodas]), CALCULATE(MAX(Linija[Minutės per savaitę])))
    * CALCULATE(COUNTROWS(Data), Data[Savaitės dienos nr] = 1)
```

**Prastovų dalis %**

```dax
DIVIDE([Prastovos min], [Galimos minutės])
```

</details>

### 5 Atsargos

| Matas | Formatas | Aprašymas |
|---|---|---|
| `Likutis vnt` | `#,0` | Likutis paskutinė laikotarpio inventorizacijos dieną (likutių per laiką nesumuojame). |
| `Vid. dienos pardavimai vnt` | `#,0` |  |
| `Atsargų dienos` | `0.0` | Days of cover: kelioms dienoms užtektų likučio esant laikotarpio vidutiniam pardavimų tempui. |

<details><summary>DAX kodas</summary>

**Likutis vnt**

```dax
VAR PaskutineData = MAX(Atsargos[Data])
RETURN
    CALCULATE(SUM(Atsargos[Likutis vnt]), Data[Data] = PaskutineData)
```

**Vid. dienos pardavimai vnt**

```dax
DIVIDE([Parduota vnt], COUNTROWS(Data))
```

**Atsargų dienos**

```dax
DIVIDE([Likutis vnt], [Vid. dienos pardavimai vnt])
```

</details>

### 6 Pirkimai

| Matas | Formatas | Aprašymas |
|---|---|---|
| `Pirkimų suma` | `#,0" €"` |  |
| `Pirkimų kiekis` | `#,0` | Prasminga tik vienai žaliavai (skirtingi matai: l, kg, vnt). |
| `Vid. pirkimo kaina` | `0.0000" €"` | Svertinė kaina už mato vienetą. Naudok su Žaliava filtre ar ašyje. |
| `Žaliavų kainų indeksas` | `0.0` | 100 = 2025 m. sausio kainos. Kiek dabar nupirktas žaliavų krepšelis kainuotų 2025-01 kainomis (be transporto). |
| `DI nuskaitytų pirkimų suma` | `#,0" €"` |  |
| `Pirkimų sąskaitų sk.` | `#,0` |  |

<details><summary>DAX kodas</summary>

**Pirkimų suma**

```dax
SUM(Pirkimai[Suma be PVM])
```

**Pirkimų kiekis**

```dax
SUM(Pirkimai[Kiekis])
```

**Vid. pirkimo kaina**

```dax
DIVIDE([Pirkimų suma], [Pirkimų kiekis])
```

**Žaliavų kainų indeksas**

```dax
VAR Zaliavos = FILTER(VALUES('Žaliava'[Žaliavos kodas]), 'Žaliava'[Žaliavos kodas] <> "TRANSP")
VAR Faktas = SUMX(Zaliavos, [Pirkimų suma])
VAR BazinemisKainomis =
    SUMX(
        Zaliavos,
        [Pirkimų kiekis] * CALCULATE([Vid. pirkimo kaina], REMOVEFILTERS(Data), Data[Metai-mėnuo] = "2025-01")
    )
RETURN
    DIVIDE(Faktas, BazinemisKainomis) * 100
```

**DI nuskaitytų pirkimų suma**

```dax
CALCULATE([Pirkimų suma], Pirkimai[Šaltinis] = "DI")
```

**Pirkimų sąskaitų sk.**

```dax
DISTINCTCOUNT(Pirkimai[Sąskaitos nr])
```

</details>

### 7 Finansai

| Matas | Formatas | Aprašymas |
|---|---|---|
| `Sąnaudos` | `#,0" €"` | Faktinės veiklos sąnaudos iš finansų (be žaliavų). |
| `Biudžetas` | `#,0" €"` | Naudok su Straipsnis filtre ar ašyje. |
| `Sąnaudų biudžetas` | `#,0" €"` |  |
| `Sąnaudų nuokrypis` | `+#,0" €";-#,0" €";0" €"` | Teigiamas = išleista daugiau nei planuota. |
| `Sąnaudų nuokrypis %` | `+0.0%;-0.0%;0.0%` |  |
| `Pajamų biudžetas` | `#,0" €"` |  |
| `Pajamų biudžeto įvykdymas %` | `0.0%` |  |
| `Bendrojo pelno biudžetas` | `#,0" €"` |  |
| `Veiklos pelnas` | `#,0" €"` | Supaprastintas: bendrasis pelnas minus visos finansų sąnaudos. |
| `Veiklos pelno marža %` | `0.0%` |  |

<details><summary>DAX kodas</summary>

**Sąnaudos**

```dax
SUM(Finansai[Suma])
```

**Biudžetas**

```dax
SUM('Biudžetas'[Suma])
```

**Sąnaudų biudžetas**

```dax
CALCULATE([Biudžetas], Straipsnis[Tipas] = "Sąnaudos")
```

**Sąnaudų nuokrypis**

```dax
[Sąnaudos] - [Sąnaudų biudžetas]
```

**Sąnaudų nuokrypis %**

```dax
DIVIDE([Sąnaudų nuokrypis], [Sąnaudų biudžetas])
```

**Pajamų biudžetas**

```dax
CALCULATE([Biudžetas], Straipsnis[Straipsnis] = "Pajamos")
```

**Pajamų biudžeto įvykdymas %**

```dax
DIVIDE([Pajamos], [Pajamų biudžetas])
```

**Bendrojo pelno biudžetas**

```dax
CALCULATE([Biudžetas], Straipsnis[Straipsnis] = "Bendrasis pelnas")
```

**Veiklos pelnas**

```dax
[Bendrasis pelnas] - [Sąnaudos]
```

**Veiklos pelno marža %**

```dax
DIVIDE([Veiklos pelnas], [Pajamos])
```

</details>

### 8 DI ir duomenų kokybė

| Matas | Formatas | Aprašymas |
|---|---|---|
| `DI apdorota sąskaitų` | `#,0` |  |
| `DI patvirtinta automatiškai` | `#,0` |  |
| `DI atiduota peržiūrai` | `#,0` |  |
| `DI automatizavimo lygis %` | `0%` | Kokia dalis sąskaitų pateko į ERP be žmogaus. |
| `DI kaina USD` | `0.00" $"` |  |
| `DI laikas min` | `0.0` |  |
| `Rankinio darbo laikas min` | `#,0` | Prielaida: 4 min. vienai sąskaitai suvesti rankomis (docs/di_tikslumas.md). |
| `Sutaupyta laiko min` | `#,0` |  |
| `Pašalinta dublikatų` | `#,0` |  |
| `Sutvarkyta kliento kodų` | `#,0` |  |
| `Be kliento kodo` | `#,0` |  |
| `Sutvarkyta plano kodų` | `#,0` |  |
| `Nerasta plano kodų` | `#,0` |  |
| `Rasta atvejų` | `#,0` | Lentelei su Kokybės patikros eilutėmis. |
| `Lab nr. kitu formatu` | `#,0` |  |
| `Skundo nr. kitu formatu` | `#,0` |  |
| `Siuntos be partijos` | `#,0` |  |
| `Tyrimai be ERP partijos` | `#,0` |  |

<details><summary>DAX kodas</summary>

**DI apdorota sąskaitų**

```dax
COUNTROWS('DI žurnalas')
```

**DI patvirtinta automatiškai**

```dax
CALCULATE(COUNTROWS('DI žurnalas'), 'DI žurnalas'[Statusas] = "Patvirtinta")
```

**DI atiduota peržiūrai**

```dax
CALCULATE(COUNTROWS('DI žurnalas'), 'DI žurnalas'[Statusas] = "Peržiūrai") + 0
```

**DI automatizavimo lygis %**

```dax
DIVIDE([DI patvirtinta automatiškai], [DI apdorota sąskaitų])
```

**DI kaina USD**

```dax
SUM('DI žurnalas'[Kaina USD])
```

**DI laikas min**

```dax
DIVIDE(SUM('DI žurnalas'[Trukmė s]), 60)
```

**Rankinio darbo laikas min**

```dax
[DI apdorota sąskaitų] * 4
```

**Sutaupyta laiko min**

```dax
[Rankinio darbo laikas min] - [DI laikas min]
```

**Pašalinta dublikatų**

```dax
SUM(Pardavimai[ERP eilučių]) - COUNTROWS(Pardavimai)
```

**Sutvarkyta kliento kodų**

```dax
SUM(Pardavimai[Kodas taisytas]) + 0
```

**Be kliento kodo**

```dax
CALCULATE(COUNTROWS(Pardavimai), Pardavimai[Kliento kodas] = "NEŽINOMAS") + 0
```

**Sutvarkyta plano kodų**

```dax
SUM('Gamybos planas'[Kodas taisytas]) + 0
```

**Nerasta plano kodų**

```dax
COUNTROWS(FILTER('Gamybos planas', ISBLANK(RELATED(Produktas[Prekės kodas])))) + 0
```

**Rasta atvejų**

```dax
SWITCH(
    SELECTEDVALUE('Kokybės patikros'[Nr]),
    1, [Pašalinta dublikatų],
    2, [Sutvarkyta kliento kodų],
    3, [Be kliento kodo],
    4, [Sutvarkyta plano kodų],
    5, [Nerasta plano kodų],
    6, COUNTROWS('Peržiūra') + 0,
    7, [Lab nr. kitu formatu],
    8, [Tyrimai be ERP partijos],
    9, [Skundo nr. kitu formatu],
    10, [Siuntos be partijos]
)
```

**Lab nr. kitu formatu**

```dax
SUM('Lab tyrimai'[Nr. taisytas]) + 0
```

**Skundo nr. kitu formatu**

```dax
SUM(Skundai[Nr. taisytas]) + 0
```

**Siuntos be partijos**

```dax
COUNTROWS(FILTER(Siuntos, ISBLANK(Siuntos[Partijos nr]))) + 0
```

**Tyrimai be ERP partijos**

```dax
COUNTROWS(FILTER('Lab tyrimai', ISBLANK(RELATED(Partija[Partijos nr])))) + 0
```

</details>

### 9 Orai ir prognozė

| Matas | Formatas | Aprašymas |
|---|---|---|
| `Temperatūra °C` | `0.0" °C"` | Vidutinė dienos maksimali temperatūra (tikri Open-Meteo duomenys). |
| `Norma °C` | `0.0" °C"` | 2015–2024 m. vidurkis tą pačią metų dieną. |
| `Nukrypimas nuo normos °C` | `+0.0" °C";-0.0" °C";0.0" °C"` | Kiek šiltėliau (+) ar vėsiau (−) nei įprasta. Būtent tai, ne pati temperatūra, lemia prognozės klaidą. |
| `Karštų dienų (≥25 °C)` | `#,0` | Dienų skaičius, kai maksimali temperatūra ≥ 25 °C (sumuojama per pasirinktas šalis). |
| `Prognozė vnt` | `#,0` | Planuotojo paklausos prognozė (Excel). Lyginti su Užsakyta vnt; klientų filtras prognozės nefiltruoja, tik šalis. |
| `Prognozės nuokrypis %` | `+0.0%;-0.0%;0.0%` | Kiek užsakymai viršijo (+) ar nesiekė (−) prognozės. |
| `Prognozės tikslumas %` | `0.0%` | 1 − WAPE savaitės × produkto × šalies lygiu. 100 % = prognozė tiksliai atitiko užsakymus. |
| `Paklausos jautrumas 1 °C` | `+0.0%;-0.0%;0.0%` | Regresija iš duomenų (V–IX mėn., savaitė × šalis): kiek % užsakymai viršija prognozę, kai savaitė 1 °C šiltesnė už normą. Veikia ir pagal kategoriją ar šalį. |
| `Pasirinktas nukrypimas °C` | `+0" °C";-0" °C";0" °C"` |  |
| `Rekomenduojamas prognozės pokytis %` | `+0.0%;-0.0%;0.0%` | Kiek koreguoti prognozę, jei orų prognozė rodo pasirinktą nukrypimą nuo normos. Jautrumas imamas iš visos istorijos. |
| `Prognozė su orais vnt` | `#,0` |  |
| `Papildomai reikia vnt` | `+#,0;-#,0;0` | Tiek vienetų reikėtų pagaminti papildomai pagal pasirinktą orų scenarijų. |

<details><summary>DAX kodas</summary>

**Temperatūra °C**

```dax
AVERAGE(Orai[Maks. temperatūra])
```

**Norma °C**

```dax
AVERAGE(Orai[Norma])
```

**Nukrypimas nuo normos °C**

```dax
IF(NOT ISBLANK([Temperatūra °C]), [Temperatūra °C] - [Norma °C])
```

**Karštų dienų (≥25 °C)**

```dax
CALCULATE(COUNTROWS(Orai), Orai[Maks. temperatūra] >= 25)
```

**Prognozė vnt**

```dax
SUM('Prognozė'[Prognozė vnt])
```

**Prognozės nuokrypis %**

```dax
DIVIDE([Užsakyta vnt] - [Prognozė vnt], [Prognozė vnt])
```

**Prognozės tikslumas %**

```dax
VAR Langeliai = CROSSJOIN(VALUES(Data[Savaitės pradžia]), VALUES(Produktas[Prekės kodas]), VALUES('Šalis'[Šalies kodas]))
VAR Paklaida = SUMX(Langeliai, ABS([Užsakyta vnt] - [Prognozė vnt]))
RETURN
    1 - DIVIDE(Paklaida, [Prognozė vnt])
```

**Paklausos jautrumas 1 °C**

```dax
VAR Savaites = CALCULATETABLE(VALUES(Data[Savaitės pradžia]), Data[Mėnesio nr] >= 5, Data[Mėnesio nr] <= 9)
VAR Taskai =
    FILTER(
        ADDCOLUMNS(
            CROSSJOIN(Savaites, VALUES('Šalis'[Šalies kodas])),
            "@uzsakyta", [Užsakyta vnt],
            "@prognoze", [Prognozė vnt],
            "@x", [Nukrypimas nuo normos °C]
        ),
        [@uzsakyta] > 0 && [@prognoze] > 0 && NOT ISBLANK([@x])
    )
VAR Regresija = LINESTX(Taskai, LN([@uzsakyta] / [@prognoze]), [@x])
RETURN
    IF(COUNTROWS(Taskai) >= 10, EXP(MAXX(Regresija, [Slope1])) - 1)
```

**Pasirinktas nukrypimas °C**

```dax
SELECTEDVALUE('Oro scenarijus'[Nukrypimas °C], 0)
```

**Rekomenduojamas prognozės pokytis %**

```dax
VAR Jautrumas = CALCULATE([Paklausos jautrumas 1 °C], REMOVEFILTERS(Data))
RETURN
    IF(NOT ISBLANK(Jautrumas), POWER(1 + Jautrumas, [Pasirinktas nukrypimas °C]) - 1)
```

**Prognozė su orais vnt**

```dax
[Prognozė vnt] * (1 + [Rekomenduojamas prognozės pokytis %])
```

**Papildomai reikia vnt**

```dax
[Prognozė su orais vnt] - [Prognozė vnt]
```

</details>
