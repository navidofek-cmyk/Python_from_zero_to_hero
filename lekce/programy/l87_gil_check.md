# Program — Lekce 87: Lekce 87: Free-threaded Python (3.13+) a `subinterpreters`

Patří k lekci [Lekce 87: Free-threaded Python (3.13+) a `subinterpreters`](../87_no_gil_subinterpreters.md).

## Jak spustit

```bash
python3 programy/l87_gil_check.py
```

## Zdrojový kód

### `l87_gil_check.py`

```py
"""Lekce 87 — kontrola GIL stavu."""

import sys


def main() -> None:
    print(f"Python: {sys.version}")
    if hasattr(sys, "_is_gil_enabled"):
        print(f"GIL enabled: {sys._is_gil_enabled()}")
    else:
        print("GIL je vždy enabled (Python <3.13).")


if __name__ == "__main__":
    main()

```
