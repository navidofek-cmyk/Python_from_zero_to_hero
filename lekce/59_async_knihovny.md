# Lekce 59: Async knihovny — `aiohttp`, `httpx`, `aiofiles`

## 🌐 `httpx` — moderní HTTP klient

`requests` je super, ale **synchronní**. **`httpx`** umí oboje — synchronní i async.

```bash
pip install httpx
```

### Synchronně (jako requests)

```python
import httpx

response = httpx.get("https://httpbin.org/get")
print(response.json())
```

### Asynchronně

```python
import asyncio
import httpx

async def hlavni():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://httpbin.org/get")
        print(response.json())

asyncio.run(hlavni())
```

### Paralelní stahování

```python
async def stahni(client, url):
    r = await client.get(url)
    return r.status_code, len(r.text)

async def hlavni():
    urls = ["https://httpbin.org/get"] * 10
    async with httpx.AsyncClient() as client:
        vysledky = await asyncio.gather(*(stahni(client, u) for u in urls))
    print(vysledky)
```

10 requestů paralelně!

---

## 🌐 `aiohttp` — alternativa

Trochu starší, většinou pro servery. `httpx` je modernější volba pro klienty.

```python
import aiohttp

async with aiohttp.ClientSession() as session:
    async with session.get("https://example.com") as r:
        print(await r.text())
```

---

## 📁 `aiofiles` — async I/O souborů

Klasický `open` blokuje. `aiofiles` umí asynchronní zápis/čtení.

```bash
pip install aiofiles
```

```python
import aiofiles

async def cti_a_napis():
    async with aiofiles.open("vstup.txt") as f:
        obsah = await f.read()

    async with aiofiles.open("vystup.txt", "w") as f:
        await f.write(obsah.upper())
```

---

## 🗃️ Databáze

| | Async knihovna |
|---|---|
| PostgreSQL | `asyncpg`, `psycopg` (3.x) |
| SQLite | `aiosqlite` |
| MongoDB | `motor` |
| Redis | `redis-py` (async support) |
| SQLAlchemy | `SQLAlchemy 2.x` má async |

```python
import asyncpg

async def main():
    conn = await asyncpg.connect("postgres://user:pass@host/db")
    rows = await conn.fetch("SELECT * FROM users")
    await conn.close()
```

---

## 🎯 Doporučené verze

- **HTTP klient**: `httpx` (umí sync i async, super API)
- **Web framework**: `FastAPI` (postavený na async)
- **Soubory**: `aiofiles`
- **DB**: SQLAlchemy 2.x s async, nebo přímo `asyncpg`

---

## ⚠️ Nepleť synchronní a async

```python
async def main():
    requests.get("...")    # ❌ blokuje event loop! Použij httpx.AsyncClient.
    open("...")             # ❌ blokuje. Použij aiofiles.
    time.sleep(1)           # ❌ blokuje. Použij asyncio.sleep.
```

---

## ✏️ Cvičení

1. **Httpx:** Stáhni 5 URL paralelně přes `httpx.AsyncClient`. Změř čas.
2. **Aiofiles:** Async přečti velký soubor a spočítej řádky.
3. **Mix:** Stáhni JSON z URL a ulož ho do souboru — vše asynchronně.
4. **Bench:** Porovnej `httpx` synchronní vs async pro 10 URL.
