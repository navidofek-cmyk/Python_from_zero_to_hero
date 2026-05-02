# Program — Lekce 122: Lekce 122: Async architektura ve velkém

Patří k lekci [Lekce 122: Async architektura ve velkém](../122_async_architektura.md).

## Jak spustit

```bash
python3 programy/l122_async_architektura.py
```

## Zdrojový kód

### `l122_async_architektura.py`

```py
"""Lekce 122 — Async architektura ve velkém."""

from __future__ import annotations

import asyncio
import sys
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any


# ── Backpressure s asyncio.Queue ──────────────────────────────────────────────

async def demo_backpressure() -> None:
    print("\n=== Backpressure s asyncio.Queue(maxsize=3) ===")

    fronta: asyncio.Queue[int | None] = asyncio.Queue(maxsize=3)
    log: list[str] = []

    async def producent(pocet: int) -> None:
        for i in range(pocet):
            await fronta.put(i)           # Čeká, pokud fronta plná
            log.append(f"P: {i} vloženo")
        await fronta.put(None)            # Sentinel

    async def konzument() -> None:
        while True:
            polozka = await fronta.get()
            if polozka is None:
                break
            await asyncio.sleep(0.02)     # Konzument je pomalejší
            log.append(f"K: {polozka} zpracováno")
            fronta.task_done()

    start = time.perf_counter()
    await asyncio.gather(producent(10), konzument())
    elapsed = time.perf_counter() - start

    # Ukázka prvních a posledních zpráv
    for radek in log[:4]:
        print(f"  {radek}")
    print("  ...")
    for radek in log[-3:]:
        print(f"  {radek}")
    print(f"\n  Fronta (maxsize=3) zajistila backpressure za {elapsed:.2f}s")


# ── Bounded Concurrency se Semaphore ──────────────────────────────────────────

async def demo_semaphore() -> None:
    print("\n=== Bounded Concurrency s asyncio.Semaphore(3) ===")

    semafor = asyncio.Semaphore(3)   # Max 3 souběžná volání
    aktivni: list[int] = []
    max_aktivni = 0

    async def volej_api(id_: int) -> str:
        nonlocal max_aktivni
        async with semafor:
            aktivni.append(id_)
            max_aktivni = max(max_aktivni, len(aktivni))
            await asyncio.sleep(0.05)    # Simulace API volání
            aktivni.remove(id_)
        return f"výsledek_{id_}"

    start = time.perf_counter()
    ukoly = [volej_api(i) for i in range(12)]
    vysledky = await asyncio.gather(*ukoly)
    elapsed = time.perf_counter() - start

    print(f"  12 API volání, Semaphore(3):")
    print(f"  Max souběžných: {max_aktivni} (limit 3)")
    print(f"  Čas:            {elapsed:.2f}s")
    print(f"  Bez semaforu:   ~0.05s (vše najednou)")
    print(f"  Se semaforem:   ~{12/3 * 0.05:.2f}s (v dávkách po 3)")


# ── TaskGroup (Python 3.11+) ──────────────────────────────────────────────────

async def demo_taskgroup() -> None:
    print("\n=== asyncio.TaskGroup — strukturovaná souběžnost ===")

    async def ukol(id_: int, selze: bool = False) -> int:
        await asyncio.sleep(0.01 * id_)
        if selze:
            raise ValueError(f"Úkol {id_} záměrně selhal")
        return id_ * 10

    # Scénář 1: Vše uspěje
    print("  Scénář 1 — všechny úkoly uspějí:")
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(ukol(1))
        t2 = tg.create_task(ukol(2))
        t3 = tg.create_task(ukol(3))

    print(f"  Výsledky: {t1.result()}, {t2.result()}, {t3.result()}")

    # Scénář 2: Jeden selže — ostatní jsou zrušeny
    print("\n  Scénář 2 — jeden úkol selže:")
    zrusene: list[int] = []

    async def ukol_s_log(id_: int, selze: bool = False) -> int:
        try:
            await asyncio.sleep(0.05 * id_)
            if selze:
                raise ValueError(f"Úkol {id_} selhal")
            return id_ * 10
        except asyncio.CancelledError:
            zrusene.append(id_)
            raise

    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(ukol_s_log(1))           # Pomalý
            tg.create_task(ukol_s_log(2, selze=True))  # Rychlý, selže
            tg.create_task(ukol_s_log(4))           # Pomalejší
    except* ValueError as eg:
        print(f"  Chyty: {[str(e) for e in eg.exceptions]}")

    print(f"  Zrušené úkoly: {zrusene}")


# ── Správné rušení úkolů ──────────────────────────────────────────────────────

async def demo_cancellation() -> None:
    print("\n=== Správné rušení úkolů (CancelledError) ===")

    uklideno = False

    async def dlouha_operace() -> str:
        nonlocal uklideno
        try:
            print("  Začínám dlouhou operaci...")
            await asyncio.sleep(10)   # Bude přerušena
            return "hotovo"
        except asyncio.CancelledError:
            print("  CancelledError zachycen — provádím úklid")
            uklideno = True
            raise   # KRITICKÉ: vždy re-raise!

    ukol = asyncio.create_task(dlouha_operace())
    await asyncio.sleep(0.05)   # Necháme spustit
    ukol.cancel()

    try:
        await ukol
    except asyncio.CancelledError:
        print("  Úkol byl zrušen")

    print(f"  Úklid proveden: {uklideno}")
    print()
    print("  PRAVIDLO: nikdy CancelledError nepohltit!")
    print("  ŠPATNĚ:   except Exception: pass")
    print("  SPRÁVNĚ:  except asyncio.CancelledError: ... raise")


# ── Timeout ───────────────────────────────────────────────────────────────────

async def demo_timeout() -> None:
    print("\n=== Timeout s asyncio.timeout() (Python 3.11+) ===")

    async def pomala_operace(delay: float) -> str:
        await asyncio.sleep(delay)
        return f"hotovo po {delay}s"

    # Operace stihne timeout
    print("  Test 1: operace 0.05s, timeout 0.2s:")
    try:
        async with asyncio.timeout(0.2):
            vysledek = await pomala_operace(0.05)
        print(f"    OK: {vysledek}")
    except TimeoutError:
        print("    Timeout!")

    # Operace nestihne timeout
    print("  Test 2: operace 0.5s, timeout 0.1s:")
    try:
        async with asyncio.timeout(0.1):
            vysledek = await pomala_operace(0.5)
        print(f"    OK: {vysledek}")
    except TimeoutError:
        print("    Timeout — operace trvala příliš dlouho")

    # wait_for (kompatibilní starší syntaxe)
    print("  Test 3: asyncio.wait_for (Python 3.9+):")
    try:
        vysledek = await asyncio.wait_for(pomala_operace(0.5), timeout=0.1)
    except asyncio.TimeoutError:
        print("    asyncio.TimeoutError zachycen (=TimeoutError v 3.11+)")


# ── Worker Pool ───────────────────────────────────────────────────────────────

async def demo_worker_pool() -> None:
    print("\n=== Worker Pool s backpressure ===")

    fronta: asyncio.Queue[int | None] = asyncio.Queue(maxsize=5)
    zpracovano: list[tuple[int, int]] = []   # (worker_id, položka)

    async def worker(worker_id: int) -> None:
        while True:
            polozka = await fronta.get()
            if polozka is None:
                await fronta.put(None)  # Předej sentinel dalšímu workeru
                fronta.task_done()
                break
            await asyncio.sleep(0.01)   # Simulace zpracování
            zpracovano.append((worker_id, polozka))
            fronta.task_done()

    pocet_workeru = 3
    workeri = [asyncio.create_task(worker(i)) for i in range(pocet_workeru)]

    # Vložíme 15 úkolů
    for i in range(15):
        await fronta.put(i)
    await fronta.put(None)  # Sentinel

    await asyncio.gather(*workeri)

    # Statistiky per worker
    for wid in range(pocet_workeru):
        zprac_worker = [p for w, p in zpracovano if w == wid]
        print(f"  Worker {wid}: {len(zprac_worker)} úkolů — {zprac_worker}")


# ── Rate Limiter ──────────────────────────────────────────────────────────────

class RateLimiter:
    """Omezí počet operací za sekundu pomocí tokeny bucket algoritmu."""

    def __init__(self, max_za_sekundu: int) -> None:
        self._semafor = asyncio.Semaphore(max_za_sekundu)
        self._max = max_za_sekundu

    async def acquire(self) -> None:
        await self._semafor.acquire()
        asyncio.get_event_loop().call_later(1.0, self._semafor.release)


async def demo_rate_limiter() -> None:
    print("\n=== Rate Limiter (max 5/s) ===")

    rl = RateLimiter(max_za_sekundu=5)
    casy: list[float] = []

    async def volani(id_: int) -> None:
        await rl.acquire()
        casy.append(time.perf_counter())

    start = time.perf_counter()
    await asyncio.gather(*[volani(i) for i in range(10)])
    elapsed = time.perf_counter() - start

    # Prvních 5 okamžitě, dalších 5 po 1s
    print(f"  10 volání s rate limitem 5/s:")
    print(f"  Celkový čas: {elapsed:.2f}s (očekáváno ~1s)")
    if len(casy) >= 6:
        print(f"  Volání 1-5: okamžitě")
        print(f"  Volání 6:   +{casy[5]-casy[0]:.2f}s")


# ── Hlavní funkce ──────────────────────────────────────────────────────────────

async def main() -> None:
    print("╔══════════════════════════════════════════╗")
    print("║  Lekce 122 — Async architektura          ║")
    print("╚══════════════════════════════════════════╝")

    await demo_backpressure()
    await demo_semaphore()
    await demo_taskgroup()
    await demo_cancellation()
    await demo_timeout()
    await demo_worker_pool()
    await demo_rate_limiter()

    print("\nHotovo! Klíčové poznatky:")
    print("  • Queue(maxsize=N) — backpressure, zabrání OOM")
    print("  • Semaphore(N) — omezí souběžnost na N")
    print("  • TaskGroup — strukturovaná souběžnost, auto-cancel při chybě")
    print("  • CancelledError VŽDY znovu vyhodit")
    print("  • asyncio.timeout() čistší než wait_for (Python 3.11+)")


if __name__ == "__main__":
    asyncio.run(main())

```
