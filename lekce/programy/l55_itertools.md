# Program — Lekce 55: Lekce 55: `itertools` — kouzla s iterátory

Patří k lekci [Lekce 55: `itertools` — kouzla s iterátory](../55_itertools.md).

## Jak spustit

```bash
python3 programy/l55_itertools.py
```

## Zdrojový kód

### `l55_itertools.py`

```py
"""Lekce 55 — itertools."""

import itertools as it


def main() -> None:
    # Cycle
    barvy = list(it.islice(it.cycle(["🔴", "🟢", "🔵"]), 7))
    print(f"Cycle: {barvy}")

    # Combinations
    jmena = ["Anna", "Bob", "Cyril", "Dana"]
    print("\nDvojice:")
    for a, b in it.combinations(jmena, 2):
        print(f"  {a} + {b}")

    # Pairwise (3.10+)
    cisla = [1, 3, 7, 12, 20]
    rozdily = [b - a for a, b in it.pairwise(cisla)]
    print(f"\nRozdíly {cisla}: {rozdily}")

    # Accumulate
    prijmy = [1000, 1200, 800, 1500, 900]
    kumulativne = list(it.accumulate(prijmy))
    print(f"\nPříjmy: {prijmy}")
    print(f"Kumulativně: {kumulativne}")

    # Groupby (vyžaduje seřazení)
    slova = sorted(["apple", "ant", "ball", "bat", "cat"])
    for klic, skupina in it.groupby(slova, key=lambda s: s[0]):
        print(f"  {klic}: {list(skupina)}")


if __name__ == "__main__":
    main()

```
