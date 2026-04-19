"""Mini-projekt po sekci IV: RPG postavy.

Procvičuje: třídy, dědičnost, super(), property, dataclass, Enum,
operátorové přetížení.
"""

import random
from dataclasses import dataclass, field
from enum import Enum


class Trida(Enum):
    BOJOVNIK = "🛡️ Bojovník"
    MAG = "🔮 Mág"
    LUKOSTRELEC = "🏹 Lukostřelec"


@dataclass
class Statistika:
    sila: int = 10
    obratnost: int = 10
    inteligence: int = 10

    def __add__(self, other):
        return Statistika(
            self.sila + other.sila,
            self.obratnost + other.obratnost,
            self.inteligence + other.inteligence,
        )


class Postava:
    """Základní postava (rodič)."""

    def __init__(self, jmeno: str, trida: Trida, staty: Statistika):
        self.jmeno = jmeno
        self.trida = trida
        self.staty = staty
        self._zivoty = self.max_zivoty
        self.uroven = 1

    @property
    def max_zivoty(self) -> int:
        return 50 + self.staty.sila * 5

    @property
    def zivoty(self) -> int:
        return self._zivoty

    @property
    def je_naziv(self) -> bool:
        return self._zivoty > 0

    def utoc(self) -> int:
        """Vrátí poškození."""
        return self.staty.sila + random.randint(1, 6)

    def utrp(self, poskozeni: int) -> None:
        self._zivoty = max(0, self._zivoty - poskozeni)

    def __repr__(self):
        return f"{self.trida.value} {self.jmeno} ({self._zivoty}/{self.max_zivoty} HP)"


class Bojovnik(Postava):
    def __init__(self, jmeno: str):
        super().__init__(jmeno, Trida.BOJOVNIK, Statistika(sila=15, obratnost=10, inteligence=5))

    def utoc(self) -> int:
        # Bojovník má bonus za zbroj
        return super().utoc() + 3


class Mag(Postava):
    def __init__(self, jmeno: str):
        super().__init__(jmeno, Trida.MAG, Statistika(sila=5, obratnost=8, inteligence=18))

    def utoc(self) -> int:
        # Mág útočí inteligencí
        return self.staty.inteligence + random.randint(1, 8)


class Lukostrelec(Postava):
    def __init__(self, jmeno: str):
        super().__init__(jmeno, Trida.LUKOSTRELEC, Statistika(sila=8, obratnost=16, inteligence=10))

    def utoc(self) -> int:
        # Šance na kritický zásah
        zaklad = self.staty.obratnost + random.randint(1, 4)
        if random.random() < 0.2:
            print("  💥 KRITICKÝ ZÁSAH!")
            zaklad *= 2
        return zaklad


def souboj(a: Postava, b: Postava) -> Postava:
    print(f"\n⚔️  {a.jmeno} vs {b.jmeno}")
    kolo = 1
    while a.je_naziv and b.je_naziv:
        print(f"\nKolo {kolo}:")
        for utocnik, branici in [(a, b), (b, a)]:
            if not branici.je_naziv:
                continue
            damage = utocnik.utoc()
            branici.utrp(damage)
            print(f"  {utocnik.jmeno} → {branici.jmeno} za {damage} (zbývá {branici.zivoty})")
        kolo += 1

    vitez = a if a.je_naziv else b
    print(f"\n🏆 Vítěz: {vitez}")
    return vitez


def main() -> None:
    random.seed()
    rytir = Bojovnik("Sir Lancelot")
    carodej = Mag("Gandalf")
    legolas = Lukostrelec("Legolas")

    print("Postavy:")
    for p in [rytir, carodej, legolas]:
        print(f"  {p}")

    souboj(rytir, carodej)
    print("\n" + "=" * 40)
    souboj(legolas, Bojovnik("Goblin"))


if __name__ == "__main__":
    main()
