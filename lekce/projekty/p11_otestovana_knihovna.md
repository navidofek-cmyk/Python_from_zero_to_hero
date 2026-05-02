# Projekt 11: Otestovaná knihovna — `cas-nastroje`

Mini-projekt po **sekci XI (Výkon)**. Kompletně otestovaná knihovna pro práci s časem — ukázka src/ layoutu, pytest, hypothesis a coverage.

**Použité koncepty:** pytest (88), mock (89), coverage + hypothesis (90), ruff + mypy (91), src/ layout, `pyproject.toml` (70).

## Jak spustit

```bash
cd projekty/11_otestovana_knihovna
pip install -e ".[dev]"
pytest                         # spustí testy
pytest --cov=cas_nastroje      # s coverage
ruff check .                   # lint
mypy .                         # typy
```

## Struktura

```
11_otestovana_knihovna/
├── pyproject.toml
├── src/
│   └── cas_nastroje/
│       ├── __init__.py
│       └── casy.py
└── tests/
    └── test_casy.py
```

## Zdrojový kód — `pyproject.toml`

```toml
[project]
name = "cas-nastroje"
version = "0.1.0"
description = "Užitečné funkce pro práci s časem"
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = ["pytest", "hypothesis", "pytest-cov", "ruff", "mypy"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-v --tb=short"

[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP", "RUF"]

[tool.mypy]
strict = true
files = ["src"]
```

## Zdrojový kód — `src/cas_nastroje/__init__.py`

```python
"""Mini-projekt po sekci XI: Otestovaná knihovna na práci s časem."""

from .casy import doba_mezi, pristi_pondeli, formatuj_dobu, je_vikend

__all__ = ["doba_mezi", "pristi_pondeli", "formatuj_dobu", "je_vikend"]
__version__ = "0.1.0"
```

## Zdrojový kód — `src/cas_nastroje/casy.py`

```python
"""Užitečné funkce pro práci s časem."""

from datetime import date, datetime, timedelta


def doba_mezi(od: datetime, do: datetime) -> timedelta:
    """Vrátí kladnou dobu mezi dvěma datetime."""
    return abs(do - od)


def pristi_pondeli(od: date) -> date:
    """Vrátí datum příštího pondělí (NE dnes, i kdyby dnes bylo pondělí)."""
    dni = (7 - od.weekday()) % 7
    if dni == 0:
        dni = 7
    return od + timedelta(days=dni)


def formatuj_dobu(d: timedelta) -> str:
    """Hezký popis: '2h 30m', '5d 3h', '45s'."""
    sek = int(d.total_seconds())
    if sek < 60:
        return f"{sek}s"
    if sek < 3600:
        return f"{sek // 60}m {sek % 60}s"
    if sek < 86400:
        h, zbytek = divmod(sek, 3600)
        return f"{h}h {zbytek // 60}m"
    d_, zbytek = divmod(sek, 86400)
    return f"{d_}d {zbytek // 3600}h"


def je_vikend(d: date) -> bool:
    """True pokud je sobota nebo neděle."""
    return d.weekday() >= 5
```

## Zdrojový kód — `tests/test_casy.py`

```python
"""Testy pro cas_nastroje."""

from datetime import date, datetime, timedelta

import pytest
from hypothesis import given, strategies as st

from cas_nastroje import doba_mezi, formatuj_dobu, je_vikend, pristi_pondeli


class TestDobaMezi:
    def test_kladna(self):
        a = datetime(2026, 1, 1, 12, 0)
        b = datetime(2026, 1, 1, 14, 30)
        assert doba_mezi(a, b) == timedelta(hours=2, minutes=30)

    def test_zaporna_je_kladna(self):
        a = datetime(2026, 1, 2)
        b = datetime(2026, 1, 1)
        assert doba_mezi(a, b) == timedelta(days=1)

    def test_stejna(self):
        d = datetime(2026, 1, 1)
        assert doba_mezi(d, d) == timedelta(0)


class TestPristiPondeli:
    @pytest.mark.parametrize("dnes,ocekavano", [
        (date(2026, 4, 13), date(2026, 4, 20)),    # PO → příští PO
        (date(2026, 4, 14), date(2026, 4, 20)),    # ÚT
        (date(2026, 4, 19), date(2026, 4, 20)),    # NE
        (date(2026, 4, 20), date(2026, 4, 27)),    # PO ne dnes
    ])
    def test_param(self, dnes, ocekavano):
        assert pristi_pondeli(dnes) == ocekavano

    def test_je_to_pondeli(self):
        assert pristi_pondeli(date.today()).weekday() == 0


class TestFormatujDobu:
    @pytest.mark.parametrize("sek,ocekavano", [
        (10, "10s"),
        (90, "1m 30s"),
        (3600, "1h 0m"),
        (3661, "1h 1m"),
        (86400, "1d 0h"),
        (90000, "1d 1h"),
    ])
    def test_format(self, sek, ocekavano):
        assert formatuj_dobu(timedelta(seconds=sek)) == ocekavano


class TestJeVikend:
    def test_sobota(self):
        assert je_vikend(date(2026, 4, 18))

    def test_pondeli(self):
        assert not je_vikend(date(2026, 4, 13))


@given(st.dates())
def test_pristi_pondeli_je_v_budoucnu(d):
    p = pristi_pondeli(d)
    assert p > d
    assert p.weekday() == 0
    assert (p - d).days <= 7


@given(st.integers(min_value=0, max_value=10**6))
def test_format_je_neprazdny(sek):
    s = formatuj_dobu(timedelta(seconds=sek))
    assert s
    assert any(c.isdigit() for c in s)
```
