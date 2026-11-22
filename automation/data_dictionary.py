# Paleidimas: python automation/data_dictionary.py [--tmdl powerbi/modelio_kopija_tmdl]
# Duomenų žodynas sugeneruojamas iš paties modelio (TMDL failų), todėl dokumentacija niekada neatsilieka nuo modelio:
# pakeitei matą Power BI, išsaugojai PBIP, paleidai skriptą, ir docs/duomenu_zodynas.md atnaujintas.
# Lentelės, stulpeliai, ryšiai, RLS rolės ir visi matai su aprašymais ir DAX kodu.
import argparse
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME = r"'(?:[^']|'')+'|[^\s=]+"


def unquote(name: str) -> str:
    name = name.strip()
    return name[1:-1].replace("''", "'") if name.startswith("'") else name


def indent(line: str) -> int:
    return len(line) - len(line.lstrip("\t"))


def parse_table(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    table = {"name": None, "description": "", "columns": [], "measures": [], "hidden": False, "source": "M"}
    doc: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("///"):
            doc.append(stripped[3:].strip())
            i += 1
            continue
        if indent(line) == 0 and stripped.startswith("table "):
            table["name"] = unquote(stripped[6:])
            table["description"] = " ".join(doc)
        elif indent(line) == 1 and stripped.startswith("isHidden"):
            table["hidden"] = True
        elif indent(line) == 1 and stripped.startswith("partition ") and "= calculated" in stripped:
            table["source"] = "DAX"
        elif indent(line) == 1 and stripped.startswith("column "):
            m = re.match(rf"column ({NAME})", stripped)
            col = {"name": unquote(m.group(1)), "description": " ".join(doc), "type": "", "hidden": False,
                   "calculated": "=" in stripped[len(m.group(0)):]}
            j = i + 1
            while j < len(lines) and (indent(lines[j]) >= 2 or not lines[j].strip()):
                prop = lines[j].strip()
                if prop.startswith("dataType:"):
                    col["type"] = prop.split(":", 1)[1].strip()
                elif prop == "isHidden":
                    col["hidden"] = True
                j += 1
            table["columns"].append(col)
            i = j
            doc = []
            continue
        elif indent(line) == 1 and stripped.startswith("measure "):
            m = re.match(rf"measure ({NAME})\s*=\s*(.*)", stripped)
            measure = {"name": unquote(m.group(1)), "description": " ".join(doc), "folder": "", "format": "",
                       "expression": m.group(2).strip()}
            body = []
            j = i + 1
            while j < len(lines) and (indent(lines[j]) >= 3 or not lines[j].strip()):
                body.append(lines[j][3:] if lines[j].startswith("\t\t\t") else lines[j].strip())
                j += 1
            while j < len(lines) and (indent(lines[j]) == 2 or not lines[j].strip()):
                prop = lines[j].strip()
                if prop.startswith("displayFolder:"):
                    measure["folder"] = prop.split(":", 1)[1].strip()
                elif prop.startswith("formatString:"):
                    measure["format"] = prop.split(":", 1)[1].strip()
                j += 1
            if body:
                measure["expression"] = "\n".join(b for b in body).strip()
            table["measures"].append(measure)
            i = j
            doc = []
            continue
        doc = [] if not stripped.startswith("///") else doc
        i += 1
    return table


def parse_relationships(path: Path) -> list[dict]:
    rels, cur = [], None
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        s = line.strip()
        if s.startswith("relationship "):
            cur = {"active": True, "cross": "vienkryptis"}
            rels.append(cur)
        elif cur is not None and s.startswith("fromColumn:"):
            cur["from"] = s.split(":", 1)[1].strip()
        elif cur is not None and s.startswith("toColumn:"):
            cur["to"] = s.split(":", 1)[1].strip()
        elif cur is not None and s == "isActive: false":
            cur["active"] = False
        elif cur is not None and s.startswith("crossFilteringBehavior:"):
            cur["cross"] = "abikryptis"
    return rels


def parse_roles(folder: Path) -> list[dict]:
    roles = []
    for f in sorted(folder.glob("*.tmdl")):
        text = f.read_text(encoding="utf-8-sig")
        name = re.search(r"^role (.+)$", text, re.M).group(1)
        desc = " ".join(l.strip()[3:].strip() for l in text.splitlines() if l.strip().startswith("///"))
        filters = re.findall(r"tablePermission (.+)", text)
        roles.append({"name": unquote(name), "description": desc, "filters": filters})
    return roles


def col_ref(ref: str) -> str:
    table, _, column = ref.partition(".")
    return f"{unquote(table)}[{unquote(column)}]"


def build(tmdl: Path) -> str:
    tables = [parse_table(p) for p in sorted((tmdl / "tables").glob("*.tmdl"))]
    measures = [m for t in tables for m in t["measures"]]
    rels = parse_relationships(tmdl / "relationships.tmdl")
    roles = parse_roles(tmdl / "roles") if (tmdl / "roles").exists() else []
    data_tables = [t for t in tables if t["columns"] and not t["name"].startswith("_")]

    out = [
        "# Duomenų žodynas",
        "",
        "> Sugeneruota automatiškai iš Power BI modelio (`automation/data_dictionary.py`, šaltinis "
        f"`{tmdl.relative_to(ROOT).as_posix()}`). Rankomis neredaguoti: pakeisk modelį ir paleisk skriptą iš naujo.",
        "> Sintetiniai duomenys, mokomasis pavyzdys.",
        "",
        f"Modelyje: **{len(data_tables)} lentelės**, **{len(rels)} ryšiai**, **{len(measures)} matai**, "
        f"**{len(roles)} RLS rolės**.",
        "",
        "## Turinys",
        "",
        "- [Lentelės](#lentelės)",
        "- [Ryšiai](#ryšiai)",
        "- [Prieigos rolės (RLS)](#prieigos-rolės-rls)",
        "- [Matai pagal aplanką](#matai-pagal-aplanką)",
        "",
        "## Lentelės",
        "",
        "| Lentelė | Tipas | Stulpelių | Aprašymas |",
        "|---|---|---:|---|",
    ]
    for t in sorted(data_tables, key=lambda t: t["name"]):
        kind = "DAX (skaičiuojama)" if t["source"] == "DAX" else "Power Query"
        visible = [c for c in t["columns"] if not c["hidden"]]
        out.append(f"| **{t['name']}** | {kind} | {len(visible)} | {t['description'] or '–'} |")
    out.append("")
    for t in sorted(data_tables, key=lambda t: t["name"]):
        visible = [c for c in t["columns"] if not c["hidden"]]
        out += [f"### {t['name']}", "", t["description"] or "", "",
                "| Stulpelis | Tipas | Aprašymas |", "|---|---|---|"]
        for c in visible:
            extra = " (skaičiuojamas)" if c["calculated"] else ""
            out.append(f"| {c['name']} | {c['type']}{extra} | {c['description'] or ''} |")
        hidden = [c["name"] for c in t["columns"] if c["hidden"]]
        if hidden:
            out += ["", f"Paslėpti techniniai stulpeliai (raktai ryšiams): {', '.join(hidden)}."]
        out.append("")

    out += ["## Ryšiai", "", "Visi ryšiai „daug su vienu“ (faktų lentelė → dimensija).", "",
            "| Iš (faktai) | Į (dimensija) | Pastaba |", "|---|---|---|"]
    for r in rels:
        note = ", ".join(x for x in ("neaktyvus (USERELATIONSHIP)" if not r["active"] else "",
                                     r["cross"] if r["cross"] != "vienkryptis" else "") if x)
        out.append(f"| {col_ref(r['from'])} | {col_ref(r['to'])} | {note} |")

    out += ["", "## Prieigos rolės (RLS)", "", "| Rolė | Ką mato | Filtras |", "|---|---|---|"]
    for r in roles:
        out.append(f"| {r['name']} | {r['description']} | `{'; '.join(r['filters'])}` |")

    out += ["", "## Matai pagal aplanką", ""]
    by_folder = defaultdict(list)
    for m in measures:
        by_folder[m["folder"] or "(be aplanko)"].append(m)
    for folder in sorted(by_folder):
        out += [f"### {folder}", "", "| Matas | Formatas | Aprašymas |", "|---|---|---|"]
        for m in by_folder[folder]:
            fmt = m["format"].replace("|", "\\|")
            out.append(f"| `{m['name']}` | `{fmt}` | {m['description'] or ''} |" if fmt
                       else f"| `{m['name']}` | | {m['description'] or ''} |")
        out += ["", "<details><summary>DAX kodas</summary>", ""]
        for m in by_folder[folder]:
            out += [f"**{m['name']}**", "", "```dax", m["expression"], "```", ""]
        out += ["</details>", ""]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tmdl", default=str(ROOT / "powerbi" / "modelio_kopija_tmdl"))
    args = parser.parse_args()
    tmdl = Path(args.tmdl).resolve()
    target = ROOT / "docs" / "duomenu_zodynas.md"
    target.write_text(build(tmdl), encoding="utf-8")
    print(f"Išsaugota: {target}")


if __name__ == "__main__":
    main()
