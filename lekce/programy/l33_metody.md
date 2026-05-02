# Program — Lekce 33: Lekce 33: Metody — instance, `@classmethod`, `@staticmethod`

Patří k lekci [Lekce 33: Metody — instance, `@classmethod`, `@staticmethod`](../33_metody.md).

## Jak spustit

```bash
python3 programy/l33_metody.py
```

## Zdrojový kód

### `l33_metody.py`

```py
"""Lekce 33 — instance, classmethod, staticmethod."""

from datetime import date


class Datum:
    def __init__(self, den: int, mesic: int, rok: int):
        self.den, self.mesic, self.rok = den, mesic, rok

    @classmethod
    def z_textu(cls, text: str) -> "Datum":
        d, m, r = map(int, text.split("."))
        return cls(d, m, r)

    @classmethod
    def dnes(cls) -> "Datum":
        d = date.today()
        return cls(d.day, d.month, d.year)

    def __repr__(self) -> str:
        return f"{self.den}.{self.mesic}.{self.rok}"


class Matematika:
    @staticmethod
    def je_prvocislo(n: int) -> bool:
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True


def main() -> None:
    print(Datum(24, 12, 2025))
    print(Datum.z_textu("01.01.2026"))
    print(Datum.dnes())

    print()
    for n in range(1, 20):
        if Matematika.je_prvocislo(n):
            print(f"{n} je prvočíslo")


if __name__ == "__main__":
    main()

```
