"""Lekce 119 — Performance Engineering."""

from __future__ import annotations

import cProfile
import io
import pstats
import statistics
import time
import timeit
from contextlib import contextmanager
from collections.abc import Callable, Generator
from typing import Any


# ── Utility: context manager pro měření ───────────────────────────────────────

@contextmanager
def timer(nazev: str) -> Generator[None, None, None]:
    """Měří dobu běhu bloku kódu a vypíše výsledek."""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"  [{nazev}] {elapsed * 1000:.3f} ms")


# ── Percentily latence ─────────────────────────────────────────────────────────

def vypocti_percentily(vzorky: list[float]) -> dict[str, float]:
    """Vrátí p50, p95, p99 z pole hodnot."""
    serazene = sorted(vzorky)
    n = len(serazene)

    def percentil(p: float) -> float:
        index = int(p * n)
        return serazene[min(index, n - 1)]

    return {
        "prumer": statistics.mean(serazene),
        "p50": percentil(0.50),
        "p95": percentil(0.95),
        "p99": percentil(0.99),
        "max": serazene[-1],
    }


def demo_percentily() -> None:
    print("\n=== Percentily latence ===")
    import random
    random.seed(42)
    # Simulujeme realistickou distribuci: většina < 10ms, občas outlier
    latence = [random.expovariate(1 / 3) for _ in range(990)]
    latence += [random.uniform(50, 200) for _ in range(10)]  # 1% outliery

    stats = vypocti_percentily(latence)
    for nazev, hodnota in stats.items():
        print(f"  {nazev:8s}: {hodnota:7.2f} ms")

    print()
    print("  Průměr je zkreslen outliermi — p99 ukazuje skutečné chvosty!")


# ── timeit benchmark ──────────────────────────────────────────────────────────

def demo_timeit() -> None:
    print("\n=== timeit: porovnání variant ===")

    n = 10_000

    cas_a = timeit.timeit(
        stmt="[x**2 for x in range(500)]",
        number=n,
    )
    cas_b = timeit.timeit(
        stmt="list(map(lambda x: x**2, range(500)))",
        number=n,
    )
    cas_c = timeit.timeit(
        stmt='"-".join(str(i) for i in range(100))',
        number=n,
    )

    print(f"  List comprehension x**2 : {cas_a:.4f} s / {n} opak.")
    print(f"  map+lambda x**2         : {cas_b:.4f} s / {n} opak.")
    print(f"  str join generator      : {cas_c:.4f} s / {n} opak.")
    print(f"  Poměr comprehension/map : {cas_a/cas_b:.2f}×")


# ── perf_counter benchmark ────────────────────────────────────────────────────

def zkoumana_funkce(n: int) -> list[int]:
    """Funkce, jejíž výkon měříme."""
    return [i * i for i in range(n)]


def benchmark(fn: Callable[..., Any], *args: Any, opakovani: int = 200) -> dict[str, float]:
    """Spustí funkci `opakovani`× a vrátí statistiky v µs."""
    vzorky: list[float] = []
    for _ in range(opakovani):
        t0 = time.perf_counter()
        fn(*args)
        vzorky.append((time.perf_counter() - t0) * 1e6)
    return vypocti_percentily(vzorky)


def demo_perf_counter() -> None:
    print("\n=== time.perf_counter benchmark ===")
    stats = benchmark(zkoumana_funkce, 10_000)
    print(f"  Funkce: zkoumana_funkce(10_000), 200 opakování")
    for nazev, hodnota in stats.items():
        print(f"  {nazev:8s}: {hodnota:8.2f} µs")


# ── cProfile ──────────────────────────────────────────────────────────────────

def fibonacci(n: int) -> int:
    """Rekurzivní Fibonacci — záměrně pomalý pro demo profilování."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def demo_cprofile() -> None:
    print("\n=== cProfile profilování ===")
    pr = cProfile.Profile()
    pr.enable()
    vysledek = fibonacci(28)
    pr.disable()

    vystup = io.StringIO()
    ps = pstats.Stats(pr, stream=vystup).sort_stats("cumulative")
    ps.print_stats(5)
    radky = vystup.getvalue().splitlines()

    print(f"  fibonacci(28) = {vysledek}")
    print("  Top 5 volání (zkráceně):")
    for radek in radky[5:11]:
        if radek.strip():
            print(f"  {radek}")


# ── context manager timer ─────────────────────────────────────────────────────

def demo_timer() -> None:
    print("\n=== Context manager timer ===")

    with timer("sorted() 100k prvků"):
        sorted(range(100_000), reverse=True)

    with timer("list comprehension 100k"):
        [i * 2 for i in range(100_000)]

    with timer("set z range 50k"):
        set(range(50_000))


# ── Srovnávací tabulka přístupů ────────────────────────────────────────────────

def demo_srovnani() -> None:
    print("\n=== Srovnání: list append vs comprehension vs extend ===")
    n = 100_000
    opakovani = 50

    def append_loop() -> list[int]:
        lst: list[int] = []
        for i in range(n):
            lst.append(i)
        return lst

    def comprehension() -> list[int]:
        return [i for i in range(n)]

    def extend_range() -> list[int]:
        lst: list[int] = []
        lst.extend(range(n))
        return lst

    for nazev, fn in [
        ("append v cyklu", append_loop),
        ("list comprehension", comprehension),
        ("extend(range)", extend_range),
    ]:
        vzorky = []
        for _ in range(opakovani):
            t0 = time.perf_counter()
            fn()
            vzorky.append((time.perf_counter() - t0) * 1000)
        median = statistics.median(vzorky)
        print(f"  {nazev:22s}: medián {median:.3f} ms")


# ── Hlavní funkce ──────────────────────────────────────────────────────────────

def main() -> None:
    print("╔══════════════════════════════════════════╗")
    print("║  Lekce 119 — Performance Engineering    ║")
    print("╚══════════════════════════════════════════╝")

    demo_percentily()
    demo_timeit()
    demo_perf_counter()
    demo_cprofile()
    demo_timer()
    demo_srovnani()

    print("\nHotovo! Klíčové poznatky:")
    print("  • Měř nejdříve, pak optimalizuj")
    print("  • Průměr nestačí — sleduj p95/p99")
    print("  • timeit pro mikrobenchmarky, cProfile pro celý program")
    print("  • perf_counter má nanosekundové rozlišení")


if __name__ == "__main__":
    main()
