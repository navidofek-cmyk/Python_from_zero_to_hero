# Program — Lekce 67: Lekce 67: Moduly a `import` systém

Patří k lekci [Lekce 67: Moduly a `import` systém](../67_moduly_import.md).

## Jak spustit

```bash
python3 programy/l67_balicek_demo/<soubor>.py
```

## Zdrojový kód

### `__init__.py`

```py
"""Lekce 67 — demo balíček s re-exportem."""

from .matematika import nasob, deli, faktorial

__all__ = ["nasob", "deli", "faktorial"]
__version__ = "0.1.0"

```

### `matematika.py`

```py
"""Modul matematika v balíčku."""


def nasob(a: float, b: float) -> float:
    return a * b


def deli(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("dělení nulou")
    return a / b


def faktorial(n: int) -> int:
    if n == 0:
        return 1
    return n * faktorial(n - 1)

```
