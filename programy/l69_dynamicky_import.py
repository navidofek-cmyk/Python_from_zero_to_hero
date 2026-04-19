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
