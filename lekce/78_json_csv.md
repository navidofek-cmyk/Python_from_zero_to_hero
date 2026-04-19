# Lekce 78: `json`, `csv`, `tomllib`, `configparser`, `pickle`

## 📋 JSON — nejčastější formát

```python
import json

# Z Python do JSON stringu
data = {"jmeno": "Eliška", "vek": 10, "koniky": ["čtení", "fotbal"]}
text = json.dumps(data, indent=2, ensure_ascii=False)

# Z JSON stringu zpět
data = json.loads(text)

# Soubory
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

with open("data.json", encoding="utf-8") as f:
    data = json.load(f)
```

⚠️ **`ensure_ascii=False`** aby české znaky zůstaly čitelné!

### JSON typy ↔ Python

| JSON | Python |
|---|---|
| object | dict |
| array | list |
| string | str |
| number | int / float |
| true / false | True / False |
| null | None |

JSON **neumí** datetime, set, tuple, vlastní třídy. Musíš převést.

---

## 📊 CSV

```python
import csv

# Čtení
with open("data.csv", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    for radek in reader:
        print(radek)

# Jako slovníky
with open("data.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for radek in reader:
        print(radek["jmeno"], radek["vek"])

# Zápis
with open("vystup.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["jmeno", "vek"])
    writer.writerow(["Anna", 10])

# Zápis z dict
with open("vystup.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["jmeno", "vek"])
    writer.writeheader()
    writer.writerow({"jmeno": "Anna", "vek": 10})
```

⚠️ `newline=""` — povinné pro Windows, jinak dvojité konce řádků.

---

## 📜 TOML (3.11+)

```python
import tomllib    # JEN ke čtení! Pro zápis: pip install tomli-w

with open("pyproject.toml", "rb") as f:    # binárně!
    data = tomllib.load(f)

# Z stringu
data = tomllib.loads('name = "test"\nversion = 1')
```

TOML používá `pyproject.toml` a moderní config soubory. Pro zápis chybí ve stdlib — použij `tomli-w`.

---

## ⚙️ `configparser` — INI soubory

```python
import configparser

config = configparser.ConfigParser()
config.read("settings.ini", encoding="utf-8")

print(config["database"]["host"])
print(config.getint("server", "port"))
```

`settings.ini`:
```ini
[database]
host = localhost
port = 5432

[server]
debug = true
```

(Pro nové projekty raději TOML.)

---

## 🥒 `pickle` — Python serializace

```python
import pickle

data = {"klic": [1, 2, 3], "cas": datetime.now()}

# Do souboru
with open("data.pkl", "wb") as f:
    pickle.dump(data, f)

with open("data.pkl", "rb") as f:
    nacteno = pickle.load(f)
```

⚠️ **NIKDY nedeserializuj nedůvěryhodný pickle!** Umožňuje **arbitrary code execution**. Pickle je jen pro **vlastní data** (cache, mezi-procesní komunikace).

Pro nedůvěryhodná data → **JSON** (bezpečné).

---

## 🗄️ `shelve` — pickle s klíči

```python
import shelve

with shelve.open("databaze.db") as db:
    db["uzivatel-1"] = {"jmeno": "Anna"}
    print(db["uzivatel-1"])
```

Mini-database souborem. Pro malé projekty.

---

## 🎯 Co kdy?

| Formát | Použití |
|---|---|
| **JSON** | API, výměna dat, lidsky čitelné |
| **CSV** | Tabulky, Excel kompatibilita |
| **TOML** | Konfigurace (`pyproject.toml`) |
| **YAML** | Komplexní config (Kubernetes, CI) — `pip install pyyaml` |
| **INI** | Stará konfigurace |
| **Pickle** | Vlastní cache, ne pro sdílení |

---

## ✏️ Cvičení

1. **JSON:** Vyrob slovník 3 lidí, ulož do JSON, načti zpátky, ověř rovnost.
2. **CSV:** Vytvoř CSV se zaměstnanci, čti ho jako DictReader, vypiš tabulku.
3. **TOML:** Přečti `pyproject.toml` a vypiš název projektu a verzi.
4. **Config:** Načti `settings.ini` a vypiš obsah.
5. **Pickle:** Ulož a načti složitý objekt (datetime + list + dict).
