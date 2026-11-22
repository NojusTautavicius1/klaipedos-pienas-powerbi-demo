# Mėnesio komentaras: 2026 m. spalio mėn.

> Sintetiniai duomenys, mokomasis pavyzdys. Tai ne tikri AB „Klaipėdos pienas“ skaičiai.

## Spalio pajamos 9,6 % didesnės nei pernai, bet brangesnė grietinėlė sumažino maržą 1,9 p. p.

- Spalio pajamos siekė 851,7 tūkst. € ir buvo 9,6 % didesnės nei pernai. Abu mėnesiai turėjo po 4 užsakymų savaites, todėl palyginimas tiesioginis.
- Bendrasis pelnas išaugo iki 518,7 tūkst. € (pernai 488,0 tūkst. €), tačiau marža nukrito iki 60,9 % (−1,9 p. p.), nes grietinėlė brango 19,6 %.
- Augo visos rinkos ir kategorijos: Jungtinė Karalystė +12,0 %, Centrinė Europa +10,7 %, Baltijos šalys +7,9 %. Užsakymai įvykdyti 100,0 %.
- Gamybos planas įvykdytas 96,1 %. Silpniausia buvo KRE-L2 puodelių linija (93,9 %), kurioje produkto keitimas (derinimas) sudarė 853 min. iš 1355 min. prastovų.

### Kodėl pasikeitė pelnas

Bendrasis pelnas, palyginti su pernai, išaugo 30,7 tūkst. €. Daugiausia prisidėjo kainos ir nuolaidos (+32,4 tūkst. €) bei didesnis kiekis (+22,0 tūkst. €), šiek tiek – geresnė produktų sudėtis (+4 659 €). Brangesnės žaliavos, pirmiausia grietinėlė (+19,6 %) ir šokolado glajus (+7,7 %), atėmė 28,3 tūkst. € ir lėmė maržos kritimą.

| Veiksnys | Poveikis bendrajam pelnui vs pernai |
|---|---:|
| Parduotas kiekis | +22,0 tūkst. € |
| Produktų ir klientų mix | +4,7 tūkst. € |
| Kainos ir nuolaidos | +32,4 tūkst. € |
| Žaliavų kainos | −28,3 tūkst. € |
| **Iš viso** | **+30,7 tūkst. €** |

### Į ką žiūrėti kitą mėnesį

- Grietinėlės kaina 19,6 % didesnė nei pernai; jei ji neatpigs, marža toliau liks žemesnė nei pernai (metų pradžios marža 60,7 %, pernai 62,8 %).
- Žaliavų trūkumas stabdo linijas: KLA-L3 šeimos pakuočių linijoje jis sukėlė 454 min. prastovų, KLA-L1 – 263 min., GAR-L1 – 284 min.
- Skundų gauta 6, daugiau nei vidutiniškai (4,5 per mėnesį), 2 dar neišspręsti.

### Siūlomi veiksmai

| Veiksmas | Atsakingas |
|---|---|
| Peržiūrėti KRE-L2 puodelių linijos gaminių eiliškumą ir sujungti panašius gaminius į ilgesnes partijas, kad sumažėtų 853 min. derinimo prastovų. | Gamybos skyrius |
| Susitarti su grietinėlės tiekėjais dėl kainos ir pristatymo grafiko bei užtikrinti žaliavų atsargas KLA-L3 linijai. | Pirkimų skyrius |
| Išnagrinėti ir uždaryti 2 atvirus skundus, ypač dėl pažeistos pakuotės ir skonio / kvapo. | Kokybės skyrius |

### Pagrindiniai skaičiai

| Rodiklis | Šis mėnuo | Pernai | Pokytis |
|---|---:|---:|---:|
| Pajamos | 851,7 tūkst. € | 777,2 tūkst. € | +9,6 % |
| Bendrasis pelnas | 518,7 tūkst. € | 488,0 tūkst. € | +30,7 tūkst. € |
| Marža | 60,9 % | 62,8 % | −1,9 p. p. |
| Užsakymų įvykdymas | 100,0 % | 100,0 % | |
| Gamybos plano įvykdymas | 96,1 % | | |
| Skundai | 6 | vid. 4,5 per mėn. | |

---

**Kaip tai padaryta.** Skriptas `automation/monthly_commentary.py` suskaičiuoja faktus tomis pačiomis formulėmis kaip Power BI matai (`automation/kpi.py`), Claude parašo tekstą, o skriptas patikrina kiekvieną paminėtą skaičių su faktais. Patikra: **visi 33 skaičiai sutampa su faktais**. Modelis claude-opus-5-5, bandymų: 2, kaina 0,191 $, 52 s.