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
