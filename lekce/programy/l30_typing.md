# Program — Lekce 30: Lekce 30: Anotace typů u funkcí (pokročile)

Patří k lekci [Lekce 30: Anotace typů u funkcí (pokročile)](../30_typing_funkce.md).

## Jak spustit

```bash
python3 programy/l30_typing.py
```

## Zdrojový kód

### `l30_typing.py`

```py
"""Lekce 30 — typové anotace."""

from typing import Callable, TypeVar

T = TypeVar("T")


def aplikuj(f: Callable[[int, int], int], x: int, y: int) -> int:
    return f(x, y)


def prvni(seznam: list[T]) -> T:
    return seznam[0]


def hledej(klic: str, slovnik: dict[str, int]) -> int | None:
    return slovnik.get(klic)


def udelej_dvakrat(f: Callable[[int], int], x: int) -> int:
    return f(f(x))


def main() -> None:
    print(f"aplikuj(+, 3, 5) = {aplikuj(lambda a, b: a + b, 3, 5)}")
    print(f"aplikuj(*, 3, 5) = {aplikuj(lambda a, b: a * b, 3, 5)}")

    print(f"\nprvni([1, 2, 3]) = {prvni([1, 2, 3])}")
    print(f"prvni(['a', 'b']) = {prvni(['a', 'b'])}")

    skore = {"Anna": 95, "Bob": 80}
    print(f"\nhledej('Anna') = {hledej('Anna', skore)}")
    print(f"hledej('Cyril') = {hledej('Cyril', skore)}")

    print(f"\nudelej_dvakrat(+1, 5) = {udelej_dvakrat(lambda x: x + 1, 5)}")


if __name__ == "__main__":
    main()

```
