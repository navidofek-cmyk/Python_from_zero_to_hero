"""Lekce 40 — abstraktní třídy."""

from abc import ABC, abstractmethod
from math import pi


class Tvar(ABC):
    @abstractmethod
    def obsah(self) -> float: ...

    @abstractmethod
    def obvod(self) -> float: ...

    def popis(self) -> str:
        return f"{type(self).__name__}: obsah={self.obsah():.2f}, obvod={self.obvod():.2f}"


class Kruh(Tvar):
    def __init__(self, r: float):
        self.r = r

    def obsah(self) -> float:
        return pi * self.r ** 2

    def obvod(self) -> float:
        return 2 * pi * self.r


class Obdelnik(Tvar):
    def __init__(self, a: float, b: float):
        self.a, self.b = a, b

    def obsah(self) -> float:
        return self.a * self.b

    def obvod(self) -> float:
        return 2 * (self.a + self.b)


def main() -> None:
    tvary: list[Tvar] = [Kruh(5), Obdelnik(3, 4)]
    for t in tvary:
        print(t.popis())

    try:
        Tvar()
    except TypeError as e:
        print(f"\n❌ Nelze instantiovat Tvar: {e}")


if __name__ == "__main__":
    main()
