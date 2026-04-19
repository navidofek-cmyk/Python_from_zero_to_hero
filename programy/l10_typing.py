"""Lekce 10 — komentáře, docstringy, typové hinty.

Modul ukazuje krásný kód podle PEP 8.
"""

DEFAULTNI_SAZBA: float = 0.21


def vypocet_dph(cena: float, sazba: float = DEFAULTNI_SAZBA) -> float:
    """Spočítá cenu včetně DPH.

    Args:
        cena: Cena bez DPH v Kč.
        sazba: Sazba DPH (0.21 = 21%).

    Returns:
        Cena včetně DPH zaokrouhlená na haléře.
    """
    return round(cena * (1 + sazba), 2)


def pozdrav(jmeno: str, vykricnik: bool = False) -> str:
    """Vytvoří pozdrav na míru."""
    konec = "!" if vykricnik else "."
    return f"Ahoj {jmeno}{konec}"


def main() -> None:
    print(pozdrav("Eliško", vykricnik=True))
    print(f"100 Kč s DPH = {vypocet_dph(100)} Kč")
    print(f"100 Kč s 15% = {vypocet_dph(100, sazba=0.15)} Kč")


if __name__ == "__main__":
    main()
