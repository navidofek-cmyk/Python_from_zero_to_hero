# Lekce 99: Databáze — `sqlite3`, SQLAlchemy

## 💾 `sqlite3` — vestavěná DB

SQLite je databáze v jednom souboru. Stdlib ji umí.

```python
import sqlite3

con = sqlite3.connect("mojedb.sqlite")
cur = con.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS uzivatele (
        id INTEGER PRIMARY KEY,
        jmeno TEXT NOT NULL,
        vek INTEGER
    )
""")

cur.execute("INSERT INTO uzivatele (jmeno, vek) VALUES (?, ?)", ("Anna", 12))
con.commit()

for radek in cur.execute("SELECT * FROM uzivatele"):
    print(radek)

con.close()
```

⚠️ **VŽDY parametrizované dotazy** (`?`), nikdy `f"... {jmeno}"` — SQL injection!

---

## 🛠️ Context manager

```python
with sqlite3.connect("db.sqlite") as con:
    con.execute(...)
# Auto-commit + close
```

---

## 🐘 PostgreSQL přes `psycopg`

```bash
pip install "psycopg[binary]"
```

```python
import psycopg

with psycopg.connect("postgresql://user:pass@host/db") as con:
    with con.cursor() as cur:
        cur.execute("SELECT version()")
        print(cur.fetchone())
```

`psycopg` v3 je moderní (sync i async).

---

## ⚡ `asyncpg` (async PostgreSQL)

```bash
pip install asyncpg
```

```python
import asyncpg

async def main():
    con = await asyncpg.connect("postgres://...")
    rows = await con.fetch("SELECT id, jmeno FROM users")
    for r in rows:
        print(r["jmeno"])
    await con.close()
```

Velmi rychlý.

---

## 🏗️ SQLAlchemy ORM

Místo psaní SQL ručně — **ORM** mapuje třídy na tabulky.

```bash
pip install "sqlalchemy[asyncio]"
```

```python
from sqlalchemy import create_engine, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase):
    pass

class Uzivatel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    jmeno: Mapped[str] = mapped_column(String(50))
    vek: Mapped[int]


engine = create_engine("sqlite:///db.sqlite")
Base.metadata.create_all(engine)

with Session(engine) as session:
    session.add(Uzivatel(jmeno="Anna", vek=12))
    session.commit()

    for u in session.query(Uzivatel).filter(Uzivatel.vek > 10):
        print(u.jmeno)
```

SQLAlchemy 2.x je **typovaný** (mapped_column).

---

## 🔄 Migrace — Alembic

Když měníš schéma, potřebuješ **migrace**:

```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "add field"
alembic upgrade head
```

---

## 🎯 Co kdy?

| | SQLite | PostgreSQL | NoSQL |
|---|---|---|---|
| Embedded | ✅ | ❌ | varies |
| Concurrent | omezené | ✅ | ✅ |
| Velká data | omezené | ✅ | ✅ |
| Transakce | ACID | ACID | varies |
| Pro malou app | ✅ | overkill | overkill |
| Pro webovou app | start | ✅ standard | specifické případy |

**Doporučení:** Začni se SQLite (žádný server), pro produkci **PostgreSQL** + SQLAlchemy.

---

## ✏️ Cvičení

1. **SQLite:** Vytvoř DB, tabulku `ukoly`, vlož 3 záznamy, vypiš.
2. **Parametrizace:** Schválně zkus SQL injection s `f"..."` — uvidíš proč to nikdy nedělat.
3. **SQLAlchemy:** Definuj třídu `Pes(jmeno, vek)`, uložte, načtěte.
4. **Async:** Pomocí `asyncpg` se připojte k PG (lokálně přes Docker).
