# Lekce 85: `concurrent.futures`

## ⚡ Jednotné API pro vlákna i procesy

`concurrent.futures` poskytuje **stejné API** pro `ThreadPoolExecutor` (vlákna, dobré pro I/O) a `ProcessPoolExecutor` (procesy, dobré pro CPU).

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


with ThreadPoolExecutor(max_workers=10) as exec:
    vysledky = exec.map(stahni, urls)
    
print(list(vysledky))
```

---

## 🛠️ Hlavní metody

### `map` — paralelní map

```python
with ThreadPoolExecutor() as ex:
    for vysledek in ex.map(funkce, vstupy):
        print(vysledek)
```

Zachová pořadí podle vstupů.

### `submit` — Future objekt

```python
with ThreadPoolExecutor() as ex:
    future = ex.submit(funkce, arg1, arg2)
    vysledek = future.result(timeout=10)
```

### `as_completed` — výsledky jak přijdou

```python
from concurrent.futures import as_completed

with ThreadPoolExecutor() as ex:
    futures = [ex.submit(stahni, u) for u in urls]
    for f in as_completed(futures):
        print(f.result())   # tisk podle pořadí dokončení
```

---

## 🎯 Když threading vs multiprocessing

```python
# I/O-bound — vlákna
ThreadPoolExecutor(max_workers=20)

# CPU-bound — procesy
ProcessPoolExecutor(max_workers=os.cpu_count())
```

---

## 📊 Future objekt

```python
f = ex.submit(funkce)

f.done()          # hotová?
f.cancel()        # zruš
f.result(timeout) # výsledek (block)
f.exception()     # výjimka (pokud byla)

f.add_done_callback(lambda f: print(f.result()))
```

---

## 🎯 Praktický příklad

```python
import requests
from concurrent.futures import ThreadPoolExecutor

def stahni(url):
    return url, len(requests.get(url).content)

urls = ["https://example.com"] * 50

with ThreadPoolExecutor(max_workers=10) as ex:
    for url, velikost in ex.map(stahni, urls):
        print(f"{url}: {velikost} B")
```

---

## ⚠️ Pasti

1. `ProcessPoolExecutor` má stejné pickle omezení jako `multiprocessing`.
2. **Nesnáší se s asyncio** — pokud jsi v async kódu, použij `asyncio.gather` nebo `asyncio.to_thread`.

---

## ✏️ Cvičení

1. **Stahování:** Stáhni 20 URL přes ThreadPool.
2. **CPU:** Spočítej fib(35) pro 4 různá n přes ProcessPool.
3. **As completed:** Vypiš výsledky jak přijdou (rychlejší dřív).
4. **Submit + cancel:** Spusť 10 úloh, 5 hned zruš.
