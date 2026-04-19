"""Mini-projekt po sekci IX: Log analyzer.

Procvičuje: pathlib, regex, datetime, json, Counter, argparse, logging.
"""

import argparse
import json
import logging
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


LOG_PATTERN = re.compile(
    r"^(?P<cas>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
    r"\s+\[(?P<level>\w+)\]"
    r"\s+(?P<message>.+)$"
)


def parsuj(soubor: Path):
    """Generátor parsovaných řádků."""
    with soubor.open(encoding="utf-8") as f:
        for radek in f:
            m = LOG_PATTERN.match(radek)
            if m:
                yield m.groupdict()


def analyzuj(soubor: Path) -> dict:
    levels = Counter()
    chyby = []
    pocet = 0

    for zaznam in parsuj(soubor):
        pocet += 1
        levels[zaznam["level"]] += 1
        if zaznam["level"] in {"ERROR", "CRITICAL"}:
            chyby.append(zaznam["message"])

    return {
        "soubor": str(soubor),
        "celkem": pocet,
        "levels": dict(levels),
        "top_chyby": Counter(chyby).most_common(5),
    }


def vyrob_demo_log(cesta: Path) -> None:
    radky = []
    for i, level in enumerate(["INFO", "INFO", "WARNING", "ERROR", "INFO", "ERROR", "INFO"]):
        cas = datetime.now().replace(second=i).strftime("%Y-%m-%d %H:%M:%S")
        msg = "Connection refused" if level == "ERROR" else f"Akce {i}"
        radky.append(f"{cas} [{level}] {msg}")
    cesta.write_text("\n".join(radky), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("logfile", type=Path, nargs="?")
    parser.add_argument("--demo", action="store_true", help="vyrobí ukázkový log")
    parser.add_argument("--json", action="store_true", help="výstup jako JSON")
    args = parser.parse_args()

    if args.demo:
        demo = Path("/tmp/demo.log")
        vyrob_demo_log(demo)
        log.info(f"Demo log: {demo}")
        args.logfile = demo

    if not args.logfile:
        parser.error("zadej logfile nebo --demo")

    vysledek = analyzuj(args.logfile)

    if args.json:
        print(json.dumps(vysledek, indent=2, ensure_ascii=False))
    else:
        print(f"\n📊 Soubor: {vysledek['soubor']}")
        print(f"   Celkem: {vysledek['celkem']} řádků")
        print("   Úrovně:")
        for k, v in vysledek["levels"].items():
            print(f"     {k:10s} {v}")
        if vysledek["top_chyby"]:
            print("   Top chyby:")
            for msg, n in vysledek["top_chyby"]:
                print(f"     [{n}×] {msg}")


if __name__ == "__main__":
    main()
