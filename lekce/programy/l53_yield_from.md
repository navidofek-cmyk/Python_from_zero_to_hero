# Program — Lekce 53: Lekce 53: `yield from` — delegování generátorů

Patří k lekci [Lekce 53: `yield from` — delegování generátorů](../53_yield_from.md).

## Jak spustit

```bash
python3 programy/l53_yield_from.py
```

## Zdrojový kód

### `l53_yield_from.py`

```py
"""Lekce 53 — yield from."""


def vsechny_polozky(strom):
    for prvek in strom:
        if isinstance(prvek, list):
            yield from vsechny_polozky(prvek)
        else:
            yield prvek


def cisla_az_do(n: int):
    yield from range(0, n)
    yield from range(0, -n, -1)


def main() -> None:
    strom = [1, [2, [3, 4], 5], 6, [7, [8, 9]]]
    print(f"Strom: {strom}")
    print(f"Ploše: {list(vsechny_polozky(strom))}")
    print(f"\ncisla_az_do(3): {list(cisla_az_do(3))}")


if __name__ == "__main__":
    main()

```
