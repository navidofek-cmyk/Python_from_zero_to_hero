"""Lekce 61 — try/except/else/finally."""


def bezpecne_int(text: str, default: int = 0) -> int:
    try:
        return int(text)
    except ValueError:
        return default


def bezpecne_deleni(a: float, b: float) -> float | None:
    try:
        return a / b
    except ZeroDivisionError:
        print("⚠️ Dělení nulou")
        return None
    except TypeError:
        print("⚠️ Špatný typ")
        return None


def main() -> None:
    for s in ["42", "abc", "-7", "3.14"]:
        print(f"  '{s}' → {bezpecne_int(s, default=-1)}")

    print(f"\n10 / 2 = {bezpecne_deleni(10, 2)}")
    print(f"10 / 0 = {bezpecne_deleni(10, 0)}")
    print(f"10 / 'a' = {bezpecne_deleni(10, 'a')}")

    # Else / finally
    try:
        x = int("123")
    except ValueError:
        print("Chyba")
    else:
        print(f"\n✅ x = {x}")
    finally:
        print("Úklid")


if __name__ == "__main__":
    main()
