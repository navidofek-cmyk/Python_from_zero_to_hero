# Program — Lekce 64: Lekce 64: `ExceptionGroup` a `except*` (Python 3.11+)

Patří k lekci [Lekce 64: `ExceptionGroup` a `except*` (Python 3.11+)](../64_exception_groups.md).

## Jak spustit

```bash
python3 programy/l64_exception_group.py
```

## Zdrojový kód

### `l64_exception_group.py`

```py
"""Lekce 64 — ExceptionGroup a except*."""


def validuj(data: dict) -> None:
    chyby: list[Exception] = []

    if "jmeno" not in data:
        chyby.append(ValueError("chybí jmeno"))
    if "vek" not in data:
        chyby.append(ValueError("chybí vek"))
    elif not isinstance(data["vek"], int):
        chyby.append(TypeError("vek musí být int"))
    if data.get("email") and "@" not in data["email"]:
        chyby.append(ValueError("špatný email"))

    if chyby:
        raise ExceptionGroup("Validace selhala", chyby)


def main() -> None:
    spatny = {"vek": "deset", "email": "neplatny"}

    try:
        validuj(spatny)
    except* ValueError as eg:
        print("📝 Hodnoty:")
        for e in eg.exceptions:
            print(f"  - {e}")
    except* TypeError as eg:
        print("📐 Typy:")
        for e in eg.exceptions:
            print(f"  - {e}")


if __name__ == "__main__":
    main()

```
