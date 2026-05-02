# Program — Lekce 59: Lekce 59: Async knihovny — `aiohttp`, `httpx`, `aiofiles`

Patří k lekci [Lekce 59: Async knihovny — `aiohttp`, `httpx`, `aiofiles`](../59_async_knihovny.md).

## Jak spustit

```bash
python3 programy/l59_httpx_demo.py
```

## Zdrojový kód

### `l59_httpx_demo.py`

```py
"""Lekce 59 — httpx async demo.

Vyžaduje:
    pip install httpx
nebo:
    uv add httpx
"""

import asyncio
import time


async def main() -> None:
    try:
        import httpx
    except ImportError:
        print("❌ Chybí httpx. Spusť: pip install httpx")
        return

    urls = [f"https://httpbin.org/delay/1?id={i}" for i in range(5)]

    async with httpx.AsyncClient(timeout=10) as client:
        start = time.perf_counter()
        responses = await asyncio.gather(
            *(client.get(u) for u in urls),
            return_exceptions=True,
        )
        cas = time.perf_counter() - start

    print(f"⏱️  5 requestů paralelně: {cas:.2f}s")
    for r in responses:
        if isinstance(r, Exception):
            print(f"  ❌ {r}")
        else:
            print(f"  ✅ {r.status_code}")


if __name__ == "__main__":
    asyncio.run(main())

```
