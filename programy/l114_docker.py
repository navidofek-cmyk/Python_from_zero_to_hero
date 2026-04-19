"""Lekce 114 — Containerizace: config z env v kontejneru, health check pattern."""
from __future__ import annotations

import http.server
import json
import os
import socket
import sys
import textwrap
import threading
import time
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any
from urllib.parse import urlparse

# ── Načítání konfigurace z prostředí (kontejnerový vzor) ─────────────────────

def require_env(name: str, description: str = "") -> str:
    """
    Načte povinnou proměnnou prostředí.
    Kontejner by se neměl spustit bez kritické konfigurace — fail fast.
    """
    value = os.environ.get(name, "").strip()
    if not value:
        hint = f" ({description})" if description else ""
        print(
            f"FATAL: Proměnná prostředí '{name}' není nastavena{hint}",
            file=sys.stderr,
        )
        sys.exit(1)
    return value


@dataclass(frozen=True)
class ContainerConfig:
    """Konfigurace aplikace běžící v kontejneru."""
    app_name: str
    port: int
    debug: bool
    database_url: str
    secret_key: str
    app_version: str
    app_env: str

    @classmethod
    def from_env(cls) -> ContainerConfig:
        return cls(
            app_name=os.environ.get("APP_NAME", "PythonApp"),
            port=int(os.environ.get("PORT", "8000")),
            debug=os.environ.get("DEBUG", "false").lower() in ("true", "1"),
            database_url=require_env("DATABASE_URL", "URL databáze"),
            secret_key=require_env("SECRET_KEY", "Tajný klíč aplikace"),
            app_version=os.environ.get("APP_VERSION", "0.0.0-dev"),
            app_env=os.environ.get("APP_ENV", "production"),
        )

    def __repr__(self) -> str:
        # Nikdy nevypisuj secret_key v plaintext
        sk_masked = self.secret_key[:3] + "***" if len(self.secret_key) > 3 else "***"
        return (
            f"ContainerConfig(app={self.app_name!r}, env={self.app_env!r}, "
            f"port={self.port}, version={self.app_version!r}, "
            f"secret_key={sk_masked!r})"
        )


# ── Health check handler ──────────────────────────────────────────────────────

_APP_START_TIME = time.time()
_ready = threading.Event()  # Signál, že aplikace je připravena


@dataclass
class HealthStatus:
    service: str
    ok: bool
    latency_ms: float
    message: str = ""


def check_database(db_url: str) -> HealthStatus:
    """Simuluje DB health check — v reálné aplikaci: db.execute('SELECT 1')."""
    start = time.perf_counter()
    try:
        parsed = urlparse(db_url)
        # Simulace: ověřím, že URL je parsovatelná
        if not parsed.hostname:
            raise ValueError("Neplatná URL databáze")
        latency = (time.perf_counter() - start) * 1000
        return HealthStatus("database", True, round(latency, 2))
    except Exception as e:
        return HealthStatus("database", False, 0.0, str(e))


def check_disk_space() -> HealthStatus:
    """Zkontroluje dostupné místo na disku."""
    start = time.perf_counter()
    try:
        import shutil
        usage = shutil.disk_usage("/")
        free_pct = usage.free / usage.total * 100
        latency = (time.perf_counter() - start) * 1000
        ok = free_pct > 10  # Varuj pod 10%
        msg = f"{free_pct:.1f}% volné ({usage.free // 1_000_000} MB)"
        return HealthStatus("disk", ok, round(latency, 2), msg)
    except Exception as e:
        return HealthStatus("disk", False, 0.0, str(e))


def health_response(config: ContainerConfig) -> dict[str, Any]:
    """Sestaví /health JSON odpověď."""
    checks = [
        check_database(config.database_url),
        check_disk_space(),
    ]
    all_ok = all(c.ok for c in checks)
    return {
        "status": "healthy" if all_ok else "unhealthy",
        "version": config.app_version,
        "environment": config.app_env,
        "uptime_seconds": round(time.time() - _APP_START_TIME, 1),
        "checks": {
            c.service: {
                "status": "ok" if c.ok else "error",
                "latency_ms": c.latency_ms,
                **({"message": c.message} if c.message else {}),
            }
            for c in checks
        },
    }


def readiness_response() -> dict[str, Any]:
    """
    /ready — odpověď pro Kubernetes readiness probe.
    Vrátí 200 pouze pokud je aplikace připravena přijímat provoz.
    """
    ready = _ready.is_set()
    return {
        "ready": ready,
        "uptime_seconds": round(time.time() - _APP_START_TIME, 1),
    }


# ── Jednoduchý HTTP server pro demo ──────────────────────────────────────────

class DemoHandler(http.server.BaseHTTPRequestHandler):
    """Minimalistický HTTP handler pro demonstraci health check endpointů."""

    config: ContainerConfig  # nastaveno před startem

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            data = health_response(self.config)
            status = HTTPStatus.OK if data["status"] == "healthy" else HTTPStatus.SERVICE_UNAVAILABLE
        elif self.path == "/ready":
            data = readiness_response()
            status = HTTPStatus.OK if data["ready"] else HTTPStatus.SERVICE_UNAVAILABLE
        elif self.path == "/":
            data = {
                "app": self.config.app_name,
                "version": self.config.app_version,
                "env": self.config.app_env,
            }
            status = HTTPStatus.OK
        else:
            data = {"error": "Not Found"}
            status = HTTPStatus.NOT_FOUND

        body = json.dumps(data, ensure_ascii=False, indent=2).encode()
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: Any) -> None:  # Ticho v demo
        pass


# ── Dockerfile analýza a doporučení ──────────────────────────────────────────

def analyze_dockerfile(content: str) -> list[str]:
    """Analyzuje Dockerfile a vrátí seznam doporučení."""
    issues: list[str] = []
    lines = content.splitlines()

    has_user = any(l.strip().upper().startswith("USER") and "root" not in l.lower()
                   for l in lines)
    has_healthcheck = any(l.strip().upper().startswith("HEALTHCHECK") for l in lines)
    has_multi_stage = content.count("FROM ") > 1
    has_pythonunbuffered = "PYTHONUNBUFFERED" in content
    has_no_cache = "--no-cache-dir" in content or "type=cache" in content
    copies_all_first = False
    for i, line in enumerate(lines):
        if "COPY . ." in line or "COPY ./ ./" in line:
            # Špatné pokud je před instalací závislostí
            for prev in lines[:i]:
                if "pip install" in prev.lower():
                    break
            else:
                copies_all_first = True

    if not has_multi_stage:
        issues.append("Zvažte multi-stage build — runtime obraz nemusí obsahovat build nástroje")
    if not has_user:
        issues.append("Přidejte neprivilegovaného uživatele (USER appuser) — neběžte jako root")
    if not has_healthcheck:
        issues.append("Přidejte HEALTHCHECK — orchestrátor potřebuje vědět, kdy je app ready")
    if not has_pythonunbuffered:
        issues.append("Nastavte ENV PYTHONUNBUFFERED=1 pro okamžité flush logů")
    if not has_no_cache:
        issues.append("Použijte --no-cache-dir nebo BuildKit cache mount pro pip")
    if copies_all_first:
        issues.append("Kopírujte pyproject.toml/requirements.txt PŘED kódem — lepší cache")

    return issues


# ── Vygenerování ukázkového Dockerfile ────────────────────────────────────────

EXAMPLE_DOCKERFILE = """\
# Stage 1: Builder
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src/ ./src/
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.12-slim AS runtime
RUN groupadd --gid 1001 appgroup \\
    && useradd --uid 1001 --gid appgroup --no-create-home appuser
WORKDIR /app
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appgroup /app/src /app/src
ENV PATH="/app/.venv/bin:$PATH" \\
    PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PORT=8000
USER appuser
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
"""

BAD_DOCKERFILE = """\
FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
"""


# ── Simulace kontejnerového startu ────────────────────────────────────────────

def simulate_container_startup(config: ContainerConfig) -> None:
    """Simuluje fáze startu kontejneru."""
    phases = [
        ("Konfigurace načtena z prostředí", 0.05),
        ("Připojování k databázi", 0.1),
        ("Inicializace cache (Redis)", 0.05),
        ("Migrace databáze zkontrolovány", 0.08),
        ("HTTP server startuje", 0.05),
        ("Aplikace připravena (readiness probe: OK)", 0.02),
    ]
    for phase, delay in phases:
        time.sleep(delay)
        elapsed = time.time() - _APP_START_TIME
        print(f"  [{elapsed:5.2f}s] {phase}")
    _ready.set()


# ── Hlavní funkce ─────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 65)
    print("CONTAINERIZACE PYTHON APLIKACÍ — DEMO")
    print("=" * 65)

    # Nastav testovací prostředí
    os.environ.update({
        "APP_NAME": "DemoApp",
        "APP_ENV": "development",
        "PORT": "0",  # 0 = OS přidělí volný port
        "DEBUG": "true",
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/demo",
        "SECRET_KEY": "demo-tajny-klic-pro-kontejner-32-znaku",
        "APP_VERSION": "2.1.0",
    })

    # --- 1. Načtení konfigurace ---
    print("\n[1] Načtení konfigurace z prostředí:")
    config = ContainerConfig.from_env()
    print(f"  {config}")

    # --- 2. Analýza Dockerfile ---
    print("\n[2] Analýza špatného Dockerfile:")
    issues = analyze_dockerfile(BAD_DOCKERFILE)
    for issue in issues:
        print(f"  ✗ {issue}")

    print("\n[3] Analýza správného Dockerfile (multi-stage):")
    issues_good = analyze_dockerfile(EXAMPLE_DOCKERFILE)
    if issues_good:
        for issue in issues_good:
            print(f"  ? {issue}")
    else:
        print("  Dockerfile splňuje všechna doporučení!")

    print("\n[4] Ukázkový produkční Dockerfile:")
    for line in EXAMPLE_DOCKERFILE.splitlines():
        print(f"  {line}")

    # --- 5. Simulace startu kontejneru ---
    print("\n[5] Simulace startu kontejneru:")
    startup_thread = threading.Thread(
        target=simulate_container_startup, args=(config,), daemon=True
    )
    startup_thread.start()
    startup_thread.join()

    # --- 6. Health check výstup ---
    print("\n[6] Health check odpověď (/health):")
    health_data = health_response(config)
    print(json.dumps(health_data, indent=2, ensure_ascii=False))

    print("\n[7] Readiness probe odpověď (/ready):")
    ready_data = readiness_response()
    print(json.dumps(ready_data, indent=2, ensure_ascii=False))

    # --- 8. Spuštění demo HTTP serveru ---
    print("\n[8] Spouštím demo HTTP server na náhodném portu...")

    DemoHandler.config = config  # type: ignore[attr-defined]
    server = http.server.HTTPServer(("127.0.0.1", 0), DemoHandler)
    actual_port = server.server_address[1]
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    import urllib.request

    endpoints = ["/", "/health", "/ready", "/neexistuje"]
    for endpoint in endpoints:
        url = f"http://127.0.0.1:{actual_port}{endpoint}"
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                body = json.loads(resp.read().decode())
                print(f"  GET {endpoint:15s} → {resp.status} {json.dumps(body)[:70]}")
        except urllib.error.HTTPError as e:
            body = json.loads(e.read().decode())
            print(f"  GET {endpoint:15s} → {e.code} {json.dumps(body)[:70]}")

    server.shutdown()

    # --- 9. Klíčové ENV proměnné v kontejneru ---
    print("\n[9] Klíčové proměnné prostředí v kontejneru:")
    container_env = [
        ("PYTHONUNBUFFERED", "1", "Okamžité flushovani logů na stdout"),
        ("PYTHONDONTWRITEBYTECODE", "1", "Žádné .pyc soubory v kontejneru"),
        ("PORT", "8000", "Port aplikace — konfigurovatelný"),
        ("APP_ENV", "production", "Prostředí (development/staging/production)"),
        ("APP_VERSION", "1.0.0", "Verze — nastavena při buildu"),
    ]
    for var, example, desc in container_env:
        print(f"  {var:30s} = {example!r:12s}  # {desc}")

    print("\n[10] Shrnutí best practices:")
    tips = [
        "Multi-stage build: builder + runtime (malý výsledný obraz)",
        "Kopíruj deps před kódem (lepší Docker layer cache)",
        "Neprivilegovaný uživatel (USER appuser, ne root)",
        "HEALTHCHECK pro orchestrátor (K8s, Swarm)",
        "PYTHONUNBUFFERED=1 pro okamžité logy",
        "Vše z ENV — žádná hardkódovaná konfigurace",
        ".dockerignore: vyloučit .git, .venv, *.pyc, .env",
    ]
    for tip in tips:
        print(f"  • {tip}")


if __name__ == "__main__":
    main()
