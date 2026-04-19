# Lekce 75: `os`, `shutil`, `tempfile`, `glob`

## 🗄️ `os` — operační systém

```python
import os

os.getcwd()                  # aktuální adresář
os.chdir("/tmp")             # změna adresáře
os.environ["HOME"]           # env proměnné
os.environ.get("DEBUG", "0")
os.makedirs("a/b/c", exist_ok=True)
os.remove("soubor.txt")
os.rename("a", "b")
os.cpu_count()
os.getpid()                  # PID procesu
os.uname()                   # info o systému (Unix)
```

V moderním kódu **preferuj `pathlib`** pro souborové operace. `os` zůstává pro env, procesy.

---

## 📦 `shutil` — high-level operace

```python
import shutil

shutil.copy("a.txt", "b.txt")          # kopie souboru
shutil.copy2("a.txt", "b.txt")         # i s metadata
shutil.copytree("src/", "dst/")        # rekurzivně
shutil.rmtree("staré/")                # smaž celou složku
shutil.move("a", "b")                  # přesun
shutil.disk_usage("/")                 # (total, used, free)
shutil.which("python3")                 # cesta k programu
```

---

## 🗑️ `tempfile` — bezpečné dočasné soubory

```python
import tempfile

# Dočasný SOUBOR (auto-smaže)
with tempfile.NamedTemporaryFile(mode="w", delete=True) as f:
    f.write("ahoj")
    f.flush()
    print(f.name)              # /tmp/tmpXXXXXX

# Dočasný ADRESÁŘ
with tempfile.TemporaryDirectory() as slozka:
    print(slozka)              # /tmp/tmpYYYYYY
    # ... práce ...
# Automaticky smaže
```

Lepší než ručně `/tmp/moje.txt` — žádné kolize, bezpečné, auto-úklid.

---

## 🔍 `glob` — vzory souborů

```python
import glob

glob.glob("*.py")                  # všechny .py v cwd
glob.glob("**/*.py", recursive=True)   # rekurzivně
glob.glob("data/[0-9]*.csv")       # data/0xxx.csv, data/1xxx.csv...
```

Pathlib alternativa:
```python
list(Path(".").glob("*.py"))
list(Path(".").rglob("*.py"))
```

---

## 🎯 Praktické vzory

### Bezpečný zápis (atomic)

```python
import os
from tempfile import NamedTemporaryFile

def atomicky_zapis(cesta, obsah):
    with NamedTemporaryFile("w", dir=os.path.dirname(cesta), delete=False) as f:
        f.write(obsah)
        tmp = f.name
    os.replace(tmp, cesta)         # atomická náhrada
```

Když crashne během psaní, originál není poškozený.

### Záloha před úpravou

```python
import shutil
shutil.copy("dulezite.txt", "dulezite.txt.backup")
```

---

## ✏️ Cvičení

1. **Tempdir:** Vytvoř dočasný adresář, vytvoř v něm 3 soubory, vypiš je. Po `with` se smažou.
2. **Disk usage:** Vypiš volné místo na svém disku.
3. **Atomic:** Implementuj `atomicky_zapis` a otestuj.
4. **Glob:** Najdi všechny `*.txt` v `/tmp` rekurzivně.
