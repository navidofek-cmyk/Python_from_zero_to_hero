# Lekce 111 — 12-Factor App v Pythonu

Metodologie **12-Factor App** definuje dvanáct principů pro budování moderních, škálovatelných a přenositelných aplikací. V Pythonu se tyto principy přirozeně mapují na konkrétní vzory a knihovny.

---

## 1. Codebase — jeden repozitář, mnoho nasazení

Každá aplikace žije v jednom repozitáři. Různá prostředí (dev, staging, prod) jsou realizována konfigurací, nikoli větvemi kódu.

```
repo/
├── src/
│   └── app.py
├── tests/
├── pyproject.toml
└── .env.example        ← šablona, nikdy skutečné hodnoty!
```

---

## 2. Závislosti — explicitní deklarace

Závislosti jsou vždy deklarovány v `pyproject.toml` nebo `requirements.txt`. Nikdy se nespoléhejte na systémové balíčky.

```toml
# pyproject.toml
[project]
name = "moje-aplikace"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110",
    "pydantic-settings>=2.0",
    "uvicorn[standard]>=0.29",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.4",
    "mypy>=1.9",
]
```

```bash
# Izolované prostředí — VŽDY
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

---

## 3. Konfigurace — výhradně přes proměnné prostředí

**Zlaté pravidlo:** Konfiguraci z kódu oddělují proměnné prostředí. Kód, který přečtete v repozitáři, nesmí obsahovat žádné tajné hodnoty.

```python
import os
from dataclasses import dataclass

@dataclass
class Config:
    database_url: str
    secret_key: str
    debug: bool
    port: int
    allowed_hosts: list[str]

def load_config() -> Config:
    return Config(
        database_url=os.environ["DATABASE_URL"],       # povinné — KeyError pokud chybí
        secret_key=os.environ["SECRET_KEY"],            # povinné
        debug=os.environ.get("DEBUG", "false").lower() == "true",
        port=int(os.environ.get("PORT", "8000")),
        allowed_hosts=os.environ.get("ALLOWED_HOSTS", "localhost").split(","),
    )
```

### python-dotenv vzor pro lokální vývoj

```python
# Pro lokální vývoj načítáme .env soubor, v produkci proměnné přicházejí z platformy
from pathlib import Path

def bootstrap_env() -> None:
    """Načte .env soubor pouze pokud existuje (lokální vývoj)."""
    env_file = Path(".env")
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        # Existující proměnné prostředí mají přednost (12-factor princip)
        os.environ.setdefault(key.strip(), value.strip().strip('"\''))
```

### Soubor .env.example (committed do repozitáře)

```bash
# .env.example — zkopírujte jako .env a vyplňte hodnoty
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
SECRET_KEY=your-secret-key-here
DEBUG=true
PORT=8000
ALLOWED_HOSTS=localhost,127.0.0.1
REDIS_URL=redis://localhost:6379/0
```

---

## 4. Backing services — připojené zdroje jako URL

Databáze, cache, fronty — vše je adresovatelné URL. Záměna lokální databáze za produkční = změna jedné proměnné prostředí.

```python
import os
from urllib.parse import urlparse

def get_db_config() -> dict[str, str | int]:
    url = os.environ["DATABASE_URL"]
    parsed = urlparse(url)
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5432,
        "database": parsed.path.lstrip("/"),
        "user": parsed.username or "",
        "password": parsed.password or "",
    }
```

---

## 5. Build, Release, Run — tři přísně oddělené fáze

```
Kód + deps  →  [BUILD]  →  Artefakt (wheel, Docker image)
                              ↓
Artefakt + Config  →  [RELEASE]  →  Verzovaný release (image:v1.2.3)
                                        ↓
                    [RUN]  →  Spuštění procesů z release
```

```python
# Verze se pečuje do artefaktu v době buildu, nikoli za běhu
import importlib.metadata

def get_app_version() -> str:
    try:
        return importlib.metadata.version("moje-aplikace")
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0-dev"
```

---

## 6. Procesy — bezstavové, share-nothing

12-factor procesy jsou **stateless**. Každý stav musí žít v backing service (databáze, Redis).

```python
# ŠPATNĚ — stav v paměti procesu
_cache: dict[str, str] = {}

def get_user(user_id: str) -> str:
    if user_id not in _cache:
        _cache[user_id] = db_fetch(user_id)   # při restartu ztraceno!
    return _cache[user_id]

# SPRÁVNĚ — stav v backing service
def get_user(user_id: str, redis_client: Redis) -> str:
    cached = redis_client.get(f"user:{user_id}")
    if cached:
        return cached.decode()
    user = db_fetch(user_id)
    redis_client.setex(f"user:{user_id}", 300, user)
    return user
```

---

## 7. Vazba portu — aplikace exportuje službu přes port

```python
# Aplikace sama naslouchá na portu — žádný webserver middleware
import os

port = int(os.environ.get("PORT", "8000"))
host = os.environ.get("HOST", "0.0.0.0")

# uvicorn.run(app, host=host, port=port)
```

---

## 8. Souběžnost — škálování přes procesy

Škálujeme horizontálně — více instancí, nikoli větší stroje.

```yaml
# docker-compose.yml — ukázka škálování
services:
  web:
    image: moje-aplikace:latest
    environment:
      - DATABASE_URL=${DATABASE_URL}
    deploy:
      replicas: 3
  worker:
    image: moje-aplikace:latest
    command: python -m celery worker
    deploy:
      replicas: 5
```

---

## 9. Disposability — rychlý start, graceful shutdown

```python
import signal
import sys

def graceful_shutdown(signum: int, frame: object) -> None:
    print("Přijat signál ukončení, čistím zdroje...")
    # uzavření DB spojení, dopracování požadavků...
    sys.exit(0)

signal.signal(signal.SIGTERM, graceful_shutdown)
signal.signal(signal.SIGINT, graceful_shutdown)
```

---

## 10. Dev/prod parita — minimalizace rozdílů prostředí

```python
# Stejný databázový engine v dev i prod
# ŠPATNĚ: dev=SQLite, prod=PostgreSQL
# SPRÁVNĚ: dev i prod = PostgreSQL (přes Docker)

# Stejné verze závislostí — lockfile
# pip-compile requirements.in > requirements.txt
# uv lock
```

---

## 11. Logy — streamy událostí

**Klíčový princip:** Aplikace nikdy nespravuje log soubory. Píše na `stdout` a platforma (Kubernetes, Docker, systemd) logy sbírá.

```python
import logging
import sys

def setup_logging() -> None:
    """Nastaví logování na stdout — 12-factor způsob."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stdout,     # ← STDOUT, nikoli soubor!
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

logger = logging.getLogger(__name__)

def process_request(request_id: str) -> None:
    logger.info("Zpracovávám požadavek", extra={"request_id": request_id})
    # ...
    logger.info("Požadavek zpracován", extra={"request_id": request_id})
```

---

## 12. Admin procesy — jednorázové úlohy jako procesy

```bash
# Migrace databáze — spouštěna jako jednorázový proces
python manage.py migrate

# REPL pro debug produkce
python -c "from app import db; print(db.execute('SELECT count(*) FROM users').scalar())"
```

---

## Vzorová struktura 12-factor Python projektu

```
moje-aplikace/
├── src/
│   └── moje_aplikace/
│       ├── __init__.py
│       ├── config.py        ← načítání z env
│       ├── app.py           ← aplikační logika
│       ├── logging_setup.py ← logging na stdout
│       └── health.py        ← /health endpoint
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example             ← committed
└── .env                     ← v .gitignore!
```

---

## Shrnutí

| Factor | Klíčový vzor v Pythonu |
|--------|------------------------|
| Config | `os.environ`, `pydantic-settings` |
| Závislosti | `pyproject.toml`, `uv lock` |
| Logy | `logging` → `sys.stdout` |
| Procesy | Stateless, stav do Redis/DB |
| Disposability | `signal.SIGTERM` handler |
| Dev/prod parita | Docker, stejné verze |

---

## Cvičení

1. Vezměte existující skript, který čte konfiguraci z hardkódovaných hodnot nebo konfiguračního souboru, a refaktorujte ho tak, aby četl výhradně z `os.environ`.
2. Implementujte `bootstrap_env()` funkci, která načte `.env` soubor, ale nepřepíše existující proměnné prostředí.
3. Přidejte do aplikace `SIGTERM` handler, který před ukončením vypíše zprávu a počká 5 sekund na dopracování požadavků.
4. Napište skript, který ověří, že jsou nastaveny všechny povinné proměnné prostředí, a vypíše srozumitelnou chybovou zprávu pro každou chybějící proměnnou.
