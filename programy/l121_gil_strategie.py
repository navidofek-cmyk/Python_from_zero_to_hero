"""Lekce 121 — GIL strategie v praxi."""

from __future__ import annotations

import multiprocessing
import queue
import statistics
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Any


# ── CPU bound funkce ──────────────────────────────────────────────────────────

def cpu_bound_vypocet(limit: int) -> int:
    """Čistě CPU intenzivní výpočet — součet čtverců."""
    return sum(i * i for i in range(limit))


# ── I/O bound simulace ────────────────────────────────────────────────────────

def io_bound_simulace(id_: int, delay: float = 0.05) -> str:
    """Simuluje I/O operaci (síť, disk) pomocí sleep."""
    time.sleep(delay)
    return f"io_task_{id_}_hotov"


# ── Demo: threading pro I/O bound ─────────────────────────────────────────────

def demo_threading_io() -> None:
    print("\n=== threading — I/O bound (doporučeno) ===")

    pocet = 20
    delay = 0.05  # 50ms simulace I/O

    # Sekvenční
    start = time.perf_counter()
    vysledky_seq = [io_bound_simulace(i, delay) for i in range(pocet)]
    cas_seq = time.perf_counter() - start

    # Threading
    vysledky_thr: list[str] = [""] * pocet

    def worker(i: int) -> None:
        vysledky_thr[i] = io_bound_simulace(i, delay)

    start = time.perf_counter()
    vlakna = [threading.Thread(target=worker, args=(i,)) for i in range(pocet)]
    for v in vlakna:
        v.start()
    for v in vlakna:
        v.join()
    cas_thr = time.perf_counter() - start

    print(f"  {pocet} I/O úkolů × {delay*1000:.0f}ms:")
    print(f"  Sekvenční:  {cas_seq*1000:.1f} ms")
    print(f"  Threading:  {cas_thr*1000:.1f} ms")
    print(f"  Zrychlení:  {cas_seq/cas_thr:.1f}×")
    print(f"  Výsledek threading OK: {vysledky_thr[:3]}")


# ── Demo: ThreadPoolExecutor ───────────────────────────────────────────────────

def demo_threadpool() -> None:
    print("\n=== ThreadPoolExecutor — pohodlnější API ===")

    ukoly = [(i, 0.03) for i in range(15)]

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(io_bound_simulace, i, d) for i, d in ukoly]
        vysledky = [f.result() for f in as_completed(futures)]
    cas = time.perf_counter() - start

    print(f"  15 úkolů × 30ms, max_workers=5: {cas*1000:.1f} ms")
    print(f"  (Sekvenční by bylo ~450ms)")


# ── Demo: multiprocessing pro CPU bound ───────────────────────────────────────

def demo_multiprocessing_cpu() -> None:
    print("\n=== multiprocessing — CPU bound (obchází GIL) ===")

    limity = [500_000] * 4   # 4 úkoly pro 4 CPU jádra

    # Sekvenční
    start = time.perf_counter()
    vysl_seq = [cpu_bound_vypocet(n) for n in limity]
    cas_seq = time.perf_counter() - start

    # Multiprocessing Pool
    start = time.perf_counter()
    # Poznámka: multiprocessing musí být uvnitř if __name__ == "__main__"
    # zde používáme ProcessPoolExecutor pro bezpečnost
    with ProcessPoolExecutor(max_workers=4) as executor:
        vysl_mp = list(executor.map(cpu_bound_vypocet, limity))
    cas_mp = time.perf_counter() - start

    print(f"  4× cpu_bound(500_000):")
    print(f"  Sekvenční:        {cas_seq*1000:.1f} ms")
    print(f"  ProcessPool (4):  {cas_mp*1000:.1f} ms")
    print(f"  Zrychlení:        {cas_seq/cas_mp:.1f}×")
    print(f"  Výsledky shodné:  {vysl_seq == vysl_mp}")


# ── Demo: threading NEpomáhá pro CPU bound ────────────────────────────────────

def demo_threading_cpu_nefunguje() -> None:
    print("\n=== threading NE-zrychluje CPU bound (kvůli GIL) ===")

    limity = [200_000] * 4

    # Sekvenční
    start = time.perf_counter()
    [cpu_bound_vypocet(n) for n in limity]
    cas_seq = time.perf_counter() - start

    # Threading (GIL zabrání paralelismu)
    vysledky: list[int] = [0] * 4

    def worker_cpu(i: int) -> None:
        vysledky[i] = cpu_bound_vypocet(limity[i])

    start = time.perf_counter()
    vlakna = [threading.Thread(target=worker_cpu, args=(i,)) for i in range(4)]
    for v in vlakna:
        v.start()
    for v in vlakna:
        v.join()
    cas_thr = time.perf_counter() - start

    print(f"  4× cpu_bound(200_000):")
    print(f"  Sekvenční:  {cas_seq*1000:.1f} ms")
    print(f"  Threading:  {cas_thr*1000:.1f} ms  ← žádné zrychlení (GIL)")
    if cas_thr >= cas_seq * 0.85:
        print("  Threading je stejně pomalé nebo pomalejší!")


# ── Demo: asyncio simulace (synchronní aproximace) ────────────────────────────

def demo_asyncio_popis() -> None:
    """Ukazuje asyncio principy bez spuštění event loopu v tomto demu."""
    print("\n=== asyncio — jednovláknové I/O (popis) ===")
    print("  asyncio.run(main()) spustí event loop")
    print("  await asyncio.sleep(0.1) — uvolní event loop jiné korutině")
    print("  asyncio.gather(*ukoly) — spustí všechny paralelně")
    print()
    print("  Příklad: 100 korutin × await sleep(0.1)")
    print("  Sekvenční by bylo: ~10s")
    print("  asyncio.gather:    ~0.1s  (všechny čekají najednou)")
    print()
    print("  Kód:")
    print("    import asyncio")
    print("    async def ukol(id_: int) -> str:")
    print("        await asyncio.sleep(0.1)")
    print("        return f'hotov_{id_}'")
    print("    async def main() -> None:")
    print("        vysl = await asyncio.gather(*[ukol(i) for i in range(100)])")
    print("    asyncio.run(main())")


# ── Srovnávací tabulka ────────────────────────────────────────────────────────

def demo_srovnani_tabulka() -> None:
    print("\n=== Srovnání přístupů — kdy co použít ===")

    tabulka = [
        ("Přístup", "I/O bound", "CPU bound", "Overhead", "Sdílená paměť"),
        ("threading", "Ano", "Ne (GIL)", "Nízký", "Ano"),
        ("multiprocessing", "Lze", "Ano", "Vysoký", "Ne (kopie)"),
        ("asyncio", "Ideální", "Ne", "Minimální", "Ano"),
        ("concurrent.futures", "Ano", "Ano*", "Střední", "Záleží"),
    ]

    sirky = [max(len(r[i]) for r in tabulka) for i in range(5)]
    oddelovac = "+" + "+".join("-" * (s + 2) for s in sirky) + "+"

    print("  " + oddelovac)
    for i, radek in enumerate(tabulka):
        bunky = " | ".join(str(radek[j]).ljust(sirky[j]) for j in range(5))
        print(f"  | {bunky} |")
        if i == 0:
            print("  " + oddelovac)
    print("  " + oddelovac)
    print("  * ProcessPoolExecutor pro CPU bound")


# ── Kombinace: asyncio + ProcessPool ──────────────────────────────────────────

def demo_kombinace() -> None:
    print("\n=== Kombinace: asyncio + ProcessPoolExecutor ===")
    print("  Vzor: async kód řídí I/O, CPU práce jde do procesů")
    print()
    print("  import asyncio")
    print("  from concurrent.futures import ProcessPoolExecutor")
    print()
    print("  async def main() -> None:")
    print("      loop = asyncio.get_event_loop()")
    print("      with ProcessPoolExecutor() as pool:")
    print("          # CPU práce NEblokuje event loop")
    print("          vysl = await loop.run_in_executor(pool, cpu_bound, 1_000_000)")
    print("      print(vysl)")


# ── Hlavní funkce ──────────────────────────────────────────────────────────────

def main() -> None:
    print("╔══════════════════════════════════════════╗")
    print("║  Lekce 121 — GIL strategie v praxi      ║")
    print("╚══════════════════════════════════════════╝")

    demo_threading_io()
    demo_threadpool()
    demo_multiprocessing_cpu()
    demo_threading_cpu_nefunguje()
    demo_asyncio_popis()
    demo_srovnani_tabulka()
    demo_kombinace()

    print("\nHotovo! Klíčové poznatky:")
    print("  • GIL uvolní se při I/O → threading funguje pro I/O bound")
    print("  • CPU bound → multiprocessing (vlastní GIL per proces)")
    print("  • asyncio → tisíce I/O korutin s minimální režií")
    print("  • Python 3.13+ nabízí free-threaded build (--disable-gil)")


if __name__ == "__main__":
    main()
