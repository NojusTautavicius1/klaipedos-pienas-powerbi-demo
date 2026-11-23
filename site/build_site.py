"""Paruošia pristatymo puslapio failus (site/).

1. Power BI Desktop ekrano nuotraukas apkarpo iki ataskaitos drobės → site/img/pbi/<puslapis>.png
2. Nukopijuoja README diagramas → site/img/
3. Iš „Klausk“ atsakymų (DAX užklausos rezultatas JSON) ir TMDL matų sudaro site/qa.js

Paleisti:  python site/build_site.py --shots <aplankas su PNG> --qa <qa.json>
qa.json gaunamas DAX užklausa atidarytame modelyje:
  EVALUATE SUMMARIZECOLUMNS(Atsakymai[Nr], Atsakymai[Klausimas], Atsakymai[Eilė], Atsakymai[Eilutė], ..., "A", [Atsakymas])
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
TMDL = ROOT / "powerbi" / "KlaipedosPienas.SemanticModel" / "definition" / "tables" / "_Matai.tmdl"
SLUGS = ["virselis", "klausk", "apzvalga", "kodel", "planavimas", "gamyba", "procesas",
         "kokybe", "atsaukimas", "pardavimai", "di"]
# Klausimo nr → matas, kuris skaičiuoja atsakymą (kurti_klausk.py)
MEASURES = {1: "metai", 2: "trūkumai", 3: "marža", 4: "karštis", 5: "kokybė",
            6: "procesas", 7: "partija", 8: "DI", 9: "duomenys"}


def page_name(key: str) -> str:
    return hashlib.md5(key.encode()).hexdigest()[:20]


def crop_canvas(src: Path, dst: Path) -> None:
    im = Image.open(src).convert("RGB")
    w, h = im.size
    y_mid = h // 2
    # drobės fonas: pirmas taškas iš kairės, kurio spalva sutampa su ataskaitos fonu
    left = next(x for x in range(30, w // 2) if im.getpixel((x, y_mid)) == (243, 246, 249))
    bg = im.getpixel((left + 4, y_mid))
    col = left + 4
    top = next(y for y in range(100, h) if im.getpixel((col, y)) == bg)
    bottom = top
    for y in range(top, h):
        if im.getpixel((col, y)) == bg:
            bottom = y
    right = left
    for x in range(left, w):
        if im.getpixel((x, top + 3)) == bg:
            right = x
    box = (left, top, right + 1, bottom + 1)
    out = im.crop(box)
    out.save(dst, optimize=True)
    print(f"{dst.name}: {out.size[0]}x{out.size[1]}")


def measure_dax(name: str) -> str:
    text = TMDL.read_text(encoding="utf-8")
    m = re.search(rf"\tmeasure '{re.escape(name)}' =\n(.*?)\n\t\t(?:formatString|displayFolder|lineageTag)",
                  text, re.S)
    if not m:
        return ""
    lines = [ln[3:] if ln.startswith("\t\t\t") else ln.strip() for ln in m.group(1).splitlines()]
    return f"[{name}] =\n" + "\n".join(lines)


def build_qa(qa_json: Path) -> list[dict]:
    rows = json.loads(qa_json.read_text(encoding="utf-8-sig"))
    by_q: dict[int, dict] = {}
    for r in rows:
        v = list(r.values())
        nr, klausimas, eilute, tekstas = int(v[0]), v[1], v[3], v[4]
        q = by_q.setdefault(nr, {"q": klausimas, "title": "", "points": [], "todo": "", "where": ""})
        if not tekstas:
            continue
        if eilute == "Atsakymas":
            q["title"] = tekstas
        elif eilute == "Ką daryti":
            q["todo"] = tekstas
        elif eilute == "Kur žiūrėti":
            q["where"] = tekstas.removeprefix("Puslapis ").removeprefix("Puslapiai ").rstrip(".")
        else:
            q["points"].append(tekstas)
    out = []
    for nr in sorted(by_q):
        q = by_q[nr]
        q["dax"] = measure_dax(f"Atsakymas: {MEASURES[nr]}")
        out.append(q)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", type=Path, required=True)
    ap.add_argument("--qa", type=Path, required=True)
    a = ap.parse_args()

    pbi = SITE / "img" / "pbi"
    pbi.mkdir(parents=True, exist_ok=True)
    for slug in SLUGS:
        src = a.shots / f"{page_name(slug)}.png"
        if src.exists():
            crop_canvas(src, pbi / f"{slug}.png")
        else:
            print(f"trūksta: {slug} ({src.name})")

    for f in (ROOT / "docs" / "img").glob("*.png"):
        shutil.copy2(f, SITE / "img" / f.name)

    qa = build_qa(a.qa)
    (SITE / "qa.js").write_text("window.QA = " + json.dumps(qa, ensure_ascii=False, indent=1) + ";\n",
                                encoding="utf-8")
    print(f"qa.js: {len(qa)} klausimai")


if __name__ == "__main__":
    main()
