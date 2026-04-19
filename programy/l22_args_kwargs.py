"""Lekce 22 — *args a **kwargs."""


def maximum(*cisla: int) -> int:
    if not cisla:
        raise ValueError("Žádná čísla!")
    nejvic = cisla[0]
    for x in cisla[1:]:
        if x > nejvic:
            nejvic = x
    return nejvic


def loguj_volani(funkce, *args, **kwargs):
    print(f"➡️  {funkce.__name__}(args={args}, kwargs={kwargs})")
    vysledek = funkce(*args, **kwargs)
    print(f"⬅️  vrátilo: {vysledek}")
    return vysledek


def kdo(jmeno: str, vek: int) -> str:
    return f"{jmeno}, {vek}"


def main() -> None:
    print(f"max(3, 7, 2, 9, 1) = {maximum(3, 7, 2, 9, 1)}")

    loguj_volani(maximum, 1, 5, 3, 9, 2)

    params = {"jmeno": "Bob", "vek": 11}
    print(f"\nKdo? {kdo(**params)}")

    # Spojení slovníků
    a = {"x": 1, "y": 2}
    b = {"y": 99, "z": 3}
    c = {"w": 0}
    print(f"Spojeno: { {**a, **b, **c} }")


if __name__ == "__main__":
    main()
