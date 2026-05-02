# Projekt 8: PyPI balíček — `pozdrav-cli`

Mini-projekt po **sekci VIII (Moduly a stdlib)**. Kompletní Python balíček připravený k publikaci na PyPI — CLI příkaz `pozdrav`.

**Použité koncepty:** struktura projektu (70), PyPI publikace (71), entry points (72), `pyproject.toml`, `argparse` (81).

## Jak spustit

```bash
cd projekty/08_pypi_balicek
pip install -e .
pozdrav Eliško
# Ahoj Eliško.

pozdrav Bobe --vykricnik --velka
# AHOJ BOBE!
```

## Jak publikovat

```bash
uv build
# vytvoří dist/pozdrav_cli-0.1.0-py3-none-any.whl

# Publikace na TestPyPI:
uv publish --index testpypi
```

## Struktura projektu

```
08_pypi_balicek/
├── pyproject.toml
├── README.md
└── src/
    └── pozdrav_cli/
        ├── __init__.py
        └── cli.py
```

## Zdrojový kód — `pyproject.toml`

```toml
[project]
name = "pozdrav-cli"
version = "0.1.0"
description = "Mini CLI co pozdraví"
authors = [{name = "Eliška"}]
readme = "README.md"
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = ["pytest", "ruff"]

[project.scripts]
pozdrav = "pozdrav_cli.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
```

## Zdrojový kód — `src/pozdrav_cli/__init__.py`

```python
"""Pozdrav CLI — ukázka publikovatelného balíčku."""

__version__ = "0.1.0"
```

## Zdrojový kód — `src/pozdrav_cli/cli.py`

```python
"""CLI entry point."""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(prog="pozdrav")
    parser.add_argument("jmeno", help="Jméno koho pozdravit")
    parser.add_argument("--vykricnik", action="store_true")
    parser.add_argument("--velka", action="store_true", help="VELKÝMI")
    args = parser.parse_args()

    konec = "!" if args.vykricnik else "."
    text = f"Ahoj {args.jmeno}{konec}"
    if args.velka:
        text = text.upper()
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
