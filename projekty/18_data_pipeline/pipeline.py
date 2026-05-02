"""
Projekt 18 — Data Pipeline

Kompletní data pipeline:
  Generátor dat → Kafka (nebo queue) → Polars transformace
  → Parquet uložení → Statistiky → Report

Spuštění (bez Kafka):
    uv add polars numpy
    python projekty/18_data_pipeline/pipeline.py

Spuštění (s Kafka):
    docker run -d --name kafka -p 9092:9092 bitnami/kafka:latest
    uv add polars numpy aiokafka
    python projekty/18_data_pipeline/pipeline.py --kafka
"""

import asyncio
import json
import random
import time
import tempfile
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncGenerator

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


# ── Datový model ──────────────────────────────────────────────────────────────

@dataclass
class Transakce:
    id: int
    cas: str
    uzivatel_id: int
    produkt_id: int
    kategorie: str
    castka: float
    region: str
    kanal: str


def generuj_transakce(n: int, seed: int = 42) -> list[Transakce]:
    """Generuje náhodné transakce."""
    random.seed(seed)
    kategorie = ["Elektronika", "Nábytek", "Oblečení", "Potraviny", "Sport"]
    regiony = ["Praha", "Brno", "Ostrava", "Plzeň", "Liberec"]
    kanaly = ["web", "mobile", "kiosk"]

    return [
        Transakce(
            id=i,
            cas=datetime.now(timezone.utc).isoformat(),
            uzivatel_id=random.randint(1, 1000),
            produkt_id=random.randint(1, 500),
            kategorie=random.choice(kategorie),
            castka=round(random.uniform(50, 25000), 2),
            region=random.choice(regiony),
            kanal=random.choice(kanaly),
        )
        for i in range(n)
    ]


# ── Pipeline fáze ─────────────────────────────────────────────────────────────

async def zdroj(n: int = 10000) -> AsyncGenerator[list[Transakce], None]:
    """Zdroj: generuj dávky transakcí."""
    batch_size = 1000
    vsechny = generuj_transakce(n)
    for i in range(0, len(vsechny), batch_size):
        batch = vsechny[i:i+batch_size]
        yield batch
        await asyncio.sleep(0)  # yield event loop


async def transformuj(batch: list[Transakce]) -> list[dict]:
    """Transformace: vyčisti a obohať data."""
    await asyncio.sleep(0)
    result = []
    for t in batch:
        d = asdict(t)
        # Čistění
        d["castka"] = max(0, d["castka"])
        # Obohacení
        d["je_velka_transakce"] = d["castka"] >= 10000
        d["castka_kc"] = d["castka"]
        result.append(d)
    return result


def analyzuj_polars(data: list[dict]) -> dict:
    """Analytika s Polars."""
    if not POLARS_AVAILABLE:
        # Fallback bez Polars
        celkem = sum(d["castka"] for d in data)
        return {"celkem": celkem, "pocet": len(data)}

    df = pl.DataFrame(data)

    # Agregace
    skupiny = (
        df.group_by("kategorie")
        .agg([
            pl.count().alias("pocet"),
            pl.col("castka").sum().alias("trzby"),
            pl.col("castka").mean().alias("prumer"),
            pl.col("castka").max().alias("max"),
        ])
        .sort("trzby", descending=True)
    )

    kanaly = (
        df.group_by("kanal")
        .agg(pl.count().alias("pocet"), pl.col("castka").sum().alias("trzby"))
    )

    velke = df.filter(pl.col("je_velka_transakce"))

    return {
        "celkove_trzby": df["castka"].sum(),
        "pocet_transakci": len(df),
        "prumerna_transakce": df["castka"].mean(),
        "top_kategorie": skupiny.head(3).to_dicts(),
        "kanaly": kanaly.to_dicts(),
        "velkych_transakci": len(velke),
    }


def uloz_parquet(data: list[dict], cesta: str) -> int:
    """Uloží data jako Parquet."""
    if not POLARS_AVAILABLE:
        # Fallback: JSON
        json_cesta = cesta.replace(".parquet", ".json")
        Path(json_cesta).write_text(json.dumps(data[:10]))
        return len(data)

    df = pl.DataFrame(data)
    df.write_parquet(cesta, compression="snappy")
    return len(df)


def vygeneruj_report(analyza: dict, cas_sekundy: float) -> str:
    """Vygeneruj textový report."""
    lines = [
        "=" * 55,
        "  📊 Data Pipeline Report",
        "=" * 55,
        f"  Čas zpracování: {cas_sekundy:.2f}s",
        f"  Transakcí: {analyza['pocet_transakci']:,}",
        f"  Celkové tržby: {analyza['celkove_trzby']:,.0f} Kč",
        f"  Průměr/transakce: {analyza['prumerna_transakce']:,.0f} Kč",
        f"  Velkých transakcí (≥10k): {analyza['velkych_transakci']}",
        "",
        "  Top kategorie:",
    ]
    for kat in analyza.get("top_kategorie", []):
        lines.append(f"    {kat.get('kategorie','?'):<15} {kat.get('trzby',0):>12,.0f} Kč  ({kat.get('pocet',0)} transakcí)")
    lines.append("\n  Kanály:")
    for kanal in analyza.get("kanaly", []):
        lines.append(f"    {kanal.get('kanal','?'):<10} {kanal.get('trzby',0):>12,.0f} Kč")
    return "\n".join(lines)


# ── Hlavní pipeline ───────────────────────────────────────────────────────────

async def spust_pipeline(n_transakci: int = 10000) -> dict:
    """Spustí kompletní pipeline."""
    print(f"\n🚀 Spouštím pipeline ({n_transakci:,} transakcí)...")
    start = time.perf_counter()
    vsechna_data = []

    async for batch in zdroj(n_transakci):
        transformovana = await transformuj(batch)
        vsechna_data.extend(transformovana)

    t_zprac = time.perf_counter() - start
    print(f"   Zpracováno: {len(vsechna_data):,} transakcí za {t_zprac:.2f}s")

    # Analytika
    print("   Analyzuji...")
    analyza = analyzuj_polars(vsechna_data)

    # Uložení
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
        cesta_parquet = f.name

    radku = uloz_parquet(vsechna_data, cesta_parquet)
    velikost = os.path.getsize(cesta_parquet)
    print(f"   Uloženo: {radku:,} řádků → {cesta_parquet} ({velikost:,} B)")
    os.unlink(cesta_parquet)

    celkovy_cas = time.perf_counter() - start
    report = vygeneruj_report(analyza, celkovy_cas)
    print(report)

    throughput = n_transakci / celkovy_cas
    print(f"\n  Throughput: {throughput:,.0f} transakcí/s")
    return analyza


# ── Kafka varianta ────────────────────────────────────────────────────────────

async def kafka_producer(transakce: list[Transakce], topic: str = "transakce"):
    """Posílá transakce do Kafky."""
    try:
        from aiokafka import AIOKafkaProducer
        producer = AIOKafkaProducer(bootstrap_servers="localhost:9092",
                                     value_serializer=lambda v: json.dumps(asdict(v)).encode())
        await producer.start()
        for t in transakce:
            await producer.send(topic, t)
        await producer.stop()
        print(f"  Odesláno {len(transakce)} transakcí do Kafky")
    except ImportError:
        print("  aiokafka není dostupný: uv add aiokafka")


async def main():
    print("=" * 55)
    print("  🔄 Data Pipeline — Projekt 18")
    print("=" * 55)
    print(f"  Polars dostupný: {POLARS_AVAILABLE}")
    print(f"  NumPy dostupný:  {NUMPY_AVAILABLE}")

    await spust_pipeline(50000)

    print("\n✅ Pipeline dokončena!")
    print("\nPro produkci:")
    print("  uv add polars aiokafka apache-airflow")
    print("  + Kafka broker + Grafana dashboard")


if __name__ == "__main__":
    asyncio.run(main())
