# Lekce 70: Struktura projektu, `pyproject.toml`

## 🏗️ Moderní struktura

```
muj-projekt/
├── pyproject.toml           ← konfigurace (povinné)
├── README.md
├── LICENSE
├── .gitignore
├── src/
│   └── muj_projekt/
│       ├── __init__.py
│       ├── core.py
│       └── cli.py
├── tests/
│   ├── __init__.py
│   └── test_core.py
└── .venv/                   ← virtuální prostředí (gitignore)
```

**`src/` layout** je doporučovaný — zabraňuje testovat „náhodou“ ne-nainstalovaný balíček.

---

## 📜 `pyproject.toml`

Univerzální konfigurační soubor pro Python projekty (PEP 518/621).

```toml
[project]
name = "muj-projekt"
version = "0.1.0"
description = "Krátký popis"
authors = [{name = "Eliška", email = "el@example.com"}]
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.12"
dependencies = [
    "httpx>=0.27",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]

[project.scripts]
moje-cli = "muj_projekt.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100

[tool.mypy]
strict = true
```

---

## 🎯 Hlavní sekce

### `[project]`
Metadata o tvém balíčku — jméno, verze, závislosti.

### `[build-system]`
Říká, jakým nástrojem se má balíček postavit (hatchling, setuptools, poetry-core).

### `[project.scripts]`
Po `pip install` se vytvoří CLI příkaz. `moje-cli` zavolá `main` v modulu `muj_projekt.cli`.

### `[tool.X]`
Konfigurace nástrojů (ruff, mypy, pytest, ...).

---

## 🆚 Build backends

| Backend | Popis |
|---|---|
| **hatchling** | Moderní, rychlý. Doporučuju. |
| **setuptools** | Klasický, hodně rozšířený. |
| **poetry-core** | Pokud používáš Poetry. |
| **maturin** | Pro Rust rozšíření (PyO3). |

---

## 🚀 Start s `uv`

```bash
uv init muj-projekt
cd muj-projekt
uv add httpx pydantic
uv add --dev pytest ruff
uv run pytest
```

`uv` vyrobí celou strukturu sám.

---

## 🎁 Editable install

Když vyvíjíš:
```bash
pip install -e .
# nebo
uv pip install -e .
```

`-e` = editable. Změny v souborech se projeví okamžitě, nemusíš znovu instalovat.

---

## ✏️ Cvičení

1. **Init s uv:** Vytvoř `uv init test_projekt` a podívej se, co všechno vygeneroval.
2. **Pyproject:** Otevři `pyproject.toml` a přidej dev dependencies (`pytest`, `ruff`).
3. **Script:** Přidej `[project.scripts]` co spustí tvoji `main`.
4. **Editable:** Nainstaluj projekt v editable módu a otestuj že změny v souborech se projeví.
