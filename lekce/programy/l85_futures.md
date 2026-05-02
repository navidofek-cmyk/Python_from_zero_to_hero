# Program — Lekce 85: Lekce 85: `concurrent.futures`

Patří k lekci [Lekce 85: `concurrent.futures`](../85_concurrent_futures.md).

## Jak spustit

```bash
python3 programy/l85_futures.py
```

## Zdrojový kód

### `l85_futures.py`

```py
"""Lekce 85 — concurrent.futures."""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def io_uloha(jmeno: str, doba: float) -> str:
    time.sleep(doba)
    return f"{jmeno} hotovo za {doba}s"


def main() -> None:
    ulohy = [("A", 0.5), ("B", 1.0), ("C", 0.3), ("D", 0.7)]

    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = [ex.submit(io_uloha, j, d) for j, d in ulohy]
        print("Výsledky podle pořadí dokončení:")
        for f in as_completed(futures):
            print(f"  {f.result()}")


if __name__ == "__main__":
    main()

```
