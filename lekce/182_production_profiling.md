# Lekce 182: Produkční profiling — py-spy a memray

Profiling v produkci bez zastavení procesu. py-spy sleduje CPU, memray sleduje paměť.

---

## 🚀 Instalace

```bash
uv add py-spy memray
```

---

## 🔥 py-spy — CPU flame graphs

py-spy se připne k běžícímu procesu bez modifikace kódu.

```bash
# Připojit se k běžícímu procesu
py-spy top --pid 12345               # real-time top (jako htop)
py-spy record --pid 12345 -o profile.svg  # flame graph
py-spy dump --pid 12345              # stack trace snapshot

# Spustit program a profilovat
py-spy record -o profile.svg -- python muj_program.py

# Sampling rate (výchozí 100Hz)
py-spy record --rate 200 -o fast.svg -- python program.py

# Jen určité vlákno
py-spy record --thread 1 -o thread.svg -- python program.py
```

Python benchmark pro demonstraci:

```python
# slow_program.py
import time


def pomala_funkce(n: int) -> int:
    """Záměrně pomalá implementace."""
    vysledek = 0
    for i in range(n):
        vysledek += i * i   # O(n)
    return vysledek


def rychla_funkce(n: int) -> int:
    """Optimalizovaná verze."""
    return n * (n - 1) * (2 * n - 1) // 6   # O(1)


def main():
    n = 1_000_000
    print("Pomalá:", pomala_funkce(n))
    print("Rychlá:", rychla_funkce(n))

    # Simulace webového serveru
    for i in range(100):
        pomala_funkce(n // 10)
        time.sleep(0.01)


if __name__ == "__main__":
    main()

# py-spy record -o profile.svg -- python slow_program.py
# Otevři profile.svg v prohlížeči — uvidíš kde se tráví čas
```

---

## 🧠 memray — memory profiling

```python
# memory_demo.py — ukázka memory leaků

import memray   # import volitelný — lze profilovat i bez úpravy kódu


def nacti_velky_soubor(cesta: str) -> list[str]:
    """Špatně: načte celý soubor do paměti."""
    with open(cesta) as f:
        return f.readlines()   # 1GB soubor = 1GB RAM


def nacti_velky_soubor_ok(cesta: str):
    """Správně: lazy loading."""
    with open(cesta) as f:
        yield from f   # konstantní paměť


class MemoryLeak:
    """Klasický memory leak — cache bez limitu."""
    _cache: dict = {}

    @classmethod
    def uloz(cls, klic: str, data: list) -> None:
        cls._cache[klic] = data   # nikdy se nemaže!

    @classmethod
    def oprav(cls, klic: str, data: list, max_size: int = 1000) -> None:
        if len(cls._cache) >= max_size:
            nejstarsi = next(iter(cls._cache))
            del cls._cache[nejstarsi]
        cls._cache[klic] = data
```

Spuštění profilování:
```bash
# Celý program
memray run -o profile.bin muj_program.py

# Připojit k běžícímu procesu
memray attach 12345

# Analýza výsledků
memray flamegraph profile.bin   # HTML flame graph
memray summary profile.bin      # textový souhrn
memray tree profile.bin         # stromový výpis
memray stats profile.bin        # statistiky alokací

# Live monitoring
memray live 12345               # real-time paměť
```

---

## 🔬 Inline profiling

```python
import memray


# Profiling konkrétní části kódu
with memray.Tracker("critical_section.bin"):
    # Profiluj jen tuto část
    velky_seznam = [i**2 for i in range(10_000_000)]
    del velky_seznam

# Dekorátor
@memray.track_allocations
def pamet_narocna_funkce(n: int) -> list:
    return list(range(n))
```

---

## 📊 Analýza profiling výsledků

```python
import cProfile
import pstats
import io


def profile(func, *args, **kwargs):
    """Profiluj funkci a vytiskni top 10 výsledků."""
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()

    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.sort_stats("cumulative")
    ps.print_stats(10)
    print(s.getvalue())
    return result


# Porovnání implementací
import timeit

def bench(kod: str, n: int = 1000) -> float:
    return timeit.timeit(kod, number=n, globals=globals())


print("List comprehension:", bench("[x**2 for x in range(1000)]"))
print("Generator:          ", bench("list(x**2 for x in range(1000))"))
print("Map:                ", bench("list(map(lambda x: x**2, range(1000)))"))
```

---

## 🔧 Austin — low-overhead frame sampler

```bash
# pip install austin-dist
austin -i 1000 python muj_program.py > profile.austin
# austin-tui pro interaktivní TUI
```

---

## 📈 Interpretace flame graphs

```
Flame graph čtení (y = call stack, x = čas):
  - Šírka bloku = čas strávený ve funkci + potomcích
  - Výška = hloubka volání
  - Hledej: nejšiřší bloky v horní části = bottlenecky

Memory flame graph:
  - Šírka = množství alokované paměti
  - Hledej: neočekávané alokace, memory leaky
```

---

## ✏️ Cvičení

1. Profiluj GAev z lekce 147 — kde se tráví nejvíc času? Optimalizuj.
2. Napiš program s úmyslným memory leakem, detekuj ho pomocí memray.
3. Porovnej `list.sort()` vs `sorted()` vs heapq na 10M prvcích — flame graph.
4. Profiluj FastAPI aplikaci pod zátěží (locust/wrk) — najdi bottleneck.
5. Optimalizuj pomalou funkci tak, aby py-spy neukazoval žádný dominant block.
