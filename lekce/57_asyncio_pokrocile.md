# Lekce 57: `asyncio` — `gather`, `create_task`, `TaskGroup`

## 🎯 Spouštění víc úkolů

### `gather` — počkej na všechny

```python
async def main():
    vysledky = await asyncio.gather(
        akce1(), akce2(), akce3(),
        return_exceptions=False,    # když je True, výjimky se vrátí v listu místo raise
    )
```

Spustí všechno **paralelně** a počká na všechny.

### `create_task` — spusť na pozadí

```python
async def main():
    task = asyncio.create_task(pomala_akce())
    print("Akce běží na pozadí")
    # Mezitím něco dělám...
    print("Něco jiného")
    vysledek = await task          # ← teď čekám
```

Použij když chceš **spustit a pokračovat**, počkat až později.

### `TaskGroup` (Python 3.11+) — moderní způsob

```python
async def main():
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(akce1())
        t2 = tg.create_task(akce2())
    # Při výjimce v jakémkoli tasku → ostatní se zruší a výjimka propadne ven.

    # Po with už jsou hotové
    print(t1.result(), t2.result())
```

**Doporučená moderní cesta** pro paralelní úkoly. Bezpečnější než `gather` (lépe ošetří chyby).

---

## ⏰ Timeout

### `wait_for` — jeden úkol

```python
try:
    await asyncio.wait_for(akce(), timeout=5)
except asyncio.TimeoutError:
    print("Pozdě!")
```

### `timeout` (3.11+) — kontextový

```python
async def main():
    async with asyncio.timeout(5):
        await akce()
```

---

## ❌ Cancellation

```python
task = asyncio.create_task(akce())
await asyncio.sleep(0.1)
task.cancel()                       # zruší
try:
    await task
except asyncio.CancelledError:
    print("Zrušeno")
```

V async funkci se cancellation projeví jako `CancelledError` — důležité **NEspolykat** ho:

```python
async def akce():
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("Uklízím...")
        raise                        # ← MUSÍŠ ho znovu vyhodit!
```

---

## 🚦 Synchronizace

```python
lock = asyncio.Lock()
sem = asyncio.Semaphore(5)          # max 5 najednou
event = asyncio.Event()
queue = asyncio.Queue()
```

Rate limiting přes semafor:

```python
sem = asyncio.Semaphore(10)

async def stahni(url):
    async with sem:                  # max 10 najednou
        return await fetch(url)


async def main():
    await asyncio.gather(*(stahni(u) for u in urls))
```

---

## 🎯 Praktický vzor

```python
async def main():
    urls = ["http://a", "http://b", "http://c"]

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(stahni(u)) for u in urls]

    # Po with jsou všechny hotové
    for t in tasks:
        print(t.result())
```

---

## ✏️ Cvičení

1. **TaskGroup:** Napiš `async def stahni(url, sleep)` co `await sleep` a vrátí url. Spusť 3 paralelně přes `TaskGroup`.
2. **Background:** Vytvoř task na pozadí, mezitím dělej jiné věci, na konci `await`.
3. **Timeout:** Použij `wait_for` s úlohou trvající 5s a timeoutem 2s.
4. **Semafor:** Spusť 100 úloh ale max 5 paralelně.
5. **Cancel:** Spusť úlohu, po 0.5s ji zruš, ošetři `CancelledError`.
