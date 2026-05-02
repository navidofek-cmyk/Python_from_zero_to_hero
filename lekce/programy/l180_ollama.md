# Program — Lekce 180: Lekce 180: Ollama — lokální LLM bez API klíče

Patří k lekci [Lekce 180: Ollama — lokální LLM bez API klíče](../180_ollama.md).

## Jak spustit

```bash
python3 programy/l180_ollama.py
```

## Zdrojový kód

### `l180_ollama.py`

```py
"""Lekce 180 — Ollama: lokální LLM bez API klíče.
Spuštění: uv run --with ollama l180_ollama.py
Předpoklad: ollama serve && ollama pull llama3.2
"""

import time


def demo_koncepty():
    print("=" * 50)
    print("  🦙 Ollama — lokální LLM")
    print("=" * 50)
    print("""
Instalace Ollama:
  Linux/macOS: curl -fsSL https://ollama.ai/install.sh | sh
  Windows:     winget install Ollama.Ollama

Modely:
  ollama pull llama3.2        # 2GB — dobrý, rychlý
  ollama pull mistral         # 4GB — výborný
  ollama pull codellama       # 4GB — specializovaný na kód
  ollama pull phi3            # 2GB — malý ale schopný
  ollama pull nomic-embed-text  # pro embeddings

Požadavky na HW:
  3B model:  min 4 GB RAM (CPU OK)
  7B model:  min 8 GB RAM (GPU doporučeno)
  13B model: min 16 GB RAM (GPU)
  70B model: min 64 GB RAM nebo 2× GPU
""")


def demo_s_ollama():
    try:
        import ollama

        print("=== Ollama je dostupný ===")

        # Vypíš dostupné modely
        try:
            modely = ollama.list()
            print(f"\nNainstalované modely:")
            for m in modely.get("models", []):
                nazev = m.get("model", m.get("name", "?"))
                velikost = m.get("size", 0) / 1e9
                print(f"  - {nazev} ({velikost:.1f} GB)")
        except Exception:
            print("  Ollama server neběží → spusť: ollama serve")
            return

        # Test základního volání
        modely_list = modely.get("models", [])
        if not modely_list:
            print("  Žádné modely → spusť: ollama pull llama3.2")
            return

        model = modely_list[0].get("model", modely_list[0].get("name", "llama3.2"))
        print(f"\n=== Test modelu: {model} ===")

        start = time.perf_counter()
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": "Co je Python? (1 věta)"}],
        )
        t = time.perf_counter() - start
        print(f"  Odpověď ({t:.1f}s): {response['message']['content'][:150]}")

        # Embeddings
        try:
            emb = ollama.embeddings(model=model, prompt="Python asyncio")
            print(f"\n  Embeddings dimenze: {len(emb['embedding'])}")
        except Exception as e:
            print(f"\n  Embeddings: {e}")

    except ImportError:
        print("\nOllama Python klient není dostupný: uv add ollama")
        demo_kod_ukazka()


def demo_kod_ukazka():
    print("""
=== Ollama kód (po instalaci) ===

  import ollama

  # Chat
  response = ollama.chat(
      model="llama3.2",
      messages=[{"role": "user", "content": "Co je Python?"}]
  )
  print(response["message"]["content"])

  # Streaming
  for chunk in ollama.chat(model="llama3.2",
                            messages=[...], stream=True):
      print(chunk["message"]["content"], end="")

  # Embeddings
  emb = ollama.embeddings(model="nomic-embed-text", prompt="Python")
  vektor = emb["embedding"]  # list[float]

  # Konverzace s pamětí
  history = [{"role": "system", "content": "Jsi Python expert."}]
  history.append({"role": "user", "content": "Jak funguje GIL?"})
  r = ollama.chat(model="llama3.2", messages=history)
  history.append(r["message"])
  history.append({"role": "user", "content": "Jak ho obejít?"})
  r2 = ollama.chat(model="llama3.2", messages=history)
  print(r2["message"]["content"])
""")


def demo_modelfile():
    print("\n=== Vlastní Modelfile (fine-tune chování) ===")
    print("""
  # Modelfile pro Python kurz asistenta
  FROM llama3.2

  SYSTEM \"\"\"
  Jsi expert na kurz Python: From Zero to Hero.
  Odpovídej vždy v češtině.
  Odkazuj na konkrétní lekce kurzu (1-183).
  Ukazuj praktické příklady kódu.
  \"\"\"

  PARAMETER temperature 0.7
  PARAMETER num_ctx 4096

  # Vytvoření:
  # ollama create python-kurz -f Modelfile
  # ollama run python-kurz "Vysvětli asyncio"
""")


def main():
    demo_koncepty()
    demo_s_ollama()
    demo_modelfile()
    print("\n✅ Demo dokončeno!")
    print("\nRychlý start:")
    print("  1. curl -fsSL https://ollama.ai/install.sh | sh")
    print("  2. ollama pull llama3.2")
    print("  3. uv add ollama")
    print("  4. python l180_ollama.py")


if __name__ == "__main__":
    main()

```
