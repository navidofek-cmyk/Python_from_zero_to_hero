# Lekce 112 — Observabilita v Pythonu

**Observabilita** (pozorovatelnost) je schopnost porozumět vnitřnímu stavu systému z jeho vnějších výstupů. Tři pilíře observability jsou **logy**, **metriky** a **traces** (trasování).

---

## Tři pilíře observability

```
┌─────────────────────────────────────────────────────────┐
│                    OBSERVABILITA                         │
├───────────────┬──────────────────┬──────────────────────┤
│     LOGY      │     METRIKY      │       TRACES         │
│               │                  │                      │
│ Co se stalo?  │ Jak moc? Jak     │ Kde je bottleneck?   │
│ Diskrétní     │ rychle? Trend?   │ Celá cesta požadavku │
│ události      │ Agregovaná čísla │ napříč službami      │
│               │                  │                      │
│ Elasticsearch │ Prometheus       │ Jaeger, Zipkin       │
│ Loki, CloudW. │ Grafana          │ OpenTelemetry        │
└───────────────┴──────────────────┴──────────────────────┘
```

---

## 1. Strukturované logy — JSON formátter

Klasické textové logy jsou těžko strojově zpracovatelné. Strukturované logy v JSON formátu lze indexovat, filtrovat a agregovat.

```python
import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """Formatter, který převede log záznamy do JSON formátu."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        # Přidej extra pole (correlation_id, user_id, atd.)
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord.__dict__ and not key.startswith("_"):
                log_entry[key] = value

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False, default=str)


def setup_json_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)
```

### Výstup strukturovaného logu

```json
{
  "timestamp": "2026-04-19T10:23:41.123+00:00",
  "level": "INFO",
  "logger": "app.orders",
  "message": "Objednávka vytvořena",
  "module": "orders",
  "line": 87,
  "order_id": "ord-456",
  "user_id": "usr-123",
  "amount": 1299.0,
  "currency": "CZK"
}
```

---

## 2. Metriky — simulace Prometheus vzorů

Prometheus metriky jsou čítače, měřidla a histogramy. Bez externí knihovny implementujeme stejné vzory.

```python
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Counter:
    """Monotónně rostoucí čítač — pro počty událostí."""
    name: str
    help_text: str
    _value: float = field(default=0.0, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def inc(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value += amount

    @property
    def value(self) -> float:
        return self._value

    def prometheus_text(self) -> str:
        return f"# HELP {self.name} {self.help_text}\n# TYPE {self.name} counter\n{self.name} {self._value}"


@dataclass
class Gauge:
    """Aktuální hodnota — může klesat i stoupat."""
    name: str
    help_text: str
    _value: float = field(default=0.0, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def set(self, value: float) -> None:
        with self._lock:
            self._value = value

    def inc(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value += amount

    def dec(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value -= amount

    @property
    def value(self) -> float:
        return self._value


@dataclass
class Histogram:
    """Distribuce hodnot — pro latence, velikosti."""
    name: str
    help_text: str
    buckets: list[float] = field(default_factory=lambda: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5])
    _observations: list[float] = field(default_factory=list, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def observe(self, value: float) -> None:
        with self._lock:
            self._observations.append(value)

    @property
    def count(self) -> int:
        return len(self._observations)

    @property
    def sum(self) -> float:
        return sum(self._observations)

    def percentile(self, p: float) -> float:
        if not self._observations:
            return 0.0
        sorted_obs = sorted(self._observations)
        idx = int(len(sorted_obs) * p / 100)
        return sorted_obs[min(idx, len(sorted_obs) - 1)]
```

### Použití metrik s kontextovým manažerem

```python
import contextlib
import time

@contextlib.contextmanager
def track_duration(histogram: Histogram):
    """Změří dobu trvání bloku kódu."""
    start = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - start
        histogram.observe(duration)

# Použití:
http_duration = Histogram("http_request_duration_seconds", "Latence HTTP požadavků")
http_requests = Counter("http_requests_total", "Celkový počet HTTP požadavků")

with track_duration(http_duration):
    # zpracování požadavku...
    time.sleep(0.042)

http_requests.inc()
print(f"p50: {http_duration.percentile(50):.3f}s")
print(f"p99: {http_duration.percentile(99):.3f}s")
```

---

## 3. Tracing — Correlation ID přes contextvars

Distribuované trasování propojuje logy a operace napříč vlákny a službami pomocí jedinečného identifikátoru.

```python
import uuid
from contextvars import ContextVar

# ContextVar je thread-safe a async-safe (asyncio)
_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")
_span_id: ContextVar[str] = ContextVar("span_id", default="")


def new_trace() -> str:
    """Vytvoří nový trace s unikátním correlation ID."""
    cid = str(uuid.uuid4())
    _correlation_id.set(cid)
    _span_id.set(str(uuid.uuid4())[:8])
    return cid


def get_correlation_id() -> str:
    return _correlation_id.get()


def get_span_id() -> str:
    return _span_id.get()


class TracingFilter(logging.Filter):
    """Přidá correlation_id ke každému logu automaticky."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = get_correlation_id()
        record.span_id = get_span_id()
        return True
```

### Propagace trace napříč voláními

```python
import asyncio

async def handle_request(request_id: str) -> dict:
    new_trace()  # Nastav correlation ID pro tento požadavek
    logger = logging.getLogger("app")

    logger.info("Požadavek přijat", extra={"request_id": request_id})

    # Všechny vnořené volání sdílejí stejné correlation ID
    user = await fetch_user("usr-1")
    order = await create_order(user)

    logger.info("Požadavek zpracován", extra={"order_id": order["id"]})
    return order


async def fetch_user(user_id: str) -> dict:
    logger = logging.getLogger("app.users")
    # correlation_id je automaticky dostupný přes ContextVar
    logger.info("Načítám uživatele %s", user_id)
    await asyncio.sleep(0.01)
    return {"id": user_id, "name": "Alice"}
```

---

## 4. Middleware pattern pro observabilitu

```python
from functools import wraps
from typing import Callable, TypeVar, Any
import time

F = TypeVar("F", bound=Callable[..., Any])

def observable(
    counter: Counter,
    histogram: Histogram,
    logger: logging.Logger,
) -> Callable[[F], F]:
    """Dekorátor přidávající observabilitu libovolné funkci."""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            correlation_id = get_correlation_id() or new_trace()
            logger.info(
                "Volání funkce %s zahájeno",
                func.__name__,
                extra={"correlation_id": correlation_id},
            )
            try:
                result = func(*args, **kwargs)
                counter.inc()
                return result
            except Exception as exc:
                logger.error(
                    "Chyba ve funkci %s: %s",
                    func.__name__, exc,
                    extra={"correlation_id": correlation_id},
                )
                raise
            finally:
                duration = time.perf_counter() - start
                histogram.observe(duration)
                logger.info(
                    "Volání funkce %s dokončeno za %.3fs",
                    func.__name__, duration,
                    extra={"correlation_id": correlation_id},
                )
        return wrapper  # type: ignore[return-value]
    return decorator
```

---

## 5. Health check endpoint

```python
import os
import time

_START_TIME = time.time()


def health_check() -> dict:
    """Základní health check — vrací stav aplikace."""
    return {
        "status": "healthy",
        "uptime_seconds": round(time.time() - _START_TIME, 1),
        "version": os.environ.get("APP_VERSION", "dev"),
        "checks": {
            "database": _check_database(),
            "cache": _check_cache(),
        }
    }


def _check_database() -> dict:
    # V reálné aplikaci: db.execute("SELECT 1")
    return {"status": "ok", "latency_ms": 1.2}


def _check_cache() -> dict:
    # V reálné aplikaci: redis.ping()
    return {"status": "ok", "latency_ms": 0.3}
```

---

## 6. /metrics endpoint (Prometheus exposition format)

```python
def metrics_endpoint(
    counters: list[Counter],
    gauges: list[Gauge],
    histograms: list[Histogram],
) -> str:
    """Generuje Prometheus text formát pro /metrics endpoint."""
    lines: list[str] = []

    for counter in counters:
        lines.append(f"# HELP {counter.name} {counter.help_text}")
        lines.append(f"# TYPE {counter.name} counter")
        lines.append(f"{counter.name} {counter.value}")

    for gauge in gauges:
        lines.append(f"# HELP {gauge.name} {gauge.help_text}")
        lines.append(f"# TYPE {gauge.name} gauge")
        lines.append(f"{gauge.name} {gauge.value}")

    for hist in histograms:
        lines.append(f"# HELP {hist.name} {hist.help_text}")
        lines.append(f"# TYPE {hist.name} histogram")
        lines.append(f"{hist.name}_count {hist.count}")
        lines.append(f"{hist.name}_sum {hist.sum:.6f}")

    return "\n".join(lines)
```

---

## Shrnutí

| Pilíř | Nástroj | Python vzor |
|-------|---------|-------------|
| Logy | Loki, CloudWatch | `logging` + `JsonFormatter` |
| Metriky | Prometheus + Grafana | `Counter`, `Gauge`, `Histogram` |
| Traces | Jaeger, Zipkin | `contextvars.ContextVar` |
| Integrace | OpenTelemetry | `opentelemetry-sdk` |

**Klíčová pravidla:**
- Logy = události (co se stalo)
- Metriky = agregáty (jak moc, jak rychle)
- Traces = cesty (kde je pomalé místo)
- Vše propojuje **correlation ID**

---

## Cvičení

1. Implementujte `JsonFormatter`, který přidá pole `environment` (z `os.environ.get("APP_ENV")`), `hostname` a `pid` ke každému log záznamu.
2. Přidejte do `Histogram` třídy metodu `bucket_counts()`, která vrátí počet pozorování v každém bucketu (potřebné pro Prometheus exposition format).
3. Vytvořte `middleware` funkci pro FastAPI nebo čisté WSGI, která pro každý požadavek: (a) přiřadí nové correlation ID, (b) zaznamená začátek a konec požadavku, (c) inkrementuje counter požadavků.
4. Napište test, který ověří, že `ContextVar` skutečně izoluje correlation ID mezi vlákny — spusťte 10 souběžných vláken, každé s jiným ID, a ověřte, že nedochází k prolínání.
