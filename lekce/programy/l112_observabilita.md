# Program — Lekce 112: Lekce 112 — Observabilita v Pythonu

Patří k lekci [Lekce 112 — Observabilita v Pythonu](../112_observabilita.md).

## Jak spustit

```bash
python3 programy/l112_observabilita.py
```

## Zdrojový kód

### `l112_observabilita.py`

```py
"""Lekce 112 — Observabilita: logy, metriky, tracing."""
from __future__ import annotations

import contextlib
import json
import logging
import math
import random
import sys
import threading
import time
import uuid
from collections import defaultdict
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Generator, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

# ── JSON Formatter pro strukturované logy ────────────────────────────────────

class JsonFormatter(logging.Formatter):
    """Formatter zapisující log záznamy jako JSON — strojově zpracovatelné."""

    IGNORED_ATTRS: frozenset[str] = frozenset({
        "args", "created", "exc_info", "exc_text", "filename",
        "funcName", "levelno", "lineno", "message", "module",
        "msecs", "msg", "name", "pathname", "process",
        "processName", "relativeCreated", "stack_info",
        "taskName", "thread", "threadName",
    })

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        # Přidej extra pole předaná přes extra={...}
        for key, value in record.__dict__.items():
            if key not in self.IGNORED_ATTRS and not key.startswith("_"):
                entry[key] = value
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False, default=str)


def setup_json_logging(level: int = logging.INFO) -> None:
    """Inicializuje JSON logování na stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = []
    root.addHandler(handler)
    root.setLevel(level)


# ── Metriky (Prometheus vzor, čistá stdlib) ───────────────────────────────────

@dataclass
class Counter:
    """Monotónně rostoucí čítač událostí."""
    name: str
    help_text: str
    _values: dict[tuple[str, ...], float] = field(default_factory=dict, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def inc(self, amount: float = 1.0, **labels: str) -> None:
        key = tuple(sorted(labels.items()))
        with self._lock:
            self._values[key] = self._values.get(key, 0.0) + amount

    def total(self) -> float:
        return sum(self._values.values())

    def prometheus_lines(self) -> list[str]:
        lines = [
            f"# HELP {self.name} {self.help_text}",
            f"# TYPE {self.name} counter",
        ]
        for label_key, value in self._values.items():
            if label_key:
                label_str = ",".join(f'{k}="{v}"' for k, v in label_key)
                lines.append(f"{self.name}{{{label_str}}} {value}")
            else:
                lines.append(f"{self.name} {value}")
        return lines


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
    """Distribuce hodnot — pro latence a velikosti."""
    name: str
    help_text: str
    buckets: list[float] = field(
        default_factory=lambda: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
    )
    _observations: list[float] = field(default_factory=list, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def observe(self, value: float) -> None:
        with self._lock:
            self._observations.append(value)

    @property
    def count(self) -> int:
        return len(self._observations)

    @property
    def total_sum(self) -> float:
        return sum(self._observations)

    def percentile(self, p: float) -> float:
        """Vrátí p-tý percentil (0–100)."""
        with self._lock:
            if not self._observations:
                return 0.0
            sorted_obs = sorted(self._observations)
            idx = max(0, int(math.ceil(len(sorted_obs) * p / 100)) - 1)
            return sorted_obs[idx]

    def bucket_counts(self) -> dict[float, int]:
        """Počet pozorování <= každé hranici (kumulativní)."""
        with self._lock:
            return {
                b: sum(1 for x in self._observations if x <= b)
                for b in self.buckets
            }

    def summary(self) -> str:
        return (
            f"n={self.count} sum={self.total_sum:.3f}s "
            f"p50={self.percentile(50):.3f}s "
            f"p95={self.percentile(95):.3f}s "
            f"p99={self.percentile(99):.3f}s"
        )


@contextlib.contextmanager
def track_duration(histogram: Histogram) -> Generator[None, None, None]:
    """Kontextový manažer měřící dobu trvání bloku."""
    start = time.perf_counter()
    try:
        yield
    finally:
        histogram.observe(time.perf_counter() - start)


# ── Tracing — Correlation ID přes ContextVar ─────────────────────────────────

_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")
_span_id: ContextVar[str] = ContextVar("span_id", default="")


def new_trace(parent_id: str | None = None) -> str:
    """Vytvoří nový trace context. Vrátí correlation ID."""
    cid = parent_id or str(uuid.uuid4())
    _correlation_id.set(cid)
    _span_id.set(uuid.uuid4().hex[:8])
    return cid


def get_trace_context() -> dict[str, str]:
    return {
        "correlation_id": _correlation_id.get() or "-",
        "span_id": _span_id.get() or "-",
    }


class TracingFilter(logging.Filter):
    """Automaticky přidá trace kontext ke každému log záznamu."""

    def filter(self, record: logging.LogRecord) -> bool:
        ctx = get_trace_context()
        record.correlation_id = ctx["correlation_id"]  # type: ignore[attr-defined]
        record.span_id = ctx["span_id"]                # type: ignore[attr-defined]
        return True


# ── Observable dekorátor (middleware pattern) ─────────────────────────────────

def observable(
    counter: Counter,
    histogram: Histogram,
    logger: logging.Logger,
) -> Callable[[F], F]:
    """Dekorátor přidávající automatickou observabilitu libovolné funkci."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            ctx = get_trace_context()
            logger.info(
                "→ %s zahájeno",
                func.__name__,
                extra=ctx,
            )
            try:
                with track_duration(histogram):
                    result = func(*args, **kwargs)
                counter.inc(status="ok", function=func.__name__)
                logger.info(
                    "← %s dokončeno",
                    func.__name__,
                    extra=ctx,
                )
                return result
            except Exception as exc:
                counter.inc(status="error", function=func.__name__)
                logger.error(
                    "✗ %s selhalo: %s",
                    func.__name__, exc,
                    extra=ctx,
                    exc_info=True,
                )
                raise

        return wrapper  # type: ignore[return-value]

    return decorator


# ── Simulace aplikace s observabilitou ────────────────────────────────────────

# Globální registry metrik
REQUEST_COUNTER = Counter("http_requests_total", "Počet HTTP požadavků")
REQUEST_DURATION = Histogram("http_request_duration_seconds", "Latence HTTP požadavků")
ACTIVE_REQUESTS = Gauge("http_active_requests", "Aktivní HTTP požadavky")
DB_QUERY_DURATION = Histogram("db_query_duration_seconds", "Latence DB dotazů")
DB_QUERY_COUNTER = Counter("db_queries_total", "Počet DB dotazů")

_logger = logging.getLogger("app.sim")


def simulate_db_query(query_type: str) -> dict[str, Any]:
    """Simuluje DB dotaz s náhodnou latencí."""
    latency = random.gauss(0.015, 0.005)  # průměr 15ms, sigma 5ms
    time.sleep(max(0.001, latency))
    DB_QUERY_DURATION.observe(latency)
    DB_QUERY_COUNTER.inc(query_type=query_type)
    return {"rows": random.randint(0, 100), "latency_ms": round(latency * 1000, 2)}


@observable(REQUEST_COUNTER, REQUEST_DURATION, _logger)
def handle_request(path: str, method: str = "GET") -> dict[str, Any]:
    """Zpracuje simulovaný HTTP požadavek."""
    ACTIVE_REQUESTS.inc()
    try:
        _logger.info("Zpracovávám %s %s", method, path)
        # Simuluj práci: DB dotaz + zpracování
        result = simulate_db_query("SELECT")
        # Občasná pomalejší operace
        if random.random() < 0.15:
            time.sleep(random.uniform(0.05, 0.2))
            _logger.warning("Pomalý požadavek detekován", extra=get_trace_context())
        return {"status": 200, "path": path, "db_rows": result["rows"]}
    finally:
        ACTIVE_REQUESTS.dec()


def simulate_traffic(n_requests: int = 20) -> None:
    """Simuluje provoz — vlákna jako souběžní klienti."""
    paths = ["/api/users", "/api/orders", "/api/products", "/health"]

    def make_request(i: int) -> None:
        # Každé vlákno dostane vlastní trace kontext (ContextVar izolace)
        new_trace()
        path = random.choice(paths)
        handle_request(path)

    threads = [threading.Thread(target=make_request, args=(i,)) for i in range(n_requests)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


# ── /metrics výstup ───────────────────────────────────────────────────────────

def render_metrics() -> str:
    """Vygeneruje Prometheus exposition format."""
    lines: list[str] = []
    for counter in [REQUEST_COUNTER, DB_QUERY_COUNTER]:
        lines.extend(counter.prometheus_lines())
        lines.append("")
    return "\n".join(lines)


# ── Hlavní funkce ─────────────────────────────────────────────────────────────

def main() -> None:
    setup_json_logging(logging.WARNING)  # Omez JSON logy pro přehlednost dema

    # Přidej TracingFilter na root logger
    tracing_filter = TracingFilter()
    logging.getLogger().addFilter(tracing_filter)

    print("=" * 65)
    print("OBSERVABILITA — DEMO: LOGY, METRIKY, TRACING")
    print("=" * 65)

    # --- 1. Strukturované logy ---
    print("\n[1] Strukturované JSON logy:")
    setup_json_logging(logging.DEBUG)
    demo_logger = logging.getLogger("demo")
    new_trace()
    demo_logger.info(
        "Objednávka vytvořena",
        extra={**get_trace_context(), "order_id": "ord-789", "amount": 1299.0},
    )
    demo_logger.warning(
        "Zásoby nízké",
        extra={**get_trace_context(), "product_id": "prod-42", "stock": 3},
    )
    setup_json_logging(logging.WARNING)  # zpět na WARNING pro simulaci

    # --- 2. Simulace provozu s metrikami ---
    print("\n[2] Simulace 30 souběžných HTTP požadavků...")
    random.seed(42)
    start = time.perf_counter()
    simulate_traffic(n_requests=30)
    elapsed = time.perf_counter() - start
    print(f"    Dokončeno za {elapsed:.2f}s")

    # --- 3. Výsledky metrik ---
    print("\n[3] Výsledky metrik:")
    print(f"    HTTP požadavků celkem : {REQUEST_COUNTER.total():.0f}")
    print(f"    HTTP latence          : {REQUEST_DURATION.summary()}")
    print(f"    DB dotazů celkem      : {DB_QUERY_COUNTER.total():.0f}")
    print(f"    DB latence            : {DB_QUERY_DURATION.summary()}")
    print(f"    Aktivní požadavky nyní: {ACTIVE_REQUESTS.value:.0f}")

    print("\n    Histogram HTTP latence — bucket counts:")
    for boundary, count in REQUEST_DURATION.bucket_counts().items():
        bar = "█" * min(count, 30)
        print(f"    <= {boundary:5.3f}s  {count:3d}  {bar}")

    # --- 4. Prometheus /metrics ukázka ---
    print("\n[4] Prometheus /metrics výstup (úryvek):")
    metrics_text = render_metrics()
    for line in metrics_text.splitlines()[:15]:
        print(f"    {line}")

    # --- 5. ContextVar izolace mezi vlákny ---
    print("\n[5] ContextVar izolace — každé vlákno má vlastní correlation_id:")
    results: list[tuple[int, str]] = []
    results_lock = threading.Lock()

    def capture_context(thread_num: int) -> None:
        cid = new_trace()
        time.sleep(random.uniform(0.001, 0.01))
        with results_lock:
            results.append((thread_num, cid))

    threads = [threading.Thread(target=capture_context, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    results.sort()
    for num, cid in results:
        print(f"    Vlákno {num}: correlation_id = {cid[:18]}...")
    unique_ids = len({cid for _, cid in results})
    print(f"    Unikátních ID: {unique_ids}/5 — izolace funguje: {unique_ids == 5}")

    print("\n[6] Shrnutí pilířů observability:")
    for pilir, popis in [
        ("Logy    ", "JsonFormatter → stdout → Loki/CloudWatch"),
        ("Metriky ", "Counter/Gauge/Histogram → /metrics → Prometheus → Grafana"),
        ("Tracing ", "ContextVar correlation_id → Jaeger/Zipkin"),
    ]:
        print(f"    {pilir} : {popis}")


if __name__ == "__main__":
    main()

```
