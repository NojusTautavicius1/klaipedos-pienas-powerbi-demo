# „Klausk duomenų“: Claude atsako į vadovo klausimus

> Sintetiniai duomenys. Tai mokomasis pavyzdys, ne tikri AB „Klaipėdos pienas“ skaičiai. Orai tikri (Open-Meteo).

Claude Code per [Power BI Modeling MCP](https://github.com/microsoft/powerbi-modeling-mcp) jungiasi prie atidaryto Power BI Desktop modelio, pats parašo DAX užklausas ir atsako lietuviškai. Modelio jis nekeičia, tik skaito. Taisyklės aprašytos skile [`/klausk-duomenu`](../.claude/skills/klausk-duomenu/SKILL.md).

Žemiau pateikti 4 klausimai ir atsakymai, kuriuos modelis grąžino 2026-11-21.

---

## 1. Kodėl 2026 m. birželį trūko DIONE puodelių?

**Iš karto dvi priežastys: karščio banga ir sugedusi linija.**

- Birželį puodelių pristatyta tik **77,4 %** užsakymų, o kitų kategorijų **99,0 %**. Problema yra vienos linijos.
- 2026-06-22 savaitę Europoje buvo karščio banga: Londonas **+10,0 °C**, Berlynas +8,8, Varšuva +6,2, Klaipėda +3,6 virš normos. Puodelių užsakymai viršijo prognozę **+33 %**.
- Tą pačią savaitę Kretingos puodelių linijoje (KRE-L2) sugedo šaldymo kompresorius. Per VI–VII prastovos buvo: gedimas 2 379 min., atsarginių dalių laukimas 2 165 min., tunelio remontas 1 649 min. Linija pagamino **79 %** plano.
- Prarasta **381 731 vnt.** ir **199 566 €** pajamų. Daugiausia nukentėjo Lidl Lietuva (91 906 vnt.), Tesco UK (56 027) ir vietiniai tinklai (49 421).
- Pasekmė kokybei: kol kompresorius neveikė, tunelis ledus grūdino per šiltai. Iš tų partijų gauta **17 skundų dėl ledo kristalų**.

**Ką daryti:** šaldymo įrangai sezono metu taikyti prevencinę priežiūrą (gegužę) ir laikyti atsargines dalis vietoje. Prognozėje atsižvelgti į orų prognozę (žr. 4 klausimą).

---

## 2. Kodėl marža krito, nors pardavimai augo?

**Pelnas augo, bet lėčiau nei pajamos, nes pabrango grietinėlė.**

- IV–IX pajamos **+8,9 %** (9,88 → 10,76 mln. €), o žaliavų marža krito **62,8 % → 60,2 %**.
- Bendrasis pelnas vis tiek **+267 649 €**. Jį sudaro kiekis **+417 185 €**, kainos ir nuolaidos +136 027 €, mix +46 942 €, o žaliavų kainos atėmė **−332 505 €**.
- Grietinėlė 35 % (tiekėjas T02) nuo balandžio **+17,9 %** (3,08 → 3,63 €/kg). Vien ji kainavo **+307 tūkst. €**, t. y. ~92 % viso žaliavų poveikio. Kitos žaliavos pabrango nedaug: šokolado glajus +6,7 %, pienas +2,9 %.

**Ką daryti:** derėtis su T02 arba ieškoti antro grietinėlės tiekėjo. Peržiūrėti produktų su daugiausia grietinėlės (plombyras, tortai) kainas.

---

## 3. Gavome skundą dėl svetimkūnio. Kas gavo tą partiją ir iš ko ji pagaminta?

**Partija P26-001885 (KAR KAR šerbetas mangų 500 ml, 2026-07-17) atsekta 100 %.**

- Skundas SK-26-0074, Costco UK, 2026-08-18.
- Pagaminta 8 458 vnt., brokas 157, **išsiųsta 8 301**, sandėlyje nieko nebeliko.
- Klientai: Lidl Lietuva 3 021, Lidl Latvija 1 348, Tesco UK 1 290, vietiniai tinklai 1 249, Costco UK 779, HoReCa 614.
- Žaliavos iš 3 tiekėjų sąskaitų: CT26-0027 (cukrus), FV/OS/26-0027 (vaisių tyrė, Lenkija), SP26-0027 (pakuotės).
- Metalo detektoriaus patikra buvo atitikusi. Plastiko jis neaptinka, todėl pirmiausia tikrinti fasavimo tarpines ir tyrės tiekėją.

**Ką daryti:** informuoti 6 klientus, paprašyti tyrės tiekėjo partijos sertifikato. BRC atšaukimo testas užtruko vieną užklausą.

---

## 4. Kiek papildomai pagaminti, jei kitą savaitę bus karšta?

**Modelis iš istorijos išmoko: +1 °C virš normos ≈ +4,5 % užsakymų** (šerbetui 5,8 %, tortams 0,9 %).

- Patikra su tikra karščio bangos savaite (2026-06-22, visos šalys, +6 °C): planuotojo prognozė buvo **561 889 vnt.**, modelis su orais būtų prognozavęs **732 108 vnt.**, o užsakyta **734 238 vnt.** (skirtumas 0,3 %).
- JK, jei bus +8 °C: prognozę reikia didinti **+45 %**, t. y. papildomai **+50 340 vnt.** per savaitę.

**Ką daryti:** kas savaitę į planavimą įtraukti 7 dienų orų prognozę rinkų miestams. Power BI tam turi slankiklį „Oro scenarijus“.

---

### Kaip suskaičiuota (pavyzdys)

```dax
EVALUATE
VAR Karstis = TREATAS({DATE(2026, 6, 22)}, Data[Savaitės pradžia])
RETURN
ROW(
    "Prognozė", CALCULATE([Prognozė vnt], Karstis),
    "Su orais (+6 °C)", CALCULATE([Prognozė su orais vnt], Karstis, 'Oro scenarijus'[Nukrypimas °C] = 6),
    "Užsakyta", CALCULATE([Užsakyta vnt], Karstis)
)
```

Jautrumas skaičiuojamas DAX regresija (`LINESTX`) iš savaičių × šalių: `ln(užsakyta / prognozė)` pagal nukrypimą nuo normos.
