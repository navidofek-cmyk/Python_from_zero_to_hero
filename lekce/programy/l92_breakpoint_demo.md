# Program — Lekce 92: Lekce 92: Debugging — `pdb`, `breakpoint()`, `traceback`

Patří k lekci [Lekce 92: Debugging — `pdb`, `breakpoint()`, `traceback`](../92_debugging.md).

## Jak spustit

```bash
python3 programy/l92_breakpoint_demo.py
```

## Zdrojový kód

### `l92_breakpoint_demo.py`

```py
"""Lekce 92 — debugger demo.

Spuštění:
    python3 l92_breakpoint_demo.py
    (V breakpointu zkus: l, p x, p y, n, c)
"""


def vypocet(x: int) -> int:
    y = x * 2
    z = y + 10
    # Odkomentuj pro debugger:
    # breakpoint()
    return z * x


def main() -> None:
    print(f"vypocet(5) = {vypocet(5)}")


if __name__ == "__main__":
    main()

```
