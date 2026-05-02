# Program — Lekce 12: Lekce 12: N-tice (`tuple`)

Patří k lekci [Lekce 12: N-tice (`tuple`)](../12_ntice.md).

## Jak spustit

```bash
python3 programy/l12_ntice.py
```

## Zdrojový kód

### `l12_ntice.py`

```py
"""Lekce 12 — n-tice a unpacking."""

from typing import NamedTuple


class Pes(NamedTuple):
    jmeno: str
    vek: int
    plemeno: str


def min_max(cisla: list[int]) -> tuple[int, int]:
    return min(cisla), max(cisla)


def main() -> None:
    # Unpacking
    bod = (50.08, 14.42)
    x, y = bod
    print(f"Praha: x={x}, y={y}")

    # Záměna
    a, b = "ahoj", "svete"
    a, b = b, a
    print(f"Po záměně: a={a}, b={b}")

    # Hvězdička
    prvni, *stred, posledni = [1, 2, 3, 4, 5]
    print(f"prvni={prvni}, stred={stred}, posledni={posledni}")

    # Funkce vracející tuple
    nejmin, nejvic = min_max([3, 1, 4, 1, 5, 9, 2, 6])
    print(f"Min: {nejmin}, Max: {nejvic}")

    # NamedTuple
    psi = [
        Pes("Rex", 3, "labrador"),
        Pes("Bonzo", 7, "kníračovec"),
        Pes("Punťa", 1, "pudl"),
    ]
    for p in psi:
        print(f"🐕 {p.jmeno} ({p.plemeno}, {p.vek}r)")


if __name__ == "__main__":
    main()

```
