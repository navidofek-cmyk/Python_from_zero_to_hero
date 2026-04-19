# Lekce 100: AI/ML a LLM — práce s API

## 🤖 LLM v Pythonu

V 2026 je práce s LLM (jako Claude) běžná. Nejčastěji přes API.

---

## 🎯 Anthropic Claude API

```bash
pip install anthropic
```

```python
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

response = client.messages.create(
    model="claude-opus-4-7",      # nejnovější Opus
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Vysvětli rekurzi 10leté dítě."}
    ],
)

print(response.content[0].text)
```

### Streamování

```python
with client.messages.stream(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Napiš kratkou báseň"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### Prompt caching (úspora ceny)

```python
response = client.messages.create(
    model="claude-opus-4-7",
    system=[
        {"type": "text", "text": dlouhy_kontext, "cache_control": {"type": "ephemeral"}}
    ],
    messages=[...],
)
```

Cached system prompt se účtuje **levněji** při dalším volání.

---

## 🔧 Tool use / function calling

```python
tools = [{
    "name": "vrat_pocasi",
    "description": "Vrátí počasí pro město",
    "input_schema": {
        "type": "object",
        "properties": {
            "mesto": {"type": "string"},
        },
        "required": ["mesto"],
    },
}]

response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "Jaké je počasí v Praze?"}],
)
```

Claude pak vrátí `tool_use` blok a ty zavoláš svoji funkci a pošleš výsledek zpátky.

---

## 🧮 Embeddings

Embedding = převod textu na **vektor** (seznam čísel). Podobné texty mají blízké vektory.

```bash
pip install sentence-transformers
```

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
vektory = model.encode(["pes", "kočka", "auto"])
# (3, 384) — 3 vektory dimenze 384
```

Pro produkci spíš embeddings API od OpenAI/Voyage/Cohere.

---

## 🔍 RAG — Retrieval-Augmented Generation

Vzor: stáhni relevantní dokumenty z DB → pošli s otázkou do LLM.

```python
# 1. Najdi top 3 relevantní dokumenty (vektorové vyhledávání)
relevantni = vector_db.search(otazka, k=3)

# 2. Pošli s otázkou
prompt = f"""Podle těchto dokumentů odpověz:

{chr(10).join(relevantni)}

Otázka: {otazka}
"""

odpoved = client.messages.create(model="claude-opus-4-7", messages=[{"role": "user", "content": prompt}])
```

**Vector DB**: Qdrant, Weaviate, Pinecone, pgvector.

---

## 🎯 Bezpečnost a praxe

✅ API klíče v env (`os.environ`), **NIKDY** v kódu.
✅ Rate limiting / retry s `tenacity`.
✅ Cache odpovědí pro deterministické dotazy.
✅ Validace a sanitizace LLM výstupu před použitím.
✅ Sledování ceny (`usage` v response).

❌ Žádné PII / hesla v promptu.
❌ Žádné slepé spuštění LLM výstupu (eval, exec, shell).

---

## ✏️ Cvičení

1. **Hello LLM:** Pošli „ahoj“ do Claude API a vypiš odpověď.
2. **Streamování:** Vyzkoušej streamování — text přichází postupně.
3. **Tool use:** Definuj nástroj `secti(a, b)` a nech Claude ho použít.
4. **Mini RAG:** 3 dokumenty v paměti, vyhledávání jednoduchým keyword matchem, pak pošli do LLM.
