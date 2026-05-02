"""Generuje lekce/programy/*.md pro každý soubor v programy/ a aktualizuje mkdocs.yml + lekce/index.md."""

import re
from pathlib import Path

ROOT = Path(__file__).parent
PROGRAMY_DIR = ROOT / "programy"
LEKCE_DIR = ROOT / "lekce"
OUT_DIR = LEKCE_DIR / "programy"
MKDOCS = ROOT / "mkdocs.yml"

OUT_DIR.mkdir(exist_ok=True)


def lekce_nazev(cislo: int) -> str:
    """Přečte první nadpis z lekce markdown souboru."""
    candidates = (
        list(LEKCE_DIR.glob(f"{cislo:02d}_*.md"))
        + list(LEKCE_DIR.glob(f"{cislo:03d}_*.md"))
        + list(LEKCE_DIR.glob(f"{cislo}_*.md"))
    )
    for f in candidates:
        if f.parent == LEKCE_DIR:  # jen přímé soubory, ne podsložky
            lines = f.read_text(encoding="utf-8").splitlines()
            for line in lines:
                if line.startswith("# "):
                    return line[2:].strip()
    return f"Lekce {cislo}"


def render_py(path: Path) -> str:
    code = path.read_text(encoding="utf-8")
    ext = path.suffix.lstrip(".")
    return f"### `{path.name}`\n\n```{ext}\n{code}\n```\n"


def render_toml(path: Path) -> str:
    code = path.read_text(encoding="utf-8")
    return f"### `{path.name}`\n\n```toml\n{code}\n```\n"


def generate_page(cislo: int, slug: str, nazev: str, source_path: Path) -> tuple[str, str]:
    """Vrátí (soubor_v_out_dir, obsah_markdown)."""
    out_name = f"l{cislo:02d}_{slug}.md" if cislo < 100 else f"l{cislo}_{slug}.md"
    lekce_link = f"../{ cislo:02d}_{slug}.md" if cislo < 10 else None

    # Najdi slug lekce souboru
    lekce_candidates = (
        list(LEKCE_DIR.glob(f"{cislo:02d}_*.md"))
        + list(LEKCE_DIR.glob(f"{cislo:03d}_*.md"))
        + list(LEKCE_DIR.glob(f"{cislo}_*.md"))
    )
    lekce_file = next((f for f in lekce_candidates if f.parent == LEKCE_DIR), None)
    lekce_rel = f"../{lekce_file.name}" if lekce_file else None

    header = f"# Program — Lekce {cislo}: {nazev}\n\n"
    if lekce_rel:
        header += f"Patří k lekci [{nazev}]({lekce_rel}).\n\n"

    header += "## Jak spustit\n\n"
    if source_path.is_dir():
        header += f"```bash\npython3 programy/{source_path.name}/<soubor>.py\n```\n\n"
    else:
        header += f"```bash\npython3 programy/{source_path.name}\n```\n\n"

    header += "## Zdrojový kód\n\n"

    if source_path.is_file():
        body = render_py(source_path)
    else:
        # Složka — projdi všechny soubory
        parts = []
        for f in sorted(source_path.iterdir()):
            if f.name.startswith("__pycache__"):
                continue
            if f.suffix == ".py":
                parts.append(render_py(f))
            elif f.suffix == ".toml":
                parts.append(render_toml(f))
        body = "\n".join(parts)

    return out_name, header + body


def parse_programy():
    """Vrátí seřazený seznam (cislo, slug, source_path)."""
    items = []
    for entry in PROGRAMY_DIR.iterdir():
        if entry.name.startswith("__"):
            continue
        m = re.match(r"^l(\d+)_(.*)", entry.stem if entry.is_file() else entry.name)
        if not m:
            continue
        cislo = int(m.group(1))
        slug = m.group(2)
        if entry.suffix in (".py", "") or entry.is_dir():
            items.append((cislo, slug, entry))
    return sorted(items, key=lambda x: x[0])


def main():
    items = parse_programy()
    print(f"Nalezeno {len(items)} programů")

    nav_entries = []
    for cislo, slug, source in items:
        nazev = lekce_nazev(cislo)
        out_name, content = generate_page(cislo, slug, nazev, source)
        out_path = OUT_DIR / out_name
        out_path.write_text(content, encoding="utf-8")
        # Sanitize label: remove backticks and double quotes (YAML unsafe)
        safe_nazev = re.sub(r'[`"\']', "", nazev)
        label = f"L{cislo:03d} · {safe_nazev}" if cislo >= 100 else f"L{cislo:02d} · {safe_nazev}"
        nav_entries.append(f'    - "{label}": programy/{out_name}')
        print(f"  ✅ {out_name}")

    # Přidej nebo nahraď sekci Programy v mkdocs.yml
    mkdocs_text = MKDOCS.read_text(encoding="utf-8")

    new_section = (
        '\n  - "Programy":\n'
        '    - "Rozcestník": programy/index.md\n'
        + "\n".join(nav_entries)
        + "\n"
    )

    # Odstraň existující sekci Programy, pokud existuje
    mkdocs_text = re.sub(
        r'\n  - "Programy":.*?(?=\n  - "|\Z)',
        "",
        mkdocs_text,
        flags=re.DOTALL,
    )

    mkdocs_text = mkdocs_text.rstrip() + new_section
    MKDOCS.write_text(mkdocs_text, encoding="utf-8")
    print(f"\nmkdocs.yml aktualizován — {len(nav_entries)} položek přidáno")

    # Vygeneruj index.md pro programy
    index_rows = []
    for cislo, slug, source in items:
        nazev = lekce_nazev(cislo)
        out_name = f"l{cislo:02d}_{slug}.md" if cislo < 100 else f"l{cislo}_{slug}.md"
        kind = "složka" if source.is_dir() else "soubor"
        src_name = source.name
        index_rows.append(f"| [{cislo}]({out_name}) | {nazev} | `{src_name}` |")

    index_content = (
        "# Zdrojové kódy programů\n\n"
        "Ke každé lekci patří spustitelný Python program.\n\n"
        "| # | Lekce | Soubor |\n"
        "|---|-------|--------|\n"
        + "\n".join(index_rows)
        + "\n"
    )
    (OUT_DIR / "index.md").write_text(index_content, encoding="utf-8")
    print("  ✅ programy/index.md")

    # Aktualizuj počet lekcí v lekce/index.md
    aktualizuj_web_index(len(items))


def aktualizuj_web_index(pocet_lekci: int) -> None:
    """Aktualizuje počet lekcí a programů v lekce/index.md."""
    index_path = LEKCE_DIR / "index.md"
    if not index_path.exists():
        print("  ⚠  lekce/index.md neexistuje, přeskočeno")
        return

    text = index_path.read_text(encoding="utf-8")

    # Nahraď řádek s počtem lekcí (vzor: **NNN lekcí · NNN programů · ...)
    novy_radek = f"**{pocet_lekci} lekcí · {pocet_lekci} programů · 14 mini-projektů**"
    text_new = re.sub(
        r"\*\*\d+ lekcí · \d+ programů · \d+ mini-projektů\*\*",
        novy_radek,
        text,
    )

    if text_new == text:
        print("  ℹ  lekce/index.md — počet lekcí beze změny")
        return

    index_path.write_text(text_new, encoding="utf-8")
    print(f"  ✅ lekce/index.md — aktualizováno na {pocet_lekci} lekcí")


if __name__ == "__main__":
    main()
