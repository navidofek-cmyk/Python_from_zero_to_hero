# Lekce 58: Async iterátory a generátory

## 🔄 `async for`

Stejně jako `for` iteruje synchronně, **`async for`** iteruje asynchronně. Hodí se pro **streamy dat** (čtení paketů, řádky ze síťě, prvky z DB).

```python
async for radek in stream:
    print(radek)
```

---

## 🛠️ Async generátor

Funkce s `async def` + `yield`:

```python
async def generuj_cisla(n):
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i


async def main():
    async for x in generuj_cisla(5):
        print(x)


asyncio.run(main())
```

---

## 🚪 Async context manager

`async with` — vstup/výstup může čekat:

```python
class AsyncSpojeni:
    async def __aenter__(self):
        print("Otevírám spojení (await)...")
        await asyncio.sleep(0.1)
        return self

    async def __aexit__(self, *exc):
        print("Zavírám...")
        await asyncio.sleep(0.1)


async def main():
    async with AsyncSpojeni() as spojeni:
        print("Pracuji se spojením")
```

---

## 🎁 `@asynccontextmanager`

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def spojeni(host):
    print(f"Connect to {host}")
    yield "spojení"
    print("Disconnect")


async def main():
    async with spojeni("server") as s:
        print(f"Mám {s}")
```

---

## 📋 Async list comprehension

```python
async def main():
    vysledky = [x async for x in generuj_cisla(5)]
```

---

## 🎯 Praktický příklad — stream API

```python
async def cti_stream(url):
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as response:
            async for chunk in response.aiter_bytes():
                yield chunk


async def main():
    async for chunk in cti_stream("http://api.example.com/stream"):
        zpracuj(chunk)
```

---

## ✏️ Cvičení

1. **Async gen:** Napiš generátor co async vrací čísla 0..n s `await asyncio.sleep`.
2. **Async with:** Vyrob async context manager co loguje vstup a výstup.
3. **Async list comp:** Vyrob `[x*2 async for x in gen()]`.
4. **Stream čísel:** Async generátor co simuluje příchod paketů (každých 100ms).
