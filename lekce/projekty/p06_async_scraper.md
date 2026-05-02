# Projekt 6: Async web scraper

Mini-projekt po **sekci VI (Async)**. Stahuje více URL paralelně s omezením souběžnosti přes semafor.

**Použité koncepty:** generátory (52), `async/await` (56), `asyncio.gather` (57), semafor (86), `asynccontextmanager` (46).

## Jak spustit

```bash
pip install httpx
python3 projekty/06_async_scraper/scraper.py
```

## Zdrojový kód — `scraper.py`

```python
"""Mini-projekt po sekci VI: Async web scraper.

Procvičuje: generátory, async/await, gather, semafor, asynccontextmanager,
producent-konzument vzor.

Vyžaduje:
    pip install httpx
nebo:
    uv add httpx
"""

import asyncio
import time
from dataclasses import dataclass


@dataclass
class Vysledek:
    url: str
    status: int
    velikost: int
    cas: float


async def stahni(client, url: str, sem: asyncio.Semaphore) -> Vysledek:
    async with sem:
        start = time.perf_counter()
        try:
            r = await client.get(url, timeout=10)
            return Vysledek(url, r.status_code, len(r.content), time.perf_counter() - start)
        except Exception as e:
            print(f"❌ {url}: {e}")
            return Vysledek(url, 0, 0, time.perf_counter() - start)


async def scraper(urls: list[str], max_paralelne: int = 5) -> list[Vysledek]:
    try:
        import httpx
    except ImportError:
        print("❌ Nainstaluj httpx: pip install httpx")
        return []

    sem = asyncio.Semaphore(max_paralelne)
    async with httpx.AsyncClient() as client:
        return await asyncio.gather(*(stahni(client, u, sem) for u in urls))


def main() -> None:
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/json",
        "https://httpbin.org/html",
        "https://httpbin.org/uuid",
        "https://httpbin.org/ip",
        "https://httpbin.org/user-agent",
        "https://httpbin.org/headers",
    ]

    print(f"🌐 Stahuji {len(urls)} URL paralelně...\n")
    start = time.perf_counter()
    vysledky = asyncio.run(scraper(urls, max_paralelne=4))
    celkem = time.perf_counter() - start

    print(f"\n📊 Výsledky:")
    for v in vysledky:
        print(f"  [{v.status:3d}] {v.cas:.2f}s {v.velikost:6d}B  {v.url}")

    uspesne = sum(1 for v in vysledky if v.status == 200)
    print(f"\n✅ {uspesne}/{len(urls)} úspěšných")
    print(f"⏱️  Celkem: {celkem:.2f}s (sequenčně by bylo cca {sum(v.cas for v in vysledky):.2f}s)")


if __name__ == "__main__":
    main()
```
