# Projekt 16 — Kompletní E-shop API

FastAPI + SQLAlchemy + JWT autentizace + Redis cache + Celery async tasky.

## Instalace a spuštění

```bash
# Základní (SQLite demo)
uv add "fastapi[standard]" sqlalchemy "python-jose[cryptography]" "passlib[bcrypt]"
fastapi dev projekty/16_eshop_api/app.py

# Swagger UI: http://localhost:8000/docs
```

## API endpointy

| Metoda | Endpoint | Auth | Popis |
|--------|----------|------|-------|
| GET | `/produkty` | - | Seznam produktů (filtrování) |
| GET | `/produkty/{id}` | - | Detail produktu |
| POST | `/admin/produkty` | admin | Nový produkt |
| POST | `/auth/register` | - | Registrace |
| POST | `/auth/token` | - | Přihlášení → JWT |
| POST | `/objednavky` | user | Vytvoř objednávku |
| GET | `/moje-objednavky` | user | Moje objednávky |

## Použité technologie

- **FastAPI** — REST API (lekce 97)
- **SQLAlchemy** — ORM (lekce 99)
- **Alembic** — migrace (lekce 177)
- **JWT + bcrypt** — autentizace (lekce 165)
- **Pydantic** — validace (lekce 109)
