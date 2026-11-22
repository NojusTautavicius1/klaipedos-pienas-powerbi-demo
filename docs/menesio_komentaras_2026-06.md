# Mėnesio komentaras: 2026 m. birželio mėn.

> Sintetiniai duomenys, mokomasis pavyzdys. Tai ne tikri AB „Klaipėdos pienas“ skaičiai.

## Birželį pajamos augo 48,7 %, bet palyginamai, vienai savaitei, tik 18,9 %; puodelių linijos kompresoriaus gedimas sumažino užsakymų įvykdymą iki 90,7 %

- Pajamos siekė 2 440,8 tūkst. € (+48,7 % nei pernai), tačiau šių metų birželis turi 5 užsakymų savaites, o pernai turėjo 4. Palyginamas augimas vienai savaitei yra 18,9 %.
- Bendrasis pelnas pasiekė 1 474,0 tūkst. € (pernai 1 040,8 tūkst. €), bet marža sumažėjo iki 60,4 % (−3,0 p. p.), daugiausia dėl brangesnių žaliavų: grietinėlė pabrango 17,9 %.
- Įvykdyta tik 90,7 % užsakymų (pernai 100,0 %), prarasta 167,9 tūkst. € pajamų. Silpniausia kategorija yra plombyras puodelyje (77,4 %): Kretingos puodelių linija KRE-L2 įvykdė 82,8 % plano, nes per karščio bangą sugedęs šaldymo kompresorius sukėlė 2 379 min. prastovų.
- Sąnaudos sudarė 685,2 tūkst. € ir viršijo 673,2 tūkst. € biudžetą. Labiausiai viršytas marketingo biudžetas (+5,8 tūkst. €).

### Kodėl pasikeitė pelnas

Bendrasis pelnas, palyginti su pernai, išaugo 433,2 tūkst. €. Didesnis parduotas kiekis, kurį padidino ir papildoma užsakymų savaitė, pridėjo 500,2 tūkst. €, o geresnė produktų struktūra – dar 16,7 tūkst. €. Brangesnės žaliavos atėmė 75,9 tūkst. €, kainos ir nuolaidos – 7,8 tūkst. €.

| Veiksnys | Poveikis bendrajam pelnui vs pernai |
|---|---:|
| Parduotas kiekis | +500,2 tūkst. € |
| Produktų ir klientų mix | +16,7 tūkst. € |
| Kainos ir nuolaidos | −7,8 tūkst. € |
| Žaliavų kainos | −75,9 tūkst. € |
| **Iš viso** | **+433,2 tūkst. €** |

### Į ką žiūrėti kitą mėnesį

- Kitos karščio bangos metu KRE-L2 šaldymo kompresorius gali vėl sustoti, o liepą ledų paklausa didžiausia.
- Šeimos pakuočių linija KLA-L3 (didžiausia kategorija, 679,1 tūkst. €) prastovėjo 183 min. dėl žaliavų trūkumo ir 177 min. dėl pakavimo įrangos gedimo.
- Brangstanti grietinėlė (+17,9 %) toliau mažins maržą. Iš 4 skundų 2 susiję su etikete ar alergenų informacija, 2 skundai dar atviri.

### Siūlomi veiksmai

| Veiksmas | Atsakingas |
|---|---|
| Per 2 savaites suremontuoti arba pakeisti KRE-L2 šaldymo kompresorių ir parengti atsarginio šaldymo sprendimą karščio dienoms; peržiūrėti KLA-L3 pakavimo įrangą. | Gamybos ir techninės priežiūros skyrius |
| Su klientais suderinti neįvykdytų plombyro puodelyje užsakymų pristatymo grafiką ir liepos kiekius pagal realų KRE-L2 pajėgumą. | Pardavimų ir planavimo skyrius |
| Užtikrinti KLA-L3 žaliavų atsargas ir pateikti grietinėlės kainos fiksavimo ar alternatyvių tiekėjų pasiūlymą; uždaryti 2 atvirus skundus ir patikrinti alergenų etiketes. | Pirkimų ir kokybės skyriai |

### Pagrindiniai skaičiai

| Rodiklis | Šis mėnuo | Pernai | Pokytis |
|---|---:|---:|---:|
| Pajamos | 2 440,8 tūkst. € | 1 641,9 tūkst. € | +48,7 % |
| Bendrasis pelnas | 1 474,0 tūkst. € | 1 040,8 tūkst. € | +433,2 tūkst. € |
| Marža | 60,4 % | 63,4 % | −3,0 p. p. |
| Užsakymų įvykdymas | 90,7 % | 100,0 % | |
| Gamybos plano įvykdymas | 92,3 % | | |
| Skundai | 4 | vid. 4,5 per mėn. | |

---

**Kaip tai padaryta.** Skriptas `automation/monthly_commentary.py` suskaičiuoja faktus tomis pačiomis formulėmis kaip Power BI matai (`automation/kpi.py`), Claude parašo tekstą, o skriptas patikrina kiekvieną paminėtą skaičių su faktais. Patikra: **visi 31 skaičiai sutampa su faktais**. Modelis claude-opus-5-5, bandymų: 1, kaina 0,117 $, 41 s.