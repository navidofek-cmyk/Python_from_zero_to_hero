# Program — Lekce 90: Lekce 90: Coverage a property-based testing

Patří k lekci [Lekce 90: Coverage a property-based testing](../90_coverage_hypothesis.md).

## Jak spustit

```bash
python3 programy/l90_hypothesis_demo.py
```

## Zdrojový kód

### `l90_hypothesis_demo.py`

```py
"""Lekce 90 — hypothesis property-based testing.

Spuštění:
    pip install hypothesis
    pytest l90_hypothesis_demo.py -v
"""

from hypothesis import given
from hypothesis import strategies as st


def reverz(s: str) -> str:
    return s[::-1]


def je_palindrom(s: str) -> bool:
    return s == reverz(s)


@given(st.text())
def test_reverz_dvakrat(s):
    assert reverz(reverz(s)) == s


@given(st.lists(st.integers()))
def test_sort_invarianty(seznam):
    s = sorted(seznam)
    assert len(s) == len(seznam)
    assert all(s[i] <= s[i + 1] for i in range(len(s) - 1))


@given(st.text())
def test_palindrom_self_reverse(s):
    if s == "":
        assert je_palindrom(s)

```
