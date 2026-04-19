# Lekce 107: Idempotence, retry, timeouty, circuit breaker

## Proč potřebujeme retry a circuit breaker?

Distribuované systémy selhávají. Síť je nespolehlivá. Databáze občas nedostupná. Bez ochrany se chyby kaskádově šíří celým systémem.

```
Bez ochrany:
  Klient → Service A → Service B → Database
  Database padla → B čeká → A čeká → Klient timeout → frustrace

S ochranou:
  Klient → Service A → [Circuit Breaker] → Service B
  B padla → CB se otevře → A okamžitě vrátí fallback → Klient dostane odpověď
```

---

## Idempotence

Operace je **idempotentní** pokud vícenásobné provedení = jednorázové provedení.

```python
# Idempotentní: PUT (přepíše stav)
PUT /users/42  {"jmeno": "Anna"}   # 2× stejný výsledek

# NENÍ idempotentní: POST bez deduplication
POST /payments  {"castka": 100}    # každé volání vytvoří novou platbu!

# Idempotentní POST — pomocí idempotency key
POST /payments
Idempotency-Key: "550e8400-e29b-41d4-a716-446655440000"
{"castka": 100}
# Server uloží key, při opakování vrátí stejnou odpověď
```

---

## Retry s exponential backoff

Exponential backoff: každý další pokus čeká dvojnásobně dlouho + jitter (náhodné zpoždění).

```python
import time
import random
from typing import Callable, TypeVar

T = TypeVar("T")

def retry_s_backoff(
    fn: Callable[[], T],
    max_pokusy: int = 3,
    zakladni_zpozdeni: float = 1.0,
    nasobitel: float = 2.0,
    max_zpozdeni: float = 30.0,
) -> T:
    for pokus in range(1, max_pokusy + 1):
        try:
            return fn()
        except Exception as exc:
            if pokus == max_pokusy:
                raise
            zpozdeni = min(zakladni_zpozdeni * (nasobitel ** (pokus - 1)), max_zpozdeni)
            jitter = random.uniform(0, zpozdeni * 0.1)  # ±10% jitter
            print(f"Pokus {pokus} selhal ({exc}), čekám {zpozdeni + jitter:.2f}s")
            time.sleep(zpozdeni + jitter)
    raise RuntimeError("Nedosažitelné")
```

---

## Dekorátor pro retry

```python
import functools

def retry(
    max_pokusy: int = 3,
    vyjimky: tuple[type[Exception], ...] = (Exception,),
    zakladni_zpozdeni: float = 1.0,
):
    def dekorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for pokus in range(1, max_pokusy + 1):
                try:
                    return fn(*args, **kwargs)
                except vyjimky as exc:
                    if pokus == max_pokusy:
                        raise
                    zpozdeni = zakladni_zpozdeni * (2 ** (pokus - 1))
                    print(f"[retry] {fn.__name__}: pokus {pokus}/{max_pokusy}, čekám {zpozdeni}s")
                    time.sleep(zpozdeni)
        return wrapper
    return dekorator

@retry(max_pokusy=3, vyjimky=(ConnectionError,), zakladni_zpozdeni=0.5)
def nacti_data_z_api(url: str) -> dict:
    ...  # může vyhodit ConnectionError
```

---

## Tenacity (knihovna)

V produkci se používá `tenacity` — bohatší API:

```python
# pip install tenacity
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log,
)
import logging

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(ConnectionError),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def volej_api(url: str) -> dict:
    ...
```

---

## Circuit Breaker pattern

Tři stavy:

```
CLOSED (normální provoz)
   │  N selhání za sebou
   ▼
OPEN (vypnut, odmítá ihned)
   │  timeout (recovery window)
   ▼
HALF_OPEN (zkušební provoz)
   │  úspěch → CLOSED
   │  selhání → OPEN
```

```python
from enum import Enum, auto
from datetime import datetime, timedelta

class StavCB(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()

class CircuitBreaker:
    def __init__(
        self,
        prah_selhani: int = 3,
        timeout_obnovy: float = 30.0,
    ) -> None:
        self.stav = StavCB.CLOSED
        self._prah = prah_selhani
        self._timeout = timeout_obnovy
        self._pocet_selhani = 0
        self._otevreno_v: datetime | None = None

    def __call__(self, fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            self._zkontroluj_prechod()
            if self.stav == StavCB.OPEN:
                raise RuntimeError(f"Circuit breaker OPEN — volání odmítnuto")
            try:
                vysledek = fn(*args, **kwargs)
                self._pri_uspechu()
                return vysledek
            except Exception:
                self._pri_selhani()
                raise
        return wrapper

    def _zkontroluj_prechod(self) -> None:
        if self.stav == StavCB.OPEN and self._otevreno_v:
            if datetime.now() - self._otevreno_v > timedelta(seconds=self._timeout):
                self.stav = StavCB.HALF_OPEN

    def _pri_uspechu(self) -> None:
        self._pocet_selhani = 0
        self.stav = StavCB.CLOSED

    def _pri_selhani(self) -> None:
        self._pocet_selhani += 1
        if self._pocet_selhani >= self._prah:
            self.stav = StavCB.OPEN
            self._otevreno_v = datetime.now()
```

---

## Timeout

```python
import signal

class TimeoutChyba(Exception):
    pass

def s_timeoutem(sekund: float):
    """Dekorátor pro Unix systémy (signal.alarm)."""
    def dekorator(fn):
        def handler(signum, frame):
            raise TimeoutChyba(f"Timeout po {sekund}s")
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(int(sekund))
            try:
                return fn(*args, **kwargs)
            finally:
                signal.alarm(0)
        return wrapper
    return dekorator
```

Pro produkci: `asyncio.wait_for`, `concurrent.futures.TimeoutError`, nebo `httpx`/`requests` timeout parametr.

---

## Shrnutí

| Technika | Kdy použít | Pythonic způsob |
|----------|-----------|-----------------|
| Idempotence | Vždy u plateb, emailů | Idempotency-Key v hlavičce |
| Retry + backoff | Přechodné chyby sítě | `tenacity` nebo vlastní dekorátor |
| Circuit Breaker | Ochrana před kaskádovým selháním | Vlastní třída nebo `pybreaker` |
| Timeout | Každé I/O volání | `httpx(timeout=5)`, `asyncio.wait_for` |

---

## Cvičení

1. Rozšiř `CircuitBreaker` o metodu `statistiky()` která vrátí počet úspěchů/selhání.
2. Přidej do retry dekorátoru parametr `on_retry: Callable` — callback volaný před každým pokusem.
3. Implementuj `RetryWithIdempotencyKey` — při retry neposílá nový požadavek, ale opakuje se stejným klíčem.
4. Kombinuj retry + circuit breaker: `@retry(3) + @circuit_breaker` — v jakém pořadí?
