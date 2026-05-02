# Program — Lekce 113: Lekce 113 — Konfigurace v produkci

Patří k lekci [Lekce 113 — Konfigurace v produkci](../113_konfigurace_produkce.md).

## Jak spustit

```bash
python3 programy/l113_konfigurace_produkce.py
```

## Zdrojový kód

### `l113_konfigurace_produkce.py`

```py
"""Lekce 113 — Konfigurace v produkci: pydantic-settings vzor, secrety, feature flags."""
from __future__ import annotations

import json
import os
import re
import signal
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, NamedTuple


# ── Pomocné funkce ────────────────────────────────────────────────────────────

class ConfigError(Exception):
    """Chyba konfigurace — aplikace se nesmí spustit s neplatnou konfigurací."""


def _require_env(name: str) -> str:
    """Načte povinnou proměnnou prostředí. Vyvolá ConfigError pokud chybí."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConfigError(f"Povinná proměnná prostředí '{name}' není nastavena")
    return value


SENSITIVE_RE = re.compile(
    r"(password|passwd|secret|key|token|credential|auth|api_key|private)",
    re.IGNORECASE,
)
URL_PASSWORD_RE = re.compile(r"(://[^:]+:)([^@]+)(@)")


def mask_value(key: str, value: str) -> str:
    """Zamaskuje citlivé hodnoty — bezpečné pro logy."""
    if SENSITIVE_RE.search(key):
        if len(value) <= 4:
            return "***"
        return value[:3] + ("*" * min(len(value) - 4, 6)) + value[-1:]
    # Zamaskuj heslo v URL (postgresql://user:heslo@host)
    return URL_PASSWORD_RE.sub(r"\1***\3", value)


# ── Datové třídy konfigurace ──────────────────────────────────────────────────

@dataclass(frozen=True)
class DatabaseConfig:
    url: str
    pool_size: int
    pool_timeout: int
    echo: bool

    @classmethod
    def from_env(cls) -> DatabaseConfig:
        url = _require_env("DATABASE_URL")
        env = os.environ.get("APP_ENV", "production")
        if "sqlite" in url.lower() and env == "production":
            raise ConfigError("SQLite je zakázána v produkčním prostředí!")
        return cls(
            url=url,
            pool_size=int(os.environ.get("DB_POOL_SIZE", "10")),
            pool_timeout=int(os.environ.get("DB_POOL_TIMEOUT", "30")),
            echo=os.environ.get("DB_ECHO", "false").lower() in ("true", "1"),
        )

    def safe_repr(self) -> str:
        """Bezpečná reprezentace bez hesla."""
        return f"DatabaseConfig(url={mask_value('url', self.url)!r}, pool_size={self.pool_size})"


@dataclass(frozen=True)
class RedisConfig:
    url: str
    max_connections: int
    decode_responses: bool

    @classmethod
    def from_env(cls) -> RedisConfig:
        return cls(
            url=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
            max_connections=int(os.environ.get("REDIS_MAX_CONN", "50")),
            decode_responses=True,
        )


@dataclass(frozen=True)
class AppConfig:
    app_name: str
    environment: str
    debug: bool
    secret_key: str
    allowed_hosts: list[str]
    database: DatabaseConfig
    redis: RedisConfig
    log_level: str
    version: str

    @classmethod
    def from_env(cls) -> AppConfig:
        """Sestaví konfiguraci z prostředí. Fail fast při chybě."""
        return cls(
            app_name=os.environ.get("APP_NAME", "PythonApp"),
            environment=os.environ.get("APP_ENV", "production"),
            debug=os.environ.get("DEBUG", "false").lower() in ("true", "1"),
            secret_key=_require_env("SECRET_KEY"),
            allowed_hosts=[
                h.strip() for h in os.environ.get("ALLOWED_HOSTS", "localhost").split(",")
                if h.strip()
            ],
            database=DatabaseConfig.from_env(),
            redis=RedisConfig.from_env(),
            log_level=os.environ.get("LOG_LEVEL", "INFO").upper(),
            version=os.environ.get("APP_VERSION", "0.0.0-dev"),
        )

    def display(self) -> str:
        """Bezpečný výpis konfigurace (tajné hodnoty zamaskované)."""
        lines = [
            f"AppConfig:",
            f"  app_name     = {self.app_name!r}",
            f"  environment  = {self.environment!r}",
            f"  version      = {self.version!r}",
            f"  debug        = {self.debug}",
            f"  log_level    = {self.log_level}",
            f"  secret_key   = {mask_value('secret_key', self.secret_key)!r}",
            f"  allowed_hosts= {self.allowed_hosts}",
            f"  database     = {self.database.safe_repr()}",
            f"  redis.url    = {mask_value('redis_url', self.redis.url)!r}",
        ]
        return "\n".join(lines)


# ── Validace konfigurace (fail fast) ─────────────────────────────────────────

class ValidationResult(NamedTuple):
    is_valid: bool
    errors: list[str]
    warnings: list[str]


def validate_config(config: AppConfig) -> ValidationResult:
    """Validuje konfiguraci pro dané prostředí."""
    errors: list[str] = []
    warnings: list[str] = []

    if config.environment == "production":
        if config.debug:
            errors.append("DEBUG=true je zakázáno v produkci")
        if len(config.secret_key) < 32:
            errors.append(f"SECRET_KEY je příliš krátký ({len(config.secret_key)} znaků, minimum 32)")
        if "localhost" in config.database.url or "127.0.0.1" in config.database.url:
            errors.append("Databáze na localhost není povolena v produkci")
        if config.allowed_hosts == ["localhost"] or not config.allowed_hosts:
            warnings.append("ALLOWED_HOSTS obsahuje pouze localhost — ověřte nastavení")
        if config.log_level == "DEBUG":
            warnings.append("LOG_LEVEL=DEBUG generuje velké množství logů")

    if config.log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        errors.append(f"Neznámý LOG_LEVEL: {config.log_level!r}")

    if config.redis.max_connections < 1:
        errors.append("REDIS_MAX_CONN musí být kladné číslo")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def startup_check(config: AppConfig) -> None:
    """Spustí validaci při startu — ukončí aplikaci při kritické chybě."""
    result = validate_config(config)
    for w in result.warnings:
        print(f"  VAROVÁNÍ: {w}", file=sys.stderr)
    if not result.is_valid:
        print("FATÁLNÍ CHYBA: Neplatná konfigurace!", file=sys.stderr)
        for e in result.errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)


# ── Feature flags ─────────────────────────────────────────────────────────────

@dataclass
class FeatureFlag:
    name: str
    default: bool
    description: str
    rollout_percent: int = 100  # 0–100: procentuální rollout

    @property
    def enabled(self) -> bool:
        """Přečte aktuální stav z proměnné prostředí."""
        env_val = os.environ.get(f"FEATURE_{self.name.upper()}")
        if env_val is None:
            return self.default
        return env_val.lower() in ("true", "1", "yes", "on")

    def enabled_for(self, user_id: str) -> bool:
        """Procentuální rollout na základě user_id hashe."""
        if not self.enabled:
            return False
        if self.rollout_percent >= 100:
            return True
        # Deterministický hash pro konzistentní přiřazení
        h = hash(f"{self.name}:{user_id}") % 100
        return h < self.rollout_percent


class Features:
    """Registr feature flags aplikace."""
    NEW_CHECKOUT = FeatureFlag("NEW_CHECKOUT", False, "Nový checkout flow", rollout_percent=20)
    DARK_MODE = FeatureFlag("DARK_MODE", True, "Tmavý režim UI")
    AI_RECOMMENDATIONS = FeatureFlag("AI_RECOMMENDATIONS", False, "AI doporučení", rollout_percent=5)
    RATE_LIMITING = FeatureFlag("RATE_LIMITING", True, "Rate limiting API")
    MAINTENANCE = FeatureFlag("MAINTENANCE", False, "Maintenance stránka")
    NEW_SEARCH = FeatureFlag("NEW_SEARCH", False, "Nový vyhledávací engine", rollout_percent=50)

    @classmethod
    def all_flags(cls) -> list[FeatureFlag]:
        return [v for v in cls.__dict__.values() if isinstance(v, FeatureFlag)]


# ── Hot-reload konfigurace (SIGHUP) ───────────────────────────────────────────

_current_config: AppConfig | None = None
_config_lock = threading.Lock()


def get_config() -> AppConfig:
    """Vrátí aktuální konfiguraci (thread-safe)."""
    global _current_config
    with _config_lock:
        if _current_config is None:
            _current_config = AppConfig.from_env()
        return _current_config


def reload_config() -> AppConfig:
    """Znovu načte konfiguraci z prostředí (pro SIGHUP)."""
    global _current_config
    print("  Znovu načítám konfiguraci z prostředí...", file=sys.stderr)
    new_config = AppConfig.from_env()
    with _config_lock:
        _current_config = new_config
    print("  Konfigurace úspěšně obnovena.", file=sys.stderr)
    return new_config


def install_sighup_handler() -> None:
    """Nainstaluje SIGHUP handler pro hot-reload konfigurace."""
    def _handler(signum: int, frame: object) -> None:
        reload_config()

    if hasattr(signal, "SIGHUP"):  # Unix only
        signal.signal(signal.SIGHUP, _handler)


# ── Audit prostředí ───────────────────────────────────────────────────────────

@dataclass
class EnvAuditEntry:
    key: str
    is_sensitive: bool
    is_set: bool
    masked_value: str
    warning: str | None = None


def audit_environment() -> list[EnvAuditEntry]:
    """Projde prostředí a identifikuje potenciálně citlivé proměnné."""
    entries: list[EnvAuditEntry] = []
    for key, value in sorted(os.environ.items()):
        sensitive = bool(SENSITIVE_RE.search(key))
        warning: str | None = None
        if sensitive and len(value) < 16:
            warning = f"Citlivá proměnná '{key}' je příliš krátká ({len(value)} znaků)"
        entries.append(EnvAuditEntry(
            key=key,
            is_sensitive=sensitive,
            is_set=bool(value),
            masked_value=mask_value(key, value) if value else "<prázdná>",
            warning=warning,
        ))
    return entries


# ── Hlavní funkce ─────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 65)
    print("KONFIGURACE V PRODUKCI — DEMO")
    print("=" * 65)

    # Nastav testovací prostředí
    os.environ.update({
        "APP_NAME": "ProdukcioníApp",
        "APP_ENV": "development",
        "SECRET_KEY": "demo-klic-pro-lokalni-vyvoj-minimalne-32-znaku",
        "DATABASE_URL": "postgresql://appuser:tajne-heslo@db-server/appdb",
        "REDIS_URL": "redis://localhost:6379/0",
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
        "APP_VERSION": "1.5.3",
        "ALLOWED_HOSTS": "localhost,myapp.example.com",
        # Feature flags
        "FEATURE_NEW_CHECKOUT": "false",
        "FEATURE_DARK_MODE": "true",
        "FEATURE_NEW_SEARCH": "true",
    })

    # --- 1. Načtení konfigurace ---
    print("\n[1] Načítání konfigurace z prostředí:")
    try:
        config = AppConfig.from_env()
        print(config.display())
    except ConfigError as e:
        print(f"  CHYBA: {e}")
        return

    # --- 2. Validace ---
    print("\n[2] Validace konfigurace pro prostředí 'development':")
    result = validate_config(config)
    print(f"  Platná: {result.is_valid}")
    for w in result.warnings:
        print(f"  VAROVÁNÍ: {w}")
    for e in result.errors:
        print(f"  CHYBA: {e}")

    # Simuluj produkční selhání
    print("\n[3] Simulace produkční validace se špatnou konfigurací:")
    os.environ["APP_ENV"] = "production"
    os.environ["DEBUG"] = "true"
    os.environ["SECRET_KEY"] = "kratky"
    os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
    try:
        bad_config = AppConfig.from_env()
        bad_result = validate_config(bad_config)
        if not bad_result.is_valid:
            print("  Zachyceny produkční chyby konfigurace:")
            for err in bad_result.errors:
                print(f"    - {err}")
    except ConfigError as e:
        print(f"  ConfigError: {e}")

    # Obnov správnou konfiguraci
    os.environ.update({
        "APP_ENV": "development",
        "DEBUG": "true",
        "SECRET_KEY": "demo-klic-pro-lokalni-vyvoj-minimalne-32-znaku",
        "DATABASE_URL": "postgresql://appuser:tajne-heslo@db-server/appdb",
    })
    global _current_config
    _current_config = None

    # --- 4. Feature flags ---
    print("\n[4] Feature flags:")
    for flag in Features.all_flags():
        status = "ZAPNUT " if flag.enabled else "VYPNUT "
        print(f"  {status} {flag.name:25s} — {flag.description}")

    # Procentuální rollout pro různé uživatele
    print("\n[5] Procentuální rollout (NEW_CHECKOUT=20%, NEW_SEARCH=50%):")
    test_users = [f"user-{i:03d}" for i in range(10)]
    for uid in test_users:
        checkout = "OK" if Features.NEW_CHECKOUT.enabled_for(uid) else "--"
        search = "OK" if Features.NEW_SEARCH.enabled_for(uid) else "--"
        print(f"  {uid}: NEW_CHECKOUT={checkout}  NEW_SEARCH={search}")

    # --- 6. Maskování hodnot ---
    print("\n[6] Maskování citlivých hodnot v logách:")
    test_cases: list[tuple[str, str]] = [
        ("SECRET_KEY", "super-tajny-klic-produkce"),
        ("DATABASE_URL", "postgresql://admin:HesloXYZ@prod-db.example.com/myapp"),
        ("API_TOKEN", "ghp_abc123def456ghi789"),
        ("APP_NAME", "MojeAplikace"),
        ("PORT", "8000"),
        ("REDIS_PASSWORD", "redis-secret"),
    ]
    for key, value in test_cases:
        masked = mask_value(key, value)
        changed = " ← MASKOVÁNO" if masked != value else ""
        print(f"  {key:20s}: {masked!r}{changed}")

    # --- 7. Audit prostředí ---
    print("\n[7] Audit prostředí — citlivé proměnné:")
    entries = audit_environment()
    sensitive = [e for e in entries if e.is_sensitive]
    print(f"  Celkem proměnných: {len(entries)}, citlivých: {len(sensitive)}")
    for entry in sensitive[:8]:
        warn = f"  ⚠ {entry.warning}" if entry.warning else ""
        print(f"  {entry.key:25s} = {entry.masked_value}{warn}")

    # --- 8. Hot-reload simulace ---
    print("\n[8] Hot-reload konfigurace (SIGHUP simulace):")
    install_sighup_handler()
    c1 = get_config()
    print(f"  Verze před reload : {c1.version!r}")
    os.environ["APP_VERSION"] = "1.5.4-hotfix"
    _current_config = None  # simulace SIGHUP
    c2 = reload_config()
    print(f"  Verze po reload   : {c2.version!r}")
    print(f"  Konfigurace obnovena bez restartu procesu: {c1.version != c2.version}")

    print("\n[9] Shrnutí doporučení:")
    rules = [
        "Secrets NIKDY v kódu ani commited v gitu",
        "Každé prostředí = vlastní sada proměnných prostředí",
        "Konfigurace validována při startu — fail fast",
        "Citlivé hodnoty maskovat před logováním",
        "Feature flags pro postupný rollout bez redeploymentu",
        "Hot-reload přes SIGHUP pro změny za běhu",
    ]
    for i, rule in enumerate(rules, 1):
        print(f"  {i}. {rule}")


if __name__ == "__main__":
    main()

```
