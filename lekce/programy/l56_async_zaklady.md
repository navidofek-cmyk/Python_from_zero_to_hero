# Program — Lekce 56: Lekce 56: `async`/`await` základ

Patří k lekci [Lekce 56: `async`/`await` základ](../56_async_zaklady.md).

## Jak spustit

```bash
python3 programy/l56_async_zaklady.py
```

## Zdrojový kód

### `l56_async_zaklady.py`

```py
"""Lekce 56 — async základy."""

import asyncio
import time


async def stahni(url: str, sleep: float = 1.0) -> str:
    await asyncio.sleep(sleep)
    return f"data z {url}"


async def main() -> None:
    print("=== Synchronně (await jeden po druhém) ===")
    start = time.perf_counter()
    for u in ["a", "b", "c"]:
        await stahni(u)
    print(f"⏱️  {time.perf_counter() - start:.2f}s\n")

    print("=== Asynchronně (gather) ===")
    start = time.perf_counter()
    vysledky = await asyncio.gather(stahni("a"), stahni("b"), stahni("c"))
    print(f"⏱️  {time.perf_counter() - start:.2f}s")
    print(vysledky)


if __name__ == "__main__":
    asyncio.run(main())

```
