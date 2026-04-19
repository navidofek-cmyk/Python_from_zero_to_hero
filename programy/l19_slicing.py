"""Lekce 19 — slicing pokročile."""


def main() -> None:
    s = "Příšerně žluťoučký kůň úpěl ďábelské ódy"
    print(f"Původní: {s}")
    print(f"Pozpátku: {s[::-1]}")
    print(f"Každé 3.: {s[::3]}")

    # Slice objekt
    kazdy_treti = slice(None, None, 3)
    print(f"\nSlice obj: {s[kazdy_treti]}")

    # Slice nahrazení
    seznam = [1, 2, 3, 4, 5, 6, 7, 8]
    seznam[2:5] = [99]            # 3 prvky → 1
    print(f"\nPo nahrazení: {seznam}")

    # Prostředních 5 z 20
    velky = list(range(100, 200))
    sklz = (len(velky) - 5) // 2
    prostrednich = velky[sklz:sklz + 5]
    print(f"Prostředních 5: {prostrednich}")


if __name__ == "__main__":
    main()
