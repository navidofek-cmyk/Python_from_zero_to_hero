# Lekce 139: Elasticsearch — fulltext vyhledávání

Elasticsearch je **distribuovaný vyhledávací a analytický engine** postavený na Apache Lucene. Extrémně rychlé fulltext vyhledávání, fazetová navigace, geolokace, logy a metriky.

---

## 🚀 Instalace

```bash
uv add elasticsearch

# Elasticsearch server (Docker)
docker run -d --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  elasticsearch:8.12.0
```

---

## 🔌 Připojení

```python
from elasticsearch import Elasticsearch

# Lokální bez autentizace
es = Elasticsearch("http://localhost:9200")

# S autentizací (produkce)
es = Elasticsearch(
    "https://my-cluster.es.io:443",
    api_key="muj-api-klic",
)

# Ověření
print(es.info())
print(es.ping())  # True
```

---

## 📋 Indexy a mappings

Index = přibližně tabulka v SQL. Mapping = schéma polí.

```python
# Vytvoř index s explicitním mappingem
es.indices.create(
    index="produkty",
    body={
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "czech_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "asciifolding"]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "nazev": {
                    "type": "text",
                    "analyzer": "czech_analyzer",
                    "fields": {
                        "keyword": {"type": "keyword"}  # pro řazení/agregace
                    }
                },
                "popis": {"type": "text", "analyzer": "czech_analyzer"},
                "cena": {"type": "float"},
                "kategorie": {"type": "keyword"},
                "tagy": {"type": "keyword"},
                "dostupnost": {"type": "boolean"},
                "vytvoreno": {"type": "date"},
                "lokace": {"type": "geo_point"},
            }
        }
    }
)
```

---

## 📝 CRUD operace

### Indexování (vkládání) dokumentů

```python
from datetime import datetime

# Jeden dokument s explicitním ID
es.index(
    index="produkty",
    id="1",
    document={
        "nazev": "MacBook Pro 14",
        "popis": "Výkonný notebook od Apple s čipem M3 Pro.",
        "cena": 65000.0,
        "kategorie": "Elektronika",
        "tagy": ["notebook", "apple", "m3"],
        "dostupnost": True,
        "vytvoreno": datetime.utcnow().isoformat()
    }
)

# Dávkové indexování (bulk) — mnohem rychlejší pro velká data
from elasticsearch.helpers import bulk

dokumenty = [
    {
        "_index": "produkty",
        "_id": str(i),
        "_source": {
            "nazev": f"Produkt {i}",
            "cena": i * 100.0,
            "kategorie": "Kategorie A" if i % 2 == 0 else "Kategorie B",
            "dostupnost": True,
        }
    }
    for i in range(1, 101)
]

uspech, chyby = bulk(es, dokumenty)
print(f"Indexováno: {uspech}, Chyby: {len(chyby)}")

# Refresh — zpřístupní dokumenty pro vyhledávání okamžitě
es.indices.refresh(index="produkty")
```

### Čtení dokumentu

```python
doc = es.get(index="produkty", id="1")
print(doc["_source"])

# Existuje?
es.exists(index="produkty", id="1")
```

### Aktualizace

```python
# Částečná aktualizace (PATCH)
es.update(
    index="produkty",
    id="1",
    doc={"cena": 60000.0, "aktualizovano": datetime.utcnow().isoformat()}
)

# Script aktualizace
es.update(
    index="produkty",
    id="1",
    script={
        "source": "ctx._source.cena *= params.sleva",
        "params": {"sleva": 0.9}
    }
)
```

### Mazání

```python
es.delete(index="produkty", id="1")
es.delete_by_query(
    index="produkty",
    body={"query": {"term": {"dostupnost": False}}}
)
```

---

## 🔍 Vyhledávání — Query DSL

### Match query — fulltext

```python
# Základní fulltext
vysledek = es.search(
    index="produkty",
    query={"match": {"nazev": "MacBook notebook"}}
)

# Phrase match — hledá přesnou frázi
vysledek = es.search(
    index="produkty",
    query={"match_phrase": {"popis": "výkonný notebook"}}
)

# Multi-field search
vysledek = es.search(
    index="produkty",
    query={
        "multi_match": {
            "query": "apple notebook",
            "fields": ["nazev^2", "popis"],  # nazev má 2× váhu
            "type": "best_fields"
        }
    }
)
```

### Term query — přesná shoda (keyword pole)

```python
# Přesná shoda (neanalyzuje se)
vysledek = es.search(
    index="produkty",
    query={"term": {"kategorie": "Elektronika"}}
)

# Více hodnot
vysledek = es.search(
    index="produkty",
    query={"terms": {"kategorie": ["Elektronika", "Nábytek"]}}
)
```

### Range query

```python
vysledek = es.search(
    index="produkty",
    query={
        "range": {
            "cena": {"gte": 1000, "lte": 50000}
        }
    }
)
```

### Bool query — kombinace podmínek

```python
vysledek = es.search(
    index="produkty",
    query={
        "bool": {
            "must": [
                {"match": {"nazev": "notebook"}}
            ],
            "filter": [
                {"term": {"dostupnost": True}},
                {"range": {"cena": {"lte": 70000}}}
            ],
            "must_not": [
                {"term": {"kategorie": "Nábytek"}}
            ],
            "should": [
                {"term": {"tagy": "apple"}},
                {"term": {"tagy": "gaming"}}
            ],
            "minimum_should_match": 1
        }
    }
)
```

### Fuzzy — přibližná shoda (překlepy)

```python
vysledek = es.search(
    index="produkty",
    query={
        "fuzzy": {
            "nazev": {
                "value": "notbook",  # překlep
                "fuzziness": "AUTO"  # automatická tolerance
            }
        }
    }
)
```

---

## 📊 Agregace

```python
vysledek = es.search(
    index="produkty",
    size=0,  # nechceme dokumenty, jen agregace
    aggs={
        # Fazetová navigace — počty podle kategorie
        "podle_kategorie": {
            "terms": {"field": "kategorie", "size": 10}
        },
        # Průměrná cena
        "prumerna_cena": {
            "avg": {"field": "cena"}
        },
        # Histogram cen
        "histogram_cen": {
            "histogram": {"field": "cena", "interval": 5000}
        },
        # Vnořená agregace — průměr pro každou kategorii
        "kategorie_s_prumerem": {
            "terms": {"field": "kategorie"},
            "aggs": {
                "prumer": {"avg": {"field": "cena"}}
            }
        }
    }
)

for bucket in vysledek["aggregations"]["podle_kategorie"]["buckets"]:
    print(f"{bucket['key']}: {bucket['doc_count']}")
```

---

## 🌍 Geolokace

```python
# Index s geo_point
es.index(
    index="restaurace",
    id="1",
    document={
        "nazev": "U Zlatého tygra",
        "lokace": {"lat": 50.0835, "lon": 14.4175}  # Praha
    }
)

# Najdi restaurace do 5 km od středu Prahy
vysledek = es.search(
    index="restaurace",
    query={
        "geo_distance": {
            "distance": "5km",
            "lokace": {"lat": 50.0755, "lon": 14.4378}
        }
    }
)
```

---

## ⚡ Async Elasticsearch

```python
import asyncio
from elasticsearch import AsyncElasticsearch

async def main():
    es = AsyncElasticsearch("http://localhost:9200")

    await es.index(index="test", id="1", document={"klic": "hodnota"})
    doc = await es.get(index="test", id="1")
    print(doc["_source"])

    await es.close()

asyncio.run(main())
```

---

## 🎯 Kdy použít Elasticsearch

| Případ | ES | PostgreSQL full-text | Redis |
|--------|----|---------------------|-------|
| Fulltext přes miliony dokumentů | ✅ | pomalejší | ❌ |
| Fazetová navigace (e-shop filtry) | ✅ | složité | ❌ |
| Log analýza (ELK stack) | ✅ | ❌ | ❌ |
| Geolokace | ✅ | PostGIS | ❌ |
| Překlepy (fuzzy) | ✅ | omezené | ❌ |
| ACID transakce | ❌ | ✅ | ❌ |
| Jednoduché dotazy | overkill | ✅ | ✅ |

---

## ✏️ Cvičení

1. Spusť ES v Dockeru, vytvoř index `knihy` (název, autor, popis, rok, žánr).
2. Vlož 20 knih (dávkově), implementuj fulltext search přes název a popis.
3. Přidej fazetovou navigaci — počty knih podle žánru a rok vydání (histogram).
4. Implementuj **autocomplete** — prefix query na název knihy.
5. Navrhni query pro e-shop: hledej "python programování", filtruj cenu 200–500 Kč, jen skladem, seřaď dle relevance.
