# Lekce 181: Mutation testing + Fuzzing

Mutation testing ověří, že tvoje testy skutečně zachytí chyby. Fuzzing generuje náhodné vstupy a hledá pády.

---

## 🧬 Mutation Testing — mutmut

```bash
uv add mutmut
```

Mutmut mění kód (mutanty) a kontroluje, jestli testy selžou.

```python
# src/kalkulacka.py — kód k testování
def secti(a: int, b: int) -> int:
    return a + b

def odecti(a: int, b: int) -> int:
    return a - b

def vydel(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Dělení nulou")
    return a / b

def je_prvocislo(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
```

```python
# tests/test_kalkulacka.py
import pytest
from src.kalkulacka import secti, odecti, vydel, je_prvocislo

def test_secti():
    assert secti(2, 3) == 5

def test_odecti():
    assert odecti(5, 3) == 2

def test_vydel():
    assert vydel(10, 2) == 5.0

def test_vydel_nulou():
    with pytest.raises(ValueError):
        vydel(5, 0)

def test_prvocislo():
    assert je_prvocislo(7) == True
    assert je_prvocislo(4) == False
```

Spuštění:
```bash
mutmut run
mutmut results
# Survived mutants (problematické):
mutmut show 1   # ukáže konkrétní mutant
mutmut apply 1  # aplikuje mutant (pro debugging)
```

---

## 🔍 Příklady mutantů

```python
# Mutmut vygeneruje tyto mutanty z kódu:

# Původní:  return a + b
# Mutant 1: return a - b   ← testy by měly zachytit
# Mutant 2: return a * b   ← testy by měly zachytit
# Mutant 3: return a + b + 1  ← testy by měly zachytit

# Původní:  if b == 0:
# Mutant 4: if b != 0:    ← testy by měly zachytit
# Mutant 5: if b <= 0:    ← hraniční případ

# Původní:  return False
# Mutant 6: return True   ← testy by měly zachytit
```

Lepší test:
```python
def test_secti_silnejsi():
    assert secti(2, 3) == 5
    assert secti(-1, 1) == 0
    assert secti(0, 0) == 0
    assert secti(100, -50) == 50
    # Teď mutanty nesurviví!
```

---

## 🐛 Fuzzing — atheris + hypothesis

### Atheris — coverage-guided fuzzing

```bash
uv add atheris
```

```python
# fuzz_parser.py
import atheris
import sys


def parsuj_datum(text: str) -> dict:
    """Parser data — potenciálně crashuje na neočekávaných vstupech."""
    import re
    m = re.match(r"(\d{1,4})-(\d{1,2})-(\d{1,2})", text)
    if not m:
        return {}
    rok, mesic, den = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if mesic > 12 or den > 31:
        raise ValueError(f"Neplatné datum: {text}")
    return {"rok": rok, "mesic": mesic, "den": den}


@atheris.instrument_func
def fuzz_target(data: bytes):
    text = data.decode("utf-8", errors="replace")
    try:
        parsuj_datum(text)
    except ValueError:
        pass   # očekávané výjimky jsou OK
    except Exception as e:
        # Neočekávané výjimky = chyba!
        print(f"CRASH: {e!r} na vstupu: {text!r}")
        raise


if __name__ == "__main__":
    atheris.Setup(sys.argv, fuzz_target)
    atheris.Fuzz()
```

Spuštění:
```bash
python fuzz_parser.py -max_total_time=30   # fuzz 30 sekund
```

### Hypothesis — property-based testing

```python
from hypothesis import given, strategies as st, settings, assume
import hypothesis.strategies as st


# Property-based testy
@given(st.integers(), st.integers())
def test_secti_komutativni(a, b):
    """Sčítání je komutativní."""
    assert secti(a, b) == secti(b, a)


@given(st.integers())
def test_secti_s_nulou(a):
    """a + 0 == a vždy."""
    assert secti(a, 0) == a


@given(st.floats(allow_nan=False, allow_infinity=False, min_value=0.001),
       st.floats(allow_nan=False, allow_infinity=False, min_value=0.001))
def test_vydel_inverzni(a, b):
    """(a / b) * b ≈ a"""
    assume(b != 0)
    vysledek = vydel(a, b) * b
    assert abs(vysledek - a) < 1e-9


@given(st.integers(min_value=2, max_value=10000))
def test_prvocislo_konzistentni(n):
    """Prvočíslo má právě 2 dělitele."""
    if je_prvocislo(n):
        delitele = [i for i in range(1, n+1) if n % i == 0]
        assert len(delitele) == 2, f"{n} je prvočíslo ale má dělitele {delitele}"
```

---

## 🔬 Fuzzing HTTP API

```python
from hypothesis import given, strategies as st
from fastapi.testclient import TestClient
import json


def test_api_fuzz(client: TestClient):
    """Fuzzing FastAPI endpointů."""

    @given(
        jmeno=st.text(min_size=0, max_size=1000),
        vek=st.integers(min_value=-1000, max_value=1000),
        email=st.text(max_size=500),
    )
    def vyzkoušej(jmeno, vek, email):
        response = client.post("/users", json={
            "jmeno": jmeno,
            "vek": vek,
            "email": email,
        })
        # Server nesmí crashnout (5xx je chyba)
        assert response.status_code != 500, f"500 na vstupu: {jmeno!r}, {vek}, {email!r}"
        # 200 nebo 422 (validation error) jsou OK

    vyzkoušej()
```

---

## 📊 Mutation score

```
Mutation score = zabitých mutantů / celkových mutantů * 100%

< 50%  — testy jsou špatné
50-80% — průměrné testy
> 80%  — dobré testy
> 90%  — výborné testy (cíl pro kritický kód)
```

---

## ✏️ Cvičení

1. Spusť mutmut na projektu Todo list (projekt 2) — jaký je mutation score?
2. Napiš Hypothesis testy pro řadící algoritmy z lekce 143.
3. Fuzzuj parsovací funkce v log analyzátoru (projekt 9) pomocí atheris.
4. Napiš property-based testy pro BST z lekce 144 — ověř invarianty.
5. Kombinuj mutation testing + fuzzing: fuzzing najde edge cases, mutation testing ověří testy.
