# Program — Lekce 25: Lekce 25: Closure a `nonlocal`

Patří k lekci [Lekce 25: Closure a `nonlocal`](../25_closure.md).

## Jak spustit

```bash
python3 programy/l25_closure.py
```

## Zdrojový kód

### `l25_closure.py`

```py
"""Lekce 25 — closure a nonlocal."""


def vyrob_pricitac(o_kolik: int):
    def pridej(x: int) -> int:
        return x + o_kolik
    return pridej


def vyrob_pocitadlo():
    n = 0

    def zvyseni() -> int:
        nonlocal n
        n += 1
        return n

    def stav() -> int:
        return n

    return zvyseni, stav


def vyrob_validator(min_delka: int):
    def validuj(text: str) -> bool:
        return len(text) >= min_delka
    return validuj


def main() -> None:
    pricti_5 = vyrob_pricitac(5)
    pricti_10 = vyrob_pricitac(10)
    print(f"100 + 5  = {pricti_5(100)}")
    print(f"100 + 10 = {pricti_10(100)}")

    zvys, stav = vyrob_pocitadlo()
    for _ in range(5):
        zvys()
    print(f"\nPo 5 voláních: stav = {stav()}")

    val_heslo = vyrob_validator(8)
    val_pin = vyrob_validator(4)
    print(f"\nHeslo 'abc'      OK? {val_heslo('abc')}")
    print(f"Heslo 'abcdefgh' OK? {val_heslo('abcdefgh')}")
    print(f"PIN '12'         OK? {val_pin('12')}")
    print(f"PIN '1234'       OK? {val_pin('1234')}")

    # Past s pozdním vyhodnocením
    spatne = [lambda: i for i in range(3)]
    spravne = [lambda i=i: i for i in range(3)]
    print(f"\n❌ Past:    {[f() for f in spatne]}")
    print(f"✅ Správně: {[f() for f in spravne]}")


if __name__ == "__main__":
    main()

```
