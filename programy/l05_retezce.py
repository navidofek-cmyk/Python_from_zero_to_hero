"""Lekce 5 — řetězce a f-stringy."""


def main() -> None:
    jmeno = "Eliška"
    vek = 10

    # Slicing
    print(f"První písmeno: {jmeno[0]}")
    print(f"Poslední:      {jmeno[-1]}")
    print(f"První tři:     {jmeno[:3]}")
    print(f"Pozpátku:      {jmeno[::-1]}")

    # F-stringy
    print(f"\nAhoj {jmeno}, je ti {vek} let.")
    print(f"Za rok ti bude {vek + 1}.")
    print(f"Velkými: {jmeno.upper()}")

    # Formátování čísel
    pi = 3.14159265
    print(f"\nPi na 2 místa: {pi:.2f}")
    print(f"Milion s oddělovači: {1_000_000:,}")
    print(f"Tři čtvrtě jako %: {0.75:.1%}")
    print(f"Doplnění nulami: {42:05d}")

    # Debug trik
    print(f"\nDebug: {pi=}")

    # Metody
    text = "  ahoj svete  "
    print(f"\nstrip:    '{text.strip()}'")
    print(f"upper:    '{text.upper()}'")
    print(f"split:    {text.split()}")
    print(f"replace:  '{text.replace('o', '0')}'")


if __name__ == "__main__":
    main()
