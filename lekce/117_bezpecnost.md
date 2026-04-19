# Lekce 117 — Bezpečnost Python aplikací (OWASP Top 10)

OWASP Top 10 je seznam nejzávažnějších bezpečnostních rizik webových aplikací. Python vývojáři musejí těmto útokům aktivně předcházet.

---

## OWASP Top 10 (2021)

```
A01 Broken Access Control       — Nedostatečná kontrola oprávnění
A02 Cryptographic Failures      — Slabá kryptografie, plaintext
A03 Injection                   — SQL, OS, LDAP injection
A04 Insecure Design             — Architekturas. chyby
A05 Security Misconfiguration   — DEBUG=true, default hesla
A06 Vulnerable Components       — Zranitelné závislosti
A07 Auth Failures               — Slabá autentizace
A08 Software Integrity Failures — Nevalidovaný kód/data
A09 Logging Failures            — Chybějící logy bezpec. událostí
A10 SSRF                        — Server-Side Request Forgery
```

---

## A03 — Injection: SQL Injection

SQL Injection je nejstarší a stále nejrozšířenější útok.

```python
import sqlite3

# ŠPATNĚ — SQL injection zranitelnost!
def get_user_vulnerable(username: str) -> dict | None:
    conn = sqlite3.connect(":memory:")
    # Útočník zadá: admin' OR '1'='1
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor = conn.execute(query)
    return cursor.fetchone()

# SPRÁVNĚ — parametrizované dotazy (binding)
def get_user_safe(conn: sqlite3.Connection, username: str) -> tuple | None:
    cursor = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,),   # Hodnota je vždy escapovaná driverem
    )
    return cursor.fetchone()

# SPRÁVNĚ — ORM (SQLAlchemy) automaticky escapuje
# User.query.filter_by(username=username).first()

# Ukázka útoku:
# username = "admin' OR '1'='1' --"
# Výsledný dotaz: SELECT * FROM users WHERE username = 'admin' OR '1'='1' --'
# → vrátí VŠECHNY uživatele!
```

### Prevence SQL injection

```python
from typing import Any

def safe_query(
    conn: sqlite3.Connection,
    table: str,
    filters: dict[str, Any],
) -> list[tuple]:
    """Bezpečný generický dotaz s whitelist tabulky."""
    ALLOWED_TABLES = frozenset({"users", "orders", "products"})
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Nepovolená tabulka: {table!r}")

    # Parametrizace placeholderů — nikdy f-string pro hodnoty!
    where_clauses = [f"{col} = ?" for col in filters.keys()]
    query = f"SELECT * FROM {table}"  # table je z whitelist — bezpečné
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    return conn.execute(query, list(filters.values())).fetchall()
```

---

## A08 — Pickle nebezpečí

`pickle` deserializuje libovolný Python kód — nikdy nepickujte nedůvěryhodná data.

```python
import pickle
import json

# ŠPATNĚ — pickle deserializace nedůvěryhodných dat = RCE!
def load_user_data_vulnerable(data: bytes) -> dict:
    return pickle.loads(data)  # Útočník může spustit libovolný kód!

# Proof of concept útoku:
import os

class MaliciousPayload:
    def __reduce__(self):
        return (os.system, ("rm -rf /tmp/test",))

# payload = pickle.dumps(MaliciousPayload())
# pickle.loads(payload)  → spustí příkaz!

# SPRÁVNĚ — JSON pro přenos dat
def save_user_data_safe(data: dict) -> bytes:
    return json.dumps(data).encode("utf-8")

def load_user_data_safe(raw: bytes) -> dict:
    parsed = json.loads(raw.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("Očekáván JSON objekt")
    return parsed

# Pokud MUSÍTE pickle — podepisujte data!
import hashlib
import hmac

def safe_pickle_dumps(data: object, secret: bytes) -> tuple[bytes, bytes]:
    payload = pickle.dumps(data)
    signature = hmac.new(secret, payload, hashlib.sha256).digest()
    return payload, signature

def safe_pickle_loads(payload: bytes, signature: bytes, secret: bytes) -> object:
    expected = hmac.new(secret, payload, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected):
        raise ValueError("Neplatný podpis — data byla pozměněna!")
    return pickle.loads(payload)
```

---

## A10 — SSRF (Server-Side Request Forgery)

Útočník přiměje server, aby volal interní služby.

```python
import ipaddress
import re
from urllib.parse import urlparse

ALLOWED_SCHEMES = frozenset({"https"})
BLOCKED_HOSTS = frozenset({
    "localhost", "127.0.0.1", "0.0.0.0",
    "169.254.169.254",  # AWS metadata endpoint!
    "metadata.google.internal",  # GCP metadata
})
BLOCKED_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
]


def validate_url_for_fetch(url: str) -> str:
    """
    Validuje URL před HTTP požadavkem — prevence SSRF.
    Vyvolá ValueError pro nebezpečné URL.
    """
    parsed = urlparse(url)

    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"Nepovolen protokol: {parsed.scheme!r} (povoleno: https)")

    host = parsed.hostname or ""
    if not host:
        raise ValueError("URL musí mít hostname")

    if host.lower() in BLOCKED_HOSTS:
        raise ValueError(f"Blokovaný hostname: {host!r}")

    # Ověř IP adresy
    try:
        addr = ipaddress.ip_address(host)
        for network in BLOCKED_NETWORKS:
            if addr in network:
                raise ValueError(f"Blokovaná IP síť: {addr} je v {network}")
    except ValueError as e:
        if "Blokovaná" in str(e):
            raise
        # Hostname (ne IP) — DNS resolution by se měla provést a zkontrolovat také
        pass

    return url
```

---

## A02 — Kryptografické selhání

```python
import hashlib
import hmac
import os
import secrets

# ŠPATNĚ — MD5/SHA1 pro hesla!
def bad_hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()  # crack za sekundy!

# SPRÁVNĚ — bcrypt/argon2 nebo alespoň PBKDF2 (stdlib)
def hash_password(password: str) -> str:
    """Bezpečné hashování hesla pomocí PBKDF2-HMAC-SHA256."""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations=600_000,  # OWASP doporučení 2023
        dklen=32,
    )
    return salt.hex() + ":" + key.hex()


def verify_password(password: str, stored: str) -> bool:
    salt_hex, key_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    key = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 600_000, 32
    )
    return hmac.compare_digest(key.hex(), key_hex)


# Bezpečné generování tokenů
def generate_token(n_bytes: int = 32) -> str:
    return secrets.token_urlsafe(n_bytes)


def generate_otp(length: int = 6) -> str:
    return "".join(str(secrets.randbelow(10)) for _ in range(length))
```

---

## A01 — Broken Access Control

```python
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Callable


class Role(Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"


@dataclass
class User:
    id: str
    username: str
    role: Role


def require_role(*roles: Role):
    """Dekorátor pro kontrolu oprávnění (RBAC)."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(user: User, *args, **kwargs):
            if user.role not in roles:
                raise PermissionError(
                    f"Uživatel {user.username!r} ({user.role.value}) "
                    f"nemá oprávnění pro {func.__name__!r}"
                )
            return func(user, *args, **kwargs)
        return wrapper
    return decorator


@require_role(Role.ADMIN)
def delete_user(current_user: User, target_user_id: str) -> None:
    print(f"Admin {current_user.username} smazal uživatele {target_user_id}")


@require_role(Role.ADMIN, Role.USER)
def update_profile(current_user: User, target_user_id: str, data: dict) -> None:
    # Kontrola ownership — uživatel může měnit jen svůj profil!
    if current_user.role != Role.ADMIN and current_user.id != target_user_id:
        raise PermissionError("Nelze měnit cizí profil")
    print(f"Profil {target_user_id} aktualizován")
```

---

## Bandit — statická analýza bezpečnosti

```bash
# Instalace
pip install bandit

# Kontrola projektu
bandit -r src/ -ll -ii

# Výstup:
# >> Issue: [B608:hardcoded_sql_expressions] Possible SQL injection
#    Severity: Medium   Confidence: Medium
#    Location: src/db.py:45

# Konfigurace v pyproject.toml
[tool.bandit]
exclude_dirs = ["tests"]
skips = ["B101"]  # B101 = assert použití v testech je OK
```

---

## A05 — Security Misconfiguration

```python
import os
import sys

def production_security_check() -> list[str]:
    """Zkontroluje základní bezpečnostní konfiguraci."""
    issues: list[str] = []

    if os.environ.get("DEBUG", "false").lower() == "true":
        env = os.environ.get("APP_ENV", "production")
        if env == "production":
            issues.append("KRITICKÉ: DEBUG=true v produkci!")

    secret = os.environ.get("SECRET_KEY", "")
    if len(secret) < 32:
        issues.append(f"SECRET_KEY je příliš krátký ({len(secret)} znaků)")
    if secret in ("secret", "changeme", "development", "insecure"):
        issues.append("SECRET_KEY má výchozí/nebezpečnou hodnotu!")

    allowed_hosts = os.environ.get("ALLOWED_HOSTS", "")
    if "*" in allowed_hosts:
        issues.append("ALLOWED_HOSTS obsahuje wildcard '*' — nebezpečné v produkci")

    return issues
```

---

## Shrnutí

| Zranitelnost | Prevence v Pythonu |
|-------------|-------------------|
| SQL Injection | Parametrizované dotazy (`?`), ORM |
| XSS | Jinja2 auto-escape, `markupsafe.escape()` |
| Pickle/Deserializace | JSON místo pickle, HMAC podpis |
| SSRF | URL validace, whitelist, blocked networks |
| Slabá kryptografie | `hashlib.pbkdf2_hmac`, `secrets`, bcrypt |
| Broken Access Control | RBAC dekorátor, ownership check |
| Secret exposure | `os.environ`, nikdy v kódu |
| Závislosti | `pip-audit`, Dependabot |

---

## Cvičení

1. Napište test, který ověří, že `get_user_safe()` odolá SQL injection — zkuste vstupy: `"'; DROP TABLE users; --"`, `"admin' OR '1'='1"`, `"admin\x00"`.
2. Implementujte `SecureToken` třídu, která generuje HMAC-podepsané tokeny s expirací (timestamp v payload) a ověřuje je.
3. Rozšiřte `validate_url_for_fetch()` o DNS resolution — po překladu hostname na IP adresu ověřte, zda výsledná IP není v blokovaných sítích.
4. Napište pre-commit hook, který spouští `bandit` na změněné Python soubory a selže pokud najde issue se severity HIGH nebo CRITICAL.
