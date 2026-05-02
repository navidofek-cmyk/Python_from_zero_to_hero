# Lekce 180: Ollama — lokální LLM bez API klíče

Ollama spouští LLM lokálně. Žádné API klíče, žádné poplatky, žádná síť. Ideální pro vývoj, soukromá data, offline použití.

---

## 🚀 Instalace

```bash
# Ollama server
curl -fsSL https://ollama.ai/install.sh | sh
# nebo: brew install ollama (macOS)
# nebo: winget install Ollama.Ollama (Windows)

# Stáhni model
ollama pull llama3.2        # 2GB, dobrý výkon
ollama pull mistral         # 4GB, výborný
ollama pull codellama       # 4GB, specializovaný na kód
ollama pull phi3            # 2GB, malý ale schopný

# Python klient
uv add ollama
```

---

## 🔌 Základní použití

```python
import ollama


# Jednoduchá odpověď
response = ollama.chat(
    model="llama3.2",
    messages=[{"role": "user", "content": "Co je Python?"}],
)
print(response["message"]["content"])

# Streaming
for chunk in ollama.chat(
    model="llama3.2",
    messages=[{"role": "user", "content": "Vysvětli asyncio"}],
    stream=True,
):
    print(chunk["message"]["content"], end="", flush=True)
```

---

## 💬 Konverzace s pamětí

```python
from dataclasses import dataclass, field


@dataclass
class OllamaChat:
    model: str = "llama3.2"
    system: str = "Jsi Python expert."
    history: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if self.system:
            self.history.append({"role": "system", "content": self.system})

    def chat(self, zprava: str) -> str:
        self.history.append({"role": "user", "content": zprava})
        response = ollama.chat(model=self.model, messages=self.history)
        odpoved = response["message"]["content"]
        self.history.append({"role": "assistant", "content": odpoved})
        return odpoved

    def reset(self):
        self.history = [{"role": "system", "content": self.system}]


chat = OllamaChat(model="llama3.2", system="Jsi expert na Python kurzy.")
print(chat.chat("Jaký je rozdíl mezi list a tuple?"))
print(chat.chat("Kdy bych měl použít který?"))  # pamatuje kontext
```

---

## 🔢 Embeddings

```python
# Lokální embeddings — bez volání externího API
response = ollama.embeddings(
    model="nomic-embed-text",  # ollama pull nomic-embed-text
    prompt="Python asyncio coroutines",
)
vektor = response["embedding"]
print(f"Dimenze embeddings: {len(vektor)}")


# RAG s lokálními embeddings
import numpy as np
from pathlib import Path


def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def embed(text: str) -> list[float]:
    return ollama.embeddings(model="nomic-embed-text", prompt=text)["embedding"]


# Indexuj dokumenty
dokumenty = [
    "Python je interpretovaný jazyk s dynamickým typováním",
    "asyncio umožňuje asynchronní programování v Pythonu",
    "FastAPI je moderní web framework pro Python",
    "Pandas je knihovna pro datovou analýzu",
]

print("Indexuji dokumenty...")
embeddingy = [embed(d) for d in dokumenty]


def hledej(dotaz: str, top_k: int = 2):
    q_emb = embed(dotaz)
    scores = [(cosine_sim(q_emb, e), d) for e, d in zip(embeddingy, dokumenty)]
    return sorted(scores, reverse=True)[:top_k]


vysledky = hledej("jak programovat asynchronně")
for skore, dok in vysledky:
    print(f"  [{skore:.3f}] {dok}")
```

---

## 🤖 Ollama + FastAPI (lokální chatbot API)

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import ollama
import json

app = FastAPI(title="Lokální LLM API")


class ChatRequest(BaseModel):
    zprava: str
    model: str = "llama3.2"
    system: str = "Jsi Python expert."


@app.post("/chat")
async def chat(request: ChatRequest):
    response = ollama.chat(
        model=request.model,
        messages=[
            {"role": "system", "content": request.system},
            {"role": "user", "content": request.zprava},
        ],
    )
    return {"odpoved": response["message"]["content"]}


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    def generate():
        for chunk in ollama.chat(
            model=request.model,
            messages=[
                {"role": "system", "content": request.system},
                {"role": "user", "content": request.zprava},
            ],
            stream=True,
        ):
            yield json.dumps({"text": chunk["message"]["content"]}) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")


@app.get("/modely")
async def list_models():
    models = ollama.list()
    return {"modely": [m["model"] for m in models["models"]]}
```

---

## 📊 Srovnání modelů

```python
def benchmark_modely(dotaz: str, modely: list[str]) -> None:
    import time

    print(f"Dotaz: {dotaz}\n")
    for model in modely:
        try:
            start = time.perf_counter()
            r = ollama.chat(model=model, messages=[{"role":"user","content":dotaz}])
            t = time.perf_counter() - start
            odpoved = r["message"]["content"][:100]
            tokens = len(odpoved.split())
            print(f"  [{model}] {t:.1f}s — {tokens} slov")
            print(f"    {odpoved}...")
        except Exception as e:
            print(f"  [{model}] Chyba: {e}")


# benchmark_modely("Napiš funkci pro Fibonacci", ["llama3.2", "mistral", "phi3"])
```

---

## 🎯 Ollama vs API

| | Ollama | Anthropic API |
|---|--------|--------------|
| Cena | zdarma | platí se za tokeny |
| Soukromí | ✅ vše lokálně | data odesílána |
| Výkon | závisí na HW | výborný |
| Modely | open-source | proprietární |
| Setup | 5 minut | API klíč |
| GPU nutné | doporučeno | NE |
| Internet | NE | nutný |

---

## ✏️ Cvičení

1. Postav lokální RAG systém: Ollama embeddings + Chroma + llama3.2.
2. Napiš **model router** — jednoduché dotazy → phi3, složité → mistral.
3. Benchmark: porovnej kvalitu odpovědí llama3.2 vs mistral vs Claude Haiku.
4. Implementuj **fine-tuned Modelfile** — přizpůsob model pro Python kurz.
5. Postav offline chatbot pro kurz — funguje bez internetu.
