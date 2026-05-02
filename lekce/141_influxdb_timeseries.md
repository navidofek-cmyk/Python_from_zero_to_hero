# Lekce 141: Time-series databáze — InfluxDB

Time-series databáze jsou optimalizovány pro **data s časovou značkou** — metriky, senzory, logy, monitoring. InfluxDB je nejpopulárnější Python-friendly time-series DB.

---

## 🚀 Instalace

```bash
uv add influxdb-client

# InfluxDB server (Docker)
docker run -d --name influxdb \
  -p 8086:8086 \
  -e DOCKER_INFLUXDB_INIT_MODE=setup \
  -e DOCKER_INFLUXDB_INIT_USERNAME=admin \
  -e DOCKER_INFLUXDB_INIT_PASSWORD=heslo1234 \
  -e DOCKER_INFLUXDB_INIT_ORG=moje-org \
  -e DOCKER_INFLUXDB_INIT_BUCKET=metriky \
  -e DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=muj-token \
  influxdb:2.7

# Web UI: http://localhost:8086
```

---

## 🔑 Koncepty InfluxDB 2.x

| Pojem | Popis | SQL analogie |
|-------|-------|-------------|
| **Bucket** | úložiště s retencí | databáze |
| **Measurement** | typ měření | tabulka |
| **Tag** | indexovaný metadata string | indexovaný sloupec |
| **Field** | naměřená hodnota (číslo/string) | sloupec |
| **Timestamp** | čas měření | PRIMARY KEY (čas) |
| **Point** | jeden datový bod | řádek |

---

## 🔌 Připojení a zápis

```python
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timezone

# Připojení
client = InfluxDBClient(
    url="http://localhost:8086",
    token="muj-token",
    org="moje-org"
)

write_api = client.write_api(write_options=SYNCHRONOUS)

# Jeden bod
bod = (
    Point("teplota")
    .tag("mistnost", "obyvak")
    .tag("senzor", "DHT22-01")
    .field("hodnota", 22.5)
    .field("vlhkost", 55.0)
    .time(datetime.now(timezone.utc))
)

write_api.write(bucket="metriky", record=bod)
```

### Dávkový zápis

```python
import random
from datetime import timedelta

# Simulace senzorových dat za posledních 24 hodin
body = []
cas = datetime.now(timezone.utc) - timedelta(hours=24)

while cas < datetime.now(timezone.utc):
    for mistnost in ["obyvak", "loznice", "kuchyn"]:
        bod = (
            Point("teplota")
            .tag("mistnost", mistnost)
            .field("hodnota", round(random.uniform(18.0, 26.0), 1))
            .field("vlhkost", round(random.uniform(40.0, 70.0), 1))
            .time(cas)
        )
        body.append(bod)
    cas += timedelta(minutes=5)

write_api.write(bucket="metriky", record=body)
print(f"Zapsáno {len(body)} bodů")
```

### Line protocol (textový formát)

```python
# Přímý line protocol — nejrychlejší zápis
radky = [
    f"cpu,host=server1,core=0 usage=45.2,temp=72.1 {int(datetime.now().timestamp() * 1e9)}",
    f"cpu,host=server1,core=1 usage=32.7,temp=68.5 {int(datetime.now().timestamp() * 1e9)}",
]

write_api.write(bucket="metriky", record="\n".join(radky), precision=WritePrecision.NANOSECONDS)
```

---

## 🔍 Dotazování — Flux jazyk

Flux je funkcionální dotazovací jazyk InfluxDB.

```python
query_api = client.query_api()

# Základní dotaz — průměrná teplota za posledních 6 hodin
flux = """
from(bucket: "metriky")
  |> range(start: -6h)
  |> filter(fn: (r) => r._measurement == "teplota")
  |> filter(fn: (r) => r._field == "hodnota")
  |> filter(fn: (r) => r.mistnost == "obyvak")
  |> mean()
"""

tabulky = query_api.query(flux)
for tabulka in tabulky:
    for zaznam in tabulka.records:
        print(f"Průměrná teplota: {zaznam.get_value():.1f}°C")
```

### Agregace a window funkce

```python
# Agregace po 1 hodině
flux = """
from(bucket: "metriky")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "teplota" and r._field == "hodnota")
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
  |> yield(name: "hodinovy_prumer")
"""

# Pivot — více fields jako sloupce
flux_pivot = """
from(bucket: "metriky")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "teplota")
  |> pivot(rowKey: ["_time", "mistnost"], columnKey: ["_field"], valueColumn: "_value")
"""

# Detekce anomálií — hodnoty mimo rozsah
flux_anomalie = """
from(bucket: "metriky")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "teplota" and r._field == "hodnota")
  |> filter(fn: (r) => r._value > 25.0 or r._value < 15.0)
"""

tabulky = query_api.query(flux_anomalie)
for tabulka in tabulky:
    for zaznam in tabulka.records:
        print(f"ANOMÁLIE: {zaznam['mistnost']} = {zaznam.get_value()}°C @ {zaznam.get_time()}")
```

### Výsledky jako pandas DataFrame

```python
import pandas as pd

flux = """
from(bucket: "metriky")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "teplota" and r._field == "hodnota")
  |> aggregateWindow(every: 30m, fn: mean)
"""

df = query_api.query_data_frame(flux)
print(df.head())
print(df.describe())
```

---

## 📊 Monitoring aplikace

```python
import time
import psutil
from threading import Thread
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

client = InfluxDBClient(url="http://localhost:8086", token="muj-token", org="moje-org")
write_api = client.write_api(write_options=SYNCHRONOUS)

BEZI = True


def sbírej_metriky(interval: float = 5.0):
    """Sbírá systémové metriky každých interval sekund."""
    while BEZI:
        # CPU
        for i, pct in enumerate(psutil.cpu_percent(percpu=True)):
            write_api.write("metriky", record=(
                Point("cpu")
                .tag("core", str(i))
                .field("usage_percent", pct)
            ))

        # Paměť
        mem = psutil.virtual_memory()
        write_api.write("metriky", record=(
            Point("memory")
            .field("total_gb", mem.total / 1e9)
            .field("used_gb", mem.used / 1e9)
            .field("percent", mem.percent)
        ))

        # Disk
        disk = psutil.disk_usage("/")
        write_api.write("metriky", record=(
            Point("disk")
            .tag("mount", "/")
            .field("used_gb", disk.used / 1e9)
            .field("percent", disk.percent)
        ))

        time.sleep(interval)


# Spuštění v background vlákně
monitor = Thread(target=sbírej_metriky, daemon=True)
monitor.start()

print("Monitorování spuštěno. Ctrl+C pro zastavení.")
try:
    time.sleep(30)  # sbírej 30 sekund
except KeyboardInterrupt:
    BEZI = False
    print("Zastaveno.")

client.close()
```

---

## 🔔 Alerting — Tasks v InfluxDB

Flux task = periodicky spouštěný dotaz (jako cron).

```python
# Vytvoř task pro detekci vysoké teploty
tasks_api = client.tasks_api()

flux_task = """
option task = {
  name: "alert_vysoka_teplota",
  every: 5m
}

from(bucket: "metriky")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "teplota" and r._field == "hodnota")
  |> filter(fn: (r) => r._value > 30.0)
  |> to(bucket: "alerty", org: "moje-org")
"""

task = tasks_api.create_task_every(
    name="alert_vysoka_teplota",
    flux=flux_task,
    every="5m",
    org="moje-org"
)
print(f"Task vytvořen: {task.id}")
```

---

## 🔄 Retence a downsampling

```python
# Vytvoř bucket s retencí 30 dní
buckets_api = client.buckets_api()
from influxdb_client import BucketRetentionRules

bucket = buckets_api.create_bucket(
    bucket_name="metriky-raw",
    retention_rules=BucketRetentionRules(
        type="expire",
        every_seconds=30 * 24 * 3600  # 30 dní
    ),
    org="moje-org"
)

# Downsampling task — zapiš hodinové průměry do long-term bucketu
flux_downsample = """
option task = {name: "downsample_hodinove", every: 1h}

from(bucket: "metriky-raw")
  |> range(start: -1h)
  |> aggregateWindow(every: 1h, fn: mean)
  |> to(bucket: "metriky-monthly", org: "moje-org")
"""
```

---

## 🎯 Kdy použít time-series DB

| Případ | InfluxDB | PostgreSQL | Redis |
|--------|---------|-----------|-------|
| IoT senzory (miliony bodů/s) | ✅ | pomalé | ❌ |
| Aplikační metriky | ✅ | ✅ | ✅ (limitované) |
| Downsampling/retence | ✅ automaticky | manuálně | ❌ |
| Grafana dashboardy | ✅ nativní | ✅ | ✅ |
| Komplexní dotazy | Flux | SQL | ❌ |
| ACID transakce | ❌ | ✅ | ❌ |

**Alternativy:** TimescaleDB (PostgreSQL rozšíření), Prometheus + Grafana, VictoriaMetrics.

---

## ✏️ Cvičení

1. Spusť InfluxDB v Dockeru, zapiš simulovaná data z 3 senzorů teploty za 7 dní.
2. Napiš Flux dotaz: průměrná, minimální a maximální teplota po hodinách pro každou místnost.
3. Implementuj jednoduchý monitoring Python aplikace — zaznamenej čas odpovědi HTTP requestů.
4. Napiš detekci anomálií — upozorni když teplota přesáhne 28°C.
5. Porovnej zápis 100 000 bodů v InfluxDB vs PostgreSQL — čas a velikost na disku.
