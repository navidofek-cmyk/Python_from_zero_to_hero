# Program — Lekce 4: Lekce 4: Základní typy — int, float, bool, complex

Patří k lekci [Lekce 4: Základní typy — int, float, bool, complex](../04_zakladni_typy.md).

## Jak spustit

```bash
python3 programy/l04_typy.py
```

## Zdrojový kód

### `l04_typy.py`

```py
"""Lekce 4 — int, float, bool a jejich kouzla."""

from decimal import Decimal


def main() -> None:
    # int — celé číslo bez limitu
    obrovske = 2 ** 200
    print(f"2 na 200 má {len(str(obrovske))} cifer")

    # Float a jeho podivnost
    print(f"0.1 + 0.2 = {0.1 + 0.2}    ← podivné!")
    print(f"S Decimal: {Decimal('0.1') + Decimal('0.2')}    ← přesně")

    # Operace
    print(f"10 / 3  = {10 / 3}     (vždy float)")
    print(f"10 // 3 = {10 // 3}    (celočíselné)")
    print(f"10 % 3  = {10 % 3}     (zbytek)")

    # Bool je int!
    print(f"True + True = {True + True}    🤨")

    # Převody
    print(f"int('42')   = {int('42')}")
    print(f"int(3.9)    = {int(3.9)}    (uřízne)")
    print(f"round(3.9)  = {round(3.9)}   (zaokrouhlí)")


if __name__ == "__main__":
    main()

```
