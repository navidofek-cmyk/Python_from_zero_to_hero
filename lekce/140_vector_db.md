# Lekce 140: Vector databáze — embeddings a sémantické vyhledávání

Vektorové databáze ukládají **numerické reprezentace** (embeddings) textu, obrázků nebo jiných dat. Umožňují **sémantické vyhledávání** — najdi podobné věci i bez shody klíčových slov.

---

## 🧠 Jak to funguje

```
Text → Embedding model → Vektor [0.23, -0.11, 0.87, ...]
                          (typicky 384–3072 čísel)

Dotaz: "rychlý automobil"
DB obsahuje: "sportovní vůz" → vysoká podobnost (cosine similarity ≈ 0.92)
DB obsahuje: "recepty na polévku" → nízká podobnost (cosine similarity ≈ 0.05)
```

---

## 🚀 Instalace

```bash
# ChromaDB — nejjednodušší, embedded
uv add chromadb

# Sentence transformers — lokální embedding model
uv add sentence-transformers

# OpenAI embeddings (alternativa)
uv add openai

# pgvector — PostgreSQL rozšíření
uv add pgvector psycopg2-binary sqlalchemy

# Qdrant — produkční vector DB
uv add qdrant-client
```

---

## 🔵 ChromaDB — nejjednodušší start

```python
import chromadb
from chromadb.utils import embedding_functions

# In-memory (pro testování)
client = chromadb.Client()

# Persistentní
client = chromadb.PersistentClient(path="./chroma_db")

# Embedding funkce — výchozí je all-MiniLM-L6-v2 (lokální, bez API)
ef = embedding_functions.DefaultEmbeddingFunction()

# Vytvoř kolekci
kolekce = client.create_collection(
    name="dokumenty",
    embedding_function=ef,
    metadata={"hnsw:space": "cosine"}  # metrika podobnosti
)
```

### Přidávání dokumentů

```python
# Dokumenty — ChromaDB je automaticky embeduje
kolekce.add(
    documents=[
        "Python je interpretovaný programovací jazyk.",
        "FastAPI je moderní webový framework pro Python.",
        "SQLAlchemy je ORM pro Python a SQL databáze.",
        "Docker kontejnerizuje aplikace a jejich závislosti.",
        "Kubernetes orchestruje Docker kontejnery ve clusteru.",
        "Redis je in-memory key-value databáze pro cache.",
        "Elasticsearch umožňuje fulltext vyhledávání v datech.",
        "NumPy poskytuje vícerozměrná pole pro vědecké výpočty.",
        "Pandas je knihovna pro datovou analýzu v Pythonu.",
        "PyTorch je framework pro strojové učení a neuronové sítě.",
    ],
    ids=[f"doc_{i}" for i in range(10)],
    metadatas=[
        {"kategorie": "jazyk"},
        {"kategorie": "web"},
        {"kategorie": "databaze"},
        {"kategorie": "infrastruktura"},
        {"kategorie": "infrastruktura"},
        {"kategorie": "databaze"},
        {"kategorie": "databaze"},
        {"kategorie": "data"},
        {"kategorie": "data"},
        {"kategorie": "ml"},
    ]
)
```

### Sémantické vyhledávání

```python
# Najdi nejpodobnější dokumenty
vysledky = kolekce.query(
    query_texts=["jak uložit data v Pythonu"],
    n_results=3
)

print("Nejpodobnější dokumenty:")
for dok, dist, meta in zip(
    vysledky["documents"][0],
    vysledky["distances"][0],
    vysledky["metadatas"][0]
):
    print(f"  [{dist:.3f}] {dok[:60]}... (kategorie: {meta['kategorie']})")

# S filtrováním metadata
vysledky = kolekce.query(
    query_texts=["databáze pro Python"],
    n_results=3,
    where={"kategorie": "databaze"}  # filtruj jen databázové dokumenty
)
```

---

## 🤗 Sentence Transformers — vlastní embeddings

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Načti model (stáhne se automaticky, ~90 MB)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Zakóduj text → vektor
vektory = model.encode([
    "Python je skvělý jazyk",
    "Programování v Pythonu je zábava",
    "Recepty na českou kuchyni",
])

print(f"Dimenze vektoru: {vektory.shape}")  # (3, 384)

# Kosinusová podobnost
from sklearn.metrics.pairwise import cosine_similarity

similarity = cosine_similarity(vektory)
print(f"Python ↔ Programování: {similarity[0][1]:.3f}")  # vysoké ~0.85
print(f"Python ↔ Recepty:      {similarity[0][2]:.3f}")  # nízké ~0.12
```

---

## 🐘 pgvector — vektory v PostgreSQL

```bash
# PostgreSQL s pgvector rozšířením (Docker)
docker run -d --name pgvector \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=heslo \
  pgvector/pgvector:pg16
```

```python
import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer

con = psycopg2.connect("postgresql://postgres:heslo@localhost:5432/postgres")
cur = con.cursor()

# Aktivuj rozšíření
cur.execute("CREATE EXTENSION IF NOT EXISTS vector")

# Tabulka s vektorovým sloupcem
cur.execute("""
    CREATE TABLE IF NOT EXISTS dokumenty (
        id SERIAL PRIMARY KEY,
        obsah TEXT,
        kategorie VARCHAR(50),
        embedding vector(384)   -- dimenze modelu all-MiniLM-L6-v2
    )
""")

# Index pro rychlé vyhledávání (HNSW)
cur.execute("""
    CREATE INDEX IF NOT EXISTS dokumenty_embedding_idx
    ON dokumenty USING hnsw (embedding vector_cosine_ops)
""")
con.commit()

# Vkládání s embeddingy
model = SentenceTransformer("all-MiniLM-L6-v2")

texty = [
    ("Python ORM knihovny pro databáze", "python"),
    ("Kontejnerizace s Dockerem", "devops"),
    ("Strojové učení s PyTorchem", "ml"),
]

for obsah, kategorie in texty:
    embedding = model.encode(obsah).tolist()
    cur.execute(
        "INSERT INTO dokumenty (obsah, kategorie, embedding) VALUES (%s, %s, %s)",
        (obsah, kategorie, embedding)
    )

con.commit()

# Sémantické vyhledávání
dotaz = "jak trénovat neuronové sítě"
dotaz_embedding = model.encode(dotaz).tolist()

cur.execute("""
    SELECT obsah, kategorie,
           1 - (embedding <=> %s::vector) as podobnost
    FROM dokumenty
    ORDER BY embedding <=> %s::vector
    LIMIT 3
""", (dotaz_embedding, dotaz_embedding))

print(f"Výsledky pro: '{dotaz}'")
for radek in cur.fetchall():
    print(f"  [{radek[2]:.3f}] {radek[0]} ({radek[1]})")

cur.close()
con.close()
```

---

## 🔍 RAG — Retrieval Augmented Generation

RAG = najdi relevantní dokumenty + použij je jako kontext pro LLM.

```python
import chromadb
from anthropic import Anthropic
from sentence_transformers import SentenceTransformer

# Znalostní báze
DOKUMENTY = [
    "Naše firma nabízí 30denní záruku vrácení peněz.",
    "Doprava je zdarma při objednávce nad 1500 Kč.",
    "Zákaznická podpora je dostupná Po-Pá 9-17h na tel. 800-123-456.",
    "Produkty lze vrátit do 30 dnů v originálním obalu.",
    "Platbu lze provést kartou, převodem nebo dobírkou.",
    "Expresní doručení do 24h je možné za příplatek 99 Kč.",
]

# Inicializace
client = chromadb.Client()
kolekce = client.create_collection("znalostni_baze")
kolekce.add(
    documents=DOKUMENTY,
    ids=[f"dok_{i}" for i in range(len(DOKUMENTY))]
)

anthropic = Anthropic()


def rag_odpoved(dotaz: str, n_dokumentu: int = 3) -> str:
    # 1. Najdi relevantní dokumenty
    vysledky = kolekce.query(query_texts=[dotaz], n_results=n_dokumentu)
    relevantni = "\n".join(vysledky["documents"][0])

    # 2. Pošli LLM dotaz + kontext
    zprava = anthropic.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system=f"""Jsi zákaznická podpora. Odpovídej pouze na základě poskytnutého kontextu.
Pokud odpověď není v kontextu, řekni to.

Kontext:
{relevantni}""",
        messages=[{"role": "user", "content": dotaz}]
    )
    return zprava.content[0].text


# Test
print(rag_odpoved("Jak dlouho trvá doručení?"))
print(rag_odpoved("Mohu platit kryptoměnou?"))
```

---

## 🚀 Qdrant — produkční vector DB

```python
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
)
import numpy as np

# In-memory nebo server
client = QdrantClient(":memory:")
# client = QdrantClient(host="localhost", port=6333)

# Vytvoř kolekci
client.create_collection(
    collection_name="produkty",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# Vlož body (vektory + metadata)
body = [
    PointStruct(
        id=i,
        vector=np.random.rand(384).tolist(),
        payload={"nazev": f"Produkt {i}", "kategorie": "elektronika", "cena": i * 100}
    )
    for i in range(100)
]
client.upsert(collection_name="produkty", points=body)

# Vyhledávání s filtrem
vysledky = client.search(
    collection_name="produkty",
    query_vector=np.random.rand(384).tolist(),
    query_filter=Filter(
        must=[FieldCondition(key="kategorie", match=MatchValue(value="elektronika"))]
    ),
    limit=5,
    with_payload=True
)

for v in vysledky:
    print(f"  [{v.score:.3f}] {v.payload['nazev']}, cena: {v.payload['cena']} Kč")
```

---

## 🎯 Srovnání vector databází

| | ChromaDB | pgvector | Qdrant | Pinecone |
|---|---------|---------|--------|---------|
| Typ | embedded | PostgreSQL ext. | standalone | cloud |
| Jednoduchost | ✅ nejjednodušší | ✅ zná SQL | střední | ✅ |
| Produkce | ✅ | ✅ | ✅ | ✅ |
| Offline / self-hosted | ✅ | ✅ | ✅ | ❌ |
| Filtrování metadat | základní | SQL | pokročilé | základní |
| Škálování | omezené | PostgreSQL | ✅ clustering | ✅ |
| Cena | zdarma | zdarma | zdarma | placené |
| Ideální pro | vývoj, RAG | existující PG | produkce | cloud-first |

---

## ✏️ Cvičení

1. Vytvoř ChromaDB kolekci z 20 článků Wikipedie, implementuj sémantické vyhledávání.
2. Porovnej výsledky klíčového (Elasticsearch) vs sémantického (ChromaDB) vyhledávání na stejných datech.
3. Implementuj RAG chatbot pro dokumentaci kurzu — odpovídá otázky na základě lekcí.
4. Nainstaluj pgvector, ulož 1000 vektorů, porovnej rychlost s ChromaDB.
5. Implementuj **hybridní vyhledávání** — kombinuj fulltext (BM25) + sémantické skóre (Reciprocal Rank Fusion).
