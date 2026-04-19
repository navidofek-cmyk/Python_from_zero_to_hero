# Lekce 124: Caching vrstvy

Cache je dočasné úložiště výsledků výpočtů nebo dat. Správná cache výrazně snižuje latenci a zátěž na backend systémy.

---

## `functools.lru_cache`

Nejjednodušší caching v Pythonu — vestavěný dekorátor pro memoizaci čistých funkcí.

```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

# Bez cache: exponenciální čas
# S cache: lineární čas
start = time.perf_counter()
print(fib(40))
print(f"Čas: {time.perf_counter()-start:.4f}s")

# Statistiky cache
info = fib.cache_info()
print(f"Hits: {info.hits}, Misses: {info.misses}, Size: {info.currsize}")

# Vymazání cache
fib.cache_clear()
```

`@cache` (Python 3.9+) je totéž jako `@lru_cache(maxsize=None)` — neomezená cache.

```python
from functools import cache

@cache
def tezky_vypocet(n: int) -> int:
    return sum(range(n))
```

---

## Vlastní LRU Cache implementace

Pochopení implementace pomáhá ladit chování. LRU = Least Recently Used — vyřazuje nejdéle nepoužité položky.

```python
from collections import OrderedDict
from typing import TypeVar, Generic

K = TypeVar("K")
V = TypeVar("V")

class LRUCache(Generic[K, V]):
    """LRU cache s maximální kapacitou."""

    def __init__(self, kapacita: int) -> None:
        self._kapacita = kapacita
        self._cache: OrderedDict[K, V] = OrderedDict()

    def get(self, klic: K) -> V | None:
        if klic not in self._cache:
            return None
        self._cache.move_to_end(klic)   # Přesunout na konec = "nedávno použitý"
        return self._cache[klic]

    def put(self, klic: K, hodnota: V) -> None:
        if klic in self._cache:
            self._cache.move_to_end(klic)
        self._cache[klic] = hodnota
        if len(self._cache) > self._kapacita:
            self._cache.popitem(last=False)   # Odstraní nejstarší (začátek)

    def __len__(self) -> int:
        return len(self._cache)

    def __repr__(self) -> str:
        return f"LRUCache({dict(self._cache)})"
```

---

## Cache-Aside Pattern

Aplikace sama řídí cache — nejběžnější vzor. Read-through a write-through jsou automatičtější varianty.

```
get(key):
    1. Zkus cache
    2. Cache hit → vrať hodnotu
    3. Cache miss → načti z DB → ulož do cache → vrať hodnotu
```

```python
import time
from typing import Any

class CacheAside:
    def __init__(self) -> None:
        self._cache: dict[str, Any] = {}
        self._db: dict[str, Any] = {"user:1": "Alice", "user:2": "Bob"}

    def get(self, klic: str) -> Any:
        # 1. Cache lookup
        if klic in self._cache:
            print(f"  CACHE HIT: {klic}")
            return self._cache[klic]

        # 2. Cache miss — načti z DB
        print(f"  CACHE MISS: {klic} — načítám z DB")
        hodnota = self._db.get(klic)
        if hodnota is not None:
            self._cache[klic] = hodnota
        return hodnota

    def invalidate(self, klic: str) -> None:
        """Po zápisu do DB invalidujeme cache."""
        self._cache.pop(klic, None)

    def write(self, klic: str, hodnota: Any) -> None:
        self._db[klic] = hodnota
        self.invalidate(klic)   # Invalidate on write
```

---

## TTL Cache — cache s expirací

LRU cache nevyprší — TTL (Time To Live) cache automaticky zahodí staré položky.

```python
import time
from dataclasses import dataclass
from typing import Any

@dataclass
class CacheEntry:
    hodnota: Any
    expiry: float   # Unix timestamp

class TTLCache:
    """Cache s automatickou expirací položek."""

    def __init__(self, ttl_sekund: float) -> None:
        self._ttl = ttl_sekund
        self._data: dict[str, CacheEntry] = {}

    def get(self, klic: str) -> Any | None:
        entry = self._data.get(klic)
        if entry is None:
            return None
        if time.monotonic() > entry.expiry:
            del self._data[klic]   # Lazy eviction
            return None
        return entry.hodnota

    def put(self, klic: str, hodnota: Any) -> None:
        self._data[klic] = CacheEntry(
            hodnota=hodnota,
            expiry=time.monotonic() + self._ttl,
        )

    def evict_expired(self) -> int:
        """Aktivní čištění — vhodné volat periodicky."""
        now = time.monotonic()
        expired = [k for k, e in self._data.items() if now > e.expiry]
        for k in expired:
            del self._data[k]
        return len(expired)
```

---

## Request Coalescing (Thundering Herd)

Problém: 100 požadavků dorazí současně pro stejný klíč při cache miss → 100 dotazů do DB.

Řešení: První požadavek spustí načítání, ostatní čekají na výsledek.

```python
import threading
import time
from typing import Any

class CoalescingCache:
    """Zhroutí paralelní requesty pro stejný klíč do jednoho DB dotazu."""

    def __init__(self) -> None:
        self._cache: dict[str, Any] = {}
        self._pending: dict[str, threading.Event] = {}
        self._zamek = threading.Lock()

    def get(self, klic: str, loader: Any) -> Any:
        # 1. Cache hit
        with self._zamek:
            if klic in self._cache:
                return self._cache[klic]

            # 2. Někdo jiný již načítá — čekej
            if klic in self._pending:
                event = self._pending[klic]
            else:
                # 3. Jsem první — zaregistruji event
                event = threading.Event()
                self._pending[klic] = event
                event = None   # Signál, že jsem "majitel"

        if event is not None:
            # Čekám na výsledek jiného vlákna
            event.wait(timeout=5.0)
            with self._zamek:
                return self._cache.get(klic)

        # Načítám jako první (owner)
        try:
            hodnota = loader(klic)   # Volání DB / API
            with self._zamek:
                self._cache[klic] = hodnota
            return hodnota
        finally:
            with self._zamek:
                ev = self._pending.pop(klic, None)
            if ev:
                ev.set()   # Probudí čekající vlákna
```

---

## Porovnání caching vzorů

| Vzor | Popis | Kdy použít |
|---|---|---|
| **LRU Cache** | Vyřazuje nejdéle nepoužité | Výpočetně drahé funkce |
| **TTL Cache** | Expiruje po čase | Data, která zastarají |
| **Cache-Aside** | Aplikace řídí cache ručně | Flexibilita, oddělení zod. |
| **Write-Through** | Zápis do DB i cache najednou | Konzistence na prvním místě |
| **Write-Behind** | Zápis do cache, async do DB | Vysoký write throughput |
| **Request Coalescing** | Sloučí paralelní requesty | Cache stampede prevence |

---

## Cache invalidation — nejtěžší problém

> "There are only two hard things in Computer Science: cache invalidation and naming things." — Phil Karlton

Strategie invalidace:

```python
# 1. Time-based (TTL) — nejjednodušší, ale nepřesné
# 2. Event-based — při změně dat vymaž klíč
# 3. Versioned keys — přidej verzi do klíče
klic_v1 = "user:1:v1"
klic_v2 = "user:1:v2"   # Nová verze = automatická invalidace

# 4. Cache tags — skupina klíčů pod jedním tagem
```

---

## Shrnutí

- `functools.lru_cache` / `@cache` — okamžité memoizování čistých funkcí
- Vlastní `LRUCache` pomocí `OrderedDict` — kontrola nad chováním
- **Cache-aside**: aplikace = odpovědnost za cache, nejčastější vzor
- **TTL cache**: data s dobou platnosti, lazy eviction
- **Request coalescing**: zabrání cache stampede při high concurrency

---

## Cvičení

1. Implementuj `LFU Cache` (Least Frequently Used) — vyřadí nejméně používanou položku.
2. Rozšiř `TTLCache` o sliding window TTL — TTL se obnovuje při každém přístupu.
3. Napiš dekorátor `@ttl_cache(seconds=60)` analogický k `@lru_cache`.
4. Implementuj dvouvrstvou cache: L1 (in-memory, max 100 položek) + L2 (simulovaná "vzdálená" cache).
