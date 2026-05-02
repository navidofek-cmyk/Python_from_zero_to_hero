# Lekce 176: Prometheus + Grafana — monitoring

Prometheus sbírá metriky pull modelem, Grafana je vizualizuje. Standard pro monitoring Python aplikací v Kubernetes.

---

## 🚀 Instalace

```bash
uv add prometheus-client

# Docker stack
docker run -d --name prometheus -p 9090:9090 \
  -v ./prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

docker run -d --name grafana -p 3000:3000 grafana/grafana
```

---

## 📊 Základní metriky

```python
from prometheus_client import (
    Counter, Gauge, Histogram, Summary,
    start_http_server, REGISTRY
)
import time
import random


# Counter — monotonicky roste (requesty, chyby)
http_requests = Counter(
    "http_requests_total",
    "Celkový počet HTTP requestů",
    labelnames=["method", "endpoint", "status_code"],
)

# Gauge — aktuální hodnota (queue size, CPU %)
aktivni_spojeni = Gauge(
    "active_connections",
    "Počet aktivních spojení",
)

worker_fronta = Gauge(
    "worker_queue_size",
    "Velikost fronty workerů",
    labelnames=["queue_name"],
)

# Histogram — distribuce (latency, velikost response)
request_latency = Histogram(
    "request_duration_seconds",
    "Latency HTTP requestů",
    labelnames=["endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

# Summary — podobné Histogramu, počítá percentily
db_query_duration = Summary(
    "db_query_duration_seconds",
    "Čas DB dotazů",
    labelnames=["query_type"],
)


# Použití
def simuluj_request(endpoint: str):
    start = time.perf_counter()
    status = random.choice(["200", "200", "200", "404", "500"])

    # Counter
    http_requests.labels(method="GET", endpoint=endpoint, status_code=status).inc()

    # Histogram
    duration = time.perf_counter() - start + random.uniform(0.01, 0.5)
    request_latency.labels(endpoint=endpoint).observe(duration)

    return status


# Gauge context manager
with aktivni_spojeni.track_inprogress():
    simuluj_request("/api/orders")

# Start metrics server
# start_http_server(8000)  # http://localhost:8000/metrics
```

---

## 🏗️ FastAPI integrace

```python
from fastapi import FastAPI, Request, Response
from prometheus_client import make_asgi_app, Counter, Histogram
import time

app = FastAPI()

# Přidej /metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

REQUEST_COUNT = Counter("fastapi_requests_total", "Requesty", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("fastapi_request_duration_seconds", "Latency", ["endpoint"])


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
    ).inc()
    REQUEST_LATENCY.labels(endpoint=request.url.path).observe(duration)
    return response


@app.get("/orders")
async def orders():
    return {"orders": [1, 2, 3]}
```

---

## ⚙️ Prometheus konfigurace

`prometheus.yml`:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]

rule_files:
  - "alerts.yml"

scrape_configs:
  - job_name: "fastapi"
    static_configs:
      - targets: ["app:8000"]
    metrics_path: /metrics

  - job_name: "redis"
    static_configs:
      - targets: ["redis-exporter:9121"]
```

---

## 🔔 Alerting

`alerts.yml`:
```yaml
groups:
  - name: aplikace
    rules:
      - alert: VysokaLatency
        expr: histogram_quantile(0.99, rate(fastapi_request_duration_seconds_bucket[5m])) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "p99 latency > 1s na {{ $labels.endpoint }}"

      - alert: VysokáChybovost
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Chybovost > 5%"

      - alert: PamětKritická
        expr: process_resident_memory_bytes > 500 * 1024 * 1024
        for: 10m
        labels:
          severity: warning
```

---

## 📈 PromQL — dotazovací jazyk

```promql
# Počet requestů za sekundu
rate(http_requests_total[5m])

# p99 latency
histogram_quantile(0.99, rate(request_duration_seconds_bucket[5m]))

# Chybovost (%)
rate(http_requests_total{status_code=~"5.."}[5m])
/ rate(http_requests_total[5m]) * 100

# Dostupnost (SLO)
1 - (
  sum(rate(http_requests_total{status_code=~"5.."}[30d]))
  / sum(rate(http_requests_total[30d]))
)
```

---

## 🎨 Grafana dashboard (kód)

```python
# Programatické vytváření dashboardů pomocí grafonnet/python
# pip install grafana-foundation-sdk

from grafana_foundation_sdk.builders import dashboard, timeseries

panel = (
    timeseries.Panel()
    .title("Request latency p99")
    .datasource({"type": "prometheus"})
    .targets([{
        "expr": "histogram_quantile(0.99, rate(request_duration_seconds_bucket[5m]))",
        "legendFormat": "p99",
    }])
)
```

---

## ✏️ Cvičení

1. Instrumentuj FastAPI aplikaci — přidej metriky pro všechny endpointy.
2. Nastav Grafana dashboard s: request rate, latency p50/p95/p99, error rate.
3. Napiš alert pro SLO violation — dostupnost < 99.9% za posledních 30 dní.
4. Přidej business metriky — `orders_created_total`, `revenue_czk_total`.
5. Implementuj **custom exporter** pro monitorování Redis fronty.
