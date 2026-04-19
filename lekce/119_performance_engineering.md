# Lekce 119: Performance Engineering

Performance engineering je systematický přístup k měření, analýze a optimalizaci výkonu programů. Nejdříve měř, pak optimalizuj — nikdy naopak.

---

## Latence vs Throughput

| Metrika | Definice | Příklad |
|---|---|---|
| **Latence** | Čas na zpracování jednoho požadavku | 5 ms na jedno volání DB |
| **Throughput** | Počet požadavků za časovou jednotku | 2 000 req/s |
| **Percentil p50** | Medián — 50 % požadavků je rychlejších | Typická odpověď |
| **Percentil p95** | 95 % požadavků je rychlejších | Skoro-nejhorší případ |
| **Percentil p99** | 99 % požadavků je rychlejších | Důležité pro SLA |

Proč nestačí průměr? Jeden pomalý požadavek (outlier) průměr zkresluje minimálně, ale p99 odhalí skutečné chvosty distribuce.

```python
import statistics

latence_ms = [1, 2, 1, 3, 2, 1, 2, 150, 2, 1]  # 150 ms = outlier

print(f"Průměr: {statistics.mean(latence_ms):.1f} ms")
print(f"Medián (p50): {statistics.median(latence_ms):.1f} ms")

serazene = sorted(latence_ms)
p95 = serazene[int(0.95 * len(serazene))]
p99 = serazene[int(0.99 * len(serazene))]
print(f"p95: {p95} ms")
print(f"p99: {p99} ms")
```

---

## Měření s `timeit`

Modul `timeit` spouští kód opakovaně a vrátí celkový čas. Eliminuje šum OS scheduleru.

```python
import timeit

# Jednoduchý způsob — vrátí čas v sekundách pro 1 000 000 opakování
cas = timeit.timeit("'-'.join(str(n) for n in range(100))", number=1_000_000)
print(f"Celkem: {cas:.3f} s")

# Porovnání dvou variant
varianta_a = timeit.timeit(
    stmt="[x**2 for x in range(1000)]",
    number=10_000,
)
varianta_b = timeit.timeit(
    stmt="list(map(lambda x: x**2, range(1000)))",
    number=10_000,
)
print(f"List comprehension: {varianta_a:.4f} s")
print(f"map+lambda:         {varianta_b:.4f} s")
```

---

## Přesné měření s `time.perf_counter`

`time.perf_counter()` vrací čas s nejvyšší dostupnou rozlišovací schopností (nanosekundy). Ideální pro benchmarky v kódu.

```python
import time

def moje_funkce(n: int) -> list[int]:
    return [i * i for i in range(n)]

# Měření jednoho průběhu
start = time.perf_counter()
vysledek = moje_funkce(100_000)
konec = time.perf_counter()
print(f"Trvalo: {(konec - start) * 1000:.2f} ms")

# Lepší: více vzorků, spočteme statistiky
vzorky: list[float] = []
for _ in range(100):
    t0 = time.perf_counter()
    moje_funkce(10_000)
    vzorky.append(time.perf_counter() - t0)

import statistics
print(f"Medián: {statistics.median(vzorky)*1e6:.1f} µs")
print(f"Stdev:  {statistics.stdev(vzorky)*1e6:.1f} µs")
```

---

## Context manager pro benchmarky

```python
import time
from contextlib import contextmanager
from collections.abc import Generator

@contextmanager
def timer(nazev: str) -> Generator[None, None, None]:
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"[{nazev}] {elapsed * 1000:.3f} ms")

with timer("serazeni"):
    data = sorted(range(100_000), reverse=True)
```

---

## cProfile — profilování

```python
import cProfile
import pstats
import io

def tezka_funkce() -> int:
    total = 0
    for i in range(100_000):
        total += i * i
    return total

pr = cProfile.Profile()
pr.enable()
tezka_funkce()
pr.disable()

vystup = io.StringIO()
ps = pstats.Stats(pr, stream=vystup).sort_stats("cumulative")
ps.print_stats(10)
print(vystup.getvalue())
```

---

## Flame Graphs — py-spy

`py-spy` je externí nástroj (ne stdlib), ale klíčový pro produkci:

```bash
# Instalace
pip install py-spy

# Nahrání běžícího procesu (PID 12345)
py-spy record -o profile.svg --pid 12345

# Přímé spuštění
py-spy record -o profile.svg -- python muj_program.py
```

Flame graph zobrazuje:
- **Osa X** = čas (šířka = kolik % CPU funkce spotřebovala)
- **Osa Y** = zásobník volání (call stack)
- Hledáme nejširší "plameny" — tam je bottleneck

Alternativy v stdlib: `cProfile` + vizualizace přes `snakeviz` (pip).

---

## Mikro-optimalizace: co (ne)dělat

| Přístup | Rychlost | Poznámka |
|---|---|---|
| `list.append` v cyklu | Středně | Přijatelné |
| List comprehension | Rychlejší | Preferovat |
| `"".join(list)` | Rychlé | Místo `+=` pro string |
| `set` pro hledání | O(1) | Místo `list` O(n) |
| `local = global_fn` | Mírně rychlejší | Lokální lookup je rychlejší |
| `__slots__` | Méně RAM | Úspora paměti u mnoha instancí |

---

## Shrnutí

- Vždy **měř nejdříve** — předčasná optimalizace je zdroj problémů
- Používej `time.perf_counter()` pro přesné benchmarky v kódu
- `timeit` pro porovnání malých kódových fragmentů
- `cProfile` pro nalezení bottlenecku v celém programu
- `py-spy` pro produkční flame graphs (bez zastavení procesu)
- Sleduj **p95/p99**, ne jen průměr — důležité pro SLA

---

## Cvičení

1. Změř pomocí `timeit` rozdíl mezi `dict.get()` a `try/except KeyError` pro existující klíč.
2. Napiš funkci, která spustí zadanou funkci 1 000× a vrátí `dict` s p50, p95, p99.
3. Vyprofiluj pomocí `cProfile` rekurzivní Fibonacci(30) a najdi nejpomalejší volání.
4. Porovnej výkon `list` vs `deque` pro operaci `appendleft` / `insert(0, ...)`.
