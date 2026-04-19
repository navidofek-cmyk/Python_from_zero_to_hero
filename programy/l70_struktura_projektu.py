"""Lekce 70 — Struktura projektu, pyproject.toml."""

from __future__ import annotations

import pathlib
import tempfile
import textwrap


# ── Šablona moderní struktury projektu ───────────────────────────────────────

STRUKTURA = """
muj-projekt/
├── pyproject.toml           ← konfigurace (povinné)
├── README.md
├── LICENSE
├── .gitignore
├── src/
│   └── muj_projekt/
│       ├── __init__.py
│       ├── core.py
│       └── cli.py
├── tests/
│   ├── __init__.py
│   └── test_core.py
└── .venv/                   ← virtuální prostředí (gitignore)
"""

PYPROJECT_TOML = """\
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "muj-projekt"
version = "0.1.0"
description = "Ukázkový projekt"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
dependencies = [
    "httpx>=0.27",
]

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]

[project.scripts]
muj-cli = "muj_projekt.cli:main"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]

[tool.mypy]
strict = true
"""


# ── Generátor struktury projektu ─────────────────────────────────────────────

def vytvor_projekt(zakladni_adresar: pathlib.Path, nazev: str) -> pathlib.Path:
    root = zakladni_adresar / nazev
    src_pkg = root / "src" / nazev.replace("-", "_")
    tests = root / "tests"

    for adresar in [src_pkg, tests]:
        adresar.mkdir(parents=True, exist_ok=True)

    # pyproject.toml
    (root / "pyproject.toml").write_text(
        PYPROJECT_TOML.replace("muj-projekt", nazev)
                      .replace("muj_projekt", nazev.replace("-", "_"))
    )

    # README
    (root / "README.md").write_text(f"# {nazev}\n\nPopis projektu.\n")

    # .gitignore
    (root / ".gitignore").write_text(textwrap.dedent("""\
        .venv/
        __pycache__/
        dist/
        *.egg-info/
        .mypy_cache/
        .ruff_cache/
        .pytest_cache/
    """))

    # src balíček
    (src_pkg / "__init__.py").write_text(f'"""Balíček {nazev}."""\n\n__version__ = "0.1.0"\n')
    (src_pkg / "core.py").write_text(textwrap.dedent("""\
        \"\"\"Jádro aplikace.\"\"\"

        def pozdrav(jmeno: str) -> str:
            return f"Ahoj, {jmeno}!"
    """))
    (src_pkg / "cli.py").write_text(textwrap.dedent("""\
        \"\"\"CLI vstupní bod.\"\"\"

        import argparse


        def main() -> None:
            parser = argparse.ArgumentParser()
            parser.add_argument("jmeno", help="Tvoje jméno")
            args = parser.parse_args()
            from .core import pozdrav
            print(pozdrav(args.jmeno))
    """))

    # tests
    (tests / "__init__.py").write_text("")
    pkg_var = nazev.replace("-", "_")
    (tests / "test_core.py").write_text(textwrap.dedent(f"""\
        from {pkg_var}.core import pozdrav


        def test_pozdrav():
            assert pozdrav("Anna") == "Ahoj, Anna!"
    """))

    return root


def zobraz_strom(adresar: pathlib.Path, prefix: str = "") -> None:
    polozky = sorted(adresar.iterdir(), key=lambda p: (p.is_file(), p.name))
    for i, polozka in enumerate(polozky):
        konektor = "└── " if i == len(polozky) - 1 else "├── "
        print(f"{prefix}{konektor}{polozka.name}")
        if polozka.is_dir():
            rozsireni = "    " if i == len(polozky) - 1 else "│   "
            zobraz_strom(polozka, prefix + rozsireni)


def main() -> None:
    print("=== Lekce 70: Struktura projektu ===")

    print("\n--- Doporučená struktura ---")
    print(STRUKTURA)

    print("--- pyproject.toml šablona ---")
    print(PYPROJECT_TOML)

    print("--- Generování skutečné struktury ---")
    with tempfile.TemporaryDirectory() as tmp:
        root = vytvor_projekt(pathlib.Path(tmp), "muj-projekt")
        print(f"\nVytvořeno v: {root}")
        zobraz_strom(root)

        print("\n--- Obsah pyproject.toml ---")
        print((root / "pyproject.toml").read_text())

        print("--- Obsah src/muj_projekt/core.py ---")
        print((root / "src" / "muj_projekt" / "core.py").read_text())


if __name__ == "__main__":
    main()
