# Lekce 114 — Containerizace Python aplikací

Docker je standard pro balení a spouštění Python aplikací. Správně napsaný Dockerfile zajistí malý obraz, rychlé buildy a bezpečný provoz.

---

## Proč containerizovat?

```
Bez kontejnerů:                  S kontejnery:
"U mě funguje!"          →       "Všude stejné prostředí"
Různé Python verze       →       Přesná verze v Dockerfilu
Konflikty závislostí     →       Izolované venv uvnitř obrazu
"Deploy manuálně"        →       docker push → k8s apply
```

---

## 1. Základní Dockerfile (naivní — poučný příklad)

```dockerfile
# ŠPATNĚ — nepraktické, pomalé, velké
FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

Problémy:
- Každá změna kódu přeinstaluje VŠECHNY závislosti
- Obraz obsahuje build nástroje (~1 GB)
- Běží jako root (bezpečnostní riziko)
- Žádný health check

---

## 2. Produkční Dockerfile — multi-stage build

```dockerfile
# ─── Stage 1: Builder ───────────────────────────────────────────
FROM python:3.12-slim AS builder

# Nainstaluj uv (moderní, rychlý package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Kopíruj POUZE dependency soubory — cachuje se dokud se nezmění
COPY pyproject.toml uv.lock ./

# Instaluj závislosti do izolovaného adresáře
RUN uv sync --frozen --no-dev --no-install-project

# Teprve teď zkopíruj kód (invaliduje cache jen při změně kódu)
COPY src/ ./src/
RUN uv sync --frozen --no-dev


# ─── Stage 2: Runtime ────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Bezpečnost: neprivilegovaný uživatel
RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --no-create-home appuser

WORKDIR /app

# Zkopíruj POUZE artefakty z builderu — bez build nástrojů
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appgroup /app/src /app/src

# Nastavení prostředí
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

USER appuser

# Health check — Kubernetes/Docker Swarm ho používá
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:$PORT/health')"

EXPOSE $PORT

CMD ["python", "-m", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 3. Multi-stage s pip (bez uv)

```dockerfile
FROM python:3.12-slim AS builder

WORKDIR /app

# Pip cache mount — Docker BuildKit
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefix=/install -r requirements.txt

# ─────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

COPY --from=builder /install /usr/local
COPY src/ /app/src/

RUN useradd --system --no-create-home appuser
USER appuser

WORKDIR /app
ENV PYTHONUNBUFFERED=1
CMD ["python", "src/app.py"]
```

---

## 4. .dockerignore — co nevkládat do obrazu

```dockerignore
# .dockerignore
__pycache__/
*.py[cod]
*.egg-info/
.git/
.github/
.venv/
venv/
.env
.env.*
!.env.example
*.log
.pytest_cache/
.mypy_cache/
.ruff_cache/
dist/
build/
docs/
tests/
*.md
!README.md
```

---

## 5. Čtení konfigurace z env v kontejneru

```python
import os
import sys

def require_env(name: str) -> str:
    """Povinná env proměnná — bez ní kontejner nespustíme."""
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"FATAL: Proměnná prostředí '{name}' není nastavena", file=sys.stderr)
        sys.exit(1)
    return value

# Konfigurace přichází VÝHRADNĚ z prostředí (12-factor)
config = {
    "database_url": require_env("DATABASE_URL"),
    "secret_key": require_env("SECRET_KEY"),
    "port": int(os.environ.get("PORT", "8000")),
    "debug": os.environ.get("DEBUG", "false").lower() == "true",
}
```

---

## 6. Health check endpoint vzor

```python
import time
import os

_START_TIME = time.time()


def health_check_handler() -> tuple[int, dict]:
    """
    Jednoduchý health check.
    Vrátí (HTTP status kód, JSON tělo).
    """
    checks: dict[str, dict] = {}

    # Databáze
    try:
        # db.execute("SELECT 1")
        checks["database"] = {"status": "ok"}
    except Exception as e:
        checks["database"] = {"status": "error", "message": str(e)}

    overall = "healthy" if all(
        c["status"] == "ok" for c in checks.values()
    ) else "unhealthy"

    status_code = 200 if overall == "healthy" else 503

    return status_code, {
        "status": overall,
        "uptime": round(time.time() - _START_TIME),
        "version": os.environ.get("APP_VERSION", "dev"),
        "checks": checks,
    }
```

---

## 7. docker-compose pro lokální vývoj

```yaml
# docker-compose.yml
services:
  app:
    build:
      context: .
      target: runtime          # Multi-stage: spustíme runtime stage
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=development
      - DEBUG=true
      - DATABASE_URL=postgresql://appuser:heslo@db:5432/appdb
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=lokalni-dev-klic-minimum-32-znaku-zde
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 10s
      timeout: 5s
      retries: 3

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: heslo
      POSTGRES_DB: appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d appdb"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru

volumes:
  postgres_data:
```

---

## 8. Optimalizace velikosti obrazu

```
# Porovnání base obrazů:
python:3.12           ~1.0 GB   # Plný Debian — pouze pro build
python:3.12-slim      ~130 MB   # Slim Debian — dobrý základ
python:3.12-alpine    ~55 MB    # Alpine — malý, ale komplikace s C extenzemi
gcr.io/distroless/...  ~30 MB   # Minimalistický — bez shellu
```

```dockerfile
# Triky pro menší obraz:
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*
```

---

## Shrnutí

| Technika | Účel |
|----------|------|
| Multi-stage build | Malý runtime obraz bez build nástrojů |
| Layer caching | Kopíruj deps před kódem |
| Neprivilegovaný user | Bezpečnost — ne root |
| `PYTHONUNBUFFERED=1` | Logy okamžitě na stdout |
| `PYTHONDONTWRITEBYTECODE=1` | Žádné `.pyc` soubory |
| HEALTHCHECK | Orchestrátor ví, kdy je app ready |
| .dockerignore | Vyloučí zbytečné soubory z build kontextu |

---

## Cvičení

1. Napište Dockerfile pro FastAPI aplikaci s multi-stage buildem (builder + runtime), neprivilegovaným uživatelem a health checkem.
2. Přidejte do Dockerfile build argument `APP_VERSION` a promítněte ho do proměnné prostředí `APP_VERSION` v runtime stage.
3. Napište skript, který ověří, že výsledný Docker obraz: (a) neběží jako root, (b) má nastavenou proměnnou `PYTHONUNBUFFERED`, (c) exponuje správný port.
4. Vytvořte `docker-compose.override.yml` pro vývoj, který přimontuje lokální kód jako volume (hot-reload) a přepíše CMD na `uvicorn --reload`.
