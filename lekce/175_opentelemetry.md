# Lekce 175: OpenTelemetry — distribuované trasování

OpenTelemetry (OTel) je standard pro sběr telemetrie: traces, metrics, logs. Vidíš jak request prochází microservices.

---

## 🚀 Instalace

```bash
uv add opentelemetry-sdk opentelemetry-exporter-otlp \
       opentelemetry-instrumentation-fastapi \
       opentelemetry-instrumentation-httpx \
       opentelemetry-instrumentation-sqlalchemy
```

---

## 🔍 Traces — sleduj request přes services

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource


def nastav_tracing(service_name: str):
    resource = Resource(attributes={"service.name": service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)


tracer = nastav_tracing("order-service")


def zpracuj_objednavku(order_id: int) -> dict:
    with tracer.start_as_current_span("zpracuj_objednavku") as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("service.version", "1.2.0")
        span.add_event("začátek zpracování")

        # Vnořený span pro DB dotaz
        with tracer.start_as_current_span("db.select_order"):
            objednavka = {"id": order_id, "cena": 1500}

        # Vnořený span pro platbu
        with tracer.start_as_current_span("payment.charge") as payment_span:
            payment_span.set_attribute("payment.amount", objednavka["cena"])
            vysledek = {"status": "ok", "transaction_id": "txn_123"}

        span.set_attribute("order.status", "completed")
        span.add_event("objednávka dokončena")
        return vysledek
```

---

## 📊 Metrics

```python
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
import time


meter_provider = MeterProvider(
    metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter())]
)
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("order-service")

# Counter — počítadlo (monotonicky roste)
objednavky_counter = meter.create_counter(
    "objednavky.celkem",
    description="Počet objednávek",
    unit="1",
)

# Histogram — distribuce hodnot
latency_histogram = meter.create_histogram(
    "request.latency",
    description="Latency requestů",
    unit="ms",
)

# Gauge — aktuální hodnota
fronta_gauge = meter.create_observable_gauge(
    "fronta.velikost",
    callbacks=[lambda options: [metrics.Observation(42)]],
)


def zpracuj_request():
    start = time.perf_counter()
    try:
        # ... logika ...
        objednavky_counter.add(1, {"status": "success", "typ": "web"})
    finally:
        ms = (time.perf_counter() - start) * 1000
        latency_histogram.record(ms, {"endpoint": "/orders"})
```

---

## 🏗️ FastAPI automatická instrumentace

```python
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

app = FastAPI()

# Automatická instrumentace — žádné ruční span vytváření!
FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()
SQLAlchemyInstrumentor().instrument()


@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    # Každý request automaticky vytvoří span se:
    # - HTTP method, URL, status code
    # - Request/response headers (volitelně)
    # - Correlation s downstream calls
    return {"order_id": order_id}
```

---

## 🐳 Docker: Jaeger + Collector

```yaml
# docker-compose.yml
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"   # UI
      - "4317:4317"     # OTLP gRPC

  otel-collector:
    image: otel/opentelemetry-collector:latest
    volumes:
      - ./otel-config.yml:/etc/otel/config.yaml
    command: ["--config=/etc/otel/config.yaml"]
    ports:
      - "4317:4317"
```

`otel-config.yml`:
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

exporters:
  jaeger:
    endpoint: jaeger:14250
  prometheus:
    endpoint: "0.0.0.0:8889"

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [jaeger]
    metrics:
      receivers: [otlp]
      exporters: [prometheus]
```

---

## 🔗 Propagace kontextu

```python
import httpx
from opentelemetry.propagate import inject, extract
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

# Klient — přidej trace context do headers
async def volej_service(url: str) -> dict:
    headers = {}
    inject(headers)   # přidá traceparent header
    async with httpx.AsyncClient() as client:
        return (await client.get(url, headers=headers)).json()


# Server — extrahuj trace context z headers
from fastapi import Request
@app.get("/downstream")
async def downstream(request: Request):
    ctx = extract(dict(request.headers))
    with tracer.start_as_current_span("downstream_handler", context=ctx):
        return {"zpracováno": True}
```

---

## ✏️ Cvičení

1. Nastav Jaeger lokálně, přidej tracing do microservices z lekce 171.
2. Implementuj **custom span attributes** — přidej user_id, tenant_id ke každému spanu.
3. Napiš **middleware** pro FastAPI, který automaticky přidává business metriky.
4. Postav **alerting** v Grafana — alert když p99 latency > 500ms.
5. Porovnej overhead OTel instrumentace: benchmark s a bez instrumentace.
