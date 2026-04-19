# Lekce 90: Coverage a property-based testing

## 📊 Coverage — kolik kódu je otestováno?

```bash
pip install coverage
coverage run -m pytest
coverage report
coverage html              # HTML report v htmlcov/
```

Nebo `pytest-cov`:

```bash
pip install pytest-cov
pytest --cov=src --cov-report=html
```

### Cíl

- 80–90 % je super.
- 100 % je často přemrštěné — některé řádky (defensive) testovat nemusíš.

### `# pragma: no cover`

```python
def f():
    if velmi_vzacny_pripad:    # pragma: no cover
        return None
    ...
```

---

## 🎲 Property-based testing — `hypothesis`

Místo psaní konkrétních testů necháš `hypothesis` **vygenerovat tisíce vstupů**:

```bash
pip install hypothesis
```

```python
from hypothesis import given
from hypothesis import strategies as st


def reverz(s: str) -> str:
    return s[::-1]


@given(st.text())
def test_reverz_dvakrat(s):
    assert reverz(reverz(s)) == s
```

Hypothesis vygeneruje **stovky náhodných řetězců** a otestuje invariant. Pokud najde chybu, **zmenšuje vstup** dokud nedostane minimální příklad.

### Strategies

```python
st.integers()
st.integers(min_value=0, max_value=100)
st.text()
st.lists(st.integers())
st.dictionaries(st.text(), st.integers())
st.composite(...)         # vlastní
```

### Příklad — sort invariant

```python
@given(st.lists(st.integers()))
def test_sort(seznam):
    s = sorted(seznam)
    # Délka je stejná
    assert len(s) == len(seznam)
    # Je seřazený
    assert all(s[i] <= s[i+1] for i in range(len(s)-1))
    # Obsahuje stejné prvky
    assert sorted(s) == sorted(seznam)
```

---

## 🎯 Doctest — testy v dokumentaci

```python
def secti(a, b):
    """Sečte dvě čísla.

    >>> secti(2, 3)
    5
    >>> secti(-1, 1)
    0
    """
    return a + b
```

```bash
python -m doctest -v moje.py
pytest --doctest-modules
```

Hodí se na **malé příklady v docstringu**.

---

## ✏️ Cvičení

1. **Coverage:** Pusť `pytest --cov` na svůj projekt. Co je otestováno?
2. **Hypothesis:** Otestuj funkci `je_palindrom(s)` pomocí Hypothesis.
3. **Reverz:** Otestuj invariant `reverz(reverz(x)) == x` pro `text` i `list`.
4. **Doctest:** Přidej doctest do funkce a spusť.
