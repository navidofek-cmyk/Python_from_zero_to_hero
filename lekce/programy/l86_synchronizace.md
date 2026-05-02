# Program — Lekce 86: Lekce 86: Synchronizační primitiva

Patří k lekci [Lekce 86: Synchronizační primitiva](../86_synchronizace.md).

## Jak spustit

```bash
python3 programy/l86_synchronizace.py
```

## Zdrojový kód

### `l86_synchronizace.py`

```py
"""Lekce 86 — Queue producent/konzument s threading."""

import queue
import threading
import time
import random


def producent(q: queue.Queue, n: int) -> None:
    for i in range(n):
        item = f"item-{i}"
        time.sleep(random.uniform(0.05, 0.15))
        q.put(item)
        print(f"📦 vyrobil {item}")
    for _ in range(POCET_KONZ):
        q.put(None)


def konzument(q: queue.Queue, jmeno: str) -> None:
    while True:
        item = q.get()
        if item is None:
            q.task_done()
            break
        time.sleep(random.uniform(0.1, 0.3))
        print(f"  🛒 [{jmeno}] zpracoval {item}")
        q.task_done()


POCET_KONZ = 3


def main() -> None:
    q = queue.Queue(maxsize=4)
    p = threading.Thread(target=producent, args=(q, 10))
    konz = [threading.Thread(target=konzument, args=(q, f"K{i}")) for i in range(POCET_KONZ)]

    p.start()
    for k in konz:
        k.start()
    p.join()
    for k in konz:
        k.join()


if __name__ == "__main__":
    main()

```
