# Lekce 88: `unittest` a `pytest`

## 🧪 Proč testovat?

Testy jsou **automatický kontrolor**, který vždycky znova ověří, že tvůj kód funguje. Když změníš jednu věc, testy ti hned řeknou, jestli jsi něco rozbil.

---

## 🐍 `unittest` — stdlib

```python
import unittest

class TestKalkulacka(unittest.TestCase):
    def test_secti(self):
        self.assertEqual(2 + 3, 5)

    def test_negativni(self):
        self.assertEqual(-2 + -3, -5)

if __name__ == "__main__":
    unittest.main()
```

```bash
python -m unittest test_kalkulacka.py
```

**Funguje, ale je upovídané.** V moderním Pythonu používáme `pytest`.

---

## 🚀 `pytest` — moderní

```bash
pip install pytest
```

```python
# test_kalkulacka.py
def test_secti():
    assert 2 + 3 == 5

def test_negativni():
    assert -2 + -3 == -5
```

```bash
pytest
# nebo
pytest -v               # detailní výstup
pytest -k "secti"       # jen testy s "secti" v názvu
pytest test_x.py        # konkrétní soubor
pytest test_x.py::test_y   # konkrétní test
```

**Žádná třída, žádné `assertEqual` — jen `assert`!**

---

## 🛠️ `pytest` fixtures

**Fixture** = setup před testem (DB, soubor, mock).

```python
import pytest

@pytest.fixture
def vzorovy_seznam():
    return [1, 2, 3, 4, 5]


def test_soucet(vzorovy_seznam):       # ← injektovaná fixture
    assert sum(vzorovy_seznam) == 15

def test_max(vzorovy_seznam):
    assert max(vzorovy_seznam) == 5
```

### Setup + teardown

```python
@pytest.fixture
def docasny_soubor(tmp_path):     # tmp_path je built-in!
    soubor = tmp_path / "test.txt"
    soubor.write_text("ahoj")
    yield soubor
    # po `yield` = teardown (úklid), ale tmp_path se uklidí sám


def test_cti(docasny_soubor):
    assert docasny_soubor.read_text() == "ahoj"
```

### Scope

```python
@pytest.fixture(scope="session")    # jen jednou na celý běh
def databaze():
    return setup_db()
```

Scope: `function` (default), `class`, `module`, `session`.

---

## 🎯 `parametrize` — hromadný test

```python
@pytest.mark.parametrize("vstup,vystup", [
    (2, 4),
    (3, 9),
    (-1, 1),
    (0, 0),
])
def test_ctverec(vstup, vystup):
    assert vstup ** 2 == vystup
```

Spustí se **4× s různými hodnotami**.

---

## 🏷️ Marks

```python
@pytest.mark.skip(reason="Ještě se nedokončilo")
def test_neco(): ...

@pytest.mark.skipif(sys.version_info < (3, 12), reason="Vyžaduje 3.12+")
def test_nove(): ...

@pytest.mark.xfail(reason="Známý bug, fix v dalším release")
def test_bug(): ...

@pytest.mark.slow
def test_pomale(): ...
```

Filtrování:
```bash
pytest -m "not slow"
pytest -m "slow"
```

---

## ❗ Testování výjimek

```python
def test_deleni_nulou():
    with pytest.raises(ZeroDivisionError):
        1 / 0

def test_s_zpravou():
    with pytest.raises(ValueError, match="špatný"):
        raise ValueError("špatný vstup")
```

---

## 🎯 Konvence

- Soubory `test_*.py` nebo `*_test.py`
- Funkce `test_*`
- Třídy `Test*`
- Adresář `tests/` vedle `src/`

---

## ✏️ Cvičení

1. **První test:** Vyrob `test_kalkulacka.py` s testy pro `secti`, `odecti`, `nasob`.
2. **Fixture:** Vyrob fixture `prazdny_dict` a testy co ho použijí.
3. **Parametrize:** Otestuj `is_even(n)` pro 6 různých vstupů.
4. **Raises:** Test že `1/0` vyhodí `ZeroDivisionError`.
5. **Tmp path:** Test funkce co píše do souboru — použij `tmp_path`.
