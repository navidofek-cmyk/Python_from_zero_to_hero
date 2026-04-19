# pozdrav-cli

Mini CLI co pozdraví — ukázka publikovatelného Python balíčku.

## Instalace

```bash
pip install -e .          # editable mode pro vývoj
# nebo
uv pip install -e .
```

## Použití

```bash
pozdrav Eliško
# Ahoj Eliško.

pozdrav Bobe --vykricnik --velka
# AHOJ BOBE!
```

## Build

```bash
uv build
# nebo
pip install build && python -m build
```

Vytvoří `dist/pozdrav_cli-0.1.0-py3-none-any.whl` a `.tar.gz`.

## Publikace

1. Účet na [pypi.org](https://pypi.org)
2. API token
3. `twine upload dist/*` nebo `uv publish`

Test první na [test.pypi.org](https://test.pypi.org)!
