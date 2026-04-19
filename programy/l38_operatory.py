"""Lekce 38 — operátorové přetížení."""


class Vektor:
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y

    def __add__(self, other):
        return Vektor(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vektor(self.x - other.x, self.y - other.y)

    def __mul__(self, skalar: float):
        return Vektor(self.x * skalar, self.y * skalar)

    __rmul__ = __mul__

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __repr__(self):
        return f"Vektor({self.x}, {self.y})"

    def __abs__(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5


class Penize:
    def __init__(self, castka: float, mena: str = "CZK"):
        self.castka = castka
        self.mena = mena

    def __add__(self, other):
        if self.mena != other.mena:
            raise ValueError(f"Nelze sčítat {self.mena} a {other.mena}")
        return Penize(self.castka + other.castka, self.mena)

    def __mul__(self, n):
        return Penize(self.castka * n, self.mena)

    def __repr__(self):
        return f"{self.castka} {self.mena}"


def main() -> None:
    a = Vektor(1, 2)
    b = Vektor(3, 4)
    print(f"{a} + {b} = {a + b}")
    print(f"3 * {a} = {3 * a}")
    print(f"|{b}| = {abs(b):.2f}")

    print(f"\n{Penize(100) + Penize(50)}")
    print(f"{Penize(100) * 3}")


if __name__ == "__main__":
    main()
