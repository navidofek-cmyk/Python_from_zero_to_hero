# Lekce 91: Statická analýza — `mypy`, `ruff`, `black`

## 🧐 Statická analýza = kontrola bez spuštění

Najde chyby a nesedící typy ve tvém kódu **před spuštěním**.

---

## 🏷️ `mypy` / `pyright` — typový checker

### Instalace

```bash
pip install mypy
mypy muj_modul.py
```

```python
def secti(a: int, b: int) -> int:
    return a + b

secti("ahoj", 5)
# error: Argument 1 has incompatible type "str"; expected "int"
```

### Konfigurace v `pyproject.toml`

```toml
[tool.mypy]
python_version = "3.12"
strict = true
files = ["src/", "tests/"]
```

`strict = true` zapne všechny kontroly. Pro postupné přidávání typu se hodí volnější:

```toml
[tool.mypy]
disallow_untyped_defs = true
warn_unused_ignores = true
```

### `pyright` (Microsoft, používaný v Pylance)

Často **rychlejší** a **přísnější** než mypy.

```bash
pip install pyright
pyright muj_modul.py
```

VS Code s Pylance má `pyright` zabudovaný.

---

## ⚡ `ruff` — linter + formatter (super rychlý)

Ruff je **napsaný v Rustu** — 100× rychlejší než klasický `flake8` + `isort` + `black` dohromady.

```bash
pip install ruff
ruff check .              # najde chyby
ruff check --fix .         # automatické opravy
ruff format .              # naformátuje (nahrazuje black)
```

### Konfigurace

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP", "RUF"]    # sady pravidel
ignore = ["E501"]
```

Pravidla:
- `E`/`W` — pycodestyle (PEP 8)
- `F` — pyflakes (chyby)
- `I` — isort (importy)
- `B` — bugbear (bugy)
- `UP` — pyupgrade (modern syntax)
- `RUF` — ruff specifické

---

## 🎨 `black` (klasika, ale `ruff format` ho nahradil)

```bash
pip install black
black .
```

Bezkonfigurační autoformatter. Dnes ale **`ruff format`** dělá totéž a je **rychlejší**.

---

## 🏗️ Pre-commit hook

Aby se to spustilo **automaticky před každým commitem**:

```bash
pip install pre-commit
```

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
```

```bash
pre-commit install
# Od teď se spustí při každém commitu
```

---

## 🎯 Doporučený stack 2026

```
ruff (lint + format)  + pyright (typy) + pytest
```

To je všechno. `flake8`, `black`, `isort`, `pylint`, `mypy` jsou OK, ale **ruff + pyright** je v 2026 standard.

---

## ✏️ Cvičení

1. **Ruff:** `pip install ruff && ruff check .` na svém projektu. Opravy zkus přes `--fix`.
2. **Pyright:** Nainstaluj a pusť na svůj kód.
3. **Konfig:** Vyrob `pyproject.toml` s `[tool.ruff]` a `[tool.mypy]`.
4. **Pre-commit:** Nainstaluj a otestuj.
