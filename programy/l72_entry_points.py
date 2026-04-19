"""Lekce 72 — Entry points a CLI skripty."""

from __future__ import annotations

import argparse
import importlib.metadata
import sys
import textwrap


# ── Co jsou entry points ─────────────────────────────────────────────────────

VYSVETLENI = """\
Entry point = mechanismus, kterým balíček registruje funkce
dostupné ostatním balíčkům nebo jako CLI příkazy.

V pyproject.toml:

  [project.scripts]
  moje-cli = "muj_projekt.cli:main"
  ↑                ↑              ↑
  příkaz v PATH    modul          funkce

Po `pip install`:
  $ moje-cli --help   ← zavolá muj_projekt.cli.main()
"""

PYPROJECT_ENTRY_POINTS = """\
# CLI příkazy
[project.scripts]
muj-nastroj = "muj_projekt.cli:main"

# GUI aplikace (Windows/macOS)
[project.gui-scripts]
muj-gui = "muj_projekt.gui:main"

# Pluginy (vlastní skupiny)
[project.entry-points."muj_projekt.pluginy"]
csv   = "muj_projekt.pluginy.csv_plugin:CSVPlugin"
excel = "muj_projekt.pluginy.excel_plugin:ExcelPlugin"
"""


# ── Vlastní CLI s argparse ────────────────────────────────────────────────────

def vytvor_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="muj-nastroj",
        description="Ukázkový CLI nástroj",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Příklady:
              muj-nastroj pozdrav Anna
              muj-nastroj pocitej --od 1 --do 10
              muj-nastroj info --verbose
        """),
    )

    subparsers = parser.add_subparsers(dest="prikaz", metavar="PŘÍKAZ")

    # subcommand: pozdrav
    p_pozdrav = subparsers.add_parser("pozdrav", help="Pozdrav uživatele")
    p_pozdrav.add_argument("jmeno", help="Jméno uživatele")
    p_pozdrav.add_argument("-v", "--verbose", action="store_true")

    # subcommand: pocitej
    p_pocitej = subparsers.add_parser("pocitej", help="Sečti čísla v rozsahu")
    p_pocitej.add_argument("--od", type=int, default=1)
    p_pocitej.add_argument("--do", type=int, default=10)

    # subcommand: info
    p_info = subparsers.add_parser("info", help="Informace o prostředí")
    p_info.add_argument("--verbose", action="store_true")

    return parser


def spust_cli(argv: list[str] | None = None) -> int:
    parser = vytvor_parser()
    args = parser.parse_args(argv)

    if args.prikaz == "pozdrav":
        if args.verbose:
            print(f"Spouštím pozdrav pro uživatele: {args.jmeno!r}")
        print(f"Ahoj, {args.jmeno}!")
        return 0

    elif args.prikaz == "pocitej":
        vysledek = sum(range(args.od, args.do + 1))
        print(f"Součet {args.od}..{args.do} = {vysledek}")
        return 0

    elif args.prikaz == "info":
        print(f"Python: {sys.version}")
        print(f"Platform: {sys.platform}")
        if args.verbose:
            print(f"Prefix: {sys.prefix}")
            print(f"Path[0]: {sys.path[0]}")
        return 0

    else:
        parser.print_help()
        return 1


# ── Čtení entry points za běhu ───────────────────────────────────────────────

def zobraz_nainstalowane_entry_points() -> None:
    print("\n--- Entry points nainstalovaných balíčků (ukázka) ---")
    skupiny = ["console_scripts", "distutils.commands"]
    for skupina in skupiny:
        eps = importlib.metadata.entry_points(group=skupina)
        eps_list = list(eps)
        if eps_list:
            print(f"\n  [{skupina}] — {len(eps_list)} entry points")
            for ep in eps_list[:5]:
                print(f"    {ep.name:30} → {ep.value}")
            if len(eps_list) > 5:
                print(f"    ... a {len(eps_list) - 5} dalších")


# ── Plugin systém pomocí entry points ────────────────────────────────────────

class PluginRegistry:
    """Jednoduchý plugin registr — simuluje entry_points mechanismus."""

    def __init__(self):
        self._pluginy: dict[str, type] = {}

    def registruj(self, nazev: str):
        def dekorator(cls):
            self._pluginy[nazev] = cls
            return cls
        return dekorator

    def nacti(self, nazev: str):
        if nazev not in self._pluginy:
            raise KeyError(f"Plugin {nazev!r} není registrován. Dostupné: {list(self._pluginy)}")
        return self._pluginy[nazev]()

    def vsechny(self) -> list[str]:
        return list(self._pluginy)


registry = PluginRegistry()


@registry.registruj("json")
class JsonPlugin:
    def zpracuj(self, data: str) -> str:
        return f"[JSON] zpracováno: {data}"


@registry.registruj("csv")
class CsvPlugin:
    def zpracuj(self, data: str) -> str:
        return f"[CSV] zpracováno: {data}"


def main() -> None:
    print("=== Lekce 72: Entry Points ===\n")

    print("--- Co jsou entry points ---")
    print(textwrap.indent(VYSVETLENI, "  "))

    print("--- pyproject.toml konfigurace ---")
    print(textwrap.indent(PYPROJECT_ENTRY_POINTS, "  "))

    print("--- Demo CLI (simulace) ---")
    testove_prikazy = [
        ["pozdrav", "Anna"],
        ["pozdrav", "--verbose", "Bob"],
        ["pocitej", "--od", "1", "--do", "5"],
        ["info"],
    ]
    for prikaz in testove_prikazy:
        print(f"\n  $ muj-nastroj {' '.join(prikaz)}")
        spust_cli(prikaz)

    print("\n--- Plugin systém ---")
    print(f"  Registrované pluginy: {registry.vsechny()}")
    for nazev in registry.vsechny():
        plugin = registry.nacti(nazev)
        print(f"  {plugin.zpracuj('testdata')}")

    zobraz_nainstalowane_entry_points()


if __name__ == "__main__":
    main()
