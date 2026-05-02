# Projekt 16: Kompletní E-shop API

FastAPI + SQLAlchemy + JWT + Redis cache + Celery. Produkčně připravené REST API pro e-shop.

**Použité koncepty:** FastAPI (97), SQLAlchemy (99), JWT (165), Alembic (177), Pydantic (109).

## Spuštění

```bash
uv add "fastapi[standard]" sqlalchemy "python-jose[cryptography]" "passlib[bcrypt]"
fastapi dev projekty/16_eshop_api/app.py
# Swagger UI: http://localhost:8000/docs
```

## Endpointy

| Endpoint | Auth | Popis |
|----------|------|-------|
| `GET /produkty` | - | Seznam s filtrováním |
| `POST /auth/register` | - | Registrace |
| `POST /auth/token` | - | JWT přihlášení |
| `POST /objednavky` | JWT | Vytvoř objednávku |
| `GET /moje-objednavky` | JWT | Moje objednávky |

Zdrojový kód: `projekty/16_eshop_api/app.py`
