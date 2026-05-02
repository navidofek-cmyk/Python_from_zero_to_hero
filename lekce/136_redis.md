# Lekce 136: Redis — key-value databáze

Redis je **in-memory databáze** — extrémně rychlá (sub-millisecond), podporuje bohaté datové struktury. Používá se na cache, sessions, pub/sub, rate limiting, fronty.

---

## 🚀 Instalace

```bash
# Závislosti
uv add redis hiredis

# Redis server (Docker — nejjednodušší)
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Nebo lokálně
# Ubuntu: sudo apt install redis-server && sudo systemctl start redis
# macOS:  brew install redis && brew services start redis
```

---

## 🔌 Připojení

```python
import redis

# Synchronní
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
r.ping()  # True

# Z URL
r = redis.from_url("redis://localhost:6379/0", decode_responses=True)

# S heslem
r = redis.Redis(host="localhost", password="tajne", decode_responses=True)
```

---

## 🗂️ Datové struktury

### String — základní key-value

```python
r.set("jmeno", "Anna")
r.set("pocitadlo", 0)

print(r.get("jmeno"))       # "Anna"
print(r.incr("pocitadlo"))  # 1
print(r.incr("pocitadlo"))  # 2

# TTL (expirace)
r.set("token", "abc123", ex=3600)   # vyprší za 1 hodinu
r.set("token", "abc123", px=5000)   # vyprší za 5 sekund
r.ttl("token")                       # zbývající čas v sekundách
r.persist("token")                   # zruší expiraci
```

### Hash — slovník v Redis

```python
r.hset("uzivatel:1", mapping={"jmeno": "Anna", "vek": "30", "email": "anna@example.com"})
r.hget("uzivatel:1", "jmeno")         # "Anna"
r.hmget("uzivatel:1", "jmeno", "vek") # ["Anna", "30"]
r.hgetall("uzivatel:1")               # {"jmeno": "Anna", "vek": "30", ...}
r.hincrby("uzivatel:1", "vek", 1)     # vek = 31
r.hdel("uzivatel:1", "email")
```

### List — fronta / zásobník

```python
r.rpush("fronta", "ukol1", "ukol2", "ukol3")  # přidej na konec
r.lpush("fronta", "urgentni")                  # přidej na začátek
r.lrange("fronta", 0, -1)   # celý list
r.lpop("fronta")            # "urgentni" — vyjmi ze začátku
r.rpop("fronta")            # "ukol3" — vyjmi z konce
r.llen("fronta")            # délka
r.blpop("fronta", timeout=5)  # blocking pop — čeká max 5s
```

### Set — množina (unikátní hodnoty)

```python
r.sadd("oblibene", "python", "rust", "go")
r.sadd("oblibene", "python")  # duplikát ignorován
r.smembers("oblibene")        # {"python", "rust", "go"}
r.sismember("oblibene", "java")  # False
r.scard("oblibene")              # 3

# Množinové operace
r.sadd("backend", "python", "java", "go")
r.sunion("oblibene", "backend")   # sjednocení
r.sinter("oblibene", "backend")   # průnik
r.sdiff("oblibene", "backend")    # rozdíl
```

### Sorted Set — seřazená množina (leaderboard)

```python
r.zadd("skore", {"anna": 100, "bob": 85, "carol": 120})
r.zincrby("skore", 10, "bob")              # bob = 95
r.zrange("skore", 0, -1, withscores=True)  # od nejmenšího
r.zrevrange("skore", 0, 2, withscores=True)  # top 3
r.zrank("skore", "bob")                    # pozice (od 0)
r.zscore("skore", "anna")                  # 100.0
```

---

## ⚡ Cache — nejčastější použití

```python
import json
import hashlib
import redis

r = redis.Redis(decode_responses=True)


def cache_klic(func_name: str, *args) -> str:
    klic = f"{func_name}:{hashlib.md5(str(args).encode()).hexdigest()[:8]}"
    return klic


def nacti_data_z_db(uzivatel_id: int) -> dict:
    """Simulace pomalého DB dotazu."""
    import time
    time.sleep(0.5)
    return {"id": uzivatel_id, "jmeno": "Anna", "email": "anna@example.com"}


def get_uzivatel(uzivatel_id: int) -> dict:
    klic = cache_klic("uzivatel", uzivatel_id)

    # Cache hit?
    cached = r.get(klic)
    if cached:
        print("  [CACHE HIT]")
        return json.loads(cached)

    # Cache miss — dotaz do DB
    print("  [CACHE MISS] — dotaz do DB")
    data = nacti_data_z_db(uzivatel_id)
    r.set(klic, json.dumps(data), ex=300)  # cache na 5 minut
    return data
```

---

## 🔒 Rate limiting

```python
def rate_limit(user_id: str, limit: int = 10, window: int = 60) -> bool:
    """Vrátí False pokud uživatel překročil limit požadavků za window sekund."""
    klic = f"ratelimit:{user_id}:{int(time.time()) // window}"

    pipe = r.pipeline()
    pipe.incr(klic)
    pipe.expire(klic, window)
    count, _ = pipe.execute()

    return count <= limit
```

---

## 📡 Pub/Sub — publish / subscribe

```python
import threading
import time
import redis

r = redis.Redis(decode_responses=True)


def subscriber():
    sub = r.pubsub()
    sub.subscribe("novinky")
    print("Subscriber naslouchá...")
    for zprava in sub.listen():
        if zprava["type"] == "message":
            print(f"  Přijato: {zprava['data']}")


# Spusť subscriber v jiném vlákně
t = threading.Thread(target=subscriber, daemon=True)
t.start()

time.sleep(0.1)
r.publish("novinky", "Ahoj světe!")
r.publish("novinky", "Druhá zpráva")
time.sleep(0.1)
```

---

## 🔁 Pipeline — dávkové příkazy

```python
# Bez pipeline — 1000 round-trips
for i in range(1000):
    r.set(f"klic:{i}", i)

# S pipeline — 1 round-trip
pipe = r.pipeline()
for i in range(1000):
    pipe.set(f"klic:{i}", i)
pipe.execute()  # 10-50× rychlejší
```

---

## 🔐 Transakce (MULTI/EXEC)

```python
# Atomická operace
with r.pipeline() as pipe:
    while True:
        try:
            pipe.watch("ucet:1", "ucet:2")
            zustatok1 = int(r.get("ucet:1") or 0)
            zustatok2 = int(r.get("ucet:2") or 0)

            pipe.multi()
            pipe.set("ucet:1", zustatok1 - 100)
            pipe.set("ucet:2", zustatok2 + 100)
            pipe.execute()
            break
        except redis.WatchError:
            continue  # někdo změnil hodnotu — zkus znovu
```

---

## ⚡ Async Redis

```python
import asyncio
import redis.asyncio as aioredis

async def main():
    r = aioredis.from_url("redis://localhost", decode_responses=True)
    await r.set("klic", "hodnota")
    print(await r.get("klic"))
    await r.aclose()

asyncio.run(main())
```

---

## 🎯 Kdy použít Redis

| Případ | Řešení |
|--------|--------|
| Cache API odpovědí | `SET key value EX ttl` |
| Session storage | Hash |
| Leaderboard | Sorted Set |
| Fronta úloh | List + `BLPOP` |
| Pub/Sub události | Pub/Sub |
| Rate limiting | INCR + EXPIRE |
| Distributed lock | `SET NX EX` |
| Real-time počítadla | INCR |

---

## ✏️ Cvičení

1. Spusť Redis v Dockeru, připoj se a ulož/přečti 5 klíčů.
2. Implementuj jednoduchý **session store** — `set_session(id, data)` + `get_session(id)`.
3. Vytvoř **leaderboard** hráčů přes Sorted Set, přidej 10 hráčů a vypiš top 3.
4. Implementuj **distribuovaný zámek** pomocí `SET key NX EX 10`.
5. Napiš jednoduchý **task queue** — producer přidává úkoly přes RPUSH, worker je zpracovává přes BLPOP.
