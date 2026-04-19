# Lekce 56: `async`/`await` základ

## 🍳 Proč async?

Představ si, že vaříš večeři:
- **Synchronní** kuchař: nakrájí cibuli, **stojí 10 minut a kouká** jak se vaří voda, pak nakrájí maso, pak **stojí** jak se peče.
- **Asynchronní** kuchař: nakrájí cibuli, dá vodu vařit, **mezitím krájí maso**, pak dá maso na pánev, **mezitím nakrájí přílohu**...

Asynchronní kuchař stihne víc, **i když má jednu ruku**. To je `async` v Pythonu — jeden vlákno, ale **mezi I/O čekáním** dělá jiné věci.

---

## 🛠️ `async def` a `await`

```python
import asyncio

async def vital():
    print("Začínám...")
    await asyncio.sleep(1)        # ← uvolní procesor na 1s
    print("...končím!")


asyncio.run(vital())
```

- `async def` = **korutina** (asynchronní funkce)
- `await x` = „pozastav mě, až bude `x` hotová pokračuj“
- `asyncio.run()` spustí event loop

---

## 🔄 Pozor: korutinu MUSÍŠ awaitovat

```python
async def neco(): print("ahoj")

neco()                  # ❌ jen vyrobí korutinu, NEspustí ji
                        # RuntimeWarning: coroutine never awaited

asyncio.run(neco())     # ✅ teď to běží
```

---

## ⚡ Hlavní benefit — paralelní I/O

### Synchronně (pomalu)

```python
import time

def stahni(url):
    time.sleep(1)        # simuluje request
    return f"data z {url}"

start = time.time()
for url in ["a", "b", "c"]:
    stahni(url)
print(f"⏱️  {time.time()-start:.1f}s")    # ~3s
```

### Asynchronně (rychle)

```python
import asyncio

async def stahni(url):
    await asyncio.sleep(1)
    return f"data z {url}"

async def main():
    vysledky = await asyncio.gather(
        stahni("a"),
        stahni("b"),
        stahni("c"),
    )
    print(vysledky)

asyncio.run(main())     # ~1s !!!
```

3× rychlejší! Protože `sleep` neblokuje — uvolní ruce a dělá jiné stahování.

---

## 🎯 `asyncio.gather` — spuštění naráz

```python
vysledky = await asyncio.gather(task1(), task2(), task3())
```

Vrací seznam výsledků v pořadí podle vstupů.

---

## ⏰ `asyncio.wait_for` — timeout

```python
try:
    vysledek = await asyncio.wait_for(stahni("pomalu"), timeout=2.0)
except asyncio.TimeoutError:
    print("Trvalo to moc dlouho!")
```

---

## ⚠️ Pravidla async

1. `await` **funguje jen uvnitř `async def`**.
2. **NEvolej `time.sleep`** v async kódu — blokuje! Použij `await asyncio.sleep`.
3. `requests`, klasický `open` jsou synchronní → blokují. Použij `httpx`, `aiofiles`.
4. Jeden event loop na program (`asyncio.run` ho vytvoří).

---

## 🆚 Async vs threading

| | async | threading |
|---|---|---|
| Pro I/O | ✅ excelentní | OK |
| Pro CPU | ❌ neefektivní | OK (ale GIL) |
| Pravdivý paralelismus | Ne (1 thread) | Ne (kvůli GIL) |
| Náročné na zdroje | Lehké | Středně |
| Komplexita | Středná | Středná |

Pro **CPU-bound** úlohy potřebuješ `multiprocessing` (lekce 84).

---

## ✏️ Cvičení

1. **Spuštění:** Napiš `async def` co `await asyncio.sleep(1)` a vypíše „hotovo“. Spusť přes `asyncio.run`.
2. **Gather:** Spusť 3 sleepy paralelně a změř — měl by trvat 1s, ne 3s.
3. **Pokus s wait_for:** Implementuj 5sekundovou úlohu s timeoutem 2s.
4. **Sleep:** Vyzkoušej rozdíl — ve `time.sleep(1)` ve smyčce 3× vs `asyncio.gather` 3 sleepů.
