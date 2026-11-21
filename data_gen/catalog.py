# Sintetinio pavyzdžio katalogas. Pavadinimai tikri (DIONE, KAR KAR, tinklai), visi skaičiai išgalvoti.
# Tiekėjai išgalvoti.
from dataclasses import dataclass, field

SUPPLIERS = [
    # kodas, pavadinimas, šalis, PVM kodas, valiuta, pristatymo dažnis savaitėmis
    ("T01", "UAB „Nemuno slėnio pienas“", "LT", "LT999100011", "EUR", 1),
    ("T02", "UAB „Kuršių grietinėlė“", "LT", "LT999100022", "EUR", 1),
    ("T03", "UAB „Cukraus taškas“", "LT", "LT999100033", "EUR", 1),
    ("T04", "SIA „Rīgas kakao“", "LV", "LV40009990044", "EUR", 2),
    ("T05", "UAB „Vaflių meistrai“", "LT", "LT999100055", "EUR", 1),
    ("T06", "Owocowy Sad Sp. z o.o.", "PL", "PL9990006600", "EUR", 1),
    ("T07", "UAB „Šaldo pakuotės“", "LT", "LT999100077", "EUR", 1),
]

# kodas, pavadinimas, matas, bazinė kaina €/mato vnt., tiekėjas, pakuotės dydis užsakant
MATERIALS = [
    ("Z-PIEN", "Pienas 3,5 %", "l", 0.42, "T01", 1000),
    ("Z-GRIE", "Grietinėlė 35 %", "kg", 3.10, "T02", 20),
    ("Z-CUKR", "Cukrus", "kg", 0.85, "T03", 50),
    ("Z-KAKA", "Kakavos milteliai", "kg", 7.80, "T04", 25),
    ("Z-SOKO", "Šokolado glajus", "kg", 6.20, "T04", 25),
    ("Z-VAFL", "Vafliniai rageliai", "vnt", 0.045, "T05", 1000),
    ("Z-UOGA", "Uogų ir vaisių tyrė", "kg", 2.90, "T06", 20),
    ("Z-PAKU", "Pakuotės ir etiketės", "vnt", 0.035, "T07", 5000),
]

# kodas, gamykla, linija, prieinamos minutės per savaitę
LINES = [
    ("KLA-L1", "Klaipėda", "Pagaliukų linija", 4800),
    ("KLA-L2", "Klaipėda", "Ragelių linija", 4800),
    ("KLA-L3", "Klaipėda", "Šeimos pakuočių linija", 4800),
    ("KRE-L1", "Kretinga", "Vaikiškų ledų linija", 4800),
    ("KRE-L2", "Kretinga", "Puodelių linija", 4800),
    ("GAR-L1", "Gargždai", "Šerbetų ir tortų linija", 4800),
]

# kodas, pavadinimas, šalis, rinka, vadybininko rolė (RLS), apimties svoris, kainos nuolaida, ar tinklas daro akcijas
CUSTOMERS = [
    ("C01", "Lidl Lietuva", "LT", "Baltijos šalys", "Baltijos šalių vadybininkas", 0.22, 0.04, True),
    ("C02", "Lidl Latvija", "LV", "Baltijos šalys", "Baltijos šalių vadybininkas", 0.08, 0.04, True),
    ("C03", "Lidl Eesti", "EE", "Baltijos šalys", "Baltijos šalių vadybininkas", 0.06, 0.04, True),
    ("C04", "Kaufland Polska", "PL", "Centrinė Europa", "Eksporto vadybininkas (DE/PL)", 0.10, 0.06, False),
    ("C05", "Kaufland Deutschland", "DE", "Centrinė Europa", "Eksporto vadybininkas (DE/PL)", 0.12, 0.06, False),
    ("C06", "Tesco UK", "GB", "Jungtinė Karalystė", "Eksporto vadybininkas (UK)", 0.14, 0.05, False),
    ("C07", "Costco UK", "GB", "Jungtinė Karalystė", "Eksporto vadybininkas (UK)", 0.08, 0.08, False),
    ("C08", "Vietiniai prekybos tinklai", "LT", "Baltijos šalys", "Baltijos šalių vadybininkas", 0.14, 0.00, False),
    ("C09", "HoReCa ir didmena", "LT", "Baltijos šalys", "Baltijos šalių vadybininkas", 0.06, 0.02, False),
]

# Receptas 1 litrui produkto (kg arba l). Pakuotės ir rageliai skaičiuojami vienetais, ne litrais.
RECIPES_PER_LITRE = {
    "Plombyras puodelyje": {"Z-PIEN": 0.45, "Z-GRIE": 0.30, "Z-CUKR": 0.16},
    "Ledai ant pagaliuko": {"Z-PIEN": 0.50, "Z-GRIE": 0.22, "Z-CUKR": 0.16, "Z-SOKO": 0.18},
    "Ledai su vafliu": {"Z-PIEN": 0.50, "Z-GRIE": 0.22, "Z-CUKR": 0.16, "Z-SOKO": 0.05},
    "Šeimos pakuotė": {"Z-PIEN": 0.55, "Z-GRIE": 0.20, "Z-CUKR": 0.15},
    "Vaikiški ledai": {"Z-PIEN": 0.60, "Z-GRIE": 0.10, "Z-CUKR": 0.18, "Z-UOGA": 0.05},
    "Šerbetas": {"Z-CUKR": 0.25, "Z-UOGA": 0.35},
    "Ledų tortas": {"Z-PIEN": 0.40, "Z-GRIE": 0.32, "Z-CUKR": 0.15, "Z-SOKO": 0.08},
}

# kategorija: (prekės ženklas, tūris ml, kaina €/vnt, linija, pakuočių vnt., ar naudoja ragelį, sezoniškumo profilis)
CATEGORIES = {
    "Plombyras puodelyje": ("DIONE", 120, 0.55, "KRE-L2", 1, False, "vasara"),
    "Ledai ant pagaliuko": ("DIONE", 80, 0.65, "KLA-L1", 1, False, "vasara"),
    "Ledai su vafliu": ("KAR KAR", 110, 0.75, "KLA-L2", 1, True, "vasara"),
    "Šeimos pakuotė": ("DIONE", 1000, 2.90, "KLA-L3", 4, False, "vasara"),
    "Vaikiški ledai": ("KAR KAR", 60, 0.40, "KRE-L1", 1, False, "vasara"),
    "Šerbetas": ("KAR KAR", 500, 1.90, "GAR-L1", 3, False, "vasara"),
    "Ledų tortas": ("DIONE", 900, 4.90, "GAR-L1", 6, False, "sventes"),
}

# kategorija -> [(skonis, plano kodo dalis, bazinė savaitės paklausa vnt., ar šokoladinis)]
FLAVOURS = {
    "Plombyras puodelyje": [("vanilinis", "VAN", 30000, False), ("šokoladinis", "SOK", 18000, True),
                            ("braškinis", "BRA", 14000, False), ("karamelinis", "KAR", 10000, False)],
    "Ledai ant pagaliuko": [("vanilė šokolade", "VAN", 16000, False), ("karamelė šokolade", "KAR", 11000, False),
                            ("kokosas šokolade", "KOK", 7000, False)],
    "Ledai su vafliu": [("vanilinis", "VAN", 15000, False), ("šokoladinis", "SOK", 11000, True),
                        ("braškinis", "BRA", 8000, False), ("pistacijų", "PIS", 5000, False)],
    "Šeimos pakuotė": [("vanilinis", "VAN", 6000, False), ("šokoladinis", "SOK", 4500, True),
                       ("su razinomis", "RAZ", 2500, False), ("mėtinis", "MET", 1800, False)],
    "Vaikiški ledai": [("braškių", "BRA", 12000, False), ("bananų", "BAN", 8000, False),
                       ("spalvotas", "SPA", 7000, False)],
    "Šerbetas": [("citrinų", "CIT", 2500, False), ("mangų", "MAN", 2200, False), ("aviečių", "AVI", 1800, False)],
    "Ledų tortas": [("vanilės ir šokolado", "VSO", 1200, True), ("braškių", "BRA", 800, False),
                    ("karamelės", "KAR", 700, False)],
}

CATEGORY_CODES = {
    "Plombyras puodelyje": "PLO", "Ledai ant pagaliuko": "ESK", "Ledai su vafliu": "RAG",
    "Šeimos pakuotė": "SEI", "Vaikiški ledai": "VAI", "Šerbetas": "SER", "Ledų tortas": "TOR",
}


@dataclass
class Product:
    sku: str
    plan_code: str
    name: str
    brand: str
    category: str
    volume_ml: int
    list_price: float
    line: str
    base_weekly: float
    season: str
    recipe: dict = field(default_factory=dict)  # žaliavos kodas -> kiekis vienetui


def build_products() -> list[Product]:
    products = []
    number = 100100
    for category, flavours in FLAVOURS.items():
        brand, volume, price, line, pack_units, uses_wafer, season = CATEGORIES[category]
        for flavour, code, base, chocolate in flavours:
            number += 1
            litres = volume / 1000
            recipe = {m: round(q * litres, 5) for m, q in RECIPES_PER_LITRE[category].items()}
            if chocolate:
                recipe["Z-KAKA"] = round(0.03 * litres, 5)
            if uses_wafer:
                recipe["Z-VAFL"] = 1
            recipe["Z-PAKU"] = pack_units
            brand_code = "DIO" if brand == "DIONE" else "KKR"
            products.append(Product(
                sku=str(number),
                plan_code=f"{brand_code}-{CATEGORY_CODES[category]}-{code}-{volume}",
                name=f"{brand} {category.lower()} {flavour} {volume} ml",
                brand=brand, category=category, volume_ml=volume, list_price=price,
                line=line, base_weekly=base, season=season, recipe=recipe,
            ))
    return products
