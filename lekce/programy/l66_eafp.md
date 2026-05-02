# Program — Lekce 66: Lekce 66: EAFP vs LBYL — pythonský přístup

Patří k lekci [Lekce 66: EAFP vs LBYL — pythonský přístup](../66_eafp_lbyl.md).

## Jak spustit

```bash
python3 programy/l66_eafp.py
```

## Zdrojový kód

### `l66_eafp.py`

```py
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

```
