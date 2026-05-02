# Program — Lekce 111: Lekce 111 — 12-Factor App v Pythonu

Patří k lekci [Lekce 111 — 12-Factor App v Pythonu](../111_12factor.md).

## Jak spustit

```bash
python3 programy/l111_12factor.py
```

## Zdrojový kód

### `l111_12factor.py`

```py
"""Lekce 111 — 12-Factor App v Pythonu."""
from __future__ import annotations

import logging
import os
import signal
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import NoReturn

# ── Simulace .env souboru pro demo ───────────────────────────────────────────

DEMO_ENV_CONTENT = """\
# Ukázkový .env soubor (v reálném projektu nikdy necommitovat!)
APP_NAME=MojeAplikace
APP_ENV=development
PORT=8000
DEBUG=true
DATABASE_URL=postgresql://user:heslo@localhost:5432/mydb
SECRET_KEY=super-tajny-klic-pouze-pro-demo
ALLOWED_HOSTS=localhost,127.0.0.1
MAX_WORKERS=4
"""


# ── Načítání .env souboru (bez externích závislostí) ─────────────────────────

def bootstrap_env(env_path: Path | None = None) -> dict[str, str]:
    """
    Načte .env soubor a nastaví proměnné prostředí.
    Existující proměnné prostředí mají přednost (12-factor princip).
    Vrátí dict načtených proměnných.
    """
    loaded: dict[str, str] = {}
    if env_path is None:
        env_path = Path(".env")

    if not env_path.exists():
        return loaded

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("\"'")
        # Existující env proměnná má přednost
        os.environ.setdefault(key, value)
        loaded[key] = value

    return loaded


# ── Konfigurace načítaná z prostředí ─────────────────────────────────────────

REQUIRED_VARS: list[str] = ["APP_NAME", "SECRET_KEY", "DATABASE_URL"]


@dataclass
class AppConfig:
    app_name: str
    app_env: str
    port: int
    debug: bool
    database_url: str
    secret_key: str
    allowed_hosts: list[str]
    max_workers: int


def load_config() -> AppConfig:
    """
    Načte konfiguraci z proměnných prostředí.
    Vyvolá chybu s přehledem chybějících povinných proměnných.
    """
    missing = [var for var in REQUIRED_VARS if var not in os.environ]
    if missing:
        print("CHYBA: Chybí povinné proměnné prostředí:", file=sys.stderr)
        for var in missing:
            print(f"  - {var}", file=sys.stderr)
        sys.exit(1)

    return AppConfig(
        app_name=os.environ["APP_NAME"],
        app_env=os.environ.get("APP_ENV", "production"),
        port=int(os.environ.get("PORT", "8000")),
        debug=os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes"),
        database_url=os.environ["DATABASE_URL"],
        secret_key=os.environ["SECRET_KEY"],
        allowed_hosts=os.environ.get("ALLOWED_HOSTS", "localhost").split(","),
        max_workers=int(os.environ.get("MAX_WORKERS", "2")),
    )


# ── Logging na stdout (12-factor faktor 11) ───────────────────────────────────

def setup_logging(debug: bool = False) -> None:
    """Nastaví logování na stdout — nikdy do souboru."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


# ── Stateless zpracování požadavků ────────────────────────────────────────────

# Simulace databáze jako backing service
_FAKE_DB: dict[str, dict[str, str]] = {
    "user:1": {"id": "1", "name": "Alice", "role": "admin"},
    "user:2": {"id": "2", "name": "Bob", "role": "user"},
}

# Simulace cache (backing service — Redis by byl v produkci)
_FAKE_CACHE: dict[str, tuple[str, float]] = {}
CACHE_TTL: int = 30  # sekund


def get_user_stateless(user_id: str) -> dict[str, str] | None:
    """
    12-factor stateless přístup k datům.
    Cache je backing service — při restartu procesu není ztracena.
    """
    logger = logging.getLogger("app.users")
    cache_key = f"user:{user_id}"

    # Zkontroluj cache (simulace Redis GET)
    if cache_key in _FAKE_CACHE:
        value, stored_at = _FAKE_CACHE[cache_key]
        if time.time() - stored_at < CACHE_TTL:
            logger.debug("Cache HIT pro %s", cache_key)
            # V reálném kódu: json.loads(value)
            return _FAKE_DB.get(cache_key)

    # Načti z databáze (simulace DB query)
    logger.debug("Cache MISS pro %s, načítám z DB", cache_key)
    user = _FAKE_DB.get(cache_key)
    if user:
        _FAKE_CACHE[cache_key] = (str(user), time.time())

    return user


# ── Graceful shutdown (12-factor faktor 9) ────────────────────────────────────

_SHUTDOWN_REQUESTED: bool = False


def install_signal_handlers() -> None:
    """Nainstaluje handlery pro graceful shutdown."""
    logger = logging.getLogger("app.lifecycle")

    def _handle_sigterm(signum: int, frame: object) -> None:
        global _SHUTDOWN_REQUESTED
        logger.info(
            "Přijat signál %s — zahajuji graceful shutdown...",
            signal.Signals(signum).name,
        )
        _SHUTDOWN_REQUESTED = True

    signal.signal(signal.SIGTERM, _handle_sigterm)
    signal.signal(signal.SIGINT, _handle_sigterm)
    logger.info("Signal handlery nainstalovány (SIGTERM, SIGINT)")


# ── Verze aplikace (build-time artefakt) ──────────────────────────────────────

def get_app_version() -> str:
    """Načte verzi z package metadata (nastavena při buildu)."""
    try:
        import importlib.metadata
        return importlib.metadata.version("moje-aplikace")
    except Exception:
        # V dev prostředí verze nemusí být nainstalována
        return os.environ.get("APP_VERSION", "0.0.0-dev")


# ── Validace prostředí ────────────────────────────────────────────────────────

@dataclass
class EnvCheck:
    name: str
    present: bool
    required: bool
    masked_value: str


def check_environment() -> list[EnvCheck]:
    """Zkontroluje a zobrazí stav proměnných prostředí."""
    checks: list[EnvCheck] = []
    all_vars = [
        ("APP_NAME", True),
        ("APP_ENV", False),
        ("PORT", False),
        ("DEBUG", False),
        ("DATABASE_URL", True),
        ("SECRET_KEY", True),
        ("ALLOWED_HOSTS", False),
        ("MAX_WORKERS", False),
    ]

    for var_name, required in all_vars:
        value = os.environ.get(var_name)
        present = value is not None
        # Maskuj citlivé hodnoty
        if present and any(s in var_name for s in ("SECRET", "PASSWORD", "KEY", "TOKEN")):
            masked = value[:3] + "***" + value[-2:] if len(value) > 5 else "***"
        elif present:
            masked = value[:50] + ("..." if len(value) > 50 else "")
        else:
            masked = "<NENASTAVENO>"

        checks.append(EnvCheck(var_name, present, required, masked))

    return checks


# ── Simulace jednoduchého request-response cyklu ──────────────────────────────

def simulate_requests(config: AppConfig, count: int = 5) -> None:
    """Simuluje zpracování HTTP požadavků — stateless, bez sdílené paměti."""
    logger = logging.getLogger("app.requests")
    logger.info("Spouštím simulaci %d požadavků na portu %d", count, config.port)

    for i in range(1, count + 1):
        if _SHUTDOWN_REQUESTED:
            logger.info("Shutdown požadován, přerušuji zpracování")
            break

        user_id = str((i % 2) + 1)
        user = get_user_stateless(user_id)
        if user:
            logger.info(
                "GET /users/%s → 200 OK | user=%s role=%s | req=%d",
                user_id, user["name"], user["role"], i,
            )
        else:
            logger.warning("GET /users/%s → 404 Not Found | req=%d", user_id, i)

        time.sleep(0.05)


# ── Hlavní funkce ─────────────────────────────────────────────────────────────

def main() -> None:
    # Krok 1: Načtení .env pro lokální vývoj (simulace)
    print("=" * 60)
    print("12-FACTOR APP DEMO")
    print("=" * 60)

    # Vytvoříme dočasný .env soubor pro demo
    tmp_env = Path("/tmp/demo_12factor.env")
    tmp_env.write_text(DEMO_ENV_CONTENT, encoding="utf-8")
    loaded = bootstrap_env(tmp_env)
    print(f"\n[1] Načteno {len(loaded)} proměnných z .env souboru")

    # Krok 2: Nastavení logování (stdout!)
    setup_logging(debug=True)
    logger = logging.getLogger("app.main")

    # Krok 3: Kontrola prostředí
    print("\n[2] Kontrola proměnných prostředí:")
    checks = check_environment()
    for check in checks:
        status = "OK  " if check.present else ("CHYBÍ!" if check.required else "výchozí")
        req_marker = "[povinná]" if check.required else "[volitelná]"
        print(f"    {status} {req_marker:12s} {check.name:20s} = {check.masked_value}")

    # Krok 4: Načtení konfigurace
    print("\n[3] Načítání konfigurace...")
    config = load_config()
    logger.info(
        "Konfigurace načtena: app=%s env=%s port=%d debug=%s workers=%d",
        config.app_name, config.app_env, config.port,
        config.debug, config.max_workers,
    )

    # Krok 5: Verze aplikace
    version = get_app_version()
    logger.info("Verze aplikace: %s", version)

    # Krok 6: Signal handlery
    install_signal_handlers()

    # Krok 7: Simulace provozu
    print("\n[4] Simulace zpracování požadavků (stateless):")
    simulate_requests(config, count=6)

    # Krok 8: Shrnutí 12 faktorů
    print("\n[5] Přehled implementovaných 12-factor principů:")
    principles = [
        ("I.   Codebase",      "Jeden repozitář, mnoho nasazení"),
        ("II.  Závislosti",    "pyproject.toml + venv"),
        ("III. Konfigurace",   "os.environ — bez secrets v kódu"),
        ("IV.  Backing svc",   "DB/cache jako URL proměnná prostředí"),
        ("V.   Build/Run",     "Oddělené fáze: wheel → image → run"),
        ("VI.  Procesy",       "Stateless — stav v backing service"),
        ("VII. Vazba portu",   "PORT z os.environ"),
        ("VIII.Souběžnost",    "Horizontální škálování procesů"),
        ("IX.  Disposability", "Rychlý start + SIGTERM handler"),
        ("X.   Dev/prod",      "Docker, stejné engine lokálně i prod"),
        ("XI.  Logy",          "logging → sys.stdout (ne soubory)"),
        ("XII. Admin proc.",   "Jednorázové: python manage.py migrate"),
    ]
    for num, desc in principles:
        print(f"    {num:20s} — {desc}")

    logger.info("Demo dokončeno. Aplikace připravena k ukončení.")
    tmp_env.unlink(missing_ok=True)


if __name__ == "__main__":
    main()

```
