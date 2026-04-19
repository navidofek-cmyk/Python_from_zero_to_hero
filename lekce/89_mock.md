# Lekce 89: Mockování — `unittest.mock`, `monkeypatch`

## 🎭 Co je mock?

**Mock** = falešný objekt, kterým **nahradíš skutečnou závislost** v testu (DB, HTTP, čas).

Proč? Aby test:
- Byl **rychlý** (žádné skutečné HTTP)
- Byl **deterministický** (žádné random selhání síťě)
- Šlo testovat **bez závislostí** (žádný internet, žádná DB)

---

## 🛠️ `unittest.mock.MagicMock`

```python
from unittest.mock import MagicMock

mock = MagicMock()
mock.metoda(1, 2)
mock.metoda.assert_called_with(1, 2)
mock.metoda.call_count            # 1
```

`MagicMock` reaguje na **cokoli** — `mock.cokoli.cokoli()` jen vrátí další MagicMock.

---

## 🔧 `patch` — nahrazení v modulu

```python
from unittest.mock import patch

# Předpokládejme:
# def stahni_pocet():
#     return requests.get("...").json()["pocet"]

@patch("muj_modul.requests.get")
def test_stahni_pocet(mock_get):
    mock_get.return_value.json.return_value = {"pocet": 42}
    assert stahni_pocet() == 42
    mock_get.assert_called_once_with("...")
```

`patch("modul.kde_se_pouziva")` — důležité! Patchuj **tam, kde se to importuje a používá**, ne tam, kde je definováno.

### Context manager verze

```python
def test_stahni():
    with patch("muj_modul.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"x": 1}
        ...
```

---

## 🎯 `pytest`'s `monkeypatch`

`monkeypatch` je vestavěná `pytest` fixture pro nahrazování:

```python
def test_env(monkeypatch):
    monkeypatch.setenv("API_KEY", "test123")
    assert get_api_key() == "test123"
    # po testu se vrátí původní hodnota


def test_funkce(monkeypatch):
    monkeypatch.setattr("muj_modul.cas", lambda: 1234567890)
    assert get_cas() == 1234567890
```

---

## 🎬 Pytest vs. mock

```python
# unittest.mock
@patch("muj.requests.get")
def test_x(mock_get):
    mock_get.return_value.json.return_value = {"x": 1}

# pytest monkeypatch (verbose)
def test_y(monkeypatch):
    fake = MagicMock()
    fake.return_value.json.return_value = {"x": 1}
    monkeypatch.setattr("muj.requests.get", fake)
```

Většinou používám **kombinaci** — `monkeypatch` na env/atributy, `patch` na složitější mocky.

---

## 🎁 `responses` / `respx` pro HTTP

Pro `requests`:
```python
import responses

@responses.activate
def test_api():
    responses.add(responses.GET, "https://api.x/data", json={"x": 1})
    assert moje_funkce() == 1
```

Pro `httpx`:
```python
import respx

@respx.mock
def test_api():
    respx.get("https://api.x/data").respond(json={"x": 1})
    ...
```

---

## ✏️ Cvičení

1. **MagicMock:** Vyrob mock co předstírá `requests.get(...).json()` výstup.
2. **Patch:** Patchni `time.sleep` aby v testu nečekal.
3. **Monkeypatch env:** Test funkce co čte `os.environ.get("CESTA")`.
4. **Patch metoda:** Test třídy s `patch.object`.
