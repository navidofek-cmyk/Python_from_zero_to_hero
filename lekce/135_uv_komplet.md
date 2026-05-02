# Lekce 135: uv — kompletní průvodce

`uv` je moderní náhrada za `pip`, `pip-tools`, `virtualenv`, `pipx` a částečně i `poetry` — vše v jednom binárním souboru napsaném v Rustu. Je **10–100× rychlejší** než pip.

---

## 🚀 Instalace

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Přes pip (fallback)
pip install uv
```

Ověření:
```bash
uv --version
# uv 0.5.x
```

---

## 📦 Základní správa balíčků

### Virtuální prostředí

```bash
uv venv                    # vytvoří .venv v aktuální složce
uv venv .venv --python 3.12  # konkrétní verze Pythonu
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### Instalace balíčků

```bash
uv pip install requests          # jako pip install
uv pip install "fastapi[standard]"
uv pip install -r requirements.txt
uv pip install -e .              # editable install
```

### Generování lock souboru

```bash
uv pip compile requirements.in -o requirements.txt   # deterministický lock
uv pip sync requirements.txt                          # přesná synchronizace
```

---

## 📋 Projekty s `pyproject.toml`

### Nový projekt

```bash
uv init muj-projekt      # vytvoří složku s pyproject.toml + hello.py
cd muj-projekt
uv run hello.py          # spustí skript v prostředí projektu
```

Vygenerovaný `pyproject.toml`:

```toml
[project]
name = "muj-projekt"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []
```

### Přidávání závislostí

```bash
uv add requests           # přidá do [project.dependencies] + uv.lock
uv add "fastapi[standard]"
uv add --dev pytest ruff  # vývojové závislosti
uv remove requests        # odstraní
```

### uv.lock

```bash
uv lock          # vygeneruje uv.lock (deterministický, verzovaný v gitu)
uv sync          # nainstaluje přesně dle uv.lock
uv sync --frozen # bez aktualizace lock souboru (CI/CD)
```

---

## ▶️ Spouštění skriptů

### `uv run`

```bash
uv run main.py           # spustí v prostředí projektu
uv run pytest            # spustí pytest
uv run -- python -c "import sys; print(sys.version)"
```

### Inline závislosti (PEP 723)

Skript si může nést vlastní závislosti přímo v komentáři:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
#   "rich",
# ]
# ///

import requests
from rich import print

r = requests.get("https://httpbin.org/json")
print(r.json())
```

Spuštění:
```bash
uv run skript.py   # uv automaticky nainstaluje requests + rich
```

Sdílení skriptu bez requirements.txt — pošli jediný soubor!

---

## 🔧 uv tool — globální CLI nástroje

```bash
uv tool install ruff         # nainstaluje ruff globálně (izolovaně)
uv tool install black
uv tool install httpie
uv tool list                 # seznam nainstalovaných nástrojů
uv tool upgrade ruff         # aktualizace

# Jednorázové spuštění bez instalace:
uvx ruff check .             # = uv tool run ruff check .
uvx black --check main.py
```

---

## 🐍 Správa verzí Pythonu

```bash
uv python list               # dostupné verze
uv python install 3.13       # stáhne a nainstaluje CPython 3.13
uv python pin 3.12           # zapíše .python-version do projektu
uv python find 3.11          # najde cestu k interpreteru
```

---

## 🏢 Workspaces (monorepo)

Workspace = více projektů sdílí jeden `uv.lock`.

Struktura:
```
muj-monorepo/
├── pyproject.toml        # root workspace
├── uv.lock
├── packages/
│   ├── api/
│   │   └── pyproject.toml
│   └── sdilena-lib/
│       └── pyproject.toml
```

Root `pyproject.toml`:
```toml
[tool.uv.workspace]
members = ["packages/*"]
```

```bash
uv sync                  # nainstaluje všechny workspace members
uv run --package api uvicorn app:app
```

---

## 🔁 CI/CD s uv

GitHub Actions:

```yaml
- uses: astral-sh/setup-uv@v3
  with:
    version: "latest"

- run: uv sync --frozen
- run: uv run pytest
- run: uvx ruff check .
```

---

## ⚡ Srovnání rychlosti

| Operace | pip | uv |
|---------|-----|----|
| Install requests | ~2s | ~0.1s |
| Install FastAPI | ~8s | ~0.5s |
| Resolve 100 deps | ~30s | ~1s |

uv používá paralelní stahování, Rust parser a agresivní cache (`~/.cache/uv`).

---

## 🎯 Kdy použít co

| Potřeba | Příkaz |
|---------|--------|
| Nový projekt | `uv init` |
| Přidat závislost | `uv add` |
| Spustit skript | `uv run` |
| Jednorázový skript | inline deps + `uv run` |
| CLI nástroj globálně | `uv tool install` |
| Konkrétní Python | `uv python install` |
| CI/CD | `uv sync --frozen` |
| Sdílet monorepo | workspace |

---

## ✏️ Cvičení

1. Vytvoř nový projekt `uv init cviceni`, přidej `httpx`, spusť `uv run` skript.
2. Napiš standalone skript s inline závislostmi (`requests`, `rich`) a spusť přes `uv run`.
3. Nainstaluj `ruff` jako globální nástroj přes `uv tool install`, zkontroluj projekt.
4. Vyzkoušej `uv python install 3.13` a `uv venv --python 3.13`.
