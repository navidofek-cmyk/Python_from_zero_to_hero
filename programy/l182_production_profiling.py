"""Lekce 182 — Produkční profiling: py-spy a memray.
Spuštění: uv run l182_production_profiling.py
Pro skutečný profiling: uv add py-spy memray
"""

import cProfile
import pstats
import io
import time
import sys
import tracemalloc


# ── CPU profiling ─────────────────────────────────────────────────────────────

def pomala_funkce(n):
    return sum(i*i for i in range(n))

def rychla_funkce(n):
    return n * (n-1) * (2*n-1) // 6

def bubble_sort_slow(arr):
    arr = arr[:]
    for i in range(len(arr)):
        for j in range(len(arr)-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr


def demo_cprofile():
    print("=" * 50)
    print("  🔥 Produkční profiling Demo")
    print("=" * 50)

    print("\n=== cProfile — CPU profiling ===")
    import random; random.seed(42)
    data = [random.randint(0, 1000) for _ in range(500)]

    def workload():
        pomala_funkce(100000)
        bubble_sort_slow(data[:100])
        rychla_funkce(100000)

    pr = cProfile.Profile()
    pr.enable()
    workload()
    pr.disable()

    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats(8)
    print(s.getvalue()[:800])


def demo_timeit():
    print("=== timeit — micro-benchmark ===")
    import timeit

    n = 100000
    testy = [
        ("pomala_funkce", f"pomala_funkce({n})", {"pomala_funkce": pomala_funkce}),
        ("rychla_funkce", f"rychla_funkce({n})", {"rychla_funkce": rychla_funkce}),
        ("list comp",     f"sum(i*i for i in range({n}))", {}),
        ("sum range",     f"sum(range({n}))", {}),
    ]

    for nazev, stmt, globs in testy:
        t = timeit.timeit(stmt, number=100, globals=globs)
        print(f"  {nazev:<20}: {t*10:.3f}ms/call")


def demo_tracemalloc():
    print("\n=== tracemalloc — paměťové profiling ===")

    tracemalloc.start()

    # Operace s pamětí
    velky_seznam = [i**2 for i in range(1_000_000)]
    snapshot1 = tracemalloc.take_snapshot()

    del velky_seznam
    import gc; gc.collect()
    snapshot2 = tracemalloc.take_snapshot()

    stats = snapshot1.statistics("lineno")
    print(f"  Top alokace:")
    for stat in stats[:3]:
        print(f"    {stat.count} alokací, {stat.size/1024:.1f} KB")
        print(f"    {stat.traceback.format()[-1] if stat.traceback else '?'}")

    tracemalloc.stop()


def demo_pyspy_prikazy():
    print("\n=== py-spy příkazy (pro produkci) ===")
    print("""
  # Připojit k běžícímu procesu
  py-spy top --pid $(pgrep -f uvicorn)    # real-time top
  py-spy record -o profile.svg --pid PID  # flame graph

  # Spustit s profilem
  py-spy record -o profile.svg -- python server.py

  # Stack snapshot
  py-spy dump --pid PID

  Flame graph čtení:
    - Šířka = čas strávený ve funkci
    - Výška = hloubka zásobníku
    - Nejširší bloky nahoře = bottlenecky
""")


def demo_memray_prikazy():
    print("=== memray příkazy ===")
    print("""
  memray run -o profile.bin muj_program.py
  memray flamegraph profile.bin   # HTML flame graph
  memray summary profile.bin      # textový souhrn
  memray live PID                  # real-time

  Inline:
    with memray.Tracker("out.bin"):
        velká_operace()
""")


def demo_memory_leak():
    print("\n=== Detekce memory leaku ===")
    tracemalloc.start()
    zacatek = tracemalloc.take_snapshot()

    # Simulace leaku
    cache = {}
    for i in range(1000):
        cache[f"key_{i}"] = list(range(100))  # roste donekonečna

    konec = tracemalloc.take_snapshot()
    diff = konec.compare_to(zacatek, "lineno")
    print(f"  Top 3 změny v paměti:")
    for stat in diff[:3]:
        print(f"    {stat.size_diff/1024:+.1f} KB: {stat.count_diff:+d} alokací")

    tracemalloc.stop()
    print(f"\n  Cache velikost: {len(cache)} položek = memory leak!")
    print("  Řešení: použij functools.lru_cache nebo collections.OrderedDict s maxsize")


def main():
    demo_cprofile()
    demo_timeit()
    demo_tracemalloc()
    demo_pyspy_prikazy()
    demo_memray_prikazy()
    demo_memory_leak()
    print("\n✅ Demo dokončeno!")
    print("Instalace: uv add py-spy memray")
    print("py-spy může vyžadovat sudo na Linuxu")


if __name__ == "__main__":
    main()
