"""Lekce 71 — Publikace na PyPI."""

from __future__ import annotations

import shutil
import subprocess
import sys


# ── Přehled nástrojů pro build a publish ─────────────────────────────────────

NASTROJE = {
    "uv": {
        "build": "uv build",
        "publish": "uv publish",
        "poznamka": "Nejrychlejší, doporučeno v 2025+",
    },
    "hatch": {
        "build": "hatch build",
        "publish": "hatch publish",
        "poznamka": "Komplexní správa projektů",
    },
    "build + twine": {
        "build": "python -m build",
        "publish": "twine upload dist/*",
        "poznamka": "Klasický způsob, stále funkční",
    },
}

KROKY_PUBLIKACE = [
    ("1. Účet na PyPI", "https://pypi.org/account/register/"),
    ("2. API token", "PyPI → Account Settings → API tokens"),
    ("3. ~/.pypirc nebo env", "TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-..."),
    ("4. Build", "uv build  → vytvoří dist/*.whl + dist/*.tar.gz"),
    ("5. TestPyPI (volitelné)", "uv publish --publish-url https://test.pypi.org/legacy/"),
    ("6. Publish", "uv publish"),
    ("7. Ověření", "pip install muj-projekt"),
]

PYPIRC_VZOR = """\
[distutils]
index-servers = pypi testpypi

[pypi]
username = __token__
password = pypi-AgEI...

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEI...
"""

CHECKLIST_PRED_PUBLIKACI = [
    "pyproject.toml má správnou verzi",
    "README.md je aktuální",
    "CHANGELOG je aktuální",
    "Testy prochází (pytest)",
    "Type check prošel (mypy)",
    "Linter prošel (ruff)",
    "dist/ je čistá (rm -rf dist/)",
    "Zkontroluj obsah wheelu: unzip -l dist/*.whl",
]


def zkontroluj_nastroje() -> None:
    print("--- Dostupné build nástroje ---")
    for nazev in ["uv", "hatch", "twine", "build"]:
        cesta = shutil.which(nazev)
        stav = f"✅ {cesta}" if cesta else "❌ není nainstalován"
        print(f"  {nazev:10} {stav}")


def zobraz_postup() -> None:
    print("\n--- Kroky publikace na PyPI ---")
    for krok, popis in KROKY_PUBLIKACE:
        print(f"  {krok}")
        print(f"    → {popis}")

    print("\n--- Nástroje ---")
    for nazev, info in NASTROJE.items():
        print(f"\n  [{nazev}]")
        print(f"    build:   {info['build']}")
        print(f"    publish: {info['publish']}")
        print(f"    note:    {info['poznamka']}")


def zobraz_checklist() -> None:
    print("\n--- Checklist před publikací ---")
    for polozka in CHECKLIST_PRED_PUBLIKACI:
        print(f"  ☐ {polozka}")


def zobraz_semver() -> None:
    print("\n--- Semantic Versioning (semver) ---")
    print("""
  MAJOR.MINOR.PATCH
  │     │     └── Oprava chyby (zpětně kompatibilní)
  │     └────── Nová funkce (zpětně kompatibilní)
  └──────────── Breaking change

  Příklady:
    0.1.0  → první release
    0.1.1  → bugfix
    0.2.0  → nová funkce
    1.0.0  → stabilní API, production-ready
    2.0.0  → breaking change

  Pre-release: 1.0.0a1, 1.0.0b2, 1.0.0rc1
""")


def zobraz_pypirc() -> None:
    print("--- ~/.pypirc vzor ---")
    print(PYPIRC_VZOR)
    print("  Bezpečnější varianta — env proměnné:")
    print("  export TWINE_USERNAME=__token__")
    print("  export TWINE_PASSWORD=pypi-AgEI...")


def main() -> None:
    print("=== Lekce 71: Publikace na PyPI ===\n")
    zkontroluj_nastroje()
    zobraz_postup()
    zobraz_semver()
    zobraz_checklist()
    zobraz_pypirc()

    print("\n--- Rychlý start s uv ---")
    print("""
  uv init muj-projekt
  cd muj-projekt
  # ... napiš kód ...
  uv build
  uv publish
""")


if __name__ == "__main__":
    main()
