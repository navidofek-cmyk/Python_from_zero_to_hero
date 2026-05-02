# Program — Lekce 9: Lekce 9: Smyčky — `for` a `while`

Patří k lekci [Lekce 9: Smyčky — `for` a `while`](../09_smycky.md).

## Jak spustit

```bash
python3 programy/l09_smycky.py
```

## Zdrojový kód

### `l09_smycky.py`

```py
"""Lekce 9 — for, while, FizzBuzz, trojúhelník."""


def fizzbuzz(do: int = 30) -> None:
    for n in range(1, do + 1):
        if n % 15 == 0:
            print("FizzBuzz")
        elif n % 3 == 0:
            print("Fizz")
        elif n % 5 == 0:
            print("Buzz")
        else:
            print(n)


def trojuhelnik(vyska: int = 5) -> None:
    for i in range(1, vyska + 1):
        print("*" * i)


def soucet_do(n: int) -> int:
    s = 0
    for x in range(1, n + 1):
        s += x
    return s


def main() -> None:
    print("=== FizzBuzz ===")
    fizzbuzz()

    print("\n=== Trojúhelník ===")
    trojuhelnik()

    print(f"\nSoučet 1..100 = {soucet_do(100)} (rychlejc: {sum(range(1, 101))})")


if __name__ == "__main__":
    main()

```
