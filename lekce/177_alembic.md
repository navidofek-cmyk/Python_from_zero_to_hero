# Lekce 177: Alembic — migrace databází

Alembic verzuje schéma databáze jako git verzuje kód. Každá změna = migrace = reverzibilní krok.

---

## 🚀 Instalace

```bash
uv add alembic sqlalchemy psycopg2-binary
alembic init migrations
```

---

## ⚙️ Konfigurace

`alembic.ini`:
```ini
[alembic]
script_location = migrations
sqlalchemy.url = postgresql://user:pass@localhost/mydb
# Nebo z env: sqlalchemy.url = %(DB_URL)s
```

`migrations/env.py`:
```python
from sqlalchemy import engine_from_config, pool
from alembic import context
from models import Base   # tvoje SQLAlchemy modely

config = context.config
target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

---

## 📋 SQLAlchemy modely

```python
# models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Uzivatel(Base):
    __tablename__ = "uzivatele"

    id = Column(Integer, primary_key=True)
    jmeno = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    aktivni = Column(Boolean, default=True)
    vytvoreno = Column(DateTime, default=datetime.utcnow)


class Objednavka(Base):
    __tablename__ = "objednavky"

    id = Column(Integer, primary_key=True)
    uzivatel_id = Column(Integer, ForeignKey("uzivatele.id"), nullable=False)
    celkova_cena = Column(Integer, nullable=False)   # v haléřích
    stav = Column(String(50), default="pending")
    poznamka = Column(Text)
    vytvoreno = Column(DateTime, default=datetime.utcnow)
```

---

## 🔄 Workflow migrací

```bash
# Vytvoř první migraci (autogenerovanou ze SQLAlchemy modelů)
alembic revision --autogenerate -m "vytvorit_tabulky_uzivatele_objednavky"

# Zkontroluj vygenerovaný soubor!
cat migrations/versions/abc123_vytvorit_tabulky.py

# Spusť migraci
alembic upgrade head

# Vrať zpět o jeden krok
alembic downgrade -1

# Vrať na konkrétní revizi
alembic downgrade abc123

# Historie
alembic history --verbose

# Aktuální stav
alembic current
```

---

## 📄 Vygenerovaná migrace

```python
# migrations/versions/abc123_vytvorit_tabulky.py
"""vytvorit_tabulky_uzivatele_objednavky

Revision ID: abc123
Revises:
Create Date: 2026-05-02 10:00:00
"""

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.create_table(
        "uzivatele",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("jmeno", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("aktivni", sa.Boolean(), nullable=True),
        sa.Column("vytvoreno", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_uzivatele_email", "uzivatele", ["email"])

    op.create_table(
        "objednavky",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uzivatel_id", sa.Integer(), nullable=False),
        sa.Column("celkova_cena", sa.Integer(), nullable=False),
        sa.Column("stav", sa.String(50), nullable=True),
        sa.Column("poznamka", sa.Text(), nullable=True),
        sa.Column("vytvoreno", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["uzivatel_id"], ["uzivatele.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("objednavky")
    op.drop_index("ix_uzivatele_email")
    op.drop_table("uzivatele")
```

---

## ✏️ Ruční migrace (datová)

```python
# Datové migrace — nelze autogenerovat
"""add_default_admin

Revision ID: def456
Revises: abc123
"""
from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    # Přidej sloupec
    op.add_column("uzivatele", sa.Column("role", sa.String(50), nullable=True))

    # Vyplň existující záznamy
    op.execute("UPDATE uzivatele SET role = 'user' WHERE role IS NULL")

    # Nastav NOT NULL constraint
    op.alter_column("uzivatele", "role", nullable=False, server_default="user")

    # Přidej admin uživatele
    op.execute("""
        INSERT INTO uzivatele (jmeno, email, aktivni, role, vytvoreno)
        VALUES ('Admin', 'admin@example.com', TRUE, 'admin', NOW())
        ON CONFLICT (email) DO NOTHING
    """)


def downgrade() -> None:
    op.execute("DELETE FROM uzivatele WHERE email = 'admin@example.com'")
    op.drop_column("uzivatele", "role")
```

---

## 🔒 Produkční best practices

```python
# migrations/env.py — produkční nastavení

import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, text
from alembic import context


def get_url():
    """Načti URL z env, ne z ini souboru."""
    return os.environ["DATABASE_URL"]


def run_migrations_online():
    config.set_main_option("sqlalchemy.url", get_url())

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Zamkni během migrace (PostgreSQL advisory lock)
        connection.execute(text("SELECT pg_advisory_lock(1234567890)"))
        try:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,          # detekuj změny typů
                compare_server_default=True,
            )
            with context.begin_transaction():
                context.run_migrations()
        finally:
            connection.execute(text("SELECT pg_advisory_unlock(1234567890)"))
```

CI/CD integrace:
```bash
# V Dockerfile nebo startup skriptu
alembic upgrade head && uvicorn app:app
```

---

## ✏️ Cvičení

1. Vytvoř SQLAlchemy modely pro e-shop (User, Product, Order, OrderItem) a vygeneruj migrace.
2. Napiš migraci která přejmenuje sloupec a zachová data.
3. Implementuj **multi-tenant** migrace — každý tenant má vlastní schema.
4. Přidej Alembic do CI/CD — migruj databázi před každým deploymentem.
5. Napiš test který ověří, že každá migrace je reverzibilní (upgrade → downgrade → upgrade).
