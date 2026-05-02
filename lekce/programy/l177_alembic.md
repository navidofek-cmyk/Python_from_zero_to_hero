# Program — Lekce 177: Lekce 177: Alembic — migrace databází

Patří k lekci [Lekce 177: Alembic — migrace databází](../177_alembic.md).

## Jak spustit

```bash
python3 programy/l177_alembic.py
```

## Zdrojový kód

### `l177_alembic.py`

```py
"""Lekce 177 — Alembic: migrace databází.
Spuštění: uv run --with alembic,sqlalchemy l177_alembic.py
"""


def demo_alembic_koncepty():
    print("=" * 50)
    print("  🗄️  Alembic — DB migrace")
    print("=" * 50)
    print("""
Alembic workflow:
  1. Definuj SQLAlchemy modely
  2. alembic revision --autogenerate -m "popis"
  3. Zkontroluj vygenerovaný soubor
  4. alembic upgrade head
  5. V produkci: alembic upgrade head před deploymentem

Revize = verzovaný krok změny schématu
  up:   aplikuj změnu
  down: vrať zpět (downgrade)

Příkazy:
  alembic current           → aktuální revize v DB
  alembic history           → seznam všech revizí
  alembic upgrade head      → migruj na nejnovější
  alembic downgrade -1      → vrať o 1 krok
  alembic upgrade +2        → aplikuj 2 kroky

Best practices:
  - vždy zkontroluj autogenerovanou migraci
  - testuj upgrade + downgrade v CI
  - data migrace ručně (autogenerate nezná data)
  - advisory lock v produkci (paralelní deploymenty)
""")


def demo_sqlalchemy_modely():
    print("=== SQLAlchemy modely → migrace ===")
    try:
        from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, text
        from sqlalchemy.orm import declarative_base
        from datetime import datetime

        Base = declarative_base()

        class Uzivatel(Base):
            __tablename__ = "uzivatele"
            id = Column(Integer, primary_key=True)
            jmeno = Column(String(100), nullable=False)
            email = Column(String(255), unique=True, nullable=False)
            aktivni = Column(Boolean, default=True)
            vytvoreno = Column(DateTime, default=datetime.utcnow)

        # In-memory SQLite pro demo
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)

        # Simulace dat
        from sqlalchemy.orm import Session
        with Session(engine) as session:
            session.add(Uzivatel(jmeno="Anna", email="anna@test.com"))
            session.add(Uzivatel(jmeno="Bob", email="bob@test.com"))
            session.commit()
            uzivatele = session.query(Uzivatel).all()
            print(f"  Vytvořeno {len(uzivatele)} uživatelů")
            for u in uzivatele:
                print(f"    {u.id}: {u.jmeno} ({u.email})")

        # Simulace migrace — přidání sloupce
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE uzivatele ADD COLUMN role TEXT DEFAULT 'user'"))
            conn.execute(text("UPDATE uzivatele SET role = 'admin' WHERE jmeno = 'Anna'"))
            conn.commit()
            rows = conn.execute(text("SELECT jmeno, role FROM uzivatele")).fetchall()
            print("\n  Po migraci (přidání sloupce 'role'):")
            for r in rows:
                print(f"    {r[0]}: role={r[1]}")

    except ImportError:
        print("  SQLAlchemy: uv add sqlalchemy")


def demo_alembic_migrace_kod():
    print("\n=== Ukázka Alembic migrace ===")
    print("""
# Autogenerovaná migrace (migrations/versions/abc123_.py):

def upgrade() -> None:
    op.create_table("uzivatele",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("jmeno", sa.String(100), nullable=False),
    )
    op.create_index("ix_email", "uzivatele", ["email"])

def downgrade() -> None:
    op.drop_index("ix_email")
    op.drop_table("uzivatele")

# Datová migrace (ručně):
def upgrade() -> None:
    op.add_column("uzivatele", sa.Column("role", sa.String(50)))
    op.execute("UPDATE uzivatele SET role = 'user' WHERE role IS NULL")
    op.alter_column("uzivatele", "role", nullable=False)
""")


def main():
    demo_alembic_koncepty()
    demo_sqlalchemy_modely()
    demo_alembic_migrace_kod()
    print("\n✅ Demo dokončeno!")
    print("Instalace: uv add alembic 'sqlalchemy[asyncio]' psycopg2-binary")
    print("Init:      alembic init migrations")


if __name__ == "__main__":
    main()

```
