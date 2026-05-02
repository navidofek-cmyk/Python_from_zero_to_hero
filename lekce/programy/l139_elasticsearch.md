# Program — Lekce 139: Lekce 139: Elasticsearch — fulltext vyhledávání

Patří k lekci [Lekce 139: Elasticsearch — fulltext vyhledávání](../139_elasticsearch.md).

## Jak spustit

```bash
python3 programy/l139_elasticsearch.py
```

## Zdrojový kód

### `l139_elasticsearch.py`

```py
"""Lekce 139 — Elasticsearch: fulltext vyhledávání.

Spuštění:
    docker run -d --name elasticsearch -p 9200:9200 \
      -e "discovery.type=single-node" \
      -e "xpack.security.enabled=false" \
      elasticsearch:8.12.0

    uv run --with elasticsearch l139_elasticsearch.py
"""

import time
from datetime import datetime

try:
    from elasticsearch import Elasticsearch
    from elasticsearch.helpers import bulk
except ImportError:
    print("Nainstaluj: uv add elasticsearch")
    raise

DOKUMENTY = [
    {"nazev": "Python pro začátečníky", "autor": "Jan Novák",
     "popis": "Základy programování v Pythonu. Naučte se proměnné, smyčky a funkce.",
     "cena": 349, "kategorie": "Python", "hodnoceni": 4.8, "rok": 2023},
    {"nazev": "FastAPI v praxi", "autor": "Marie Svobodová",
     "popis": "Tvorba REST API s FastAPI, Pydantic a SQLAlchemy. Produkční deployment.",
     "cena": 449, "kategorie": "Web", "hodnoceni": 4.9, "rok": 2024},
    {"nazev": "Docker a Kubernetes", "autor": "Petr Dvořák",
     "popis": "Kontejnerizace aplikací. Od Dockerfile po Kubernetes cluster.",
     "cena": 499, "kategorie": "DevOps", "hodnoceni": 4.7, "rok": 2023},
    {"nazev": "Strojové učení s Pythonem", "autor": "Eva Procházková",
     "popis": "Scikit-learn, pandas, numpy. Klasifikace, regrese, clustering.",
     "cena": 599, "kategorie": "ML", "hodnoceni": 4.6, "rok": 2024},
    {"nazev": "Async Python", "autor": "Jan Novák",
     "popis": "asyncio, aiohttp, FastAPI. Výkon pomocí asynchronního programování.",
     "cena": 399, "kategorie": "Python", "hodnoceni": 4.5, "rok": 2023},
    {"nazev": "PostgreSQL pro vývojáře", "autor": "Karel Marek",
     "popis": "SQL dotazy, indexy, transakce, replikace. Optimalizace výkonu.",
     "cena": 449, "kategorie": "Databáze", "hodnoceni": 4.7, "rok": 2022},
    {"nazev": "Redis cookbook", "autor": "Lucie Horáková",
     "popis": "Cache, pub/sub, rate limiting, fronty. Redis v produkci.",
     "cena": 379, "kategorie": "Databáze", "hodnoceni": 4.4, "rok": 2023},
    {"nazev": "Clean Code v Pythonu", "autor": "Marie Svobodová",
     "popis": "SOLID principy, design patterns, testování. Psaní čistého kódu.",
     "cena": 399, "kategorie": "Python", "hodnoceni": 4.8, "rok": 2024},
]


def pripoj() -> Elasticsearch:
    es = Elasticsearch("http://localhost:9200")
    es.ping()
    return es


def vytvor_index(es: Elasticsearch):
    if es.indices.exists(index="knihy"):
        es.indices.delete(index="knihy")

    es.indices.create(index="knihy", body={
        "settings": {"number_of_shards": 1, "number_of_replicas": 0},
        "mappings": {
            "properties": {
                "nazev": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "autor": {"type": "keyword"},
                "popis": {"type": "text"},
                "cena": {"type": "float"},
                "kategorie": {"type": "keyword"},
                "hodnoceni": {"type": "float"},
                "rok": {"type": "integer"},
            }
        }
    })
    print("✅ Index 'knihy' vytvořen")


def vloz_data(es: Elasticsearch):
    akce = [
        {"_index": "knihy", "_id": str(i), "_source": dok}
        for i, dok in enumerate(DOKUMENTY)
    ]
    uspech, chyby = bulk(es, akce)
    es.indices.refresh(index="knihy")
    print(f"✅ Vloženo {uspech} dokumentů")


def demo_fulltext(es: Elasticsearch):
    print("\n=== Fulltext vyhledávání ===")

    dotazy = [
        "Python programování",
        "databáze výkon",
        "asynchronní API",
    ]

    for dotaz in dotazy:
        vysledek = es.search(
            index="knihy",
            query={"multi_match": {
                "query": dotaz,
                "fields": ["nazev^2", "popis"]
            }},
            size=2
        )
        hity = vysledek["hits"]["hits"]
        print(f"\n  Dotaz: '{dotaz}'")
        for hit in hity:
            print(f"    [{hit['_score']:.2f}] {hit['_source']['nazev']}")


def demo_filtry(es: Elasticsearch):
    print("\n=== Kombinované filtry (bool query) ===")

    vysledek = es.search(
        index="knihy",
        query={
            "bool": {
                "must": [{"match": {"popis": "Python"}}],
                "filter": [
                    {"range": {"cena": {"lte": 450}}},
                    {"range": {"hodnoceni": {"gte": 4.6}}}
                ]
            }
        },
        sort=[{"hodnoceni": "desc"}]
    )

    print("Python knihy do 450 Kč s hodnocením ≥ 4.6:")
    for hit in vysledek["hits"]["hits"]:
        s = hit["_source"]
        print(f"  {s['nazev']} — {s['cena']} Kč, ⭐ {s['hodnoceni']}")


def demo_agregace(es: Elasticsearch):
    print("\n=== Agregace (fazetová navigace) ===")

    vysledek = es.search(
        index="knihy",
        size=0,
        aggs={
            "podle_kategorie": {
                "terms": {"field": "kategorie", "size": 10}
            },
            "prumerna_cena": {"avg": {"field": "cena"}},
            "histogram_cen": {
                "histogram": {"field": "cena", "interval": 100}
            },
            "nej_autori": {
                "terms": {"field": "autor", "size": 3}
            }
        }
    )

    aggs = vysledek["aggregations"]
    print("Podle kategorie:")
    for b in aggs["podle_kategorie"]["buckets"]:
        print(f"  {b['key']}: {b['doc_count']} knih")

    print(f"\nPrůměrná cena: {aggs['prumerna_cena']['value']:.0f} Kč")

    print("\nNejpopulárnější autoři:")
    for b in aggs["nej_autori"]["buckets"]:
        print(f"  {b['key']}: {b['doc_count']} knih")


def demo_rychlost(es: Elasticsearch):
    print("\n=== Výkon dotazů ===")

    dotazy_typy = [
        ("match", {"match": {"nazev": "Python"}}),
        ("term", {"term": {"kategorie": "Python"}}),
        ("range", {"range": {"cena": {"gte": 300, "lte": 500}}}),
        ("bool", {"bool": {"must": [{"match": {"popis": "výkon"}}],
                           "filter": [{"range": {"hodnoceni": {"gte": 4.5}}}]}}),
    ]

    for nazev, query in dotazy_typy:
        start = time.perf_counter()
        vysledek = es.search(index="knihy", query=query, size=10)
        cas = (time.perf_counter() - start) * 1000
        pocet = vysledek["hits"]["total"]["value"]
        print(f"  {nazev:<10}: {pocet} výsledků za {cas:.1f}ms")


def main():
    print("=" * 50)
    print("  🔍 Elasticsearch Demo")
    print("=" * 50)

    try:
        es = pripoj()
        print("✅ Elasticsearch připojen")
    except Exception as e:
        print(f"❌ ES nedostupný: {e}")
        print("   Spusť: docker run -d --name elasticsearch -p 9200:9200 \\")
        print('     -e "discovery.type=single-node" \\')
        print('     -e "xpack.security.enabled=false" \\')
        print("     elasticsearch:8.12.0")
        return

    vytvor_index(es)
    vloz_data(es)
    demo_fulltext(es)
    demo_filtry(es)
    demo_agregace(es)
    demo_rychlost(es)

    es.close()
    print("\n✅ Demo dokončeno!")


if __name__ == "__main__":
    main()

```
