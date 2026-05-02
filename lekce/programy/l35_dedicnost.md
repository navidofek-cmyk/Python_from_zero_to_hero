# Program — Lekce 35: Lekce 35: Dědičnost a `super()`

Patří k lekci [Lekce 35: Dědičnost a `super()`](../35_dedicnost.md).

## Jak spustit

```bash
python3 programy/l35_dedicnost.py
```

## Zdrojový kód

### `l35_dedicnost.py`

```py
"""Lekce 35 — dědičnost a super()."""


class Zvire:
    def __init__(self, jmeno: str):
        self.jmeno = jmeno

    def spi(self) -> None:
        print(f"😴 {self.jmeno} chrápe.")

    def zvuk(self) -> str:
        return "..."


class Pes(Zvire):
    def __init__(self, jmeno: str, plemeno: str):
        super().__init__(jmeno)
        self.plemeno = plemeno

    def zvuk(self) -> str:
        return "Haf!"


class Kocka(Zvire):
    def zvuk(self) -> str:
        return "Mňau!"


def main() -> None:
    zoo = [Pes("Rex", "labrador"), Kocka("Mína"), Zvire("Záhada")]
    for z in zoo:
        z.spi()
        print(f"  {z.jmeno}: {z.zvuk()}")

    print("\nMRO Pes:", [c.__name__ for c in Pes.__mro__])
    print(f"isinstance(Pes('R','l'), Zvire): {isinstance(Pes('R','l'), Zvire)}")


if __name__ == "__main__":
    main()

```
