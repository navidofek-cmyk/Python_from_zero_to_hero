# Projekt 13: Poznámkový blok s AI shrnutím

Mini-projekt po sekci XIII. Spojuje:

- **FastAPI** (lekce 97) — REST API, Pydantic validace
- **SQLite** (lekce 99) — perzistence
- **Anthropic Claude** (lekce 100) — AI shrnutí

## Funkce

- `GET /poznamky` — všechny
- `POST /poznamky` — přidej
- `POST /poznamky/{id}/shrn` — Claude udělá shrnutí

## Spuštění

```bash
pip install "fastapi[standard]" anthropic
export ANTHROPIC_API_KEY=sk-ant-...
fastapi dev app.py
```

Otevři http://127.0.0.1:8000/docs — Swagger UI.

## Jak rozšířit

1. Přidej `categories` a filtrování.
2. Přidej **streamování** AI odpovědi (`StreamingResponse`).
3. Přidej **embeddings** + vyhledávání podobných poznámek (RAG).
4. Přidej **autentizaci** (FastAPI security).
5. Předělej z SQLite na PostgreSQL + SQLAlchemy.
6. Containerizace (Dockerfile).
