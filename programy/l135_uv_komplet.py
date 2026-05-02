"""Lekce 135 — uv kompletní průvodce.

Tento soubor ukazuje použití uv v kódu.
Většina uv příkazů se spouští v terminálu.

Spuštění přímo přes uv (inline závislosti):
    uv run l135_uv_komplet.py

Nebo jako standalone skript s inline závislostmi:
    uv run --with rich,requests demo_skript.py
"""

# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "rich>=13.0",
# ]
# ///

import subprocess
import sys
from pathlib import Path


def spust_prikaz(cmd: str) -> tuple[str, int]:
    """Spustí příkaz a vrátí (výstup, návratový_kód)."""
    result = subprocess.run(
        cmd.split(),
        capture_output=True,
        text=True
    )
    return result.stdout.strip() or result.stderr.strip(), result.returncode


def zkontroluj_uv() -> bool:
    """Zkontroluj jestli je uv nainstalovaný."""
    vystup, kod = spust_prikaz("uv --version")
    if kod == 0:
        print(f"✅ uv nalezeno: {vystup}")
        return True
    print("❌ uv není nainstalované")
    print("   Instalace: curl -LsSf https://astral.sh/uv/install.sh | sh")
    return False


def ukaz_python_verze():
    """Zobraz dostupné Python verze přes uv."""
    print("\n📋 Dostupné Python verze:")
    vystup, _ = spust_prikaz("uv python list")
    if vystup:
        for radek in vystup.splitlines()[:5]:
            print(f"  {radek}")
        print("  ...")
    else:
        print("  (spusť: uv python list)")


def ukaz_nainstalovanej_nastroje():
    """Zobraz globálně nainstalované nástroje."""
    print("\n🔧 Nainstalované nástroje:")
    vystup, _ = spust_prikaz("uv tool list")
    if vystup:
        print(vystup)
    else:
        print("  Žádné nástroje (zkus: uv tool install ruff)")


def demo_inline_skript():
    """Vygeneruje ukázku standalone skriptu s inline závislostmi."""
    skript = '''\
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests>=2.31",
#   "rich>=13.0",
# ]
# ///

"""Standalone skript — spusť přes: uv run tento_skript.py"""

import requests
from rich.console import Console
from rich.table import Table

console = Console()

def main():
    console.print("[bold blue]Fetch dat z JSONPlaceholder API[/bold blue]")

    r = requests.get("https://jsonplaceholder.typicode.com/users")
    uzivatele = r.json()

    tabulka = Table("ID", "Jméno", "Email", "Město")
    for u in uzivatele[:5]:
        tabulka.add_row(
            str(u["id"]),
            u["name"],
            u["email"],
            u["address"]["city"]
        )

    console.print(tabulka)

if __name__ == "__main__":
    main()
'''
    cesta = Path("/tmp/demo_uv_script.py")
    cesta.write_text(skript)
    print(f"\n📄 Ukázkový skript uložen do: {cesta}")
    print("   Spuštění: uv run /tmp/demo_uv_script.py")
    print("   (uv automaticky nainstaluje requests a rich)")
    return cesta


def demo_pyproject():
    """Ukáže strukturu pyproject.toml pro uv projekt."""
    print("\n📦 Ukázka pyproject.toml:")
    print("""
[project]
name = "muj-projekt"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi[standard]>=0.110",
    "sqlalchemy>=2.0",
    "redis>=5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.3",
    "mypy>=1.8",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
]

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
""")


def main():
    print("=" * 50)
    print("  🚀 uv — Kompletní průvodce")
    print("=" * 50)

    if not zkontroluj_uv():
        sys.exit(1)

    print("\n📚 Nejdůležitější příkazy:")
    prikazy = [
        ("uv init muj-projekt", "Nový projekt"),
        ("uv add fastapi", "Přidej závislost"),
        ("uv add --dev pytest", "Přidej dev závislost"),
        ("uv run main.py", "Spusť skript"),
        ("uv sync", "Synchronizuj prostředí"),
        ("uv sync --frozen", "Sync bez změny lock (CI)"),
        ("uv tool install ruff", "Instaluj globální nástroj"),
        ("uvx ruff check .", "Jednorázové spuštění"),
        ("uv python install 3.13", "Instaluj Python verzi"),
        ("uv python pin 3.12", "Nastav verzi projektu"),
    ]

    for prikaz, popis in prikazy:
        print(f"  {prikaz:<35} # {popis}")

    ukaz_python_verze()
    ukaz_nainstalovanej_nastroje()
    cesta_skriptu = demo_inline_skript()
    demo_pyproject()

    print("\n✅ Hotovo! Zkus: uv run", cesta_skriptu)


if __name__ == "__main__":
    main()
