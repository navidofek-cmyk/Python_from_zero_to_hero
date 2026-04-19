"""CLI entry point."""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(prog="pozdrav")
    parser.add_argument("jmeno", help="Jméno koho pozdravit")
    parser.add_argument("--vykricnik", action="store_true")
    parser.add_argument("--velka", action="store_true", help="VELKÝMI")
    args = parser.parse_args()

    konec = "!" if args.vykricnik else "."
    text = f"Ahoj {args.jmeno}{konec}"
    if args.velka:
        text = text.upper()
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
