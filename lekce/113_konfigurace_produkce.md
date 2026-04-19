# Lekce 113 — Konfigurace v produkci

Správa konfigurace je jedna z nejdůležitějších oblastí produkčního Pythonu. Chybná správa secretů způsobuje bezpečnostní incidenty, špatně strukturovaná konfigurace komplikuje správu prostředí.

---

## Zlatá pravidla konfigurace

```
1. Secrets NIKDY v kódu ani v repozitáři
2. Každé prostředí = jiné hodnoty proměnných prostředí
3. Konfigurace se validuje při startu — fail fast
4. Výchozí hodnoty pouze pro necitlivé, nepovinné nastavení
5. Citlivé hodnoty se maskují v logech
```

---

## 1. pydantic-settings vzor (bez závislosti — dataclass pattern)

`pydantic-settings` je de facto standard pro typovanou konfiguraci v Pythonu. Ukážeme ekvivalentní vzor pomocí čisté stdlib.

```python
import os
from dataclasses import dataclass, field
from typing import Optional


class ConfigError(Exception):
    """Chyba v konfiguraci — fail fast při startu."""
    pass


@dataclass
class DatabaseConfig:
    url: str
    pool_size: int = 10
    pool_timeout: int = 30
    echo: bool = False

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        url = os.environ.get("DATABASE_URL")
        if not url:
            raise ConfigError("DATABASE_URL není nastavena")
        if url.startswith("sqlite") and os.environ.get("APP_ENV") == "production":
            raise ConfigError("SQLite není povolena v produkci!")
        return cls(
            url=url,
            pool_size=int(os.environ.get("DB_POOL_SIZE", "10")),
            pool_timeout=int(os.environ.get("DB_POOL_TIMEOUT", "30")),
            echo=os.environ.get("DB_ECHO", "false").lower() == "true",
        )


@dataclass
class RedisConfig:
    url: str
    max_connections: int = 50
    decode_responses: bool = True

    @classmethod
    def from_env(cls) -> "RedisConfig":
        return cls(
            url=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
            max_connections=int(os.environ.get("REDIS_MAX_CONN", "50")),
        )


@dataclass
class AppConfig:
    app_name: str
    environment: str
    debug: bool
    secret_key: str
    allowed_hosts: list[str]
    database: DatabaseConfig
    redis: RedisConfig
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            app_name=os.environ.get("APP_NAME", "MyApp"),
            environment=os.environ.get("APP_ENV", "production"),
            debug=os.environ.get("DEBUG", "false").lower() == "true",
            secret_key=_require_env("SECRET_KEY"),
            allowed_hosts=os.environ.get("ALLOWED_HOSTS", "").split(","),
            database=DatabaseConfig.from_env(),
            redis=RedisConfig.from_env(),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
        )


def _require_env(name: str) -> str:
    """Načte povinnou proměnnou prostředí nebo vyvolá ConfigError."""
    value = os.environ.get(name)
    if not value:
        raise ConfigError(f"Povinná proměnná prostředí '{name}' není nastavena")
    return value
```

---

## 2. Maskování citlivých hodnot

```python
import re
from dataclasses import dataclass

SENSITIVE_PATTERNS = re.compile(
    r"(password|secret|key|token|credential|auth)",
    re.IGNORECASE,
)


def mask_value(key: str, value: str) -> str:
    """Zamaskuje citlivé hodnoty pro výpis v logách."""
    if SENSITIVE_PATTERNS.search(key):
        if len(value) <= 4:
            return "***"
        return value[:3] + "***" + value[-1:]
    # Zamaskuj URL s heslem: postgresql://user:heslo@host
    url_pattern = re.compile(r"(://[^:]+:)[^@]+(@)")
    return url_pattern.sub(r"\1***\2", value)


# Příklad:
# mask_value("SECRET_KEY", "abc123xyz789") → "abc***9"
# mask_value("DATABASE_URL", "postgresql://user:heslo@host/db")
#   → "postgresql://user:***@host/db"
```

---

## 3. Secrety — správné vzory

### Nikdy v kódu

```python
# ŠPATNĚ — secrets v kódu (i v .env commited do gitu)
DATABASE_URL = "postgresql://prod_user:SuperHeslo123@prod-db/myapp"
SECRET_KEY = "django-insecure-abc123"

# SPRÁVNĚ — výhradně z prostředí
DATABASE_URL = os.environ["DATABASE_URL"]
```

### Vault / AWS Secrets Manager vzor

```python
import json
import os


def get_secret_from_vault(secret_name: str) -> dict[str, str]:
    """
    V produkci: načte secret z Vault/AWS Secrets Manager.
    Zde: simulace pomocí env proměnných.
    """
    # AWS: boto3.client("secretsmanager").get_secret_value(SecretId=secret_name)
    # Vault: hvac.Client().secrets.kv.read_secret_version(path=secret_name)
    # Simulace: secret uložen jako JSON v env proměnné
    raw = os.environ.get(f"SECRET_{secret_name.upper()}")
    if raw:
        return json.loads(raw)
    return {}


def inject_db_credentials() -> None:
    """Načte DB credentials z Vault a nastaví DATABASE_URL."""
    creds = get_secret_from_vault("database")
    if creds:
        os.environ["DATABASE_URL"] = (
            f"postgresql://{creds['username']}:{creds['password']}"
            f"@{creds['host']}/{creds['database']}"
        )
```

### Docker secrets vzor

```python
from pathlib import Path


def read_docker_secret(secret_name: str) -> str | None:
    """
    Docker Swarm montuje secrety jako soubory do /run/secrets/.
    Kubernetes je montuje jako volume.
    """
    secret_path = Path(f"/run/secrets/{secret_name}")
    if secret_path.exists():
        return secret_path.read_text().strip()
    # Fallback na proměnnou prostředí (lokální vývoj)
    return os.environ.get(secret_name.upper())
```

---

## 4. Feature flags

Feature flags umožňují vypínat/zapínat funkce bez nasazení nového kódu.

```python
import os
from dataclasses import dataclass
from typing import Any


@dataclass
class FeatureFlag:
    name: str
    default: bool
    description: str

    @property
    def enabled(self) -> bool:
        """Přečte aktuální hodnotu z proměnné prostředí."""
        env_val = os.environ.get(f"FEATURE_{self.name.upper()}")
        if env_val is None:
            return self.default
        return env_val.lower() in ("true", "1", "yes", "on")


# Registr feature flags
class FeatureFlags:
    NEW_CHECKOUT = FeatureFlag("NEW_CHECKOUT", False, "Nový checkout flow")
    DARK_MODE = FeatureFlag("DARK_MODE", True, "Tmavý režim UI")
    AI_RECOMMENDATIONS = FeatureFlag("AI_RECOMMENDATIONS", False, "AI doporučení produktů")
    RATE_LIMITING = FeatureFlag("RATE_LIMITING", True, "Rate limiting API")
    MAINTENANCE_MODE = FeatureFlag("MAINTENANCE_MODE", False, "Maintenance stránka")

    @classmethod
    def all_flags(cls) -> list[FeatureFlag]:
        return [v for v in cls.__dict__.values() if isinstance(v, FeatureFlag)]

    @classmethod
    def status_report(cls) -> dict[str, bool]:
        return {flag.name: flag.enabled for flag in cls.all_flags()}


# Použití v kódu:
def handle_checkout(cart: dict) -> dict:
    if FeatureFlags.NEW_CHECKOUT.enabled:
        return _new_checkout_flow(cart)
    return _legacy_checkout_flow(cart)
```

---

## 5. Prostředí-specifická konfigurace

```python
import os
from typing import Any


def get_env_specific_config() -> dict[str, Any]:
    """Vrátí konfigurace specifické pro prostředí."""
    env = os.environ.get("APP_ENV", "production")

    base: dict[str, Any] = {
        "debug": False,
        "log_level": "INFO",
        "db_pool_size": 10,
        "cache_ttl": 300,
        "rate_limit_rpm": 60,
    }

    overrides: dict[str, dict[str, Any]] = {
        "development": {
            "debug": True,
            "log_level": "DEBUG",
            "db_pool_size": 2,
            "cache_ttl": 0,
            "rate_limit_rpm": 10_000,
        },
        "testing": {
            "debug": True,
            "log_level": "WARNING",
            "db_pool_size": 1,
            "cache_ttl": 0,
        },
        "staging": {
            "log_level": "DEBUG",
            "rate_limit_rpm": 600,
        },
    }

    config = {**base, **overrides.get(env, {})}
    config["environment"] = env
    return config
```

---

## 6. Validace konfigurace při startu (fail fast)

```python
import sys
from dataclasses import dataclass
from typing import NamedTuple


class ValidationResult(NamedTuple):
    is_valid: bool
    errors: list[str]
    warnings: list[str]


def validate_production_config(config: AppConfig) -> ValidationResult:
    """Striktní validace pro produkční prostředí."""
    errors: list[str] = []
    warnings: list[str] = []

    if config.environment == "production":
        if config.debug:
            errors.append("DEBUG=true je zakázáno v produkci!")
        if len(config.secret_key) < 32:
            errors.append("SECRET_KEY musí mít alespoň 32 znaků")
        if "localhost" in config.database.url:
            errors.append("Produkce nesmí používat localhost databázi")
        if not config.allowed_hosts or config.allowed_hosts == [""]:
            errors.append("ALLOWED_HOSTS musí být nastaveny v produkci")
        if config.log_level == "DEBUG":
            warnings.append("LOG_LEVEL=DEBUG generuje velké množství logů v produkci")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def startup_config_check(config: AppConfig) -> None:
    """Zkontroluje konfiguraci a ukončí aplikaci pokud jsou kritické chyby."""
    result = validate_production_config(config)
    for warning in result.warnings:
        print(f"VAROVÁNÍ: {warning}", file=sys.stderr)
    if not result.is_valid:
        print("CHYBA: Neplatná konfigurace!", file=sys.stderr)
        for error in result.errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
```

---

## Shrnutí

| Oblast | Vzor | Nikdy |
|--------|------|-------|
| Secrets | `os.environ`, Vault, Docker secrets | Hardkódovat v kódu |
| Validace | Dataclass + `from_env()` + fail fast | Lazy validace za běhu |
| Feature flags | `FEATURE_X` env proměnné | DB flags bez cache |
| Prostředí | `APP_ENV` s override dict | Různé kódy pro dev/prod |
| Maskování | `mask_value()` před logováním | Logovat plaintext secrets |

---

## Cvičení

1. Implementujte `ConfigLoader` třídu, která umí načítat konfiguraci z více zdrojů v prioritním pořadí: (1) proměnné prostředí, (2) soubor `/run/secrets/`, (3) výchozí hodnoty.
2. Rozšiřte `FeatureFlag` o podporu procentuálního rollout — flag je aktivní pro X% uživatelů na základě hashe jejich user_id.
3. Napište funkci `audit_config()`, která projde všechny nastavené proměnné prostředí, identifikuje potenciálně citlivé (regex na KEY, SECRET, PASSWORD, TOKEN) a ověří, zda jsou dostatečně dlouhé.
4. Implementujte hot-reload konfigurace — funkci, která při přijetí `SIGHUP` znovu načte konfiguraci z prostředí bez restartu procesu.
