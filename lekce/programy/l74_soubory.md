# Program — Lekce 74: Lekce 74: Práce se soubory

Patří k lekci [Lekce 74: Práce se soubory](../74_soubory.md).

## Jak spustit

```bash
python3 programy/l74_soubory.py
```

## Zdrojový kód

### `l74_soubory.py`

```py
"""Lekce 74 — práce se soubory."""

from pathlib import Path
import tempfile


def main() -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("První řádek\n")
        f.write("Druhý řádek\n")
        f.write("Třetí řádek\n")
        cesta = Path(f.name)

    # Čtení po řádcích
    with cesta.open(encoding="utf-8") as f:
        for i, radek in enumerate(f, 1):
            print(f"{i}: {radek.rstrip()}")

    # Append
    with cesta.open("a", encoding="utf-8") as f:
        f.write("Připojený řádek\n")

    print(f"\nObsah po append:\n{cesta.read_text(encoding='utf-8')}")
    cesta.unlink()


if __name__ == "__main__":
    main()

```
