# Program — Lekce 54: Lekce 54: Generátorové korutiny — `send`, `throw`, `close`

Patří k lekci [Lekce 54: Generátorové korutiny — `send`, `throw`, `close`](../54_korutiny_yield.md).

## Jak spustit

```bash
python3 programy/l54_korutiny.py
```

## Zdrojový kód

### `l54_korutiny.py`

```py
"""Lekce 54 — generátorové korutiny."""


def prubezny_prumer():
    celkem = 0.0
    pocet = 0
    prumer = None
    while True:
        x = yield prumer
        celkem += x
        pocet += 1
        prumer = celkem / pocet


def main() -> None:
    p = prubezny_prumer()
    next(p)  # rozjedi
    for x in [10, 20, 30, 40]:
        print(f"po {x}: průměr = {p.send(x)}")


if __name__ == "__main__":
    main()

```
