# Program — Lekce 57: Lekce 57: `asyncio` — `gather`, `create_task`, `TaskGroup`

Patří k lekci [Lekce 57: `asyncio` — `gather`, `create_task`, `TaskGroup`](../57_asyncio_pokrocile.md).

## Jak spustit

```bash
python3 programy/l57_taskgroup.py
```

## Zdrojový kód

### `l57_taskgroup.py`

```py
"""Lekce 57 — TaskGroup, semafor, timeout."""

import asyncio
import random


async def stahni(client_id: int, sem: asyncio.Semaphore) -> str:
    async with sem:
        cas = random.uniform(0.1, 0.5)
        await asyncio.sleep(cas)
        return f"client-{client_id} ({cas:.2f}s)"


async def main() -> None:
    sem = asyncio.Semaphore(3)   # max 3 najednou

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(stahni(i, sem)) for i in range(10)]

    print("Hotovo:")
    for t in tasks:
        print(f"  {t.result()}")

    # Timeout
    try:
        async with asyncio.timeout(0.05):
            await asyncio.sleep(1)
    except TimeoutError:
        print("\n⏰ Timeout po 0.05s!")


if __name__ == "__main__":
    asyncio.run(main())

```
