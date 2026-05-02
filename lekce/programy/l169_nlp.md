# Program — Lekce 169: Lekce 169: NLP — zpracování přirozeného jazyka

Patří k lekci [Lekce 169: NLP — zpracování přirozeného jazyka](../169_nlp.md).

## Jak spustit

```bash
python3 programy/l169_nlp.py
```

## Zdrojový kód

### `l169_nlp.py`

```py
"""Lekce 169 — NLP: spaCy + TF-IDF.

Spuštění:
    uv run --with spacy,scikit-learn l169_nlp.py
    # + stáhni model: python -m spacy download en_core_web_sm
"""

import re
from collections import Counter


def demo_bez_spacy():
    """Základní NLP bez externích knihoven."""
    print("=" * 50)
    print("  🔤 NLP Demo")
    print("=" * 50)

    print("\n=== Základní tokenizace (bez knihoven) ===")
    text = "Python is great for NLP! Natural language processing is fun. I love Python."

    # Tokenizace
    tokeny = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    print(f"  Tokeny: {tokeny[:10]}...")
    print(f"  Celkem: {len(tokeny)}")

    # Stop slova
    stop_slova = {"is", "for", "the", "a", "an", "i", "and", "or", "but", "in"}
    filtrovane = [t for t in tokeny if t not in stop_slova and len(t) > 2]
    print(f"  Po filtraci: {filtrovane[:10]}")

    # Frekvence
    freq = Counter(filtrovane)
    print(f"  Nejčastější: {freq.most_common(5)}")


def demo_tfidf():
    print("\n=== TF-IDF vyhledávání ===")
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
    except ImportError:
        print("  Přeskoč: uv add scikit-learn")
        return

    dokumenty = [
        "Python is great for machine learning and data science",
        "FastAPI helps build REST APIs quickly with Python",
        "Docker containerizes applications for deployment",
        "Neural networks learn patterns from training data",
        "Python supports object-oriented and functional programming",
        "Async programming with asyncio improves Python performance",
    ]

    vectorizer = TfidfVectorizer(ngram_range=(1,2), stop_words="english")
    matrix = vectorizer.fit_transform(dokumenty)

    def hledej(dotaz, n=3):
        q = vectorizer.transform([dotaz])
        skore = cosine_similarity(q, matrix)[0]
        nejlepsi = np.argsort(skore)[::-1][:n]
        return [(dokumenty[i][:50], skore[i]) for i in nejlepsi if skore[i] > 0]

    for dotaz in ["Python programming", "machine learning", "web API"]:
        vysledky = hledej(dotaz)
        print(f"\n  Dotaz: '{dotaz}'")
        for dok, skore in vysledky:
            print(f"    [{skore:.3f}] {dok}...")


def demo_spacy():
    print("\n=== spaCy NLP pipeline ===")
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
    except Exception as e:
        print(f"  spaCy nedostupné: {e}")
        print("  Instalace: python -m spacy download en_core_web_sm")
        return

    text = "Python was created by Guido van Rossum at Google in the late 1980s."
    doc = nlp(text)

    print(f"\n  Text: {text}")
    print("\n  Tokeny (lemma, POS):")
    for tok in doc:
        if not tok.is_stop and not tok.is_punct:
            print(f"    {tok.text:<15} lemma={tok.lemma_:<12} pos={tok.pos_}")

    print("\n  Named Entities:")
    for ent in doc.ents:
        print(f"    {ent.text:<20} {ent.label_} ({spacy.explain(ent.label_)})")


def main():
    demo_bez_spacy()
    demo_tfidf()
    demo_spacy()

    print("\n✅ Demo dokončeno!")
    print("\nDalší kroky:")
    print("  uv add spacy && python -m spacy download en_core_web_sm")
    print("  uv add transformers → BERT, GPT-2, sentiment analysis")
    print("  uv add langchain    → LLM chains a agents")


if __name__ == "__main__":
    main()

```
