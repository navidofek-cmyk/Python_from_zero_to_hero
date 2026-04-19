"""Lekce 39 — __slots__ a měření paměti."""

import sys
from dataclasses import dataclass


class S_dict:
    def __init__(self):
        self.x = 1
        self.y = 2


class S_slots:
    __slots__ = ("x", "y")

    def __init__(self):
        self.x = 1
        self.y = 2


@dataclass(slots=True)
class S_data_slots:
    x: int = 1
    y: int = 2


def main() -> None:
    a = S_dict()
    b = S_slots()
    c = S_data_slots()

    velikost_a = sys.getsizeof(a) + sys.getsizeof(a.__dict__)
    velikost_b = sys.getsizeof(b)
    velikost_c = sys.getsizeof(c)

    print(f"S_dict:        {velikost_a} bytů")
    print(f"S_slots:       {velikost_b} bytů ({velikost_a/velikost_b:.1f}× méně)")
    print(f"S_data_slots:  {velikost_c} bytů")

    try:
        b.barva = "modrá"
    except AttributeError as e:
        print(f"\n❌ S_slots.barva = ... → {e}")


if __name__ == "__main__":
    main()
