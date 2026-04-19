# Lekce 60: Streamy a fronty v `asyncio`

## 📬 `asyncio.Queue`

Asynchronní fronta — producent dává, konzument bere. **Bezpečná pro concurrent přístup**.

```python
import asyncio

async def producent(q):
    for i in range(5):
        await asyncio.sleep(0.5)
        await q.put(f"item-{i}")
        print(f"📦 vyrobil item-{i}")
    await q.put(None)              # signál konce


async def konzument(q):
    while True:
        item = await q.get()
        if item is None:
            break
        print(f"🛒 zpracoval {item}")
        q.task_done()


async def main():
    q = asyncio.Queue()
    await asyncio.gather(producent(q), konzument(q))


asyncio.run(main())
```

### Druhy front

```python
asyncio.Queue(maxsize=10)        # FIFO, s limitem
asyncio.LifoQueue()              # LIFO (stack)
asyncio.PriorityQueue()          # podle priority
```

---

## 🌊 Streamy — TCP servery a klienti

```python
import asyncio

async def echo_handler(reader, writer):
    data = await reader.read(100)
    addr = writer.get_extra_info('peername')
    print(f"Přijal od {addr}: {data!r}")
    writer.write(data.upper())
    await writer.drain()
    writer.close()

async def main():
    server = await asyncio.start_server(echo_handler, "127.0.0.1", 8888)
    async with server:
        await server.serve_forever()

asyncio.run(main())
```

Klient:

```python
async def client():
    reader, writer = await asyncio.open_connection("127.0.0.1", 8888)
    writer.write(b"Ahoj")
    await writer.drain()
    data = await reader.read(100)
    print(data.decode())
    writer.close()
```

`StreamReader` / `StreamWriter` — asynchronní I/O nad TCP.

---

## 🎬 Sub-procesy async

```python
async def main():
    proc = await asyncio.create_subprocess_exec(
        "ls", "-la",
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    print(stdout.decode())
```

---

## 🎯 Producent-konzument vzor

Velmi častý:

```python
async def fetcher(urls, queue):
    for u in urls:
        data = await stahni(u)
        await queue.put(data)
    for _ in range(POCET_KONZUMENTU):
        await queue.put(None)


async def worker(queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        await zpracuj(item)
        queue.task_done()


async def main():
    queue = asyncio.Queue(maxsize=100)   # backpressure!
    await asyncio.gather(
        fetcher(urls, queue),
        *(worker(queue) for _ in range(5)),
    )
```

`maxsize` = **backpressure** — když konzument nestíhá, producent počká.

---

## ✏️ Cvičení

1. **Queue:** Napiš producent a konzument, projdou 10 položek.
2. **TCP echo server:** Implementuj echo server na portu 8888.
3. **Klient:** Napiš klienta co pošle text a vypíše odpověď.
4. **Backpressure:** Vyrob queue s `maxsize=2`, producent generuje rychle, konzument pomalu — sleduj jak producent čeká.
