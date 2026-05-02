# Program — Lekce 28: Lekce 28: Rekurze

Patří k lekci [Lekce 28: Rekurze](../28_rekurze.md).

## Jak spustit

```bash
python3 programy/l28_rekurze.py
```

## Zdrojový kód

### `l28_rekurze.py`

```py
"""Lekce 28 — rekurze."""

from functools import cache


def faktorial_rek(n: int) -> int:
    if n == 0:
        return 1
    return n * faktorial_rek(n - 1)


def faktorial_smy(n: int) -> int:
    v = 1
    for i in range(2, n + 1):
        v *= i
    return v


@cache
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def soucet_vsech(seznam) -> int:
    celkem = 0
    for prvek in seznam:
        if isinstance(prvek, list):
            celkem += soucet_vsech(prvek)
        else:
            celkem += prvek
    return celkem


def reverze(s: str) -> str:
    if len(s) <= 1:
        return s
    return reverze(s[1:]) + s[0]


def main() -> None:
    print(f"Rekurzivně 5! = {faktorial_rek(5)}")
    print(f"Smyčkou    5! = {faktorial_smy(5)}")

    print(f"\nFib(50) = {fib(50)}")

    vnoreny = [1, [2, [3, [4, 5]]], [6, 7], 8]
    print(f"\nSoučet {vnoreny} = {soucet_vsech(vnoreny)}")

    print(f"\nReverze 'Příšerně' = {reverze('Příšerně')}")


if __name__ == "__main__":
    main()

```
