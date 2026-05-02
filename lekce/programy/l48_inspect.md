# Program — Lekce 48: Lekce 48: Modul `inspect`

Patří k lekci [Lekce 48: Modul `inspect`](../48_inspect.md).

## Jak spustit

```bash
python3 programy/l48_inspect.py
```

## Zdrojový kód

### `l48_inspect.py`

```py
"""Lekce 48 — inspect."""

import inspect
import math


def secti(a: int, b: int = 0, *args, **kwargs) -> int:
    """Sečte a + b."""
    return a + b


def main() -> None:
    sig = inspect.signature(secti)
    print(f"Signature: {sig}")
    for jmeno, p in sig.parameters.items():
        print(f"  {jmeno}: kind={p.kind.name}, default={p.default!r}")

    print("\nFunkce z math (prvních 10):")
    funkce = [j for j, h in inspect.getmembers(math) if inspect.isbuiltin(h)]
    for j in funkce[:10]:
        print(f"  {j}")


if __name__ == "__main__":
    main()

```
