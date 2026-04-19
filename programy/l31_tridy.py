"""Lekce 31 — třídy základy."""


class Auto:
    def __init__(self, znacka: str, model: str, rok: int):
        self.znacka = znacka
        self.model = model
        self.rok = rok

    def popis(self) -> str:
        return f"{self.znacka} {self.model} ({self.rok})"

    def __repr__(self) -> str:
        return f"Auto({self.znacka!r}, {self.model!r}, {self.rok})"


class BankovniUcet:
    def __init__(self, majitel: str, zustatek: float = 0):
        self.majitel = majitel
        self._zustatek = zustatek

    def vloz(self, castka: float) -> None:
        self._zustatek += castka

    def vyber(self, castka: float) -> None:
        if castka > self._zustatek:
            raise ValueError("Nedostatek prostředků!")
        self._zustatek -= castka

    def zustatek(self) -> float:
        return self._zustatek


def main() -> None:
    a = Auto("Škoda", "Octavia", 2020)
    print(a.popis())
    print(a)

    u = BankovniUcet("Eliška", 1000)
    u.vloz(500)
    u.vyber(200)
    print(f"Zůstatek: {u.zustatek()} Kč")


if __name__ == "__main__":
    main()
