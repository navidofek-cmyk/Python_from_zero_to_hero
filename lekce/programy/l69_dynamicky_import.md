# Program — Lekce 69: Lekce 69: `importlib`, dynamické importy, lazy import

Patří k lekci [Lekce 69: `importlib`, dynamické importy, lazy import](../69_importlib.md).

## Jak spustit

```bash
python3 programy/l69_dynamicky_import.py
```

## Zdrojový kód

### `l69_dynamicky_import.py`

```py
"""Lekce 69 — dynamický import."""

import importlib


def lazy_numpy():
    """Importuje numpy až při prvním volání."""
    import numpy as np
    return np


def main() -> None:
    moduly = ["math", "os", "sys", "json"]
    for jmeno in moduly:
        m = importlib.import_module(jmeno)
        print(f"  {jmeno}: {m}")

    print("\n--- lazy import ---")
    try:
        np = lazy_numpy()
        print(f"  numpy: {np.__version__}")
    except ImportError:
        print("  (numpy není nainstalovaný)")


if __name__ == "__main__":
    main()

```
