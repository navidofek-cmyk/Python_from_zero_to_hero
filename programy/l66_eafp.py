"""Lekce 66 — EAFP vs LBYL."""


def lbyl(d: dict, klic: str):
    if klic in d:
        return d[klic]
    return None


def eafp(d: dict, klic: str):
    try:
        return d[klic]
    except KeyError:
        return None


def pythonic(d: dict, klic: str):
    return d.get(klic)


def main() -> None:
    d = {"a": 1}
    print(f"LBYL    'a': {lbyl(d, 'a')},  'x': {lbyl(d, 'x')}")
    print(f"EAFP    'a': {eafp(d, 'a')},  'x': {eafp(d, 'x')}")
    print(f"Pyth.get'a': {pythonic(d, 'a')},  'x': {pythonic(d, 'x')}")


if __name__ == "__main__":
    main()
