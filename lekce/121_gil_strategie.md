# Lekce 121: GIL — strategie v praxi

GIL (Global Interpreter Lock) je mutex, který zabraňuje paralelnímu spuštění Python bytecodu ve více vláknech současně. Pochopení GIL je klíčové pro správnou volbu konkurenčního modelu.

---

## Co je GIL

CPython interpret spravuje paměť pomocí reference countingu. Aby bylo toto počítání bezpečné, GIL zaručuje, že v každém okamžiku spouští bytecode pouze jedno vlákno. GIL se uvolní při I/O operacích, `time.sleep()` a volání C-extension kódu, který to explicitně dovoluje.

```
vlákno 1: [Python bytecode] ─── GIL ──► [I/O čeká, GIL uvolněn]
vlákno 2:                                        [GIL získán] ─── [Python bytecode]
```

---

## Kdy použít `threading` (I/O bound)

Vlákna jsou ideální, když vlákno **čeká** (síť, disk, sleep). Během čekání GIL není potřeba.

```python
import threading
import time
import urllib.request

URL = "https://httpbin.org/delay/1"

def stahni(url: str, vysledky: list[str], index: int) -> None:
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            vysledky[index] = f"OK {r.status}"
    except Exception as e:
        vysledky[index] = f"Chyba: {e}"

# Sekvenční
start = time.perf_counter()
# stahni(URL, [""], 0)  # ... × 5
# print(f"Sekvenční: {time.perf_counter()-start:.2f}s")  # ~5 s

# Paralelní s threading
urls = [URL] * 5
vysledky: list[str] = [""] * 5
vlakna = [threading.Thread(target=stahni, args=(u, vysledky, i))
          for i, u in enumerate(urls)]
for v in vlakna: v.start()
for v in vlakna: v.join()
# print(f"Paralelní: {time.perf_counter()-start:.2f}s")  # ~1 s
```

---

## Kdy použít `multiprocessing` (CPU bound)

Každý proces má vlastní GIL. Pro CPU-intenzivní práci obejdeme GIL pomocí více procesů.

```python
import multiprocessing
import time

def tezky_vypocet(n: int) -> int:
    """CPU bound: čistá matematika."""
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    data = [5_000_000] * 4  # 4 úkoly

    # Sekvenční
    start = time.perf_counter()
    vysledky = [tezky_vypocet(n) for n in data]
    print(f"Sekvenční: {time.perf_counter()-start:.2f}s")

    # Paralelní — 4 procesy
    start = time.perf_counter()
    with multiprocessing.Pool(4) as pool:
        vysledky = pool.map(tezky_vypocet, data)
    print(f"Multiprocessing: {time.perf_counter()-start:.2f}s")
```

---

## Kdy použít `asyncio` (Async I/O)

`asyncio` je jednovláknové — na GIL nezávisí. Vhodné pro tisíce simultánních I/O operací s minimální režií.

```python
import asyncio
import time

async def simuluj_io(id_: int, delay: float) -> str:
    await asyncio.sleep(delay)   # Simulace I/O — uvolní event loop
    return f"Úkol {id_} hotov"

async def main() -> None:
    start = time.perf_counter()
    # Spustíme 100 "I/O operací" paralelně
    ukoly = [simuluj_io(i, 0.1) for i in range(100)]
    vysledky = await asyncio.gather(*ukoly)
    print(f"100 úkolů za {time.perf_counter()-start:.2f}s")
    print(vysledky[:3])

asyncio.run(main())
# Výstup: ~0.10s (ne 10s jako sekvenční)
```

---

## Srovnání přístupů

| Kritérium | `threading` | `multiprocessing` | `asyncio` |
|---|---|---|---|
| Typ úlohy | I/O bound | CPU bound | I/O bound (async) |
| GIL | Nevýhoda (CPU), ignoruje (I/O) | Obchází (vlastní GIL) | Nevztahuje se |
| Paměť | Sdílená | Kopírovaná (fork/spawn) | Sdílená |
| Overhead | Nízký | Vysoký (spuštění procesu) | Velmi nízký |
| Škálování | Stovky vláken | Desítky procesů | Tisíce korutin |
| Ladění | Složitější (race conditions) | Složité (IPC) | Snazší (jednovláknové) |
| Komunikace | `queue.Queue`, `Lock` | `Pipe`, `Queue`, `Manager` | `asyncio.Queue` |

---

## Kdy co použít — rozhodovací strom

```
Je úloha I/O bound?
├── ANO + moderní kód → asyncio
├── ANO + synchronní knihovny → threading
└── NE (CPU bound)
    ├── Málo úkolů (< počet CPU) → multiprocessing
    └── Potřebuješ sdílenou paměť → ctypes/numpy shared arrays
```

---

## Praktický příklad — kombinace

```python
import asyncio
import concurrent.futures

def cpu_bound(n: int) -> int:
    return sum(i * i for i in range(n))

async def main() -> None:
    loop = asyncio.get_event_loop()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # CPU práci přesuneme do procesu, async IO pokračuje
        vysledek = await loop.run_in_executor(executor, cpu_bound, 5_000_000)
    print(f"Výsledek: {vysledek}")

asyncio.run(main())
```

---

## Free-threaded build (Python 3.13+)

Python 3.13 přináší experimentální **free-threaded** build (`--disable-gil`), kde GIL neexistuje. Vlákna mohou opravdu běžet paralelně.

```bash
# Instalace free-threaded buildu (3.13t)
pyenv install 3.13t
python3.13t -c "import sys; print(sys._is_gil_enabled())"  # False
```

Pozor: Většina C-extensionů zatím není thread-safe bez GIL. Pro produkci zatím opatrně.

---

## Shrnutí

- **GIL** zabraňuje paralelnímu bytecodu, uvolňuje se při I/O
- **threading** — ideální pro I/O bound (síť, disk, sleep)
- **multiprocessing** — pro CPU bound, každý proces má vlastní GIL
- **asyncio** — jednovláknové, tisíce korutin, moderní I/O
- Python 3.13+ nabízí free-threaded build jako experimentální řešení

---

## Cvičení

1. Změř čas: stažení 10 URL sekvenčně vs threading (použij `urllib.request`).
2. Porovnej výpočet prvočísel do 10 000 000: jedno vlákno vs 4 procesy (`multiprocessing.Pool`).
3. Napiš asyncio program: 1 000 korutin čeká `asyncio.sleep(0.01)` — jak dlouho trvá celkem?
4. Zkombinuj asyncio + ThreadPoolExecutor pro I/O operace s blokující knihovnou.
