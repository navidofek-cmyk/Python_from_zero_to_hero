"""Lekce 131 — RAG (Retrieval-Augmented Generation).

Plnohodnotný RAG bez externích závislostí — embeddingy jsou simulovány
bag-of-words vektorem (TF), v produkci nahraď skutečnými embeddingy
(OpenAI, Cohere, sentence-transformers...).

Pro generaci s Claude: nastav ANTHROPIC_API_KEY a odkomentuj sekci LLM.
"""

from __future__ import annotations

import math
import re
import os
from dataclasses import dataclass, field


# ── Chunking ──────────────────────────────────────────────────────────────────

def rozdel_na_chunky(text: str, velikost: int = 200, prekryv: int = 40) -> list[str]:
    chunky: list[str] = []
    start = 0
    while start < len(text):
        chunky.append(text[start : start + velikost])
        start += velikost - prekryv
    return chunky


def tokenizuj(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


# ── Embedding (naive bag-of-words TF) ────────────────────────────────────────

def sestav_slovnik(texty: list[str]) -> list[str]:
    slova: set[str] = set()
    for t in texty:
        slova.update(tokenizuj(t))
    return sorted(slova)


def embed_bow(text: str, slovnik: list[str]) -> list[float]:
    tokeny = tokenizuj(text)
    pocty = {t: tokeny.count(t) for t in set(tokeny)}
    return [pocty.get(s, 0) / max(len(tokeny), 1) for s in slovnik]


def kosinus_podobnost(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norma_a = math.sqrt(sum(x ** 2 for x in a))
    norma_b = math.sqrt(sum(x ** 2 for x in b))
    if norma_a == 0 or norma_b == 0:
        return 0.0
    return dot / (norma_a * norma_b)


# ── Dokument a VectorStore ────────────────────────────────────────────────────

@dataclass
class Dokument:
    id: str
    text: str
    embedding: list[float]
    metadata: dict = field(default_factory=dict)


class VectorStore:
    def __init__(self):
        self._dokumenty: list[Dokument] = []

    def __len__(self) -> int:
        return len(self._dokumenty)

    def pridej(self, doc: Dokument) -> None:
        self._dokumenty.append(doc)

    def hledej(self, query_embedding: list[float], k: int = 3) -> list[tuple[float, Dokument]]:
        scored = [
            (kosinus_podobnost(query_embedding, doc.embedding), doc)
            for doc in self._dokumenty
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:k]


# ── Indexace ──────────────────────────────────────────────────────────────────

class RagPipeline:
    def __init__(self, velikost_chunku: int = 200, prekryv: int = 40):
        self.velikost_chunku = velikost_chunku
        self.prekryv = prekryv
        self.store = VectorStore()
        self._slovnik: list[str] = []
        self._vsechny_texty: list[str] = []

    def indexuj(self, dokumenty: dict[str, str]) -> None:
        vsechny_chunky: list[tuple[str, str, dict]] = []
        for zdroj, text in dokumenty.items():
            for i, chunk in enumerate(rozdel_na_chunky(text, self.velikost_chunku, self.prekryv)):
                vsechny_chunky.append((f"{zdroj}_{i}", chunk, {"zdroj": zdroj, "chunk_id": i}))

        self._slovnik = sestav_slovnik([c for _, c, _ in vsechny_chunky])

        for doc_id, text, meta in vsechny_chunky:
            emb = embed_bow(text, self._slovnik)
            self.store.pridej(Dokument(id=doc_id, text=text, embedding=emb, metadata=meta))

        print(f"  Indexováno {len(self.store)} chunků ze {len(dokumenty)} dokumentů")

    def retrievuj(self, dotaz: str, k: int = 3) -> list[tuple[float, Dokument]]:
        query_emb = embed_bow(dotaz, self._slovnik)
        return self.store.hledej(query_emb, k=k)

    def odpoved_bez_llm(self, dotaz: str, k: int = 3) -> str:
        vysledky = self.retrievuj(dotaz, k=k)
        if not vysledky:
            return "Nenalezeny žádné relevantní dokumenty."
        nejlepsi_score, nejlepsi_doc = vysledky[0]
        return (
            f"Nejrelevantnější chunk (score={nejlepsi_score:.3f}, "
            f"zdroj={nejlepsi_doc.metadata['zdroj']}):\n\n"
            f"{nejlepsi_doc.text}"
        )

    def odpoved_s_claude(self, dotaz: str, k: int = 3) -> str:
        """Vyžaduje: pip install anthropic + ANTHROPIC_API_KEY."""
        try:
            import anthropic
        except ImportError:
            return "Nainstaluj: pip install anthropic"

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return "Nastav ANTHROPIC_API_KEY"

        vysledky = self.retrievuj(dotaz, k=k)
        kontext = "\n\n---\n\n".join(
            f"[Zdroj: {doc.metadata['zdroj']}, chunk {doc.metadata['chunk_id']}]\n{doc.text}"
            for _, doc in vysledky
        )

        prompt = (
            f"Na základě dokumentů níže odpověz na otázku.\n"
            f"Pokud odpověď v dokumentech není, řekni to.\n\n"
            f"Dokumenty:\n{kontext}\n\n"
            f"Otázka: {dotaz}"
        )

        client = anthropic.Anthropic(api_key=api_key)
        zprava = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return zprava.content[0].text


# ── Demo data ─────────────────────────────────────────────────────────────────

DOKUMENTY = {
    "python_zaklady": """
Python je interpretovaný, dynamicky typovaný jazyk. Byl navržen Guido van Rossumem
a poprvé vydán v roce 1991. Python klade důraz na čitelnost kódu a jednoduchost.
Podporuje více paradigmat: procedurální, objektově orientované i funkcionální programování.
Instalace Pythonu probíhá přes python.org nebo správce balíčků operačního systému.
Virtuální prostředí (venv) izolují závislosti jednotlivých projektů.
""",
    "rag_princip": """
RAG (Retrieval-Augmented Generation) je architektura pro jazykové modely, která kombinuje
vyhledávání informací s generativními schopnostmi LLM. Místo ukládání veškerých znalostí
v parametrech modelu se relevantní dokumenty vyhledají dynamicky a předají jako kontext.
Výhody RAG: aktuálnost dat, citovatelnost zdrojů, nižší cena než fine-tuning.
Nevýhody RAG: závislost na kvalitě retrieval komponenty, latence navíc.
""",
    "vector_databaze": """
Vektorové databáze ukládají vysokodimenzionální vektory (embeddingy) a umožňují
efektivní vyhledávání nejbližších sousedů (ANN - Approximate Nearest Neighbors).
Populární možnosti: ChromaDB pro lokální vývoj, Qdrant pro produkci, Pinecone jako cloud služba.
Klíčový algoritmus: HNSW (Hierarchical Navigable Small World) pro rychlé ANN vyhledávání.
Indexování je pomalejší než full-text search, ale vyhledávání sémantické podobnosti je přesnější.
""",
}


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=== RAG Pipeline Demo ===\n")

    pipeline = RagPipeline(velikost_chunku=150, prekryv=30)

    print("--- Indexace ---")
    pipeline.indexuj(DOKUMENTY)

    dotazy = [
        "Kdo vytvořil Python a kdy?",
        "Jaké jsou výhody RAG oproti fine-tuningu?",
        "Jaký algoritmus používají vektorové databáze?",
        "Co je to venv?",
    ]

    print("\n--- Retrieval (bez LLM) ---")
    for dotaz in dotazy:
        print(f"\nDotaz: {dotaz}")
        vysledky = pipeline.retrievuj(dotaz, k=2)
        for score, doc in vysledky:
            print(f"  score={score:.3f}  zdroj={doc.metadata['zdroj']}")
            print(f"  text: {doc.text[:80].strip()}...")

    print("\n--- Odpověď bez LLM (nejlepší chunk) ---")
    print(pipeline.odpoved_bez_llm("Jaké jsou nevýhody RAG?", k=1))

    print("\n--- Odpověď s Claude (pokud je ANTHROPIC_API_KEY) ---")
    odpoved = pipeline.odpoved_s_claude("Co je RAG a proč se používá?")
    print(odpoved)

    print("\n--- Kosinová podobnost demo ---")
    slovnik = ["python", "jazyk", "rag", "vyhledavani"]
    v1 = embed_bow("python je jazyk", slovnik)
    v2 = embed_bow("python programovaci jazyk", slovnik)
    v3 = embed_bow("rag vyhledavani dokumentu", slovnik)
    print(f"  python/jazyk vs python/jazyk variant: {kosinus_podobnost(v1, v2):.3f}")
    print(f"  python/jazyk vs rag/vyhledavani:      {kosinus_podobnost(v1, v3):.3f}")


if __name__ == "__main__":
    main()
