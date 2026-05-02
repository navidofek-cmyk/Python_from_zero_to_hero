# Program — Lekce 50: Lekce 50: Protokoly a `typing.Protocol` (strukturální typování)

Patří k lekci [Lekce 50: Protokoly a `typing.Protocol` (strukturální typování)](../50_protocols.md).

## Jak spustit

```bash
python3 programy/l50_protocols.py
```

## Zdrojový kód

### `l50_protocols.py`

```py
"""Lekce 50 — typing.Protocol."""

from typing import Protocol, runtime_checkable
from collections.abc import Iterable


@runtime_checkable
class Plovak(Protocol):
    def plav(self) -> None: ...


class Ryba:
    def plav(self) -> None:
        print("🐟 Plavu pod vodou")


class Lod:
    def plav(self) -> None:
        print("⛵ Plavu po hladině")


def vypust_na_vodu(x: Plovak) -> None:
    x.plav()


def soucet(cisla: Iterable[int]) -> int:
    return sum(cisla)


def main() -> None:
    vypust_na_vodu(Ryba())
    vypust_na_vodu(Lod())

    print(f"\nIsinstance(Ryba(), Plovak): {isinstance(Ryba(), Plovak)}")

    print(f"\nSoučet list:  {soucet([1, 2, 3])}")
    print(f"Součet tuple: {soucet((1, 2, 3))}")
    print(f"Součet gen:   {soucet(x for x in range(10))}")


if __name__ == "__main__":
    main()

```
