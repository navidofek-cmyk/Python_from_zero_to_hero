# Program — Lekce 41: Lekce 41: `dataclasses`

Patří k lekci [Lekce 41: `dataclasses`](../41_dataclasses.md).

## Jak spustit

```bash
python3 programy/l41_dataclasses.py
```

## Zdrojový kód

### `l41_dataclasses.py`

```py
"""Lekce 41 — dataclasses."""

from dataclasses import dataclass, field, asdict


@dataclass(frozen=True, slots=True)
class Bod:
    x: int
    y: int


@dataclass(order=True)
class Studium:
    prumer: float
    jmeno: str = field(compare=False)


@dataclass
class Tym:
    nazev: str
    clenove: list[str] = field(default_factory=list)


@dataclass
class Obdelnik:
    a: float
    b: float
    obsah: float = field(init=False)

    def __post_init__(self):
        self.obsah = self.a * self.b


def main() -> None:
    p1 = Bod(1, 2)
    p2 = Bod(1, 2)
    print(f"p1 == p2: {p1 == p2}")
    print(f"set: {sada := {p1, p2, Bod(3, 4)}}, velikost {len(sada)}")

    studium = [Studium(1.5, "Anna"), Studium(2.3, "Bob"), Studium(1.0, "Cyril")]
    studium.sort()
    print(f"\nSeřazeno: {studium}")

    t = Tym("Pythonisti")
    t.clenove.extend(["Anna", "Bob"])
    print(f"\nTým: {asdict(t)}")

    o = Obdelnik(3, 5)
    print(f"\nObdélník: {o}")


if __name__ == "__main__":
    main()

```
