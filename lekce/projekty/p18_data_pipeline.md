# Projekt 18: Data Pipeline

Kompletní async data pipeline: generátor → transformace → Polars analytika → Parquet → report.

**Použité koncepty:** asyncio (56), Polars (157), Kafka (160), Parquet/DuckDB (138).

## Spuštění

```bash
uv add polars numpy
python projekty/18_data_pipeline/pipeline.py
# Zpracuje 50 000 transakcí, vygeneruje report
```

## Výkon

- 50 000 transakcí/s na jednom CPU
- Parquet kompresi 5× vs JSON
- Async batching bez blokování

Zdrojový kód: `projekty/18_data_pipeline/pipeline.py`
