# Pirmos 90 dienų: kaip pradėčiau

Planą sudariau pagal skelbimą ir viešą informaciją apie įmonę. Ko nežinau, pažymėjau. Pirmos dvi savaitės skirtos patikrinti, ar mano prielaidos teisingos.

## Kodėl laikas palankus

Jei pradėčiau gruodį ar sausį, 90 dienų baigtųsi kovą. Tai ne sezonas: yra laiko ramiai sujungti duomenis ir patikrinti skaičius su finansais. Be to, iki gegužės, kai ledų paklausa pradeda kilti, planuotojas jau turėtų orų pataisą ir galėtų ją išbandyti pirmą sezoną. Pavyzdyje ji pagerino vasaros prognozės tikslumą nuo 88,1 % iki 94,8 % (sintetiniai duomenys, todėl tikras rezultatas bus kitoks, žr. README).

## Ką darau ir kada

### 1–2 savaitės: klausau ir surašau

- Pasikalbu su žmonėmis, kurie dabar ruošia ataskaitas rankomis: planuotoju, finansininku, pardavimų vadybininkais, kokybės specialistu, sandėliu. Kiekvieno klausiu: kokią ataskaitą darai, kiek laiko užtrunka, iš kur imi duomenis, kas ją skaito, kokio sprendimo pagal ją imamasi.
- Surašau visus duomenų šaltinius: ERP lenteles (skelbime programuotojui minimas PHP + SQL/Oracle), Excel failus, laboratorijos sistemą, sandėlį.
- Su ERP programuotoju susitariu dėl prieigos tik skaitymui (atskiras DB naudotojas arba rodiniai), kad Power BI niekada neapkrautų ir nekeistų ERP.

**Rezultatas:** ataskaitų žemėlapis (kas, ką, kiek valandų per mėnesį) ir sąrašas darbų, surikiuotas pagal sutaupytas valandas. Iš jo išrenku 2–3 greitus laimėjimus pirmam mėnesiui.

### 3–6 savaitės: vienas modelis, kuriuo pasitiki finansai

- Pirmas Power BI modelis: pardavimai, gamyba ir planuotojo Excel planas. Atnaujinimas kasdien per duomenų vartus (on-premises data gateway).
- Kiekvieną skaičių sulyginu su ERP ir finansų ataskaita iki euro. Kol finansininkas nepatvirtina, ataskaitos neplatinu. Jei skaičiai nesutampa su tuo, kas jau naudojama, žmonės grįš prie Excel.
- Duomenų kokybės patikros kaip pavyzdyje: dublikatai, neatpažinti kodai, trūkstami klientai. Jos rodomos atskirame puslapyje, o ne taisomos tyliai.
- Prieigos (RLS): vadybininkas mato savo tinklus, vadovybė viską.

**Rezultatas:** vadovybės apžvalga ir „Kodėl?“ puslapis (pelno pokyčio skaidymas į kiekį, mix, kainas ir žaliavas), kuriuos finansai patvirtino.

### 7–10 savaičių: automatizavimas su žmogumi cikle

- **Sąskaitų nuskaitymas su DI**, pilotas su 2–3 tiekėjais. Dvi savaites DI ir žmogus dirba lygiagrečiai, palyginame kiekvieną lauką. Į ERP importuojame tik tada, kai tikslumas aiškus. Abejotinos sąskaitos (nesutampa sumos, kita valiuta, dublikatas, keistas tekstas dokumente) visada keliauja žmogui.
- **Mėnesio komentaras:** skriptas suskaičiuoja rodiklius, Claude parašo juodraštį, skriptas patikrina kiekvieną skaičių. Finansininkas peržiūri ir išsiunčia. Pavyzdys: [menesio_komentaras_2026-10.md](menesio_komentaras_2026-10.md).
- Kitos rankinės ataskaitos iš 1–2 savaičių sąrašo.

**Rezultatas:** išmatuota nauda valandomis per mėnesį ir DI tikslumas su tikromis sąskaitomis.

### 11–13 savaičių: pasiruošimas sezonui ir perdavimas

- **Orų pataisa planuotojui** su tikrais 2–3 metų duomenimis: patikra tokiu pat būdu kaip pavyzdyje (jautrumas skaičiuojamas iš ankstesnių metų, tikrinamas su vėlesniais). Rezultatas keliauja planuotojui į Excel jo įprastu formatu.
- **Atsekamumas:** jei įmonė sertifikuota pagal BRCGS ar IFS, bent kartą per metus reikia atsekamumo testo (BRCGS reikalauja jį atlikti per 4 val.). Partija → klientai → tiekėjų sąskaitos viename puslapyje šį testą sutrumpina iki kelių minučių. [KLAUSIMAS: koks sertifikatas ir kaip testas daromas dabar?]
- **Mokymai:** po valandą kiekvienam skyriui su jų pačių duomenimis, ne bendras Power BI kursas. Trumpas gidas „kaip rasti atsakymą į savo klausimą“.
- **Dokumentacija:** duomenų žodynas generuojamas iš modelio automatiškai ([duomenu_zodynas.md](duomenu_zodynas.md)), todėl neatsilieka nuo pakeitimų.

## Kaip matuosiu naudą

| Rodiklis | Kaip matuoju |
|---|---|
| Sutaupytos valandos per mėnesį | Pirmų savaičių žemėlapis prieš ir po |
| Kiek laiko užtrunka mėnesio ataskaita | Nuo mėnesio pabaigos iki išsiuntimo vadovybei |
| Prognozės tikslumas vasarą | 1 − Σ\|užsakyta − prognozė\| / Σ prognozė, savaitė × šalis × produktas |
| DI sąskaitų tikslumas | Laukų lygiu, lyginant su žmogaus suvestais duomenimis |
| Kiek žmonių naudojasi ataskaitomis | Power BI naudojimo ataskaita |

## Ko nedarysiu

- Nekeisiu ERP ir nerašysiu į jį tiesiogiai. Duomenys į ERP keliauja tik per importo failą, kurį priima esamas mechanizmas. [KLAUSIMAS: ar ERP turi importą, ar reikės programuotojo pagalbos?]
- Nenaudosiu DI finansiniams duomenims be patikros taisyklėmis ir be žmogaus abejotiniems atvejams.
- Nekursiu ataskaitos, kuri neturi savininko ir neatsako į konkretų klausimą.

## Ko man reikėtų iš įmonės

- Prieigos prie ERP duomenų tik skaitymui ir ERP programuotojo valandos per savaitę pirmą mėnesį.
- Power BI licencijų: bendrinamas ataskaitas kurti ir žiūrėti reikia Pro licencijos kiekvienam naudotojui, nebent įmonė turi Premium/Fabric talpą. [KLAUSIMAS: ar įmonė jau turi Microsoft 365 ir Power BI?]
- Sprendimo dėl DI paslaugų: kokius dokumentus galima siųsti išorės API. Claude API pagal komercines sąlygas klientų duomenų nenaudoja modeliams mokyti, bet tai turi patvirtinti įmonės atsakingas asmuo.
