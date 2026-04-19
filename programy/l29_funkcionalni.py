"""Lekce 29 — map, filter, comprehensions, generátory."""


def main() -> None:
    cisla = [1, 2, 3, 4, 5]

    # map vs comprehension
    ctverce_map = list(map(lambda x: x * x, cisla))
    ctverce_comp = [x * x for x in cisla]
    print(f"map:  {ctverce_map}")
    print(f"comp: {ctverce_comp}")

    # Filter
    suda = [x for x in range(10) if x % 2 == 0]
    print(f"Sudá: {suda}")

    # Generátor — úspora paměti
    soucet_velky = sum(x * x for x in range(1_000_000))
    print(f"Součet čtverců 0..999999 = {soucet_velky:,}")

    # Dict comp
    delky = {slovo: len(slovo) for slovo in ["pes", "kočka", "myš"]}
    print(f"Délky: {delky}")

    # Zploštění
    matice = [[1, 2], [3, 4], [5, 6]]
    ploche = [x for radek in matice for x in radek]
    print(f"Zploštění {matice} = {ploche}")

    # Násobilka
    nasobilka = [[i * j for j in range(1, 6)] for i in range(1, 6)]
    print("\nNásobilka 5×5:")
    for r in nasobilka:
        print("  ", r)


if __name__ == "__main__":
    main()
