# Program — Lekce 37: Lekce 37: Dunder metody

Patří k lekci [Lekce 37: Dunder metody](../37_dunder_metody.md).

## Jak spustit

```bash
python3 programy/l37_dunder.py
```

## Zdrojový kód

### `l37_dunder.py`

```py
"""Lekce 37 — dunder metody."""

from functools import total_ordering


@total_ordering
class Verze:
    def __init__(self, major: int, minor: int, patch: int = 0):
        self.major, self.minor, self.patch = major, minor, patch

    def __repr__(self) -> str:
        return f"Verze({self.major}, {self.minor}, {self.patch})"

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def _key(self):
        return (self.major, self.minor, self.patch)

    def __eq__(self, other):
        if not isinstance(other, Verze):
            return NotImplemented
        return self._key() == other._key()

    def __lt__(self, other):
        return self._key() < other._key()

    def __hash__(self):
        return hash(self._key())


class Vozik:
    def __init__(self):
        self.polozky: list[str] = []

    def __len__(self) -> int:
        return len(self.polozky)

    def __bool__(self) -> bool:
        return bool(self.polozky)

    def __contains__(self, polozka: str) -> bool:
        return polozka in self.polozky


def main() -> None:
    v1 = Verze(1, 2, 3)
    v2 = Verze(1, 2, 3)
    v3 = Verze(1, 5, 0)

    print(v1, v3)
    print(f"v1 == v2: {v1 == v2}")
    print(f"v1 < v3:  {v1 < v3}")
    print(f"v3 >= v1: {v3 >= v1}")

    sada = {v1, v2, v3}
    print(f"\nSet (díky __hash__): {sada}")

    voz = Vozik()
    print(f"\nPrázdný voz, bool: {bool(voz)}")
    voz.polozky.extend(["mléko", "chléb"])
    print(f"Po nákupu, len: {len(voz)}, 'mléko' in voz: {'mléko' in voz}")


if __name__ == "__main__":
    main()

```
