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
        assert je_vikend(date(2026, 4, 18))    # SO

    def test_pondeli(self):
        assert not je_vikend(date(2026, 4, 13))


# Property-based: pristi_pondeli vždycky vrátí datum
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
