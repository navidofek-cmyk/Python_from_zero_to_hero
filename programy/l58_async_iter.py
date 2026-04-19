"""Lekce 58 — async iterátory a generátory."""

import asyncio
from contextlib import asynccontextmanager


async def generuj_pakety(n: int):
    for i in range(n):
        await asyncio.sleep(0.1)
        yield f"paket-{i}"


@asynccontextmanager
async def spojeni(host: str):
    print(f"📡 Connecting to {host}...")
    await asyncio.sleep(0.05)
    try:
        yield "spojeno"
    finally:
        print(f"🔌 Disconnecting {host}")
        await asyncio.sleep(0.05)


async def main() -> None:
    async with spojeni("server.example.com"):
        async for paket in generuj_pakety(5):
            print(f"  📨 {paket}")

    # Async list comprehension
    paketu = [p async for p in generuj_pakety(3)]
    print(f"\nAsync comp: {paketu}")


if __name__ == "__main__":
    asyncio.run(main())
