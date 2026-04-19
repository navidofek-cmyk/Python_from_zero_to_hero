"""Lekce 32 — atributy instance vs třídy."""


class Pes:
    pocet_psu = 0   # atribut TŘÍDY

    def __init__(self, jmeno: str):
        self.jmeno = jmeno
        self.triky: list[str] = []   # ✅ vlastní pro každého
        Pes.pocet_psu += 1

    def nauc(self, trik: str) -> None:
        self.triky.append(trik)


class Trezor:
    def __init__(self, obsah: str, pin: str):
        self._obsah = obsah
        self.__pin = pin

    def otevri(self, pin: str) -> str:
        if pin != self.__pin:
            return "❌ Špatný PIN"
        return f"📦 {self._obsah}"


def main() -> None:
    rex = Pes("Rex")
    bonzo = Pes("Bonzo")
    rex.nauc("sedni")
    rex.nauc("lehni")
    bonzo.nauc("aport")
    print(f"Rex umí: {rex.triky}")
    print(f"Bonzo umí: {bonzo.triky}")
    print(f"Celkem psů: {Pes.pocet_psu}")

    t = Trezor("100 zlatých", "1234")
    print(t.otevri("0000"))
    print(t.otevri("1234"))


if __name__ == "__main__":
    main()
