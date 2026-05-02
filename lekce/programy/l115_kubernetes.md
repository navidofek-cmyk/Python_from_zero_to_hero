# Program — Lekce 115: Lekce 115 — Kubernetes pro Pythonistu

Patří k lekci [Lekce 115 — Kubernetes pro Pythonistu](../115_kubernetes.md).

## Jak spustit

```bash
python3 programy/l115_kubernetes.py
```

## Zdrojový kód

### `l115_kubernetes.py`

```py
"""Lekce 115 — Kubernetes: health/readiness probes, graceful shutdown."""
from __future__ import annotations

import contextlib
import http.server
import json
import os
import signal
import sys
import threading
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Any, Generator, NamedTuple


# ── Graceful shutdown manažer ─────────────────────────────────────────────────

class GracefulShutdown:
    """
    Správce graceful shutdown pro K8s produkci.

    Kubernetes posílá SIGTERM a čeká terminationGracePeriodSeconds.
    Aplikace musí dokončit aktivní požadavky a teprve pak skončit.
    """

    def __init__(self, grace_period_seconds: int = 25) -> None:
        self._shutdown_event = threading.Event()
        self._grace_period = grace_period_seconds
        self._active_count = 0
        self._lock = threading.Lock()
        self._request_finished = threading.Condition(self._lock)
        self._logger = _make_logger("lifecycle")

    def install_handlers(self) -> None:
        """Zaregistruje SIGTERM a SIGINT handlery."""
        signal.signal(signal.SIGTERM, self._on_signal)
        signal.signal(signal.SIGINT, self._on_signal)
        self._logger("INFO", "Signal handlery nainstalovány (SIGTERM, SIGINT)")

    def _on_signal(self, signum: int, frame: object) -> None:
        sig_name = signal.Signals(signum).name
        self._logger("INFO", f"Přijat {sig_name} — zahajuji graceful shutdown (grace={self._grace_period}s)")
        self._shutdown_event.set()

    def wait_for_completion(self) -> None:
        """Čeká na dokončení všech aktivních požadavků nebo na vypršení grace period."""
        deadline = time.monotonic() + self._grace_period
        while time.monotonic() < deadline:
            with self._lock:
                if self._active_count == 0:
                    self._logger("INFO", "Všechny požadavky dokončeny — čistý shutdown")
                    return
                remaining = self._active_count
            self._logger("INFO", f"Čekám na {remaining} aktivní požadavek/ů...")
            time.sleep(0.5)
        self._logger("WARNING", f"Grace period {self._grace_period}s vypršela — vynucený shutdown")

    @property
    def is_shutting_down(self) -> bool:
        return self._shutdown_event.is_set()

    @contextlib.contextmanager
    def track_request(self) -> Generator[None, None, None]:
        """Context manager evidující aktivní požadavky."""
        with self._lock:
            self._active_count += 1
        try:
            yield
        finally:
            with self._request_finished:
                self._active_count -= 1
                self._request_finished.notify_all()

    @property
    def active_requests(self) -> int:
        with self._lock:
            return self._active_count


# ── Stav aplikace ─────────────────────────────────────────────────────────────

@dataclass
class AppState:
    """Centrální stav aplikace pro probe endpointy."""
    start_time: float = field(default_factory=time.time)
    ready: threading.Event = field(default_factory=threading.Event)
    shutdown: GracefulShutdown = field(default_factory=GracefulShutdown)
    version: str = field(default_factory=lambda: os.environ.get("APP_VERSION", "dev"))
    _checks: dict[str, bool] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def set_check(self, name: str, ok: bool) -> None:
        with self._lock:
            self._checks[name] = ok

    def all_checks_ok(self) -> bool:
        with self._lock:
            return all(self._checks.values()) and bool(self._checks)

    @property
    def uptime(self) -> float:
        return time.time() - self.start_time


# ── Probe handlery ────────────────────────────────────────────────────────────

def liveness_response(state: AppState) -> tuple[int, dict[str, Any]]:
    """
    /health — Liveness probe.
    K8s restartuje pod pokud vrátí 5xx.
    Kontroluj pouze fatální stav (deadlock, OOM, corrupt state).
    NEkontroluj dostupnost externích závislostí!
    """
    if state.shutdown.is_shutting_down:
        return 503, {
            "status": "shutting_down",
            "uptime": round(state.uptime, 1),
        }
    return 200, {
        "status": "alive",
        "version": state.version,
        "uptime": round(state.uptime, 1),
        "active_requests": state.shutdown.active_requests,
    }


def readiness_response(state: AppState) -> tuple[int, dict[str, Any]]:
    """
    /ready — Readiness probe.
    K8s odebere pod ze Service pokud vrátí 5xx (žádné nové požadavky).
    Kontroluj: inicializace dokončena, DB dostupná, cache dostupná.
    """
    if not state.ready.is_set():
        return 503, {"ready": False, "reason": "initialization_in_progress"}

    if state.shutdown.is_shutting_down:
        return 503, {"ready": False, "reason": "shutting_down"}

    if not state.all_checks_ok():
        return 503, {"ready": False, "reason": "dependency_check_failed"}

    return 200, {
        "ready": True,
        "uptime": round(state.uptime, 1),
        "version": state.version,
    }


def startup_response(state: AppState) -> tuple[int, dict[str, Any]]:
    """
    /startup — Startup probe.
    Používá se pro aplikace s dlouhým startem (ML modely, warmup).
    Dokud vrací 5xx, liveness/readiness proby se nevyhodnocují.
    """
    if state.ready.is_set():
        return 200, {"started": True}
    return 503, {"started": False, "uptime": round(state.uptime, 1)}


# ── Simulace inicializace aplikace ────────────────────────────────────────────

def simulate_initialization(state: AppState, logger: Any) -> None:
    """Simuluje pomalou inicializaci (K8s startup probe případ)."""
    steps = [
        ("Připojuji k databázi", "database", 0.15),
        ("Načítám konfiguraci", None, 0.05),
        ("Připojuji k Redis cache", "redis", 0.08),
        ("Inicializuji connection pool", None, 0.05),
        ("Zahřívám cache (warmup)", None, 0.1),
        ("Aplikace připravena", None, 0.02),
    ]
    for step_name, check_name, delay in steps:
        time.sleep(delay)
        if check_name:
            state.set_check(check_name, True)
        elapsed = state.uptime
        logger("INFO", f"[{elapsed:.2f}s] {step_name}")

    state.ready.set()
    logger("INFO", "Readiness probe: OK — pod zařazen do Service")


# ── HTTP server pro demo ───────────────────────────────────────────────────────

def make_handler(state: AppState):  # noqa: ANN201
    """Vytvoří HTTP handler s closure na stav aplikace."""

    class K8sProbeHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health":
                status, body = liveness_response(state)
            elif self.path == "/ready":
                status, body = readiness_response(state)
            elif self.path == "/startup":
                status, body = startup_response(state)
            elif self.path.startswith("/api/"):
                # Simulace aplikačního endpointu
                if state.shutdown.is_shutting_down:
                    status, body = 503, {"error": "Aplikace se vypíná"}
                else:
                    with state.shutdown.track_request():
                        time.sleep(0.05)  # simulace zpracování
                    status, body = 200, {"result": "ok", "path": self.path}
            else:
                status, body = 404, {"error": "Not Found"}

            encoded = json.dumps(body, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, fmt: str, *args: Any) -> None:
            pass  # Ticho v demo

    return K8sProbeHandler


# ── Jednoduchý logger (bez závislostí) ────────────────────────────────────────

def _make_logger(name: str):  # noqa: ANN201
    def log(level: str, msg: str) -> None:
        ts = time.strftime("%H:%M:%S")
        print(f"  [{ts}] {level:7s} [{name}] {msg}")
    return log


# ── Simulace K8s rolling update ───────────────────────────────────────────────

class PodSimulator:
    """Simuluje životní cyklus K8s podu."""

    def __init__(self, pod_name: str) -> None:
        self.pod_name = pod_name
        self.state = "Pending"
        self.restart_count = 0
        self._start_time = time.time()

    def transition(self, new_state: str) -> None:
        old = self.state
        self.state = new_state
        elapsed = time.time() - self._start_time
        print(f"  [{elapsed:.1f}s] {self.pod_name}: {old} → {new_state}")

    def simulate_lifecycle(self) -> None:
        """Simuluje normální životní cyklus podu."""
        stages = [
            ("ContainerCreating", 0.1),
            ("Running (startup)", 0.3),
            ("Running (ready)", 0.1),
        ]
        for stage, delay in stages:
            time.sleep(delay)
            self.transition(stage)

    def simulate_rolling_update(self, old_version: str, new_version: str) -> None:
        """Simuluje rolling update — zero-downtime."""
        print(f"  Spouštím nový pod ({new_version})...")
        time.sleep(0.2)
        self.transition(f"Running ({new_version})")
        print(f"  Readiness OK — odebírám starý pod ({old_version})")
        time.sleep(0.1)


# ── Hlavní funkce ─────────────────────────────────────────────────────────────

def main() -> None:
    logger = _make_logger("main")

    print("=" * 65)
    print("KUBERNETES PRO PYTHONISTU — DEMO")
    print("=" * 65)

    os.environ.setdefault("APP_VERSION", "1.5.3")

    # --- 1. Inicializace stavu a graceful shutdown ---
    print("\n[1] Inicializace aplikace a graceful shutdown manažeru:")
    state = AppState()
    state.shutdown.install_handlers()
    logger("INFO", f"Aplikace startuje, verze {state.version}")

    # --- 2. Simulace startu (startup probe) ---
    print("\n[2] Simulace inicializace (startup probe):")
    init_thread = threading.Thread(
        target=simulate_initialization,
        args=(state, logger),
        daemon=True,
    )
    init_thread.start()
    init_thread.join()

    # --- 3. Probe výstupy ---
    print("\n[3] Stav probe endpointů po inicializaci:")
    status, body = liveness_response(state)
    print(f"  /health  → HTTP {status}: {json.dumps(body)}")
    status, body = readiness_response(state)
    print(f"  /ready   → HTTP {status}: {json.dumps(body)}")
    status, body = startup_response(state)
    print(f"  /startup → HTTP {status}: {json.dumps(body)}")

    # --- 4. Spuštění HTTP serveru ---
    print("\n[4] Spouštím HTTP server s K8s probe endpointy...")
    handler_class = make_handler(state)
    server = http.server.HTTPServer(("127.0.0.1", 0), handler_class)
    port = server.server_address[1]
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    logger("INFO", f"Server naslouchá na portu {port}")

    # Simulace probe volání
    print("\n[5] Simulace K8s probe volání:")
    for endpoint, probe_name in [
        ("/health", "livenessProbe"),
        ("/ready", "readinessProbe"),
        ("/startup", "startupProbe"),
        ("/api/users", "aplikační endpoint"),
    ]:
        url = f"http://127.0.0.1:{port}{endpoint}"
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                body_data = json.loads(resp.read().decode())
                print(f"  {probe_name:20s}: GET {endpoint:10s} → {resp.status} {json.dumps(body_data)[:60]}")
        except urllib.error.HTTPError as e:
            body_data = json.loads(e.read().decode())
            print(f"  {probe_name:20s}: GET {endpoint:10s} → {e.code} {json.dumps(body_data)[:60]}")

    # --- 6. Simulace graceful shutdown ---
    print("\n[6] Simulace graceful shutdown (SIGTERM):")

    # Spuštění "dlouhého" požadavku
    request_done = threading.Event()

    def long_request() -> None:
        logger("INFO", "Začínám dlouhý požadavek (0.4s)...")
        with state.shutdown.track_request():
            time.sleep(0.4)
        logger("INFO", "Dlouhý požadavek dokončen")
        request_done.set()

    req_thread = threading.Thread(target=long_request, daemon=True)
    req_thread.start()
    time.sleep(0.05)  # Počkej než se požadavek rozběhne

    logger("INFO", f"Aktivní požadavky: {state.shutdown.active_requests}")

    # Simulace SIGTERM (nastavíme příznak přímo)
    state.shutdown._shutdown_event.set()
    logger("INFO", "SIGTERM přijat — zahajuji graceful shutdown")

    # Readiness probe by nyní vrátila 503
    status, body = readiness_response(state)
    logger("INFO", f"Readiness po SIGTERM: HTTP {status} — pod odebrán ze Service")

    # Čekání na dokončení
    state.shutdown.wait_for_completion()
    request_done.wait(timeout=2)
    logger("INFO", "Graceful shutdown dokončen")

    server.shutdown()

    # --- 7. Simulace rolling update ---
    print("\n[7] Simulace K8s rolling update (zero-downtime):")
    print("  Aktualizace z v1.5.3 na v1.5.4:")
    pod_new = PodSimulator("python-app-xyz-new")
    pod_new.simulate_rolling_update("v1.5.3", "v1.5.4")

    # --- 8. K8s YAML ukázky ---
    print("\n[8] Klíčové K8s konfigurace pro Python aplikaci:")
    yaml_snippets = [
        ("Liveness probe", "httpGet: /health — restart podu při selhání"),
        ("Readiness probe", "httpGet: /ready — odebrání ze Service při selhání"),
        ("Startup probe", "httpGet: /health — pro pomalé starty (ML modely)"),
        ("Resources", "requests: 100m CPU, 128Mi RAM | limits: 500m, 512Mi"),
        ("SIGTERM handler", "terminationGracePeriodSeconds: 30"),
        ("Secret", "valueFrom.secretKeyRef → os.environ['SECRET_KEY']"),
        ("ConfigMap", "envFrom.configMapRef → os.environ bulk"),
        ("HPA", "minReplicas: 2, maxReplicas: 20, CPU target: 70%"),
        ("PDB", "minAvailable: 2 — HA při aktualizacích"),
        ("Security context", "runAsNonRoot: true, readOnlyRootFilesystem: true"),
    ]
    for name, desc in yaml_snippets:
        print(f"  {name:22s}: {desc}")

    print("\n[9] Shrnutí — co Python aplikace potřebuje pro K8s:")
    print("  1. /health   — liveness probe (jsem naživu?)")
    print("  2. /ready    — readiness probe (mohu přijímat provoz?)")
    print("  3. SIGTERM   — graceful shutdown (dokončím aktivní požadavky)")
    print("  4. Env vars  — veškerá konfigurace z prostředí")
    print("  5. Stateless — žádný stav v paměti procesu")
    print("  6. Stdout    — logy na stdout (ne soubory)")
    print("  7. Non-root  — neprivilegovaný uživatel")


if __name__ == "__main__":
    main()

```
