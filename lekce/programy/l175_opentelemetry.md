# Program — Lekce 175: Lekce 175: OpenTelemetry — distribuované trasování

Patří k lekci [Lekce 175: OpenTelemetry — distribuované trasování](../175_opentelemetry.md).

## Jak spustit

```bash
python3 programy/l175_opentelemetry.py
```

## Zdrojový kód

### `l175_opentelemetry.py`

```py
"""Lekce 175 — OpenTelemetry: distribuované trasování.
Spuštění: uv run --with opentelemetry-sdk l175_opentelemetry.py
"""

import time
import asyncio
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Optional


# Simulace OTel bez skutečného SDK
@dataclass
class Span:
    name: str
    parent: Optional["Span"] = None
    attrs: dict = field(default_factory=dict)
    events: list[str] = field(default_factory=list)
    start: float = field(default_factory=time.perf_counter)
    end: float = 0.0

    def set_attribute(self, k, v): self.attrs[k] = v
    def add_event(self, e): self.events.append(e)
    def finish(self): self.end = time.perf_counter()
    @property
    def duration_ms(self): return (self.end - self.start) * 1000


class SimpleTracer:
    def __init__(self, service: str):
        self.service = service
        self.spans: list[Span] = []
        self._active: list[Span] = []

    @contextmanager
    def start_span(self, name: str):
        parent = self._active[-1] if self._active else None
        span = Span(name, parent)
        self._active.append(span)
        self.spans.append(span)
        try:
            yield span
        finally:
            span.finish()
            self._active.pop()

    def print_trace(self):
        print(f"\n  Trace pro '{self.service}':")
        for span in self.spans:
            depth = 0
            p = span.parent
            while p:
                depth += 1; p = p.parent
            indent = "  " + "  " * depth
            attrs = ", ".join(f"{k}={v}" for k, v in span.attrs.items())
            print(f"  {indent}[{span.duration_ms:.1f}ms] {span.name}" +
                  (f" ({attrs})" if attrs else ""))
            for ev in span.events:
                print(f"  {indent}  event: {ev}")


def demo_trace():
    print("=== Distribuované trasování (simulace) ===")
    tracer = SimpleTracer("order-service")

    with tracer.start_span("zpracuj_objednavku") as root:
        root.set_attribute("order.id", 42)
        root.set_attribute("user.id", 101)
        root.add_event("začátek zpracování")

        with tracer.start_span("db.select_order"):
            time.sleep(0.015)

        with tracer.start_span("validate_inventory") as val:
            val.set_attribute("items", 3)
            time.sleep(0.008)

        with tracer.start_span("payment.charge") as pay:
            pay.set_attribute("amount_czk", 1500)
            time.sleep(0.025)
            pay.add_event("platba autorizována")

        with tracer.start_span("send_confirmation"):
            time.sleep(0.005)

        root.set_attribute("order.status", "completed")
        root.add_event("objednávka dokončena")

    tracer.print_trace()


async def demo_async_trace():
    print("\n=== Async trace (paralelní operace) ===")
    tracer = SimpleTracer("api-gateway")

    async def fetch_user(tracer, uid):
        with tracer.start_span(f"fetch_user_{uid}") as span:
            span.set_attribute("user.id", uid)
            await asyncio.sleep(0.02)
            return {"id": uid, "name": f"User {uid}"}

    async def fetch_orders(tracer, uid):
        with tracer.start_span(f"fetch_orders_{uid}") as span:
            span.set_attribute("user.id", uid)
            await asyncio.sleep(0.03)
            return [1, 2, 3]

    with tracer.start_span("GET /profile/42") as root:
        root.set_attribute("http.method", "GET")
        root.set_attribute("http.url", "/profile/42")
        # Paralelní fetch
        user, orders = await asyncio.gather(
            fetch_user(tracer, 42),
            fetch_orders(tracer, 42)
        )
        root.set_attribute("http.status_code", 200)

    tracer.print_trace()


def demo_metrics():
    print("\n=== Metriky (simulace) ===")
    metrics = {"requests": 0, "errors": 0, "latencies": []}

    def record_request(endpoint: str, status: int, duration_ms: float):
        metrics["requests"] += 1
        if status >= 500:
            metrics["errors"] += 1
        metrics["latencies"].append(duration_ms)

    import random
    random.seed(42)
    for i in range(100):
        status = random.choice([200]*95 + [500]*5)
        lat = random.expovariate(1/50)  # exponenciální distribuce
        record_request("/api/orders", status, lat)

    lats = sorted(metrics["latencies"])
    n = len(lats)
    print(f"  Requesty: {metrics['requests']}")
    print(f"  Chybovost: {metrics['errors']/metrics['requests']*100:.1f}%")
    print(f"  p50: {lats[n//2]:.1f}ms")
    print(f"  p95: {lats[int(n*0.95)]:.1f}ms")
    print(f"  p99: {lats[int(n*0.99)]:.1f}ms")


def main():
    print("=" * 50)
    print("  🔭 OpenTelemetry Demo")
    print("=" * 50)
    demo_trace()
    asyncio.run(demo_async_trace())
    demo_metrics()
    print("\n✅ Demo dokončeno!")
    print("Instalace: uv add opentelemetry-sdk opentelemetry-exporter-otlp")
    print("Jaeger UI: docker run -p 16686:16686 jaegertracing/all-in-one")


if __name__ == "__main__":
    main()

```
