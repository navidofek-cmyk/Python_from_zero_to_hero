"""Lekce 60 — asyncio.Queue producent/konzument."""

import asyncio
import random


async def producent(q: asyncio.Queue, n: int) -> None:
    for i in range(n):
        await asyncio.sleep(random.uniform(0.05, 0.2))
        await q.put(f"item-{i}")
        print(f"📦 vyrobil item-{i}")
    await q.put(None)


async def konzument(q: asyncio.Queue) -> None:
    while True:
        item = await q.get()
        if item is None:
            break
        await asyncio.sleep(random.uniform(0.1, 0.3))
        print(f"🛒 zpracoval {item}")
        q.task_done()


async def main() -> None:
    q = asyncio.Queue(maxsize=3)   # backpressure
    await asyncio.gather(producent(q, 8), konzument(q))


if __name__ == "__main__":
    asyncio.run(main())
