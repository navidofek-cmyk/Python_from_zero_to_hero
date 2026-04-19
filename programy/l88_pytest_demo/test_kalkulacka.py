"""Lekce 88 — pytest demo.

Spuštění:
    pytest l88_pytest_demo/test_kalkulacka.py -v
"""

import pytest


def secti(a: int, b: int) -> int:
    return a + b


def deli(a: int, b: int) -> float:
    return a / b


# Základní testy
def test_secti_kladne():
    assert secti(2, 3) == 5


def test_secti_zaporne():
    assert secti(-1, -1) == -2


# Parametrize
@pytest.mark.parametrize("a,b,vysledek", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_secti_param(a, b, vysledek):
    assert secti(a, b) == vysledek


# Výjimky
def test_deli_nulou():
    with pytest.raises(ZeroDivisionError):
        deli(1, 0)


# Fixture s tmp_path
def test_zapis(tmp_path):
    soubor = tmp_path / "test.txt"
    soubor.write_text("ahoj")
    assert soubor.read_text() == "ahoj"


# Vlastní fixture
@pytest.fixture
def vzorovy_seznam():
    return [1, 2, 3, 4, 5]


def test_soucet(vzorovy_seznam):
    assert sum(vzorovy_seznam) == 15


def test_max(vzorovy_seznam):
    assert max(vzorovy_seznam) == 5
