"""Lekce 123 — Distribuované systémy."""

from __future__ import annotations

import queue
import random
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


# ── Zpráva a Message Broker ───────────────────────────────────────────────────

@dataclass
class Zprava:
    id_: str = field(default_factory=lambda: str(uuid4())[:8])
    payload: str = ""
    retry_count: int = 0
    timestamp: float = field(default_factory=time.monotonic)

    def __str__(self) -> str:
        return f"Zprava({self.id_}, '{self.payload}', retry={self.retry_count})"


class MessageBroker:
    """Jednoduchý message broker — oddělit producenty od konzumentů."""

    def __init__(self, maxsize: int = 100) -> None:
        self._fronta: queue.Queue[Zprava] = queue.Queue(maxsize=maxsize)
        self._doruceno = 0
        self._zamek = threading.Lock()

    def publish(self, zprava: Zprava) -> None:
        self._fronta.put(zprava)

    def subscribe(self, timeout: float = 1.0) -> Zprava | None:
        try:
            z = self._fronta.get(timeout=timeout)
            with self._zamek:
                self._doruceno += 1
            return z
        except queue.Empty:
            return None

    def task_done(self) -> None:
        self._fronta.task_done()

    @property
    def doruceno(self) -> int:
        with self._zamek:
            return self._doruceno


def demo_message_broker() -> None:
    print("\n=== Message Broker Pattern ===")

    broker = MessageBroker(maxsize=10)
    log: list[str] = []
    hotovo = threading.Event()

    def producent(pocet: int) -> None:
        for i in range(pocet):
            z = Zprava(payload=f"objednavka_{i:02d}")
            broker.publish(z)
            log.append(f"P→ {z}")
            time.sleep(0.01)
        hotovo.set()

    def konzument(id_: int) -> None:
        while not (hotovo.is_set() and broker._fronta.empty()):
            z = broker.subscribe(timeout=0.1)
            if z:
                time.sleep(0.02)  # Zpracování
                log.append(f"  K{id_}← {z}")
                broker.task_done()

    p = threading.Thread(target=producent, args=(8,))
    k1 = threading.Thread(target=konzument, args=(1,))
    k2 = threading.Thread(target=konzument, args=(2,))

    for t in [p, k1, k2]:
        t.start()
    for t in [p, k1, k2]:
        t.join()

    for radek in log:
        print(f"  {radek}")
    print(f"  Celkem doručeno: {broker.doruceno} zpráv")


# ── Celery-like Task Queue ────────────────────────────────────────────────────

@dataclass
class Task:
    id_: str = field(default_factory=lambda: str(uuid4())[:8])
    fn_name: str = ""
    args: tuple[Any, ...] = ()
    priorita: int = 0

    def __lt__(self, other: "Task") -> bool:
        return self.priorita < other.priorita


@dataclass
class TaskResult:
    task_id: str
    vysledek: Any = None
    chyba: str | None = None
    trvani_ms: float = 0.0


class TaskQueue:
    """Celery-like task queue: registrace funkcí, odeslání, worker pool, výsledky."""

    def __init__(self) -> None:
        self._fronta: queue.Queue[Task | None] = queue.Queue()
        self._vysledky: dict[str, TaskResult] = {}
        self._zamek = threading.Lock()
        self._funkce: dict[str, Callable[..., Any]] = {}

    def registruj(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Dekorátor: zaregistruje funkci jako task."""
        self._funkce[fn.__name__] = fn
        return fn

    def odeslat(self, fn_name: str, *args: Any) -> str:
        task = Task(fn_name=fn_name, args=args)
        self._fronta.put(task)
        return task.id_

    def spust_worker(self) -> None:
        """Blokující worker — spusť ve vlákně."""
        while True:
            item = self._fronta.get()
            if item is None:
                break
            task = item
            fn = self._funkce.get(task.fn_name)
            t0 = time.perf_counter()
            if fn is None:
                vysl = TaskResult(task.id_, chyba=f"Neznámá funkce: {task.fn_name}")
            else:
                try:
                    hodnota = fn(*task.args)
                    vysl = TaskResult(task.id_, vysledek=hodnota,
                                      trvani_ms=(time.perf_counter() - t0) * 1000)
                except Exception as e:
                    vysl = TaskResult(task.id_, chyba=str(e),
                                      trvani_ms=(time.perf_counter() - t0) * 1000)
            with self._zamek:
                self._vysledky[task.id_] = vysl
            self._fronta.task_done()

    def get_result(self, task_id: str, timeout: float = 2.0) -> TaskResult | None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with self._zamek:
                if task_id in self._vysledky:
                    return self._vysledky[task_id]
            time.sleep(0.01)
        return None

    def stop(self, pocet_workeru: int = 1) -> None:
        for _ in range(pocet_workeru):
            self._fronta.put(None)


def demo_task_queue() -> None:
    print("\n=== Celery-like Task Queue ===")

    tq = TaskQueue()

    @tq.registruj
    def secti(a: int, b: int) -> int:
        time.sleep(0.01)
        return a + b

    @tq.registruj
    def uppercase(text: str) -> str:
        time.sleep(0.01)
        return text.upper()

    @tq.registruj
    def selzi() -> None:
        raise RuntimeError("Záměrná chyba!")

    # Spustit workery
    pocet_workeru = 2
    workeri = [threading.Thread(target=tq.spust_worker, daemon=True)
               for _ in range(pocet_workeru)]
    for w in workeri:
        w.start()

    # Odeslat úkoly
    id1 = tq.odeslat("secti", 10, 32)
    id2 = tq.odeslat("uppercase", "hello world")
    id3 = tq.odeslat("selzi")
    id4 = tq.odeslat("secti", 100, 200)

    tq.stop(pocet_workeru)
    for w in workeri:
        w.join()

    for task_id, popis in [(id1, "secti(10,32)"), (id2, "uppercase(...)"),
                           (id3, "selzi()"), (id4, "secti(100,200)")]:
        r = tq.get_result(task_id)
        if r:
            if r.chyba:
                print(f"  {popis:20s}: CHYBA — {r.chyba}")
            else:
                print(f"  {popis:20s}: {r.vysledek!r} ({r.trvani_ms:.1f}ms)")


# ── Idempotency Keys ──────────────────────────────────────────────────────────

class IdempotentProcessor:
    """Zpracuje zprávu pouze jednou i při duplicitním doručení."""

    def __init__(self) -> None:
        self._zpracovane: dict[str, str] = {}  # key → výsledek
        self._zamek = threading.Lock()

    def zpracuj(self, idempotency_key: str, payload: str) -> tuple[str, bool]:
        """
        Vrací (výsledek, byl_duplikat).
        Duplikát vrátí uložený výsledek bez zpracování.
        """
        with self._zamek:
            if idempotency_key in self._zpracovane:
                return self._zpracovane[idempotency_key], True

        # Skutečné zpracování (mimo lock pro výkon)
        time.sleep(0.005)
        vysledek = f"ZPRACOVÁNO_{payload.upper()}"

        with self._zamek:
            # Double-check (mohlo přijít paralelně)
            if idempotency_key in self._zpracovane:
                return self._zpracovane[idempotency_key], True
            self._zpracovane[idempotency_key] = vysledek

        return vysledek, False


def demo_idempotency() -> None:
    print("\n=== Idempotency Keys — exactly-once sémantika ===")

    proc = IdempotentProcessor()

    klic = "objednavka-99887"
    testy = [
        (klic, "nakup_iPhone"),      # 1. pokus
        (klic, "nakup_iPhone"),      # 2. pokus (retry po selhání sítě)
        (klic, "nakup_iPhone"),      # 3. pokus (retry znovu)
        ("objednavka-11122", "jina"),  # Jiný klíč
    ]

    for key, payload in testy:
        vysledek, byl_duplikat = proc.zpracuj(key, payload)
        stav = "DUPLIKÁT" if byl_duplikat else "NOVÉ"
        print(f"  [{stav:9s}] key={key[:18]} → {vysledek}")


# ── At-Least-Once s Dead Letter Queue ────────────────────────────────────────

class AtLeastOnceQueue:
    """Fronta s automatickým retry a Dead Letter Queue."""

    def __init__(self, max_retries: int = 3) -> None:
        self._fronta: queue.Queue[tuple[Zprava, int]] = queue.Queue()
        self._dlq: list[Zprava] = []
        self._max_retries = max_retries
        self._zamek = threading.Lock()

    def put(self, zprava: Zprava) -> None:
        self._fronta.put((zprava, 0))

    def zpracuj_vse(self, handler: Callable[[Zprava], None]) -> None:
        while not self._fronta.empty():
            try:
                zprava, retries = self._fronta.get_nowait()
            except queue.Empty:
                break

            try:
                handler(zprava)
                print(f"  OK (pokus {retries+1}): {zprava}")
            except Exception as e:
                if retries + 1 < self._max_retries:
                    print(f"  Retry {retries+1}/{self._max_retries}: {zprava} — {e}")
                    self._fronta.put((zprava, retries + 1))
                else:
                    with self._zamek:
                        self._dlq.append(zprava)
                    print(f"  DLQ: {zprava} — selhalo po {self._max_retries} pokusech")

    @property
    def dlq(self) -> list[Zprava]:
        with self._zamek:
            return list(self._dlq)


def demo_at_least_once() -> None:
    print("\n=== At-Least-Once + Dead Letter Queue ===")
    random.seed(42)

    alq = AtLeastOnceQueue(max_retries=3)

    pocitadlo: dict[str, int] = {}

    def nespolehlivy_handler(z: Zprava) -> None:
        pocitadlo[z.id_] = pocitadlo.get(z.id_, 0) + 1
        # 40% šance selhání, nebo po 2 pokusech to vyjde
        if pocitadlo[z.id_] < 2 and random.random() < 0.6:
            raise ConnectionError("Simulovaná síťová chyba")

    for i in range(5):
        alq.put(Zprava(payload=f"zprava_{i}"))

    alq.zpracuj_vse(nespolehlivy_handler)

    print(f"\n  DLQ obsahuje {len(alq.dlq)} zpráv")


# ── Circuit Breaker ───────────────────────────────────────────────────────────

class CircuitBreaker:
    """
    Vzor: po N selháních po sobě přepne do OPEN stavu a odmítá požadavky.
    Po cool-down době se přepne do HALF-OPEN pro otestování.
    """

    def __init__(self, max_failures: int = 3, cooldown_s: float = 1.0) -> None:
        self._max = max_failures
        self._cooldown = cooldown_s
        self._failures = 0
        self._open_since: float | None = None
        self._zamek = threading.Lock()

    @property
    def je_otevreny(self) -> bool:
        with self._zamek:
            if self._open_since is None:
                return False
            if time.monotonic() - self._open_since > self._cooldown:
                self._open_since = None
                self._failures = 0
                return False
            return True

    def call(self, fn: Callable[[], Any]) -> Any:
        if self.je_otevreny:
            raise RuntimeError("Circuit OPEN — požadavek odmítnut")
        try:
            vysledek = fn()
            with self._zamek:
                self._failures = 0
            return vysledek
        except Exception:
            with self._zamek:
                self._failures += 1
                if self._failures >= self._max:
                    self._open_since = time.monotonic()
            raise


def demo_circuit_breaker() -> None:
    print("\n=== Circuit Breaker ===")

    cb = CircuitBreaker(max_failures=3, cooldown_s=0.5)
    selzeni = 0

    def nestabilni_sluzba() -> str:
        nonlocal selzeni
        selzeni += 1
        if selzeni <= 4:    # Prvních 4 volání selže
            raise ConnectionError("Služba nedostupná")
        return "OK"

    for i in range(8):
        try:
            vysledek = cb.call(nestabilni_sluzba)
            print(f"  Volání {i+1}: {vysledek}")
        except RuntimeError as e:
            print(f"  Volání {i+1}: CIRCUIT OPEN — {e}")
        except ConnectionError as e:
            print(f"  Volání {i+1}: Chyba — {e}")
        time.sleep(0.15)


# ── Hlavní funkce ──────────────────────────────────────────────────────────────

def main() -> None:
    print("╔══════════════════════════════════════════╗")
    print("║  Lekce 123 — Distribuované systémy      ║")
    print("╚══════════════════════════════════════════╝")

    demo_message_broker()
    demo_task_queue()
    demo_idempotency()
    demo_at_least_once()
    demo_circuit_breaker()

    print("\nHotovo! Klíčové poznatky:")
    print("  • Message broker odděluje producenty a konzumenty")
    print("  • Task queue = Celery pattern: registrace, odeslání, worker, výsledky")
    print("  • Idempotency key zabrání dvojímu zpracování při retry")
    print("  • At-least-once + idempotentní handler ≈ exactly-once")
    print("  • Circuit breaker chrání downstream služby při výpadku")


if __name__ == "__main__":
    main()
