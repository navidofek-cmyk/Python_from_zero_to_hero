# cas-nastroje (projekt 11)

Mini-projekt po sekci XI — kompletně otestovaná knihovna.

## Struktura

```
cas-nastroje/
├── pyproject.toml
├── src/
│   └── cas_nastroje/
│       ├── __init__.py
│       └── casy.py
└── tests/
    └── test_casy.py
```

## Spuštění

```bash
pip install -e ".[dev]"
pytest                        # spustí testy
pytest --cov=cas_nastroje      # s coverage
ruff check .                   # lint
mypy .                          # typy
```

## Co se procvičuje

- pytest (lekce 88)
- parametrize, fixtures
- hypothesis property-based testing (lekce 90)
- coverage
- ruff + mypy konfigurace (lekce 91)
- src/ layout, pyproject.toml (lekce 70)
