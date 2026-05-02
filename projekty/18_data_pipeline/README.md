# Projekt 18 — Data Pipeline

Kompletní async data pipeline: generátor → transformace → Polars analytika → Parquet export → report.

## Spuštění

```bash
# Základní (bez Kafka)
uv add polars numpy
python projekty/18_data_pipeline/pipeline.py

# S Kafka
docker run -d --name kafka -p 9092:9092 bitnami/kafka:latest
uv add aiokafka
python projekty/18_data_pipeline/pipeline.py --kafka
```

## Architektura

```
Generátor → async batches → transformace → Polars analytika → Parquet
                                                    ↓
                                              Report (tržby, kategorie, kanály)
```

## Výkon

- 50 000 transakcí za ~1s (bez Kafka)
- Throughput: ~50 000 transakcí/s
- Parquet kompresi snappy: ~5× menší než JSON

## Použité technologie

- **asyncio** — async pipeline (lekce 56-57)
- **Polars** — analytika (lekce 157)
- **Kafka** — streaming (lekce 160)
- **Parquet** — datový formát (lekce 138)
