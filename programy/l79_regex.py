"""Lekce 79 — regex."""

import re


EMAIL = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
PSC = re.compile(r"\b\d{3}\s?\d{2}\b")
DATUM = re.compile(r"(?P<rok>\d{4})-(?P<mesic>\d{2})-(?P<den>\d{2})")


def main() -> None:
    text = "Adresa: Hlavní 12, 110 00 Praha. Mail anna@example.com a bob@test.cz."

    # Najdi PSČ
    print(f"PSČ: {PSC.findall(text)}")

    # Najdi emaily
    emaily = re.findall(r"[\w.+-]+@[\w.-]+", text)
    print(f"Emaily: {emaily}")

    # Validuj
    for e in emaily + ["spatny", "tez@spatne"]:
        ok = bool(EMAIL.match(e))
        print(f"  {e:30s} → {'✅' if ok else '❌'}")

    # Pojmenované skupiny
    m = DATUM.search("Setkání 2026-04-18 ve 14:00")
    if m:
        print(f"\nDatum: {m.groupdict()}")


if __name__ == "__main__":
    main()
