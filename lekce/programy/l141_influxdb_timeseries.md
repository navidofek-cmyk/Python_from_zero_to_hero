# Program — Lekce 141: Lekce 141: Time-series databáze — InfluxDB

Patří k lekci [Lekce 141: Time-series databáze — InfluxDB](../141_influxdb_timeseries.md).

## Jak spustit

```bash
python3 programy/l141_influxdb_timeseries.py
```

## Zdrojový kód

### `l141_influxdb_timeseries.py`

```py
"""Lekce 141 — InfluxDB: time-series databáze.

Spuštění:
    docker run -d --name influxdb -p 8086:8086 \
      -e DOCKER_INFLUXDB_INIT_MODE=setup \
      -e DOCKER_INFLUXDB_INIT_USERNAME=admin \
      -e DOCKER_INFLUXDB_INIT_PASSWORD=heslo1234 \
      -e DOCKER_INFLUXDB_INIT_ORG=moje-org \
      -e DOCKER_INFLUXDB_INIT_BUCKET=metriky \
      -e DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=muj-token \
      influxdb:2.7

    uv run --with influxdb-client l141_influxdb_timeseries.py
"""

import random
import time
from datetime import datetime, timezone, timedelta

try:
    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS
except ImportError:
    print("Nainstaluj: uv add influxdb-client")
    raise

URL = "http://localhost:8086"
TOKEN = "muj-token"
ORG = "moje-org"
BUCKET = "metriky"


def pripoj():
    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
    client.ping()
    return client


def demo_zapis(client: InfluxDBClient):
    print("\n=== Zápis dat ===")
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
    write_api.write(bucket=BUCKET, record=bod)
    print("  Jeden bod zapsán")

    # Simulace 24 hodin senzorových dat
    body = []
    cas = datetime.now(timezone.utc) - timedelta(hours=24)
    while cas < datetime.now(timezone.utc):
        for mistnost in ["obyvak", "loznice", "kuchyn"]:
            base_temp = {"obyvak": 22, "loznice": 20, "kuchyn": 24}[mistnost]
            body.append(
                Point("teplota")
                .tag("mistnost", mistnost)
                .field("hodnota", round(base_temp + random.gauss(0, 1.5), 1))
                .field("vlhkost", round(random.uniform(40, 70), 1))
                .time(cas)
            )
        cas += timedelta(minutes=10)

    write_api.write(bucket=BUCKET, record=body)
    print(f"  Zapsáno {len(body)} bodů (simulace 24h)")


def demo_dotazy(client: InfluxDBClient):
    print("\n=== Flux dotazy ===")
    query_api = client.query_api()

    # Průměrná teplota podle místnosti
    flux = f"""
from(bucket: "{BUCKET}")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "teplota" and r._field == "hodnota")
  |> group(columns: ["mistnost"])
  |> mean()
"""
    tabulky = query_api.query(flux, org=ORG)
    print("  Průměrné teploty za 24h:")
    for tabulka in tabulky:
        for zaznam in tabulka.records:
            print(f"    {zaznam.values.get('mistnost', '?')}: "
                  f"{zaznam.get_value():.1f}°C")

    # Hodinové průměry — obývák
    flux_hodinove = f"""
from(bucket: "{BUCKET}")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "teplota"
    and r._field == "hodnota"
    and r.mistnost == "obyvak")
  |> aggregateWindow(every: 4h, fn: mean, createEmpty: false)
"""
    tabulky = query_api.query(flux_hodinove, org=ORG)
    print("\n  Obývák — průměr po 4h:")
    for tabulka in tabulky:
        for zaznam in tabulka.records:
            cas = zaznam.get_time().strftime("%H:%M")
            print(f"    {cas}: {zaznam.get_value():.1f}°C")


def demo_anomalie(client: InfluxDBClient):
    print("\n=== Detekce anomálií ===")
    query_api = client.query_api()

    # Zapiš anomálie
    write_api = client.write_api(write_options=SYNCHRONOUS)
    anomalie_body = [
        Point("teplota")
        .tag("mistnost", "kuchyn")
        .field("hodnota", 35.0)  # vysoká teplota!
        .time(datetime.now(timezone.utc) - timedelta(minutes=30)),
        Point("teplota")
        .tag("mistnost", "loznice")
        .field("hodnota", 10.0)  # nízká teplota!
        .time(datetime.now(timezone.utc) - timedelta(minutes=15)),
    ]
    write_api.write(bucket=BUCKET, record=anomalie_body)

    flux = f"""
from(bucket: "{BUCKET}")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "teplota" and r._field == "hodnota")
  |> filter(fn: (r) => r._value > 30.0 or r._value < 15.0)
"""
    tabulky = query_api.query(flux, org=ORG)
    anomalie = []
    for tabulka in tabulky:
        for zaznam in tabulka.records:
            anomalie.append((
                zaznam.values.get("mistnost"),
                zaznam.get_value(),
                zaznam.get_time()
            ))

    if anomalie:
        print(f"  🚨 Nalezeno {len(anomalie)} anomálií:")
        for mistnost, hodnota, cas in anomalie:
            status = "HORKO" if hodnota > 30 else "ZIMA"
            print(f"    [{status}] {mistnost}: {hodnota}°C @ {cas.strftime('%H:%M:%S')}")
    else:
        print("  Žádné anomálie")


def demo_monitoring_systemu(client: InfluxDBClient):
    print("\n=== Monitoring systému ===")
    write_api = client.write_api(write_options=SYNCHRONOUS)

    try:
        import psutil
        # Skutečné systémové metriky
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()

        body = [
            Point("cpu").field("usage_percent", cpu),
            Point("memory")
            .field("percent", mem.percent)
            .field("used_gb", round(mem.used / 1e9, 2)),
        ]
        write_api.write(bucket=BUCKET, record=body)
        print(f"  CPU: {cpu}%, RAM: {mem.percent}%")

    except ImportError:
        # Simulace
        body = [
            Point("cpu").field("usage_percent", random.uniform(10, 90)),
            Point("memory").field("percent", random.uniform(40, 80)),
        ]
        write_api.write(bucket=BUCKET, record=body)
        print("  Systémové metriky zapsány (simulace)")
        print("  Tip: uv add psutil → skutečné metriky")


def main():
    print("=" * 50)
    print("  📈 InfluxDB Time-Series Demo")
    print("=" * 50)

    try:
        client = pripoj()
        print("✅ InfluxDB připojeno")
    except Exception as e:
        print(f"❌ InfluxDB nedostupné: {e}")
        print("   Spusť Docker příkaz z hlavičky tohoto souboru")
        return

    demo_zapis(client)
    demo_dotazy(client)
    demo_anomalie(client)
    demo_monitoring_systemu(client)

    client.close()
    print("\n✅ Demo dokončeno!")
    print("   Web UI: http://localhost:8086 (admin/heslo1234)")


if __name__ == "__main__":
    main()

```
