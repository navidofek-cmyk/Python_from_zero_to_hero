# Program — Lekce 140: Lekce 140: Vector databáze — embeddings a sémantické vyhledávání

Patří k lekci [Lekce 140: Vector databáze — embeddings a sémantické vyhledávání](../140_vector_db.md).

## Jak spustit

```bash
python3 programy/l140_vector_db.py
```

## Zdrojový kód

### `l140_vector_db.py`

```py
"""Lekce 140 — Vector DB: embeddings a sémantické vyhledávání.

Spuštění:
    uv run --with chromadb,sentence-transformers l140_vector_db.py
"""

try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    print("Nainstaluj: uv add chromadb sentence-transformers")
    raise

DOKUMENTY = [
    ("Python je interpretovaný programovací jazyk.", "python"),
    ("FastAPI je moderní webový framework pro Python.", "web"),
    ("SQLAlchemy je ORM pro Python a SQL databáze.", "databaze"),
    ("Docker kontejnerizuje aplikace a jejich závislosti.", "devops"),
    ("Kubernetes orchestruje kontejnery ve clusteru.", "devops"),
    ("Redis je in-memory key-value databáze pro cache.", "databaze"),
    ("Elasticsearch umožňuje fulltext vyhledávání v datech.", "databaze"),
    ("NumPy poskytuje vícerozměrná pole pro vědecké výpočty.", "data"),
    ("Pandas je knihovna pro datovou analýzu v Pythonu.", "data"),
    ("PyTorch je framework pro strojové učení a neuronové sítě.", "ml"),
    ("TensorFlow je open-source ML framework od Google.", "ml"),
    ("asyncio umožňuje asynchronní programování v Pythonu.", "python"),
    ("pytest je populární testovací framework pro Python.", "python"),
    ("Git je distribuovaný systém pro správu verzí.", "devops"),
    ("PostgreSQL je výkonná open-source relační databáze.", "databaze"),
]


def demo_chromadb():
    print("\n=== ChromaDB — sémantické vyhledávání ===")

    client = chromadb.Client()
    ef = embedding_functions.DefaultEmbeddingFunction()

    kolekce = client.create_collection(
        name="tech_dokumenty",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

    # Přidej dokumenty (ChromaDB je automaticky embeduje)
    kolekce.add(
        documents=[d[0] for d in DOKUMENTY],
        ids=[f"doc_{i}" for i in range(len(DOKUMENTY))],
        metadatas=[{"kategorie": d[1]} for d in DOKUMENTY]
    )

    print(f"Indexováno {kolekce.count()} dokumentů")

    # Sémantické vyhledávání
    dotazy = [
        "jak uložit data v databázi",
        "asynchronní programování a výkon",
        "nasazení aplikace do produkce",
        "trénování modelu strojového učení",
    ]

    for dotaz in dotazy:
        vysledky = kolekce.query(query_texts=[dotaz], n_results=2)
        print(f"\n  Dotaz: '{dotaz}'")
        for dok, dist in zip(vysledky["documents"][0], vysledky["distances"][0]):
            print(f"    [{1-dist:.3f}] {dok[:65]}...")

    # S filtrem metadata
    print("\n  Filtrování — jen databázové dokumenty:")
    vysledky = kolekce.query(
        query_texts=["jak ukládat data"],
        n_results=3,
        where={"kategorie": "databaze"}
    )
    for dok in vysledky["documents"][0]:
        print(f"    • {dok}")

    return kolekce


def demo_sentence_transformers():
    print("\n=== Sentence Transformers — vlastní embeddingy ===")
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
    except ImportError:
        print("  Přeskoč — pip install sentence-transformers")
        return

    print("  Načítám model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    texty = [
        "Python je skvělý jazyk pro data science",
        "Programování v Pythonu je velmi populární",
        "Recepty na tradiční českou kuchyni",
        "Jak vařit svíčkovou na smetaně",
        "FastAPI umožňuje rychlý vývoj REST API",
    ]

    vektory = model.encode(texty)
    print(f"  Dimenze vektoru: {vektory.shape[1]}")

    from numpy.linalg import norm

    def cosine_sim(a, b):
        return np.dot(a, b) / (norm(a) * norm(b))

    print("\n  Podobnosti (kosinusová vzdálenost):")
    python1 = vektory[0]  # Python data science
    for i, (text, vektor) in enumerate(zip(texty, vektory)):
        sim = cosine_sim(python1, vektor)
        bar = "█" * int(sim * 20)
        print(f"  [{sim:.3f}] {bar:<20} {text[:45]}")


def demo_rag_simulace():
    print("\n=== RAG simulace (bez API klíče) ===")

    client = chromadb.Client()
    ef = embedding_functions.DefaultEmbeddingFunction()

    znalosti = client.create_collection("znalosti", embedding_function=ef)
    znalosti.add(
        documents=[
            "Vrácení zboží je možné do 30 dní v originálním obalu.",
            "Doprava je zdarma při objednávce nad 1500 Kč.",
            "Zákaznická podpora funguje Po-Pá 9-17h na tel. 800-123-456.",
            "Platit lze kartou, převodem nebo dobírkou.",
            "Expresní doručení do 24h za příplatek 99 Kč.",
            "Záruka na elektroniku je 24 měsíců.",
        ],
        ids=[f"info_{i}" for i in range(6)]
    )

    dotazy_zakaznika = [
        "Jak dlouho mám na vrácení?",
        "Kdy je doprava zdarma?",
        "Jak mohu platit?",
    ]

    print("  Simulace RAG chatbotu:")
    for dotaz in dotazy_zakaznika:
        vysledky = znalosti.query(query_texts=[dotaz], n_results=1)
        kontext = vysledky["documents"][0][0]
        print(f"\n  Zákazník: {dotaz}")
        print(f"  Kontext:  {kontext}")
        print(f"  Bot:      Na základě informací — {kontext.lower()}")


def main():
    print("=" * 50)
    print("  🔮 Vector DB Demo")
    print("=" * 50)

    demo_chromadb()
    demo_sentence_transformers()
    demo_rag_simulace()

    print("\n✅ Demo dokončeno!")
    print("\nDalší kroky:")
    print("  • uv add pgvector psycopg2-binary  → vektory v PostgreSQL")
    print("  • uv add qdrant-client             → produkční vector DB")
    print("  • uv add anthropic                 → embeddings přes Claude API")


if __name__ == "__main__":
    main()

```
