# Program — Lekce 91: Lekce 91: Statická analýza — `mypy`, `ruff`, `black`

Patří k lekci [Lekce 91: Statická analýza — `mypy`, `ruff`, `black`](../91_staticka_analyza.md).

## Jak spustit

```bash
python3 programy/l91_ruff_config/<soubor>.py
```

## Zdrojový kód

### `pyproject.toml`

```toml
[project]
name = "ruff-demo"
version = "0.1.0"
requires-python = ">=3.12"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP", "RUF", "SIM", "PL"]
ignore = ["E501"]

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
python_version = "3.12"
strict = true
files = ["."]

```
