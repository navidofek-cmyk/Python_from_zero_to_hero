# Program — Lekce 21: Lekce 21: Definice funkcí

Patří k lekci [Lekce 21: Definice funkcí](../21_funkce_zaklady.md).

## Jak spustit

```bash
python3 programy/l21_funkce.py
```

## Zdrojový kód

### `l21_funkce.py`

```py
"""Lekce 21 — funkce, return, default, past s mutable default."""


def faktorial(n: int) -> int:
    vysledek = 1
    for i in range(2, n + 1):
        vysledek *= i
    return vysledek


def obdelnik(a: float, b: float) -> tuple[float, float]:
    return 2 * (a + b), a * b


def past_se_seznamem(polozka, seznam=[]):
    """❌ NEDĚLEJ TO TAKHLE — jen demo pasti."""
    seznam.append(polozka)
    return seznam


def spravne(polozka, seznam=None):
    if seznam is None:
        seznam = []
    seznam.append(polozka)
    return seznam


def main() -> None:
    for n in [0, 1, 5, 10]:
        print(f"{n}! = {faktorial(n)}")

    obvod, obsah = obdelnik(3, 5)
    print(f"\nObdélník 3×5: obvod={obvod}, obsah={obsah}")

    print("\nPast:")
    print(past_se_seznamem("a"))      # ['a']
    print(past_se_seznamem("b"))      # ['a', 'b']  ← Cože?!

    print("\nSprávně:")
    print(spravne("a"))               # ['a']
    print(spravne("b"))               # ['b']  ✅


if __name__ == "__main__":
    main()

```
