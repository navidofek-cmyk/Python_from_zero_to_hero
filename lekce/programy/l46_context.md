# Program — Lekce 46: Lekce 46: Context managery a `with`

Patří k lekci [Lekce 46: Context managery a `with`](../46_context_managery.md).

## Jak spustit

```bash
python3 programy/l46_context.py
```

## Zdrojový kód

### `l46_context.py`

```py
"""Lekce 46 — context managery."""

import time
from contextlib import contextmanager, suppress


class Stopky:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *exc):
        self.uplynulo = time.perf_counter() - self.start
        print(f"⏱️  {self.uplynulo:.3f}s")
        return False


@contextmanager
def transakci(nazev: str):
    print(f"BEGIN {nazev}")
    try:
        yield
    except Exception as e:
        print(f"ROLLBACK ({e})")
        raise
    else:
        print("COMMIT")


def main() -> None:
    with Stopky():
        sum(range(5_000_000))

    with transakci("vklad"):
        print("  → vkládám 100 Kč")

    try:
        with transakci("vyber"):
            print("  → vybírám")
            raise ValueError("nedostatek prostředků")
    except ValueError:
        pass

    with suppress(ZeroDivisionError):
        x = 1 / 0
    print("\nDělení nulou bylo potlačeno.")


if __name__ == "__main__":
    main()

```
