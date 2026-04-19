"""Lekce 13 — slovníky a počítání slov."""


def pocitani_slov(text: str) -> dict[str, int]:
    pocty: dict[str, int] = {}
    for slovo in text.lower().split():
        pocty[slovo] = pocty.get(slovo, 0) + 1
    return pocty


def main() -> None:
    seznam_kontaktu = {
        "Eliška": "+420 123 456 789",
        "Bob":    "+420 987 654 321",
        "Cyril":  "+420 555 555 555",
    }

    # Bezpečné čtení
    jmeno = input("Komu zavoláš? ")
    print(f"📞 {seznam_kontaktu.get(jmeno, 'Neznámý kontakt')}")

    # Procházení
    print("\n📒 Celý seznam:")
    for jmeno, telefon in seznam_kontaktu.items():
        print(f"  {jmeno:10s} → {telefon}")

    # Počítání slov
    text = "ahoj svete ahoj kamarade svete svete"
    pocty = pocitani_slov(text)
    print(f"\n🔢 Počty: {pocty}")

    # Spojení slovníků (Python 3.9+)
    a = {"x": 1, "y": 2}
    b = {"y": 99, "z": 3}
    print(f"\nSpojeno: {a | b}")


if __name__ == "__main__":
    main()
