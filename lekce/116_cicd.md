# Lekce 116 — CI/CD pipeline pro Python projekty

CI/CD (Continuous Integration / Continuous Delivery) automatizuje testování, kontrolu kvality a nasazení Python aplikací. GitHub Actions je dnes nejrozšířenější platforma.

---

## Základní koncepty

```
Continuous Integration (CI):
  - Každý commit spustí automatické testy
  - Kontrola kvality kódu (linting, type checking)
  - Bezpečnostní audit závislostí

Continuous Delivery (CD):
  - Automatické nasazení na staging po úspěšném CI
  - Manuální souhlas pro produkci (nebo automatické)
  - Rollback při selhání

GitHub Actions klíčové pojmy:
  Workflow  = YAML soubor definující pipeline
  Job       = skupina kroků běžící na jednom runneru
  Step      = jeden příkaz nebo akce
  Runner    = virtuální stroj (ubuntu-latest, macos-latest, windows-latest)
  Artifact  = výstup jobu (wheel, coverage report)
  Secret    = šifrovaná proměnná (GitHub Settings → Secrets)
```

---

## 1. Základní CI pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    name: Tests (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Setup Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --all-extras --dev

      - name: Lint (ruff)
        run: uv run ruff check src/ tests/

      - name: Format check (ruff format)
        run: uv run ruff format --check src/ tests/

      - name: Type check (mypy)
        run: uv run mypy src/

      - name: Run tests
        run: uv run pytest tests/ -v --tb=short --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.12'
        with:
          file: ./coverage.xml
```

---

## 2. Bezpečnostní audit závislostí

```yaml
  security:
    name: Security audit
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync

      - name: pip-audit (CVE kontrola)
        run: |
          uv run pip-audit --format=json --output=audit.json || true
          uv run pip-audit  # Výstup pro logy

      - name: Trivy (container scan)
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          scan-ref: .
          format: sarif
          output: trivy-results.sarif

      - name: Upload security results
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: trivy-results.sarif

      - name: Secret scanning (gitleaks)
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 3. Build a publish Docker image

```yaml
  docker:
    name: Build Docker image
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha,prefix=sha-
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            APP_VERSION=${{ github.sha }}
```

---

## 4. Deploy na staging / produkci

```yaml
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: docker
    environment: staging

    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/python-app \
            app=ghcr.io/${{ github.repository }}:sha-${{ github.sha }} \
            -n staging
          kubectl rollout status deployment/python-app -n staging --timeout=5m
        env:
          KUBECONFIG_DATA: ${{ secrets.KUBECONFIG_STAGING }}

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment:
      name: production       # Vyžaduje manuální schválení v GitHub UI
    if: startsWith(github.ref, 'refs/tags/v')

    steps:
      - name: Deploy to Production
        run: |
          kubectl set image deployment/python-app \
            app=ghcr.io/${{ github.repository }}:${{ github.ref_name }} \
            -n production
```

---

## 5. Release workflow (tag-triggered)

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - "v*.*.*"

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Pro git log v changelogy

      - uses: astral-sh/setup-uv@v4

      - name: Build wheel
        run: uv build

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          files: dist/*
          generate_release_notes: true
          body: |
            ## Co je nového
            ${{ steps.changelog.outputs.changelog }}

      - name: Publish to PyPI
        if: "!contains(github.ref, 'rc') && !contains(github.ref, 'beta')"
        run: uv publish
        env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
```

---

## 6. Pre-commit hooks (lokální CI)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.2
    hooks:
      - id: gitleaks
```

```bash
# Instalace
pip install pre-commit
pre-commit install

# Manuální spuštění na všech souborech
pre-commit run --all-files
```

---

## 7. Dependency update automatizace (Dependabot)

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    groups:
      dev-dependencies:
        patterns: ["pytest*", "ruff*", "mypy*"]

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## Shrnutí

| Fáze CI | Nástroje |
|---------|----------|
| Lint | `ruff check`, `ruff format --check` |
| Typy | `mypy --strict` |
| Testy | `pytest --cov` |
| Bezpečnost | `pip-audit`, `trivy`, `gitleaks` |
| Build | `uv build`, `docker build` |
| Deploy | `kubectl set image`, Helm |
| Release | `uv publish`, GitHub Release |

---

## Cvičení

1. Napište kompletní `.github/workflows/ci.yml` pro Python balíček, který testuje na Python 3.11, 3.12 a 3.13, spouští `ruff`, `mypy` a `pytest`, a publikuje coverage na Codecov.
2. Přidejte job `check-dependencies`, který: (a) spustí `pip-audit` a uloží výsledek jako artifact, (b) selže pokud je nalezena vulnerabilita se CVSS score >= 7.
3. Implementujte workflow, který automaticky vytvoří GitHub Release s changelogem (z git log) při pushnutí tagu `v*.*.*`.
4. Napište pre-commit hook v Pythonu, který zkontroluje, zda `pyproject.toml` obsahuje všechny povinné metadata sekce (`[project]`, `[project.urls]`, `[tool.ruff]`).
