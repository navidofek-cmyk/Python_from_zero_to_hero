# Program — Lekce 136: Lekce 136: Redis — key-value databáze

Patří k lekci [Lekce 136: Redis — key-value databáze](../136_redis.md).

## Jak spustit

```bash
python3 programy/l136_redis.py
```

## Zdrojový kód

### `l136_redis.py`

```py
"""Lekce 136 — Redis: key-value databáze.

Spuštění:
    # Nejdřív spusť Redis:
    docker run -d --name redis -p 6379:6379 redis:7-alpine

    uv run --with redis l136_redis.py
"""

import json
import time

try:
    import redis
except ImportError:
    print("Nainstaluj: uv add redis")
    raise

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def demo_string():
    print("\n=== String (key-value) ===")
    r.set("jmeno", "Anna")
    r.set("pocitadlo", 0)
    r.set("token", "abc123", ex=60)  # vyprší za 60s

    print(f"jmeno = {r.get('jmeno')}")
    print(f"pocitadlo = {r.incr('pocitadlo')}")
    print(f"pocitadlo = {r.incr('pocitadlo')}")
    print(f"token TTL = {r.ttl('token')}s")


def demo_hash():
    print("\n=== Hash (slovník) ===")
    r.hset("uzivatel:1", mapping={
        "jmeno": "Anna",
        "vek": "30",
        "email": "anna@example.com"
    })

    print(f"jmeno = {r.hget('uzivatel:1', 'jmeno')}")
    print(f"vše = {r.hgetall('uzivatel:1')}")
    r.hincrby("uzivatel:1", "vek", 1)
    print(f"vek po inkrementu = {r.hget('uzivatel:1', 'vek')}")


def demo_list():
    print("\n=== List (fronta) ===")
    r.delete("fronta")
    r.rpush("fronta", "ukol1", "ukol2", "ukol3")
    r.lpush("fronta", "urgent!")

    print(f"fronta = {r.lrange('fronta', 0, -1)}")
    print(f"vyjmi ze začátku = {r.lpop('fronta')}")
    print(f"vyjmi z konce = {r.rpop('fronta')}")
    print(f"délka = {r.llen('fronta')}")


def demo_sorted_set():
    print("\n=== Sorted Set (leaderboard) ===")
    r.delete("skore")
    r.zadd("skore", {"anna": 100, "bob": 85, "carol": 120, "dan": 95})
    r.zincrby("skore", 15, "bob")  # bob = 100

    top3 = r.zrevrange("skore", 0, 2, withscores=True)
    print("Top 3:")
    for jmeno, skore in top3:
        print(f"  {jmeno}: {int(skore)}")


def demo_cache():
    print("\n=== Cache ===")

    def pomala_operace(klic: str) -> dict:
        """Simulace pomalého DB dotazu."""
        time.sleep(0.3)
        return {"id": klic, "data": "výsledek", "cas": time.time()}

    def get_cached(klic: str, ttl: int = 10) -> dict:
        cached = r.get(f"cache:{klic}")
        if cached:
            print("  [HIT]")
            return json.loads(cached)
        print("  [MISS] — dotaz do DB")
        data = pomala_operace(klic)
        r.set(f"cache:{klic}", json.dumps(data), ex=ttl)
        return data

    start = time.perf_counter()
    get_cached("uzivatel:42")
    print(f"  1. volání: {(time.perf_counter()-start)*1000:.0f}ms")

    start = time.perf_counter()
    get_cached("uzivatel:42")
    print(f"  2. volání (cache): {(time.perf_counter()-start)*1000:.0f}ms")


def demo_rate_limit():
    print("\n=== Rate Limiting ===")

    def rate_limit(user_id: str, limit: int = 5, window: int = 60) -> bool:
        klic = f"rl:{user_id}:{int(time.time()) // window}"
        pipe = r.pipeline()
        pipe.incr(klic)
        pipe.expire(klic, window)
        count, _ = pipe.execute()
        return count <= limit

    user = "uzivatel_123"
    for i in range(7):
        povoleno = rate_limit(user, limit=5)
        status = "✅ OK" if povoleno else "❌ BLOKOVÁNO"
        print(f"  Request {i+1}: {status}")


def demo_pipeline():
    print("\n=== Pipeline (dávkové příkazy) ===")

    # Bez pipeline
    start = time.perf_counter()
    for i in range(100):
        r.set(f"test:{i}", i)
    bez = time.perf_counter() - start

    # S pipeline
    start = time.perf_counter()
    pipe = r.pipeline()
    for i in range(100):
        pipe.set(f"test:{i}", i)
    pipe.execute()
    s = time.perf_counter() - start

    print(f"  Bez pipeline: {bez*1000:.1f}ms")
    print(f"  S pipeline:   {s*1000:.1f}ms")
    print(f"  Zrychlení:    {bez/s:.1f}×")


def main():
    print("=" * 50)
    print("  🔴 Redis Demo")
    print("=" * 50)

    try:
        r.ping()
        print("✅ Redis připojen")
    except Exception as e:
        print(f"❌ Redis nedostupný: {e}")
        print("   Spusť: docker run -d --name redis -p 6379:6379 redis:7-alpine")
        return

    demo_string()
    demo_hash()
    demo_list()
    demo_sorted_set()
    demo_cache()
    demo_rate_limit()
    demo_pipeline()

    print("\n✅ Demo dokončeno!")


if __name__ == "__main__":
    main()

```
