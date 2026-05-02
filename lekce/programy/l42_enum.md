# Program — Lekce 42: Lekce 42: `Enum`, `IntEnum`, `StrEnum`, `Flag`

Patří k lekci [Lekce 42: `Enum`, `IntEnum`, `StrEnum`, `Flag`](../42_enum.md).

## Jak spustit

```bash
python3 programy/l42_enum.py
```

## Zdrojový kód

### `l42_enum.py`

```py
"""Lekce 42 — Enum, IntEnum, Flag."""

from enum import Enum, IntEnum, Flag, auto


class Status(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"


class Den(IntEnum):
    PO = 1
    UT = 2
    ST = 3
    CT = 4
    PA = 5
    SO = 6
    NE = 7

    def je_vikend(self) -> bool:
        return self in {Den.SO, Den.NE}


class Pristup(Flag):
    CIST = auto()
    PSAT = auto()
    MAZAT = auto()


def main() -> None:
    s = Status.ACTIVE
    print(f"Status: {s.name} = {s.value!r}")

    print("\nDny:")
    for d in Den:
        zn = "🌴" if d.je_vikend() else "💼"
        print(f"  {zn} {d.name} ({d.value})")

    admin = Pristup.CIST | Pristup.PSAT | Pristup.MAZAT
    host = Pristup.CIST
    print(f"\nAdmin: {admin}")
    print(f"Host:  {host}")
    print(f"Admin smí mazat? {Pristup.MAZAT in admin}")
    print(f"Host smí psát?   {Pristup.PSAT in host}")

    # Z hodnoty
    print(f"\nz 'active': {Status('active')}")


if __name__ == "__main__":
    main()

```
