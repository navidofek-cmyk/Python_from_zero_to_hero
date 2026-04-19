"""Lekce 124 — Caching vrstvy."""

from __future__ import annotations

import functools
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


# ── functools.lru_cache ───────────────────────────────────────────────────────

@functools.lru_cache(maxsize=256)
def fib(n: int) -> int:
    """Fibonacci s LRU cache — bez cache by byl exponenciální."""
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


@functools.cache   # Python 3.9+ — neomezená cache
def tezky_vypocet(n: int) -> int:
    """Simulace drahého výpočtu."""
    time.sleep(0.001)
    return n * n


def demo_lru_cache() -> None:
    print("\n=== functools.lru_cache ===")

    fib.cache_clear()
    start = time.perf_counter()
    vysledek = fib(40)
    cas1 = time.perf_counter() - start

    start = time.perf_counter()
    fib(40)
    cas2 = time.perf_counter() - start

    info = fib.cache_info()
    print(f"  fib(40) = {vysledek}")
    print(f"  1. volání: {cas1*1000:.2f} ms")
    print(f"  2. volání: {cas2*1000:.4f} ms  (cache hit)")
    print(f"  Cache stats: hits={info.hits}, misses={info.misses}, size={info.currsize}")

    print()
    print("  @functools.cache (neomezená):")
    start = time.perf_counter()
    for i in range(100):
        tezky_vypocet(i)
    cas_miss = time.perf_counter() - start

    start = time.perf_counter()
    for i in range(100):
        tezky_vypocet(i)
    cas_hit = time.perf_counter() - start

    print(f"  100 výpočtů (cold):   {cas_miss*1000:.1f} ms")
    print(f"  100 výpočtů (cached): {cas_hit*1000:.2f} ms")
    print(f"  Zrychlení:            {cas_miss/cas_hit:.0f}×")


# ── Vlastní LRU Cache ─────────────────────────────────────────────────────────

class LRUCache(Generic[K, V]):
    """LRU cache implementovaná pomocí OrderedDict."""

    def __init__(self, kapacita: int) -> None:
        self._kapacita = kapacita
        self._cache: OrderedDict[K, V] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def get(self, klic: K) -> V | None:
        if klic not in self._cache:
            self._misses += 1
            return None
        self._hits += 1
        self._cache.move_to_end(klic)   # Přesunout na konec = "nedávno použitý"
        return self._cache[klic]

    def put(self, klic: K, hodnota: V) -> None:
        if klic in self._cache:
            self._cache.move_to_end(klic)
        self._cache[klic] = hodnota
        if len(self._cache) > self._kapacita:
            vyhozeny = self._cache.popitem(last=False)   # Nejstarší (začátek)
            return
        return

    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    def __len__(self) -> int:
        return len(self._cache)

    def __repr__(self) -> str:
        return (f"LRUCache(kapacita={self._kapacita}, size={len(self)}, "
                f"hit_rate={self.hit_rate():.1%})")


def demo_lru_vlastni() -> None:
    print("\n=== Vlastní LRU Cache implementace ===")

    cache: LRUCache[str, int] = LRUCache(kapacita=3)

    ops = [
        ("put", "a", 1), ("put", "b", 2), ("put", "c", 3),
        ("get", "a", None),   # Hit, přesune a na konec
        ("put", "d", 4),      # Evict b (nejstarší nepoužitý)
        ("get", "b", None),   # Miss — byl evictnut
        ("get", "a", None),   # Hit
        ("get", "c", None),   # Hit
        ("get", "d", None),   # Hit
    ]

    for op in ops:
        if op[0] == "put":
            cache.put(op[1], op[2])
            print(f"  put({op[1]!r}, {op[2]}) → cache: {dict(cache._cache)}")
        else:
            val = cache.get(op[1])
            print(f"  get({op[1]!r}) → {val!r}  ({'HIT' if val is not None else 'MISS'})")

    print(f"\n  {cache}")


# ── Cache-Aside Pattern ───────────────────────────────────────────────────────

class CacheAside:
    """Cache-aside: aplikace řídí cache ručně."""

    def __init__(self) -> None:
        self._cache: LRUCache[str, Any] = LRUCache(kapacita=50)
        self._db: dict[str, Any] = {
            "user:1": {"jmeno": "Alice", "vek": 30},
            "user:2": {"jmeno": "Bob", "vek": 25},
            "user:3": {"jmeno": "Carol", "vek": 35},
        }
        self._db_dotazy = 0

    def get(self, klic: str) -> Any:
        hodnota = self._cache.get(klic)
        if hodnota is not None:
            return hodnota
        # Cache miss → načti z DB
        self._db_dotazy += 1
        hodnota = self._db.get(klic)
        if hodnota is not None:
            self._cache.put(klic, hodnota)
        return hodnota

    def write(self, klic: str, hodnota: Any) -> None:
        self._db[klic] = hodnota
        # Write-invalidate: zneplatní cache po zápisu
        self._cache.put(klic, hodnota)   # Write-through varianta


def demo_cache_aside() -> None:
    print("\n=== Cache-Aside Pattern ===")

    ca = CacheAside()

    klice = ["user:1", "user:2", "user:1", "user:3", "user:1", "user:2"]
    for klic in klice:
        val = ca.get(klic)
        print(f"  get({klic!r}): {val}")

    print(f"\n  Celkem DB dotazů: {ca._db_dotazy} (z {len(klice)} požadavků)")
    print(f"  Cache: {ca._cache}")


# ── TTL Cache ─────────────────────────────────────────────────────────────────

@dataclass
class TTLEntry:
    hodnota: Any
    expiry: float


class TTLCache:
    """Cache s automatickou expirací položek (Time To Live)."""

    def __init__(self, ttl_sekund: float) -> None:
        self._ttl = ttl_sekund
        self._data: dict[str, TTLEntry] = {}
        self._zamek = threading.Lock()

    def get(self, klic: str) -> Any | None:
        with self._zamek:
            entry = self._data.get(klic)
            if entry is None:
                return None
            if time.monotonic() > entry.expiry:
                del self._data[klic]   # Lazy eviction
                return None
            return entry.hodnota

    def put(self, klic: str, hodnota: Any) -> None:
        with self._zamek:
            self._data[klic] = TTLEntry(
                hodnota=hodnota,
                expiry=time.monotonic() + self._ttl,
            )

    def evict_expired(self) -> int:
        """Aktivní čištění expirovaných položek."""
        now = time.monotonic()
        with self._zamek:
            expired = [k for k, e in self._data.items() if now > e.expiry]
            for k in expired:
                del self._data[k]
        return len(expired)

    def __len__(self) -> int:
        with self._zamek:
            return len(self._data)


def demo_ttl_cache() -> None:
    print("\n=== TTL Cache (expirování po čase) ===")

    ttl = TTLCache(ttl_sekund=0.15)

    ttl.put("a", "hodnota_a")
    ttl.put("b", "hodnota_b")

    print(f"  Ihned po vložení:    a={ttl.get('a')!r}, b={ttl.get('b')!r}")
    time.sleep(0.08)
    print(f"  Po 80ms:             a={ttl.get('a')!r}, b={ttl.get('b')!r}")

    ttl.put("c", "hodnota_c")  # Přidáme nový klíč

    time.sleep(0.10)  # Celkem 180ms od vložení a,b → expirují
    print(f"  Po 180ms:            a={ttl.get('a')!r}, b={ttl.get('b')!r}, c={ttl.get('c')!r}")

    pocet = ttl.evict_expired()
    print(f"  Aktivní eviction:    {pocet} položek odstraněno")
    print(f"  Zbývá v cache:       {len(ttl)} položek")


# ── TTL Cache dekorátor ───────────────────────────────────────────────────────

def ttl_cache(seconds: float) -> Callable[[Callable[..., V]], Callable[..., V]]:
    """Dekorátor @ttl_cache(seconds=N) — memoizace s expirací."""

    def dekorator(fn: Callable[..., V]) -> Callable[..., V]:
        cache: TTLCache = TTLCache(ttl_sekund=seconds)

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> V:
            klic = str((args, sorted(kwargs.items())))
            cached = cache.get(klic)
            if cached is not None:
                return cached  # type: ignore[return-value]
            vysledek = fn(*args, **kwargs)
            cache.put(klic, vysledek)
            return vysledek

        wrapper.cache = cache  # type: ignore[attr-defined]
        return wrapper

    return dekorator


@ttl_cache(seconds=0.2)
def nacti_konfiguraci(prostredi: str) -> dict[str, str]:
    """Simulace načtení konfigurace z externího zdroje."""
    print(f"    [DB] Načítám konfiguraci pro {prostredi}...")
    time.sleep(0.01)
    return {"env": prostredi, "timeout": "30", "retries": "3"}


def demo_ttl_dekorator() -> None:
    print("\n=== @ttl_cache dekorátor ===")

    for i in range(4):
        start = time.perf_counter()
        cfg = nacti_konfiguraci("production")
        elapsed = (time.perf_counter() - start) * 1000
        print(f"  Volání {i+1}: {elapsed:.1f}ms — {cfg['env']}")
        if i == 1:
            time.sleep(0.25)   # TTL expiruje mezi voláním 2 a 3


# ── Request Coalescing ────────────────────────────────────────────────────────

class CoalescingCache:
    """
    Request coalescing — zabrání thundering herd.
    Více paralelních požadavků na stejný klíč → pouze 1 DB dotaz.
    """

    def __init__(self) -> None:
        self._cache: dict[str, Any] = {}
        self._pending: dict[str, threading.Event] = {}
        self._zamek = threading.Lock()
        self._db_dotazy = 0

    def get(self, klic: str, loader: Callable[[str], Any]) -> Any:
        # 1. Cache hit
        with self._zamek:
            if klic in self._cache:
                return self._cache[klic]
            if klic in self._pending:
                event = self._pending[klic]
                smistate = False
            else:
                event_new = threading.Event()
                self._pending[klic] = event_new
                smistate = True

        if not smistate:
            # Čeká na výsledek prvního vlákna
            event.wait(timeout=5.0)
            with self._zamek:
                return self._cache.get(klic)

        # Jsem první (owner) — provedu DB dotaz
        try:
            self._db_dotazy += 1
            hodnota = loader(klic)
            with self._zamek:
                self._cache[klic] = hodnota
            return hodnota
        finally:
            with self._zamek:
                ev = self._pending.pop(klic, None)
            if ev is not None:
                ev.set()


def demo_request_coalescing() -> None:
    print("\n=== Request Coalescing (Thundering Herd prevence) ===")

    cc = CoalescingCache()
    vysledky: list[str] = []
    zamek_list = threading.Lock()

    def db_loader(klic: str) -> str:
        time.sleep(0.05)   # Simulace pomalé DB
        return f"data_pro_{klic}"

    def worker(id_: int) -> None:
        val = cc.get("hot_key", db_loader)
        with zamek_list:
            vysledky.append(f"Worker {id_}: {val}")

    # 10 vláken současně požaduje stejný klíč
    vlakna = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for v in vlakna:
        v.start()
    for v in vlakna:
        v.join()

    print(f"  10 paralelních požadavků na 'hot_key':")
    print(f"  DB dotazů celkem: {cc._db_dotazy}  (očekáváno: 1)")
    print(f"  Výsledky ({len(vysledky)} vláken):")
    for r in sorted(vysledky)[:4]:
        print(f"    {r}")
    if len(vysledky) > 4:
        print(f"    ... a {len(vysledky)-4} dalších")


# ── Dvouvrstvá cache (L1 + L2) ────────────────────────────────────────────────

class TwoLevelCache:
    """
    L1 = rychlá in-memory LRU (malá kapacita)
    L2 = pomalejší "vzdálená" cache (velká kapacita, simulovaná)
    """

    def __init__(self, l1_kapacita: int = 5, l2_kapacita: int = 50) -> None:
        self._l1: LRUCache[str, Any] = LRUCache(kapacita=l1_kapacita)
        self._l2: LRUCache[str, Any] = LRUCache(kapacita=l2_kapacita)
        self._l1_hits = self._l2_hits = self._misses = 0

    def get(self, klic: str, loader: Callable[[str], Any]) -> Any:
        # L1
        val = self._l1.get(klic)
        if val is not None:
            self._l1_hits += 1
            return val
        # L2
        val = self._l2.get(klic)
        if val is not None:
            self._l2_hits += 1
            self._l1.put(klic, val)   # Promote do L1
            return val
        # Miss → DB
        self._misses += 1
        val = loader(klic)
        self._l2.put(klic, val)
        self._l1.put(klic, val)
        return val

    def stats(self) -> str:
        total = self._l1_hits + self._l2_hits + self._misses
        return (f"L1 hits: {self._l1_hits}, L2 hits: {self._l2_hits}, "
                f"Misses: {self._misses}, Hit rate: {(self._l1_hits+self._l2_hits)/max(total,1):.1%}")


def demo_two_level_cache() -> None:
    print("\n=== Dvouvrstvá cache (L1+L2) ===")

    def fake_db(klic: str) -> str:
        time.sleep(0.005)
        return f"hodnota_{klic}"

    cache = TwoLevelCache(l1_kapacita=3, l2_kapacita=20)

    # Přístup k několika klíčům
    klice = ["a", "b", "c", "a", "d", "a", "b", "e", "a", "c", "d"]
    for klic in klice:
        cache.get(klic, fake_db)

    print(f"  {len(klice)} požadavků, L1 kapacita=3, L2 kapacita=20:")
    print(f"  {cache.stats()}")


# ── Hlavní funkce ──────────────────────────────────────────────────────────────

def main() -> None:
    print("╔══════════════════════════════════════════╗")
    print("║  Lekce 124 — Caching vrstvy             ║")
    print("╚══════════════════════════════════════════╝")

    demo_lru_cache()
    demo_lru_vlastni()
    demo_cache_aside()
    demo_ttl_cache()
    demo_ttl_dekorator()
    demo_request_coalescing()
    demo_two_level_cache()

    print("\nHotovo! Klíčové poznatky:")
    print("  • @lru_cache / @cache — okamžité memoizování čistých funkcí")
    print("  • LRUCache: OrderedDict + move_to_end → O(1) operace")
    print("  • Cache-aside: aplikace zodpovídá za invalidaci")
    print("  • TTLCache: lazy eviction + aktivní čištění")
    print("  • Request coalescing: 1 DB dotaz místo N paralelních")
    print("  • L1+L2: rychlá malá + pomalá velká cache")


if __name__ == "__main__":
    main()
