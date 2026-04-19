"""Lekce 11 — seznamy v praxi."""


def main() -> None:
    nakupni_seznam = ["mléko", "chleba", "máslo"]
    nakupni_seznam.append("sýr")
    nakupni_seznam.insert(0, "rohlík")
    nakupni_seznam.remove("chleba")

    print("📝 Nákupní seznam:")
    for i, polozka in enumerate(nakupni_seznam, 1):
        print(f"  {i}. {polozka}")

    # List comprehension
    ctverce = [x * x for x in range(1, 11)]
    suda = [x for x in ctverce if x % 2 == 0]
    print(f"\nČtverce 1-10: {ctverce}")
    print(f"Sudá z nich:  {suda}")

    # Statistika
    cisla = [3, 7, 2, 8, 5, 1, 9]
    print(f"\nČísla: {cisla}")
    print(f"Součet:  {sum(cisla)}")
    print(f"Průměr:  {sum(cisla) / len(cisla):.2f}")
    print(f"Max:     {max(cisla)}")
    print(f"Seřazeno: {sorted(cisla)}")


if __name__ == "__main__":
    main()
