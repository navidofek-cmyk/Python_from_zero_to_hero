# Projekt 13: Poznámkový blok s AI shrnutím

Mini-projekt po **sekci XIII (Architektura)**. REST API pro správu poznámek — FastAPI + SQLite + Claude AI shrnutí.

**Použité koncepty:** FastAPI (97), SQLite (99), Anthropic Claude API (100), Pydantic validace, `asynccontextmanager` (46).

## Jak spustit

```bash
pip install "fastapi[standard]" anthropic
export ANTHROPIC_API_KEY=sk-ant-...
fastapi dev projekty/13_fastapi_db_llm/app.py
```

Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API endpointy

| Metoda | Endpoint | Popis |
|--------|----------|-------|
| `GET` | `/poznamky` | Všechny poznámky |
| `POST` | `/poznamky` | Přidej poznámku |
| `POST` | `/poznamky/{id}/shrn` | Claude vytvoří shrnutí |

## Jak rozšířit

1. Přidej `categories` a filtrování.
2. Přidej **streamování** AI odpovědi (`StreamingResponse`).
3. Přidej **embeddings** + RAG vyhledávání.
4. Přidej **autentizaci** (FastAPI security).
5. Předělej z SQLite na PostgreSQL + SQLAlchemy.

## Zdrojový kód — `app.py`

```python
"""Mini-projekt po sekci XIII: FastAPI + SQLite + Claude.

Aplikace: poznámkový blok, kde k poznámce můžeš přidat AI shrnutí.

Vyžaduje:
    pip install "fastapi[standard]" anthropic
    export ANTHROPIC_API_KEY=...
"""

import os
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


DB = Path("/tmp/poznamky.sqlite")


def init_db() -> None:
    with sqlite3.connect(DB) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS poznamky (
                id INTEGER PRIMARY KEY,
                text TEXT NOT NULL,
                shrnuti TEXT
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan, title="Poznámky s AI")


class Poznamka(BaseModel):
    text: str


class Odpoved(BaseModel):
    id: int
    text: str
    shrnuti: str | None


@app.get("/poznamky")
def vse() -> list[Odpoved]:
    with sqlite3.connect(DB) as con:
        rows = con.execute("SELECT id, text, shrnuti FROM poznamky").fetchall()
    return [Odpoved(id=r[0], text=r[1], shrnuti=r[2]) for r in rows]


@app.post("/poznamky")
def pridej(p: Poznamka) -> Odpoved:
    with sqlite3.connect(DB) as con:
        cur = con.execute("INSERT INTO poznamky (text) VALUES (?)", (p.text,))
        return Odpoved(id=cur.lastrowid, text=p.text, shrnuti=None)


@app.post("/poznamky/{id}/shrn")
def shrn(id: int) -> Odpoved:
    """Použije Claude na vytvoření shrnutí."""
    try:
        from anthropic import Anthropic
    except ImportError:
        raise HTTPException(500, "anthropic není nainstalovaný")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(500, "Chybí ANTHROPIC_API_KEY")

    with sqlite3.connect(DB) as con:
        row = con.execute("SELECT text FROM poznamky WHERE id = ?", (id,)).fetchone()
        if not row:
            raise HTTPException(404, "Nenalezeno")

        client = Anthropic(api_key=api_key)
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[
                {"role": "user", "content": f"Shrň tuhle poznámku v jedné větě:\n\n{row[0]}"}
            ],
        )
        shrnuti = resp.content[0].text

        con.execute("UPDATE poznamky SET shrnuti = ? WHERE id = ?", (shrnuti, id))
        return Odpoved(id=id, text=row[0], shrnuti=shrnuti)


# Spuštění:
# fastapi dev app.py
```
