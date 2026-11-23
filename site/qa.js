window.QA = [
 {
  "q": "Kaip sekasi šiais metais, palyginti su pernai?",
  "title": "Pajamos ir pelnas auga, bet marža mažesnė nei pernai, o vasarą dalies užsakymų nespėta įvykdyti.",
  "points": [
   "2026 m. sausis–spalis: pajamos 13 758 178 € (+10,6 % vs pernai).",
   "Bendrasis pelnas 8 348 449 € (+535 733 €), marža 60,7 % (-2,1 p. p.).",
   "Užsakymų įvykdyta 97,6 %, dėl trūkumų prarasta 228 064 € pajamų.",
   "Sparčiausiai augo rinka „Jungtinė Karalystė“: +13,5 %."
  ],
  "todo": "Daugiausia dėmesio reikia dviem dalykams: grietinėlės kainai (ji mažina maržą) ir pasiruošimui karščio savaitėms (dėl jų trūksta prekių).",
  "where": "„Apžvalga“",
  "dax": "[Atsakymas: metai] =\nVAR e = SELECTEDVALUE(Atsakymai[Eilė])\nVAR P26 = DATESBETWEEN(Data[Data], DATE(2026, 1, 1), DATE(2026, 10, 31))\nVAR P25 = DATESBETWEEN(Data[Data], DATE(2025, 1, 1), DATE(2025, 10, 31))\nVAR Paj26 = CALCULATE([Pajamos], P26)\nVAR Paj25 = CALCULATE([Pajamos], P25)\nVAR Pel26 = CALCULATE([Bendrasis pelnas], P26)\nVAR Pel25 = CALCULATE([Bendrasis pelnas], P25)\nVAR M26 = CALCULATE([Marža %], P26)\nVAR M25 = CALCULATE([Marža %], P25)\nVAR Iv = CALCULATE([Užsakymų įvykdymas %], P26)\nVAR Pr = CALCULATE([Prarastos pajamos], P26)\nVAR Rinkos =\n    ADDCOLUMNS(\n        FILTER(VALUES(Klientas[Rinka]), NOT ISBLANK(Klientas[Rinka]) && Klientas[Rinka] <> \"(nenurodyta)\"),\n        \"@g\", DIVIDE(CALCULATE([Pajamos], P26), CALCULATE([Pajamos], P25)) - 1\n    )\nVAR Geriausia = TOPN(1, Rinkos, [@g], DESC)\nRETURN\n    SWITCH(\n        e,\n        1, \"Pajamos ir pelnas auga, bet marža mažesnė nei pernai, o vasarą dalies užsakymų nespėta įvykdyti.\",\n        2, \"2026 m. sausis–spalis: pajamos \" & FORMAT(Paj26, \"#,0 €\", \"lt-LT\") & \" (\" & FORMAT(DIVIDE(Paj26, Paj25) - 1, \"+0.0 %;-0.0 %\", \"lt-LT\") & \" vs pernai).\",\n        3, \"Bendrasis pelnas \" & FORMAT(Pel26, \"#,0 €\", \"lt-LT\") & \" (\" & FORMAT(Pel26 - Pel25, \"+#,0 €;-#,0 €\", \"lt-LT\") & \"), marža \" & FORMAT(M26, \"0.0 %\", \"lt-LT\") & \" (\" & FORMAT((M26 - M25) * 100, \"+0.0;-0.0\", \"lt-LT\") & \" p. p.).\",\n        4, \"Užsakymų įvykdyta \" & FORMAT(Iv, \"0.0 %\", \"lt-LT\") & \", dėl trūkumų prarasta \" & FORMAT(Pr, \"#,0 €\", \"lt-LT\") & \" pajamų.\",\n        5, \"Sparčiausiai augo rinka „\" & MAXX(Geriausia, Klientas[Rinka]) & \"“: \" & FORMAT(MAXX(Geriausia, [@g]), \"+0.0 %;-0.0 %\", \"lt-LT\") & \".\",\n        6, \"Daugiausia dėmesio reikia dviem dalykams: grietinėlės kainai (ji mažina maržą) ir pasiruošimui karščio savaitėms (dėl jų trūksta prekių).\",\n        7, \"Puslapis „Apžvalga“.\"\n    )\nisHidden"
 },
 {
  "q": "Kodėl 2026 m. birželį trūko puodelių?",
  "title": "Sutapo dvi priežastys: karščio banga ir sugedusi Kretingos puodelių linija (KRE-L2).",
  "points": [
   "Birželį pristatyta tik 77,4 % puodelių užsakymų, kitų kategorijų 99,0 %. Problema yra vienos linijos.",
   "2026-06-22 savaitę Europoje buvo karščio banga: rinkose vidutiniškai +4,9 °C virš normos, Londone +10,0 °C. Užsakymai viršijo prognozę.",
   "Tą pačią savaitę KRE-L2 sugedo šaldymo kompresorius. Per VI–VII linija pagamino 79 % plano, prastovos 7 765 min.",
   "Per VI–VII prarasta 381 731 vnt. puodelių ir 199 566 € pajamų."
  ],
  "todo": "Šaldymo įrangai daryti prevencinę priežiūrą prieš sezoną (gegužę), atsargines kompresoriaus dalis laikyti vietoje, o planuojant atsižvelgti į orų prognozę.",
  "where": "„Gamyba“ ir „Planavimas“",
  "dax": "[Atsakymas: trūkumai] =\nVAR e = SELECTEDVALUE(Atsakymai[Eilė])\nVAR Bir = DATESBETWEEN(Data[Data], DATE(2026, 6, 1), DATE(2026, 6, 30))\nVAR VIVII = DATESBETWEEN(Data[Data], DATE(2026, 6, 1), DATE(2026, 7, 31))\nVAR Karstis = DATESBETWEEN(Data[Data], DATE(2026, 6, 22), DATE(2026, 6, 28))\nVAR Puod = CALCULATE([Užsakymų įvykdymas %], Bir, Produktas[Kategorija] = \"Plombyras puodelyje\")\nVAR Kitos = CALCULATE([Užsakymų įvykdymas %], Bir, Produktas[Kategorija] <> \"Plombyras puodelyje\")\nVAR Nuokr = CALCULATE([Nukrypimas nuo normos °C], Karstis)\nVAR Lond = CALCULATE([Nukrypimas nuo normos °C], Karstis, 'Šalis'[Šalies kodas] = \"GB\")\nVAR Planas = CALCULATE([Plano įvykdymas %], VIVII, Linija[Linijos kodas] = \"KRE-L2\")\nVAR Prast = CALCULATE([Prastovos min], VIVII, Linija[Linijos kodas] = \"KRE-L2\")\nVAR PrarV = CALCULATE([Prarasta vnt], VIVII, Produktas[Kategorija] = \"Plombyras puodelyje\")\nVAR PrarE = CALCULATE([Prarastos pajamos], VIVII, Produktas[Kategorija] = \"Plombyras puodelyje\")\nRETURN\n    SWITCH(\n        e,\n        1, \"Sutapo dvi priežastys: karščio banga ir sugedusi Kretingos puodelių linija (KRE-L2).\",\n        2, \"Birželį pristatyta tik \" & FORMAT(Puod, \"0.0 %\", \"lt-LT\") & \" puodelių užsakymų, kitų kategorijų \" & FORMAT(Kitos, \"0.0 %\", \"lt-LT\") & \". Problema yra vienos linijos.\",\n        3, \"2026-06-22 savaitę Europoje buvo karščio banga: rinkose vidutiniškai \" & FORMAT(Nuokr, \"+0.0;-0.0\", \"lt-LT\") & \" °C virš normos, Londone \" & FORMAT(Lond, \"+0.0;-0.0\", \"lt-LT\") & \" °C. Užsakymai viršijo prognozę.\",\n        4, \"Tą pačią savaitę KRE-L2 sugedo šaldymo kompresorius. Per VI–VII linija pagamino \" & FORMAT(Planas, \"0 %\", \"lt-LT\") & \" plano, prastovos \" & FORMAT(Prast, \"#,0\", \"lt-LT\") & \" min.\",\n        5, \"Per VI–VII prarasta \" & FORMAT(PrarV, \"#,0\", \"lt-LT\") & \" vnt. puodelių ir \" & FORMAT(PrarE, \"#,0 €\", \"lt-LT\") & \" pajamų.\",\n        6, \"Šaldymo įrangai daryti prevencinę priežiūrą prieš sezoną (gegužę), atsargines kompresoriaus dalis laikyti vietoje, o planuojant atsižvelgti į orų prognozę.\",\n        7, \"Puslapiai „Gamyba“ ir „Planavimas“.\"\n    )\nisHidden"
 },
 {
  "q": "Kodėl krito marža, nors pardavimai augo?",
  "title": "Pelnas augo, bet lėčiau nei pajamos, nes nuo balandžio pabrango grietinėlė.",
  "points": [
   "2026 m. IV–IX pajamos +8,9 % (9,88 → 10,76 mln. €), o žaliavų marža 62,8 % → 60,2 %.",
   "Bendrasis pelnas vis tiek +267 649 €: kiekis +417 185 €, kainos ir nuolaidos +136 027 €, mix +46 942 €, žaliavų kainos -332 505 €.",
   "Grietinėlė 35 %: I–III vidutiniškai 3,10 €/kg, IV–IX 3,63 €/kg (+16,9 %)."
  ],
  "todo": "Derėtis su grietinėlės tiekėju arba ieškoti antro. Peržiūrėti kainas produktų, kuriuose daugiausia grietinėlės (plombyras, tortai).",
  "where": "„Kodėl?“ (krioklio diagrama ir pokytis pagal rinką bei kategoriją)",
  "dax": "[Atsakymas: marža] =\nVAR e = SELECTEDVALUE(Atsakymai[Eilė])\nVAR P26 = DATESBETWEEN(Data[Data], DATE(2026, 4, 1), DATE(2026, 9, 30))\nVAR P25 = DATESBETWEEN(Data[Data], DATE(2025, 4, 1), DATE(2025, 9, 30))\nVAR Paj26 = CALCULATE([Pajamos], P26)\nVAR Paj25 = CALCULATE([Pajamos], P25)\nVAR M26 = CALCULATE([Marža %], P26)\nVAR M25 = CALCULATE([Marža %], P25)\nVAR Pok = CALCULATE([Pelno pokyčis vs PY], P26)\nVAR Kiek = CALCULATE([Kiekio efektas], P26)\nVAR Mix = CALCULATE([Mix efektas], P26)\nVAR Kain = CALCULATE([Kainos ir nuolaidų efektas], P26)\nVAR Zal = CALCULATE([Žaliavų kainų efektas], P26)\nVAR G1 = CALCULATE([Vid. pirkimo kaina], DATESBETWEEN(Data[Data], DATE(2026, 1, 1), DATE(2026, 3, 31)), 'Žaliava'[Žaliava] = \"Grietinėlė 35 %\")\nVAR G2 = CALCULATE([Vid. pirkimo kaina], P26, 'Žaliava'[Žaliava] = \"Grietinėlė 35 %\")\nRETURN\n    SWITCH(\n        e,\n        1, \"Pelnas augo, bet lėčiau nei pajamos, nes nuo balandžio pabrango grietinėlė.\",\n        2, \"2026 m. IV–IX pajamos \" & FORMAT(DIVIDE(Paj26, Paj25) - 1, \"+0.0 %;-0.0 %\", \"lt-LT\") & \" (\" & FORMAT(Paj25 / 1000000, \"0.00\", \"lt-LT\") & \" → \" & FORMAT(Paj26 / 1000000, \"0.00\", \"lt-LT\") & \" mln. €), o žaliavų marža \" & FORMAT(M25, \"0.0 %\", \"lt-LT\") & \" → \" & FORMAT(M26, \"0.0 %\", \"lt-LT\") & \".\",\n        3, \"Bendrasis pelnas vis tiek \" & FORMAT(Pok, \"+#,0 €;-#,0 €\", \"lt-LT\") & \": kiekis \" & FORMAT(Kiek, \"+#,0 €;-#,0 €\", \"lt-LT\") & \", kainos ir nuolaidos \" & FORMAT(Kain, \"+#,0 €;-#,0 €\", \"lt-LT\") & \", mix \" & FORMAT(Mix, \"+#,0 €;-#,0 €\", \"lt-LT\") & \", žaliavų kainos \" & FORMAT(Zal, \"+#,0 €;-#,0 €\", \"lt-LT\") & \".\",\n        4, \"Grietinėlė 35 %: I–III vidutiniškai \" & FORMAT(G1, \"0.00\", \"lt-LT\") & \" €/kg, IV–IX \" & FORMAT(G2, \"0.00\", \"lt-LT\") & \" €/kg (\" & FORMAT(DIVIDE(G2, G1) - 1, \"+0.0 %;-0.0 %\", \"lt-LT\") & \").\",\n        6, \"Derėtis su grietinėlės tiekėju arba ieškoti antro. Peržiūrėti kainas produktų, kuriuose daugiausia grietinėlės (plombyras, tortai).\",\n        7, \"Puslapis „Kodėl?“ (krioklio diagrama ir pokytis pagal rinką bei kategoriją).\"\n    )\nisHidden"
 },
 {
  "q": "Kiek daugiau gaminti, jei kitą savaitę bus karšta?",
  "title": "Iš istorijos matyti: +1 °C virš normos ≈ +4,5 % užsakymų (gegužė–rugsėjis, visos rinkos).",
  "points": [
   "Jei bus +6 °C virš normos, prognozę reikia keisti +30,3 %.",
   "Patikra su tikra karščio savaite 2026-06-22 (+6 °C): planuotojo prognozė 561 889 vnt., su orų pataisa 732 108 vnt., iš tikrųjų užsakyta 734 238 vnt."
  ],
  "todo": "Kas savaitę į planą įtraukti 16 dienų orų prognozę. Skriptas planner_weather.py ją paima automatiškai ir įrašo į planuotojo Excel.",
  "where": "„Planavimas“",
  "dax": "[Atsakymas: karštis] =\nVAR e = SELECTEDVALUE(Atsakymai[Eilė])\nVAR J = CALCULATE([Paklausos jautrumas 1 °C], REMOVEFILTERS(Data))\nVAR N = [Pasirinktas nukrypimas °C]\nVAR R = [Rekomenduojamas prognozės pokytis %]\nVAR Sav = TREATAS({DATE(2026, 6, 22)}, Data[Savaitės pradžia])\nVAR Pr = CALCULATE([Prognozė vnt], Sav)\nVAR PrO = CALCULATE([Prognozė su orais vnt], Sav, 'Oro scenarijus'[Nukrypimas °C] = 6)\nVAR Uz = CALCULATE([Užsakyta vnt], Sav)\nRETURN\n    SWITCH(\n        e,\n        1, \"Iš istorijos matyti: +1 °C virš normos ≈ \" & FORMAT(J, \"+0.0 %;-0.0 %\", \"lt-LT\") & \" užsakymų (gegužė–rugsėjis, visos rinkos).\",\n        2, IF(N = 0, \"Slankikliu dešinėje pasirink, kiek šilčiau nei įprasta bus kitą savaitę.\", \"Jei bus \" & FORMAT(N, \"+0;-0\", \"lt-LT\") & \" °C virš normos, prognozę reikia keisti \" & FORMAT(R, \"+0.0 %;-0.0 %\", \"lt-LT\") & \".\"),\n        3, \"Patikra su tikra karščio savaite 2026-06-22 (+6 °C): planuotojo prognozė \" & FORMAT(Pr, \"#,0\", \"lt-LT\") & \" vnt., su orų pataisa \" & FORMAT(PrO, \"#,0\", \"lt-LT\") & \" vnt., iš tikrųjų užsakyta \" & FORMAT(Uz, \"#,0\", \"lt-LT\") & \" vnt.\",\n        6, \"Kas savaitę į planą įtraukti 16 dienų orų prognozę. Skriptas planner_weather.py ją paima automatiškai ir įrašo į planuotojo Excel.\",\n        7, \"Puslapis „Planavimas“.\"\n    )\nisHidden"
 },
 {
  "q": "Ar linijos gedimas paveikė kokybę?",
  "title": "Taip. Kol KRE-L2 kompresorius neveikė, šaldymo tunelis nepasiekė −35 °C, ir ledai buvo grūdinami per šiltai.",
  "points": [
   "Liepą–rugpjūtį gauta 18 skundų dėl ledo kristalų, kai kitais mėnesiais vidutiniškai 0,8 per mėnesį.",
   "Gedimo metu (06-22–07-12) pagamintų KRE-L2 partijų skundai: 43 milijonui vienetų, kai vidutiniškai 2,5.",
   "Pirmo karto atitiktis: visų partijų 95,8 %, gedimo laikotarpio KRE-L2 partijų 0 %."
  ],
  "todo": "Grūdinimo temperatūrą stebėti realiu laiku ir partiją sulaikyti automatiškai, kai riba viršijama, o ne laukti skundų.",
  "where": "„Kokybė“ ir „Procesas“",
  "dax": "[Atsakymas: kokybė] =\nVAR e = SELECTEDVALUE(Atsakymai[Eilė])\nVAR Kris = CALCULATE(COUNTROWS(Skundai), Skundai[Tipas] = \"Tekstūra (ledo kristalai)\", Skundai[Gavimo mėnuo] IN {\"2026-07\", \"2026-08\"})\nVAR KrisKiti = CALCULATE(COUNTROWS(Skundai), Skundai[Tipas] = \"Tekstūra (ledo kristalai)\", NOT Skundai[Gavimo mėnuo] IN {\"2026-07\", \"2026-08\"})\nVAR Menesiu = CALCULATE(DISTINCTCOUNT(Skundai[Gavimo mėnuo]), NOT Skundai[Gavimo mėnuo] IN {\"2026-07\", \"2026-08\"})\nVAR Gedimas = DATESBETWEEN(Data[Data], DATE(2026, 6, 22), DATE(2026, 7, 12))\nVAR SkG = CALCULATE([Skundai 1 mln. vnt.], Gedimas, Linija[Linijos kodas] = \"KRE-L2\")\nVAR SkV = [Skundai 1 mln. vnt.]\nVAR FtaV = [Pirmo karto atitiktis %]\nVAR FtaG = CALCULATE([Pirmo karto atitiktis %], Gedimas, Linija[Linijos kodas] = \"KRE-L2\")\nRETURN\n    SWITCH(\n        e,\n        1, \"Taip. Kol KRE-L2 kompresorius neveikė, šaldymo tunelis nepasiekė −35 °C, ir ledai buvo grūdinami per šiltai.\",\n        2, \"Liepą–rugpjūtį gauta \" & FORMAT(Kris, \"#,0\", \"lt-LT\") & \" skundų dėl ledo kristalų, kai kitais mėnesiais vidutiniškai \" & FORMAT(DIVIDE(KrisKiti, Menesiu), \"0.0\", \"lt-LT\") & \" per mėnesį.\",\n        3, \"Gedimo metu (06-22–07-12) pagamintų KRE-L2 partijų skundai: \" & FORMAT(SkG, \"0\", \"lt-LT\") & \" milijonui vienetų, kai vidutiniškai \" & FORMAT(SkV, \"0.0\", \"lt-LT\") & \".\",\n        4, \"Pirmo karto atitiktis: visų partijų \" & FORMAT(FtaV, \"0.0 %\", \"lt-LT\") & \", gedimo laikotarpio KRE-L2 partijų \" & FORMAT(FtaG, \"0 %\", \"lt-LT\") & \".\",\n        6, \"Grūdinimo temperatūrą stebėti realiu laiku ir partiją sulaikyti automatiškai, kai riba viršijama, o ne laukti skundų.\",\n        7, \"Puslapiai „Kokybė“ ir „Procesas“.\"\n    )\nisHidden"
 },
 {
  "q": "Kur gamyboje partija stovi ilgiausiai?",
  "title": "Ilgiausiai partija laukia prieš etapą „Šaldymas ir fasavimas“: vidutiniškai 1,7 h.",
  "points": [
   "Vidutinis gamybos ciklas 19,8 h, iš jo 13 % laiko partija tiesiog laukia eilėje.",
   "Laukimas prieš šaldymą: 2026 m. sausį 0,6 h, liepą 6,5 h, nes vasarą frizeriai perkrauti."
  ],
  "todo": "Vasarai planuoti papildomą pamainą prie frizerių arba dalį produkcijos pagaminti iš anksto, kol sezonas neprasidėjo.",
  "where": "„Procesas“",
  "dax": "[Atsakymas: procesas] =\nVAR e = SELECTEDVALUE(Atsakymai[Eilė])\nVAR Et = TOPN(1, VALUES('Partijų etapai'[Etapas]), [Vid. laukimas prieš etapą h], DESC)\nVAR EtP = MAXX(Et, 'Partijų etapai'[Etapas])\nVAR EtH = MAXX(Et, [Vid. laukimas prieš etapą h])\nVAR Cik = [Vid. gamybos ciklas h]\nVAR LD = [Laukimo dalis %]\nVAR Sau = CALCULATE([Laukimas prieš šaldymą h], DATESBETWEEN(Data[Data], DATE(2026, 1, 1), DATE(2026, 1, 31)))\nVAR Lie = CALCULATE([Laukimas prieš šaldymą h], DATESBETWEEN(Data[Data], DATE(2026, 7, 1), DATE(2026, 7, 31)))\nRETURN\n    SWITCH(\n        e,\n        1, \"Ilgiausiai partija laukia prieš etapą „\" & EtP & \"“: vidutiniškai \" & FORMAT(EtH, \"0.0\", \"lt-LT\") & \" h.\",\n        2, \"Vidutinis gamybos ciklas \" & FORMAT(Cik, \"0.0\", \"lt-LT\") & \" h, iš jo \" & FORMAT(LD, \"0 %\", \"lt-LT\") & \" laiko partija tiesiog laukia eilėje.\",\n        3, \"Laukimas prieš šaldymą: 2026 m. sausį \" & FORMAT(Sau, \"0.0\", \"lt-LT\") & \" h, liepą \" & FORMAT(Lie, \"0.0\", \"lt-LT\") & \" h, nes vasarą frizeriai perkrauti.\",\n        6, \"Vasarai planuoti papildomą pamainą prie frizerių arba dalį produkcijos pagaminti iš anksto, kol sezonas neprasidėjo.\",\n        7, \"Puslapis „Procesas“.\"\n    )\nisHidden"
 },
 {
  "q": "Kas gavo partiją ir iš ko ji pagaminta?",
  "title": "Partija P26-001885 · KAR KAR šerbetas mangų 500 ml · 2026-07-17 atsekta 100 %.",
  "points": [
   "Pagaminta 8 458 vnt., brokas 157, išsiųsta 8 301, sandėlyje liko 0 vnt.",
   "Gavo 6 klientai: Lidl Lietuva 3 021, Lidl Latvija 1 348, Tesco UK 1 290, Vietiniai prekybos tinklai 1 249, Costco UK 779, HoReCa ir didmena 614.",
   "Žaliavos iš 3 tiekėjų sąskaitų: CT26-0027 (Cukrus), SP26-0027 (Pakuotės ir etiketės), FV/OS/26-0027 (Uogų ir vaisių tyrė).",
   "Šiai partijai užregistruota skundų: 1 (Svetimkūnis)."
  ],
  "todo": "Jei reikia atšaukti, informuoti šiuos klientus ir paprašyti tiekėjų partijų sertifikatų. Visa informacija gaunama iš karto, nereikia ieškoti penkiose sistemose.",
  "where": "„Atšaukimas“",
  "dax": "[Atsakymas: partija] =\nVAR e = SELECTEDVALUE(Atsakymai[Eilė])\nVAR Pav = SELECTEDVALUE(Partija[Partija paieškai])\nVAR Pag = SUM(Partija[Pagaminta vnt])\nVAR Br = SUM(Partija[Brokas vnt])\nVAR Isv = [Išsiųsta vnt]\nVAR Lik = [Atšaukimas: likutis sandėlyje vnt]\nVAR Ats = [Atšaukimas: atsekta %]\nVAR KlSk = [Atšaukimas: klientų sk.]\nVAR Kl =\n    CONCATENATEX(\n        FILTER(VALUES(Klientas[Klientas]), [Išsiųsta vnt] > 0),\n        Klientas[Klientas] & \" \" & FORMAT([Išsiųsta vnt], \"#,0\", \"lt-LT\"),\n        \", \",\n        [Išsiųsta vnt], DESC\n    )\nVAR Tsk = [Atšaukimas: tiekėjų sąskaitų sk.]\nVAR Sas =\n    CONCATENATEX(\n        SUMMARIZE('Žaliavų sunaudojimas', 'Žaliavų sunaudojimas'[Tiekėjo sąskaita], 'Žaliava'[Žaliava]),\n        'Žaliavų sunaudojimas'[Tiekėjo sąskaita] & \" (\" & 'Žaliava'[Žaliava] & \")\",\n        \", \"\n    )\nVAR Sk = [Skundų sk.]\nVAR SkT = CONCATENATEX(VALUES(Skundai[Tipas]), Skundai[Tipas], \", \")\nRETURN\n    IF(\n        NOT HASONEVALUE(Partija[Partijos nr]),\n        IF(e = 1, \"Pasirink vieną partiją paieškos laukelyje dešinėje (pvz. P26-001885).\"),\n        SWITCH(\n            e,\n            1, \"Partija \" & Pav & \" atsekta \" & FORMAT(Ats, \"0 %\", \"lt-LT\") & \".\",\n            2, \"Pagaminta \" & FORMAT(Pag, \"#,0\", \"lt-LT\") & \" vnt., brokas \" & FORMAT(Br, \"#,0\", \"lt-LT\") & \", išsiųsta \" & FORMAT(Isv, \"#,0\", \"lt-LT\") & \", sandėlyje liko \" & FORMAT(Lik, \"#,0\", \"lt-LT\") & \" vnt.\",\n            3, \"Gavo \" & KlSk & \" klientai: \" & Kl & \".\",\n            4, \"Žaliavos iš \" & Tsk & \" tiekėjų sąskaitų: \" & Sas & \".\",\n            5, IF(Sk > 0, \"Šiai partijai užregistruota skundų: \" & Sk & \" (\" & SkT & \").\", \"Skundų šiai partijai neužregistruota.\"),\n            6, \"Jei reikia atšaukti, informuoti šiuos klientus ir paprašyti tiekėjų partijų sertifikatų. Visa informacija gaunama iš karto, nereikia ieškoti penkiose sistemose.\",\n            7, \"Puslapis „Atšaukimas“.\"\n        )\n    )\nisHidden"
 },
 {
  "q": "Kiek laiko ir pinigų sutaupo DI sąskaitoms?",
  "title": "DI apdorotos tiekėjų sąskaitos: 27. Automatiškai patvirtinta 85 %, žmogui patikrinti nukreipta: 4.",
  "points": [
   "Laikas: 1,4 min. su DI vietoje maždaug 108 min. rankomis.",
   "Kaina: 0,60 $, t. y. apie 0,02 $ už sąskaitą.",
   "Patikra su žinomais atsakymais: 378 iš 378 laukų teisingi, pagauti visi 6 „spąstai“ (nuolaida eilutėje, skenuota kopija, kita valiuta, dublikatas, nesutampanti suma, paslėpta instrukcija DI)."
  ],
  "todo": "Pradėti nuo vieno tiekėjo: pirmą mėnesį DI dirba lygiagrečiai su žmogumi, ir rezultatai lyginami.",
  "where": "„Duomenų kokybė ir DI“",
  "dax": "[Atsakymas: DI] =\nVAR e = SELECTEDVALUE(Atsakymai[Eilė])\nVAR N = [DI apdorota sąskaitų]\nVAR A = [DI automatizavimo lygis %]\nVAR P = [DI atiduota peržiūrai]\nVAR T = [DI laikas min]\nVAR R = [Rankinio darbo laikas min]\nVAR K = [DI kaina USD]\nRETURN\n    SWITCH(\n        e,\n        1, \"DI apdorotos tiekėjų sąskaitos: \" & FORMAT(N, \"#,0\", \"lt-LT\") & \". Automatiškai patvirtinta \" & FORMAT(A, \"0 %\", \"lt-LT\") & \", žmogui patikrinti nukreipta: \" & FORMAT(P, \"#,0\", \"lt-LT\") & \".\",\n        2, \"Laikas: \" & FORMAT(T, \"0.0\", \"lt-LT\") & \" min. su DI vietoje maždaug \" & FORMAT(R, \"#,0\", \"lt-LT\") & \" min. rankomis.\",\n        3, \"Kaina: \" & FORMAT(K, \"0.00\", \"lt-LT\") & \" $, t. y. apie \" & FORMAT(DIVIDE(K, N), \"0.00\", \"lt-LT\") & \" $ už sąskaitą.\",\n        4, \"Patikra su žinomais atsakymais: 378 iš 378 laukų teisingi, pagauti visi 6 „spąstai“ (nuolaida eilutėje, skenuota kopija, kita valiuta, dublikatas, nesutampanti suma, paslėpta instrukcija DI).\",\n        6, \"Pradėti nuo vieno tiekėjo: pirmą mėnesį DI dirba lygiagrečiai su žmogumi, ir rezultatai lyginami.\",\n        7, \"Puslapis „Duomenų kokybė ir DI“.\"\n    )\nisHidden"
 },
 {
  "q": "Ar galima pasitikėti šiais duomenimis?",
  "title": "Taip, nes prieš patenkant į ataskaitą duomenys patikrinami 10 taisyklėmis.",
  "points": [
   "Pašalinta dublikatų: 58. Sutvarkyta kliento kodų: 81, plano kodų: 53 (ERP ir planuotojo Excel kodai skiriasi).",
   "Partijos numeris įvestas kitu formatu: laboratorijoje 658 k., skundų registre 13 k. Sutvarkyta automatiškai.",
   "Automatiškai nesutvarkyta: eilutės be kliento kodo (28) ir nerasti plano kodai (0). Jos rodomos atskirai, kad žmogus patikrintų."
  ],
  "todo": "Tikroje įmonėje pirmiausia sulyginti ataskaitos sumas su finansų skyriaus skaičiais ir tik tada rodyti vadovams.",
  "where": "„Duomenų kokybė ir DI“",
  "dax": "[Atsakymas: duomenys] =\nVAR e = SELECTEDVALUE(Atsakymai[Eilė])\nVAR Np = COUNTROWS('Kokybės patikros')\nVAR Dub = [Pašalinta dublikatų]\nVAR Kk = [Sutvarkyta kliento kodų]\nVAR Bk = [Be kliento kodo]\nVAR Pk = [Sutvarkyta plano kodų]\nVAR Nk = [Nerasta plano kodų]\nVAR Lab = [Lab nr. kitu formatu]\nVAR SkN = [Skundo nr. kitu formatu]\nRETURN\n    SWITCH(\n        e,\n        1, \"Taip, nes prieš patenkant į ataskaitą duomenys patikrinami \" & Np & \" taisyklėmis.\",\n        2, \"Pašalinta dublikatų: \" & FORMAT(Dub, \"#,0\", \"lt-LT\") & \". Sutvarkyta kliento kodų: \" & FORMAT(Kk, \"#,0\", \"lt-LT\") & \", plano kodų: \" & FORMAT(Pk, \"#,0\", \"lt-LT\") & \" (ERP ir planuotojo Excel kodai skiriasi).\",\n        3, \"Partijos numeris įvestas kitu formatu: laboratorijoje \" & FORMAT(Lab, \"#,0\", \"lt-LT\") & \" k., skundų registre \" & FORMAT(SkN, \"#,0\", \"lt-LT\") & \" k. Sutvarkyta automatiškai.\",\n        4, \"Automatiškai nesutvarkyta: eilutės be kliento kodo (\" & FORMAT(Bk, \"#,0\", \"lt-LT\") & \") ir nerasti plano kodai (\" & FORMAT(Nk, \"#,0\", \"lt-LT\") & \"). Jos rodomos atskirai, kad žmogus patikrintų.\",\n        6, \"Tikroje įmonėje pirmiausia sulyginti ataskaitos sumas su finansų skyriaus skaičiais ir tik tada rodyti vadovams.\",\n        7, \"Puslapis „Duomenų kokybė ir DI“.\"\n    )\nisHidden"
 }
];
