# Program — Lekce 8: Lekce 8: Podmínky — `if`, `elif`, `else`

Patří k lekci [Lekce 8: Podmínky — `if`, `elif`, `else`](../08_podminky.md).

## Jak spustit

```bash
python3 programy/l08_podminky.py
```

## Zdrojový kód

### `l08_podminky.py`

```py
"""Lekce 8 — podmínky a truthy/falsy."""


def znamkuj(procenta: int) -> int:
    if procenta >= 90:
        return 1
    elif procenta >= 75:
        return 2
    elif procenta >= 60:
        return 3
    elif procenta >= 40:
        return 4
    else:
        return 5


def main() -> None:
    # Falsy demo
    for hodnota in [0, "", [], None, 1, "ahoj", [0]]:
        if hodnota:
            print(f"{hodnota!r:>10} → truthy")
        else:
            print(f"{hodnota!r:>10} → falsy")

    print()
    p = int(input("Procenta (0–100): "))
    print(f"Známka: {znamkuj(p)}")


if __name__ == "__main__":
    main()

```
