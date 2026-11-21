# Video „Klausk duomenų“ (60–90 s): scenarijus

Tikslas: per minutę parodyti, kad Power BI modelis atsako ne tik „kiek“, bet ir „kodėl“, ir kad DI dirba su tikra įmonės duomenų struktūra.

## Pasiruošimas (5 min.)

1. Atidaryk `powerbi\KlaipedosPienas.pbip` Power BI Desktop. Puslapis „Procesas“ arba „Kodėl?“.
2. VS Code šiame aplanke atidaryk Claude Code (dešinėje pusėje). Šriftą padidink iki ~16 (`Ctrl` + `+`).
3. Ekranas: kairėje Power BI, dešinėje Claude Code (`Win` + `←` / `Win` + `→`).
4. Uždaryk pranešimus (Windows „Focus“ / „Netrukdyti“).
5. Repeticija: vieną kartą paleisk 1 klausimą be įrašymo, kad MCP prisijungtų ir neklaustų leidimų įraše. Leidimų lange pasirink „Always allow“ `powerbi-modeling` įrankiams.

## Įrašymas

- **Windows:** `Win` + `Alt` + `R` (Xbox Game Bar) įrašo aktyvų langą, bet ne visą ekraną. Visam ekranui naudok **Clipchamp** → „Įrašyti ekraną“ (yra Windows 11) arba OBS.
- **GIF README failui:** ScreenToGif (nemokamas), 10–12 kadrų/s, plotis ~1200 px.

## Kadrai

| Laikas | Ekrane | Užrašas ekrane (Clipchamp) |
|---|---|---|
| 0–5 s | Power BI apžvalga: matosi KPI ir „Sintetiniai duomenys“ | „Power BI + Claude: ataskaita, kuri atsako kodėl“ |
| 5–30 s | Claude Code: įvedi `/klausk-duomenu Kodėl 2026 m. birželį trūko DIONE puodelių?`. Matosi, kaip Claude rašo DAX ir gauna rezultatus | „Claude pats rašo DAX užklausas modeliui“ |
| 30–45 s | Atsakymas: karščio banga + KRE-L2 kompresorius + 381 tūkst. vnt. + 17 skundų | „Priežasčių grandinė per 4 sistemas: orai, gamyba, pardavimai, kokybė“ |
| 45–60 s | Power BI: „Oro scenarijus“ slankiklis ant +6 °C, prognozė su orais ≈ faktiniai užsakymai | „Su orų prognoze: 732 tūkst. vs tikra 734 tūkst.“ |
| 60–75 s (nebūtina) | `/klausk-duomenu Gavome skundą dėl svetimkūnio iš partijos P26-001885. Kas ją gavo?` | „BRC atšaukimo testas per vieną klausimą“ |
| pabaiga | README nuoroda / GitHub | „github.com/… · Sintetiniai duomenys, ne tikri įmonės skaičiai“ |

## Patarimai

- Claude atsakymą galima pagreitinti montuojant (Clipchamp → „Greitis“ 2×), bet rezultatų dalį palik normaliu greičiu, kad būtų galima perskaityti.
- Jei atsakymas skiriasi nuo [klausk_duomenu.md](klausk_duomenu.md), tai normalu, nes Claude kaskart rašo pats. Svarbu, kad skaičiai sutaptų.
- Įrašyk 2–3 bandymus ir pasirink geriausią.
