# Program — Lekce 116: Lekce 116 — CI/CD pipeline pro Python projekty

Patří k lekci [Lekce 116 — CI/CD pipeline pro Python projekty](../116_cicd.md).

## Jak spustit

```bash
python3 programy/l116_cicd.py
```

## Zdrojový kód

### `l116_cicd.py`

```py
"""Lekce 116 — CI/CD: matrix build skript, pip-audit simulace, dependency check."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, NamedTuple


# ── Datové typy ───────────────────────────────────────────────────────────────

@dataclass
class PythonVersion:
    major: int
    minor: int
    patch: int = 0

    @classmethod
    def from_string(cls, s: str) -> PythonVersion:
        parts = s.lstrip("v").split(".")
        return cls(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def short(self) -> str:
        return f"{self.major}.{self.minor}"


@dataclass
class Vulnerability:
    package: str
    installed_version: str
    vulnerability_id: str
    description: str
    cvss_score: float
    fix_version: str | None = None

    @property
    def severity(self) -> str:
        if self.cvss_score >= 9.0:
            return "CRITICAL"
        if self.cvss_score >= 7.0:
            return "HIGH"
        if self.cvss_score >= 4.0:
            return "MEDIUM"
        return "LOW"


class CheckResult(NamedTuple):
    name: str
    passed: bool
    message: str
    details: list[str] = []


# ── Matrix build simulace ─────────────────────────────────────────────────────

@dataclass
class MatrixBuildJob:
    """Reprezentuje jeden job v CI matrix buildu."""
    python_version: str
    os: str
    status: str = "pending"
    duration_s: float = 0.0
    steps: list[tuple[str, str, float]] = field(default_factory=list)

    def simulate_run(self) -> bool:
        """Simuluje CI run pro danou kombinaci."""
        import random
        rng = random.Random(hash(f"{self.python_version}-{self.os}"))

        steps_config = [
            ("Checkout kódu", 0.02, 0.99),
            ("Instalace uv", 0.05, 0.99),
            (f"Setup Python {self.python_version}", 0.1, 0.98),
            ("Instalace závislostí (uv sync)", 0.15, 0.97),
            ("Linting (ruff check)", 0.08, 0.95),
            ("Formátování (ruff format --check)", 0.05, 0.96),
            ("Type checking (mypy)", 0.2, 0.90),
            ("Testy (pytest)", 0.3, 0.92),
            ("Coverage report", 0.05, 0.99),
        ]

        all_passed = True
        for step_name, duration, success_prob in steps_config:
            time.sleep(duration * 0.1)  # Zrychlená simulace
            passed = rng.random() < success_prob
            step_status = "PASS" if passed else "FAIL"
            self.steps.append((step_name, step_status, duration))
            self.duration_s += duration
            if not passed:
                all_passed = False
                break

        self.status = "success" if all_passed else "failure"
        return all_passed


def run_matrix_build(
    python_versions: list[str],
    operating_systems: list[str],
    parallel: bool = True,
) -> list[MatrixBuildJob]:
    """Spustí simulaci matrix buildu pro všechny kombinace."""
    import threading

    jobs = [
        MatrixBuildJob(pv, os_name)
        for os_name in operating_systems
        for pv in python_versions
    ]

    if parallel:
        threads = [
            threading.Thread(target=job.simulate_run)
            for job in jobs
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    else:
        for job in jobs:
            job.simulate_run()

    return jobs


# ── Pip-audit simulace ────────────────────────────────────────────────────────

# Simulovaná databáze vulnerabilit
VULN_DATABASE: list[Vulnerability] = [
    Vulnerability(
        package="requests",
        installed_version="2.28.0",
        vulnerability_id="CVE-2023-32681",
        description="Requests forwards proxy-authorization headers to destination",
        cvss_score=6.1,
        fix_version="2.31.0",
    ),
    Vulnerability(
        package="cryptography",
        installed_version="39.0.0",
        vulnerability_id="CVE-2023-38325",
        description="Bleichenbacher timing oracle in RSA PKCS#1 v1.5",
        cvss_score=7.5,
        fix_version="41.0.2",
    ),
    Vulnerability(
        package="pillow",
        installed_version="9.5.0",
        vulnerability_id="CVE-2023-44271",
        description="Uncontrolled resource consumption in PIL.ImageFont",
        cvss_score=7.5,
        fix_version="10.0.1",
    ),
    Vulnerability(
        package="urllib3",
        installed_version="1.26.14",
        vulnerability_id="CVE-2023-45803",
        description="Request body not stripped after redirect for PUT/PATCH methods",
        cvss_score=4.2,
        fix_version="2.0.7",
    ),
]


def simulate_pip_audit(
    requirements: list[tuple[str, str]],
    fail_on_cvss: float = 7.0,
) -> tuple[list[Vulnerability], bool]:
    """
    Simuluje pip-audit výsledky pro seznam požadavků.
    Vrátí (nalezené vulnerabilty, prošlo?).
    """
    installed = {pkg: ver for pkg, ver in requirements}
    found: list[Vulnerability] = []

    for vuln in VULN_DATABASE:
        if vuln.package in installed:
            installed_ver = installed[vuln.package]
            # Simulace: pokud je verze <= vulnerable verze
            if installed_ver == vuln.installed_version:
                found.append(vuln)

    critical = [v for v in found if v.cvss_score >= fail_on_cvss]
    passed = len(critical) == 0
    return found, passed


# ── Dependency check ──────────────────────────────────────────────────────────

def check_pyproject_toml(pyproject_content: str) -> list[CheckResult]:
    """Zkontroluje pyproject.toml na povinné sekce a metadata."""
    results: list[CheckResult] = []

    # Kontrola povinných sekcí
    required_sections = [
        ("[project]", "Povinná sekce [project]"),
        ("name =", "Pole 'name' v [project]"),
        ("version =", "Pole 'version' v [project]"),
        ("requires-python", "Pole 'requires-python' v [project]"),
        ("[tool.ruff]", "Konfigurace [tool.ruff]"),
        ("[tool.mypy]", "Konfigurace [tool.mypy]"),
    ]

    for pattern, description in required_sections:
        found = pattern in pyproject_content
        results.append(CheckResult(
            name=description,
            passed=found,
            message="nalezeno" if found else "CHYBÍ",
        ))

    # Kontrola verze Python (>= 3.10)
    import re
    python_req = re.search(r'requires-python\s*=\s*"([^"]+)"', pyproject_content)
    if python_req:
        req_str = python_req.group(1)
        has_minimum = ">=" in req_str
        results.append(CheckResult(
            name="requires-python má dolní mez (>=)",
            passed=has_minimum,
            message=f"hodnota: {req_str!r}",
        ))

    # Kontrola nebezpečných vzorů
    dangerous = [
        ("http://", "HTTP závislost (ne HTTPS)"),
        ("git+http://", "git+http závislost"),
        ("--index-url http", "HTTP index URL"),
    ]
    for pattern, desc in dangerous:
        found = pattern in pyproject_content
        if found:
            results.append(CheckResult(
                name=f"Nebezpečný vzor: {desc}",
                passed=False,
                message="NALEZENO — použijte HTTPS",
            ))

    return results


def check_for_hardcoded_secrets(code: str, filename: str = "<code>") -> list[CheckResult]:
    """
    Jednoduchá simulace bandit-style kontroly.
    Hledá vzory, které mohou indikovat hardkódované secrety.
    """
    import re
    results: list[CheckResult] = []

    patterns = [
        (r'password\s*=\s*["\'][^"\']{4,}["\']', "Hardkódované heslo"),
        (r'secret_key\s*=\s*["\'][^"\']{4,}["\']', "Hardkódovaný secret key"),
        (r'api_key\s*=\s*["\'][^"\']{4,}["\']', "Hardkódovaný API klíč"),
        (r'(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}', "GitHub Personal Access Token"),
        (r'-----BEGIN (RSA |EC )?PRIVATE KEY-----', "Privátní klíč v kódu"),
        (r'AKIA[0-9A-Z]{16}', "AWS Access Key ID"),
        (r'sqlite:///(?!:memory:)[^\s"\']{4,}', "SQLite soubor (ne in-memory)"),
    ]

    for pattern, description in patterns:
        matches = re.findall(pattern, code, re.IGNORECASE)
        if matches:
            results.append(CheckResult(
                name=f"Podezřelý vzor v {filename}",
                passed=False,
                message=description,
                details=[str(m)[:60] for m in matches[:3]],
            ))

    if not results:
        results.append(CheckResult(
            name=f"Secret scan ({filename})",
            passed=True,
            message="Žádné podezřelé vzory nenalezeny",
        ))

    return results


# ── GitHub Actions YAML generátor ─────────────────────────────────────────────

def generate_ci_workflow(
    python_versions: list[str],
    run_docker_build: bool = False,
) -> str:
    """Vygeneruje základní GitHub Actions CI workflow."""
    matrix_versions = json.dumps(python_versions)

    docker_job = ""
    if run_docker_build:
        docker_job = """
  docker:
    name: Build Docker image
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .
"""

    return textwrap.dedent(f"""\
        name: CI
        on:
          push:
            branches: [main, develop]
          pull_request:
            branches: [main]

        jobs:
          test:
            runs-on: ubuntu-latest
            strategy:
              matrix:
                python-version: {matrix_versions}
            steps:
              - uses: actions/checkout@v4
              - uses: astral-sh/setup-uv@v4
              - run: uv python install ${{{{ matrix.python-version }}}}
              - run: uv sync --all-extras --dev
              - run: uv run ruff check src/ tests/
              - run: uv run mypy src/
              - run: uv run pytest tests/ --cov=src --cov-report=xml

          security:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - uses: astral-sh/setup-uv@v4
              - run: uv sync
              - run: uv run pip-audit
        {docker_job}
    """)


# ── Simulace celého CI pipeline ───────────────────────────────────────────────

def print_matrix_results(jobs: list[MatrixBuildJob]) -> None:
    """Hezky vypíše výsledky matrix buildu."""
    passed = sum(1 for j in jobs if j.status == "success")
    failed = len(jobs) - passed

    print(f"\n  Matrix výsledky ({passed}/{len(jobs)} prošlo):")
    print(f"  {'Python':8s} {'OS':16s} {'Status':10s} {'Čas':8s} {'Poslední krok'}")
    print(f"  {'-'*65}")
    for job in jobs:
        last_failed = next(
            (s[0] for s in reversed(job.steps) if s[1] == "FAIL"),
            job.steps[-1][0] if job.steps else "-",
        )
        status_icon = "PASS" if job.status == "success" else "FAIL"
        print(
            f"  {job.python_version:8s} {job.os:16s} {status_icon:10s} "
            f"{job.duration_s:.1f}s    {last_failed}"
        )

    if failed > 0:
        print(f"\n  SELHALY: {failed} kombinace!")
    else:
        print("\n  Všechny kombinace prošly!")


# ── Hlavní funkce ─────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 65)
    print("CI/CD PIPELINE — DEMO")
    print("=" * 65)

    # --- 1. Matrix build ---
    print("\n[1] Simulace GitHub Actions matrix buildu:")
    print("  Python: 3.11, 3.12, 3.13 × OS: ubuntu-latest, windows-latest")
    start = time.perf_counter()
    jobs = run_matrix_build(
        python_versions=["3.11", "3.12", "3.13"],
        operating_systems=["ubuntu-latest", "windows-latest"],
        parallel=True,
    )
    elapsed = time.perf_counter() - start
    print(f"  Dokončeno za {elapsed:.2f}s (paralelně)")
    print_matrix_results(jobs)

    # --- 2. pip-audit simulace ---
    print("\n[2] pip-audit — simulace CVE kontroly závislostí:")
    test_requirements = [
        ("requests", "2.28.0"),
        ("cryptography", "39.0.0"),
        ("pillow", "9.5.0"),
        ("fastapi", "0.109.0"),
        ("pydantic", "2.5.0"),
        ("urllib3", "1.26.14"),
    ]

    vulns, passed = simulate_pip_audit(test_requirements, fail_on_cvss=7.0)
    print(f"  Kontroluji {len(test_requirements)} balíčků...")
    print(f"  Nalezeno vulnerabilit: {len(vulns)}")

    if vulns:
        print(f"\n  {'Balíček':15s} {'Verze':12s} {'CVE':20s} {'CVSS':6s} {'Severity':10s} {'Fix'}")
        print(f"  {'-'*75}")
        for v in vulns:
            fix = v.fix_version or "N/A"
            print(f"  {v.package:15s} {v.installed_version:12s} {v.vulnerability_id:20s} "
                  f"{v.cvss_score:6.1f} {v.severity:10s} >={fix}")

    critical = [v for v in vulns if v.cvss_score >= 7.0]
    if critical:
        print(f"\n  CI SELŽE: {len(critical)} HIGH/CRITICAL vulnerabilit (CVSS >= 7.0)!")
    else:
        print("\n  Žádné HIGH/CRITICAL vulnerabilit — CI prochází")

    # --- 3. pyproject.toml kontrola ---
    print("\n[3] Kontrola pyproject.toml:")
    good_pyproject = """\
[project]
name = "moje-aplikace"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = ["fastapi>=0.110", "pydantic>=2.0"]

[tool.ruff]
line-length = 100

[tool.mypy]
strict = true
"""
    bad_pyproject = """\
[project]
name = "hack"
dependencies = ["requests"]
"""

    for label, content in [("Správný", good_pyproject), ("Špatný", bad_pyproject)]:
        print(f"\n  {label} pyproject.toml:")
        results = check_pyproject_toml(content)
        for r in results:
            icon = "OK" if r.passed else "!!"
            print(f"    [{icon}] {r.message:12s} {r.name}")

    # --- 4. Secret scanning ---
    print("\n[4] Secret scanning simulace (bandit-style):")
    clean_code = """\
import os
password = os.environ["DB_PASSWORD"]
api_key = os.environ.get("API_KEY", "")
"""
    dirty_code = """\
password = "SuperHeslo123"
api_key = "ghp_abc123def456ghi789jklmno0123456789"
DATABASE_URL = "sqlite:///production.db"
"""

    for label, code in [("Čistý kód", clean_code), ("Kód s problémy", dirty_code)]:
        print(f"\n  {label}:")
        scan_results = check_for_hardcoded_secrets(code, label)
        for r in scan_results:
            icon = "OK" if r.passed else "!!"
            print(f"    [{icon}] {r.message}")
            for detail in r.details:
                print(f"         → {detail!r}")

    # --- 5. Vygenerování CI workflow ---
    print("\n[5] Vygenerovaný GitHub Actions CI workflow:")
    workflow = generate_ci_workflow(
        python_versions=["3.11", "3.12", "3.13"],
        run_docker_build=True,
    )
    for line in workflow.splitlines()[:30]:
        print(f"  {line}")
    print(f"  ... ({len(workflow.splitlines())} řádků celkem)")

    # --- 6. Dependency hash check ---
    print("\n[6] Kontrola integrity závislostí (lockfile hash simulace):")
    fake_lockfile = json.dumps({
        "requests==2.31.0": "sha256:abc123def456",
        "fastapi==0.110.0": "sha256:789xyz012uvw",
        "pydantic==2.5.0": "sha256:fed321cba654",
    }, indent=2)

    lockfile_hash = hashlib.sha256(fake_lockfile.encode()).hexdigest()[:16]
    print(f"  Lockfile hash: {lockfile_hash}")
    print(f"  Lockfile obsahuje {len(json.loads(fake_lockfile))} zamčených balíčků")
    print("  CI ověřuje: uv sync --frozen (selže pokud lockfile neodpovídá)")

    # --- 7. Shrnutí ---
    print("\n[7] Doporučený pořadí CI kroků:")
    steps = [
        ("checkout", "Stažení kódu z repozitáře"),
        ("lint", "ruff check — rychlá kontrola stylu"),
        ("format", "ruff format --check — konzistentní formátování"),
        ("types", "mypy --strict — statická analýza typů"),
        ("test", "pytest --cov — testy s pokrytím"),
        ("security", "pip-audit — CVE kontrola závislostí"),
        ("secret-scan", "gitleaks — kontrola uniknutých secretů"),
        ("build", "uv build nebo docker build"),
        ("publish", "uv publish nebo docker push (jen na main/tag)"),
        ("deploy", "kubectl set image (staging → production)"),
    ]
    for i, (name, desc) in enumerate(steps, 1):
        print(f"  {i:2d}. {name:15s} {desc}")


if __name__ == "__main__":
    main()

```
