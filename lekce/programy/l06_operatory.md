# Program — Lekce 6: Lekce 6: Operátory

Patří k lekci [Lekce 6: Operátory](../06_operatory.md).

## Jak spustit

```bash
python3 programy/l06_operatory.py
```

## Zdrojový kód

### `l06_operatory.py`

```py
"""Lekce 6 — operátory v praxi."""


def main() -> None:
    # Aritmetické
    print(f"5 ** 3   = {5 ** 3}")
    print(f"10 % 3   = {10 % 3}")
    print(f"10 // 3  = {10 // 3}")

    # Sudé/liché trik
    for n in range(1, 6):
        kind = "sudé" if n % 2 == 0 else "liché"
        print(f"{n} je {kind}")

    # Řetězené porovnání
    vek = 15
    if 0 < vek < 18:
        print(f"\nVěk {vek}: nezletilý/á")

    # Walrus :=
    print("\nNapiš pár věcí (prázdný řádek = konec):")
    while (radek := input("> ").strip()) != "":
        print(f"  napsal jsi: {radek}")
    print("Hotovo.")


if __name__ == "__main__":
    main()

```
