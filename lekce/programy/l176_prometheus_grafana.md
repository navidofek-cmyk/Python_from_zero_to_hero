# Program — Lekce 176: Lekce 176: Prometheus + Grafana — monitoring

Patří k lekci [Lekce 176: Prometheus + Grafana — monitoring](../176_prometheus_grafana.md).

## Jak spustit

```bash
python3 programy/l176_prometheus_grafana.py
```

## Zdrojový kód

### `l176_prometheus_grafana.py`

```py
"""Lekce 176 — Prometheus + Grafana: monitoring.
Spuštění: uv run --with prometheus-client l176_prometheus_grafana.py
"""

import time
import random
import threading


try:
    from prometheus_client import (
        Counter, Gauge, Histogram, start_http_server, REGISTRY,
        CollectorRegistry, push_to_gateway
    )
    PROM_AVAILABLE = True
except ImportError:
    PROM_AVAILABLE = False


def demo_bez_prometheus():
    print("=" * 50)
    print("  📊 Prometheus + Grafana — koncepty")
    print("=" * 50)
    print("""
Typy metrik:
  Counter   → monotonicky roste (requesty, chyby)
  Gauge     → aktuální hodnota (aktivní spojení, teplota)
  Histogram → distribuce hodnot s buckety (latency)
  Summary   → distribuce s percentily (p50, p95, p99)

PromQL příklady:
  rate(http_requests_total[5m])          → req/s za 5 minut
  histogram_quantile(0.99, ...)          → p99 latency
  up == 0                                → padlé instance
  process_resident_memory_bytes / 1e9    → RAM v GB

SLO monitoring:
  Dostupnost = 1 - (5xx rate / total rate)
  Latency    = p99 < 1s za posledních 30 dní
  Error rate = < 0.1% za posledních 7 dní
""")


def demo_prometheus():
    if not PROM_AVAILABLE:
        print("\nPrometheus není dostupný: uv add prometheus-client")
        return

    print("\n=== Prometheus metriky ===")

    # Vlastní registry (aby nekolidoval s globálním)
    registry = CollectorRegistry()

    requests = Counter("http_requests_total", "Requesty",
                        ["endpoint", "status"], registry=registry)
    latency = Histogram("request_duration_seconds", "Latency",
                         ["endpoint"], buckets=[.01,.05,.1,.25,.5,1,2.5],
                         registry=registry)
    aktivni = Gauge("active_connections", "Aktivní spojení", registry=registry)

    # Simulace provozu
    random.seed(42)
    endpoints = ["/api/orders", "/api/users", "/health"]
    for _ in range(200):
        ep = random.choice(endpoints)
        status = random.choice(["200"]*92 + ["500"]*5 + ["404"]*3)
        lat = random.expovariate(1/0.1)  # průměr 100ms
        requests.labels(endpoint=ep, status=status).inc()
        latency.labels(endpoint=ep).observe(lat)
        aktivni.set(random.randint(10, 50))

    # Výstup metrik
    from prometheus_client import generate_latest
    metriky = generate_latest(registry).decode()
    # Zobraz jen summary
    for radek in metriky.split("\n"):
        if "# HELP" in radek or "_sum" in radek or "_count" in radek:
            if any(m in radek for m in ["http_requests", "request_duration"]):
                print(f"  {radek}")

    # Statistiky
    print("\n  Statistiky z metrik:")
    celkem = sum(requests.labels(ep, st)._value.get()
                 for ep in endpoints for st in ["200","500","404"])
    chyby_500 = sum(requests.labels(ep, "500")._value.get() for ep in endpoints)
    print(f"  Celkem requestů: {celkem:.0f}")
    print(f"  Chybovost 5xx: {chyby_500/celkem*100:.1f}%")


def demo_alert_rules():
    print("\n=== Alert pravidla ===")
    alerts = [
        {
            "name": "VysokaLatency",
            "expr": "histogram_quantile(0.99, rate(request_duration_seconds_bucket[5m])) > 1.0",
            "severity": "warning",
            "popis": "p99 latency > 1s"
        },
        {
            "name": "VysokáChybovost",
            "expr": "rate(http_requests_total{status=~'5..'}[5m]) / rate(http_requests_total[5m]) > 0.05",
            "severity": "critical",
            "popis": "Chybovost > 5%"
        },
        {
            "name": "ServiceDown",
            "expr": "up == 0",
            "severity": "critical",
            "popis": "Instance nedostupná"
        },
    ]
    for a in alerts:
        print(f"  [{a['severity'].upper()}] {a['name']}: {a['popis']}")
        print(f"    expr: {a['expr']}\n")


def main():
    demo_bez_prometheus()
    demo_prometheus()
    demo_alert_rules()
    print("✅ Demo dokončeno!")
    print("\nSpuštění metrik serveru:")
    print("  start_http_server(8000)  → http://localhost:8000/metrics")
    print("  Prometheus scrape → Grafana dashboard")


if __name__ == "__main__":
    main()

```
