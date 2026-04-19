# Lekce 73: `pathlib` — moderní práce se soubory

## 🛣️ Místo `os.path` — `pathlib`

Starý styl (`os.path`) je řetězcový a klopotný. **`pathlib.Path`** je objekt = mnohem hezčí.

```python
from pathlib import Path
```

---

## 🛠️ Vytvoření a operátor `/`

```python
p = Path("/home/eliska")
p / "dokumenty" / "soubor.txt"     # /home/eliska/dokumenty/soubor.txt
```

`/` operátor spojuje cesty. Hezké!

```python
domu = Path.home()                  # ~
cwd = Path.cwd()                    # aktuální adresář
soubor = Path(__file__)             # tento .py soubor
```

---

## 🔍 Vlastnosti

```python
p = Path("/home/eliska/foto.png")
p.name           # "foto.png"
p.stem           # "foto"
p.suffix         # ".png"
p.parent         # /home/eliska
p.parts          # ('/', 'home', 'eliska', 'foto.png')
p.absolute()
p.is_absolute()
```

---

## 📝 Čtení a zápis

```python
p = Path("data.txt")

text = p.read_text(encoding="utf-8")
p.write_text("Ahoj svete", encoding="utf-8")

bytes_data = p.read_bytes()
p.write_bytes(b"\x00\x01\x02")
```

Bez `with open(...)` — velmi pohodlné pro krátké operace.

Pro **velké soubory** stále `with p.open()`:

```python
with p.open() as f:
    for radek in f:
        ...
```

---

## ❓ Existence a typ

```python
p.exists()
p.is_file()
p.is_dir()
p.is_symlink()
```

---

## 📂 Operace s adresáři

```python
slozka = Path("muj_projekt")

slozka.mkdir(parents=True, exist_ok=True)   # vytvoř (i s rodiči)
slozka.rmdir()                                # smaž (musí být prázdná)

# Procházení
for item in slozka.iterdir():
    print(item)

# Glob
for soubor in slozka.glob("*.py"):
    print(soubor)

for soubor in slozka.rglob("*.py"):    # rekurzivně
    print(soubor)
```

---

## 🔄 Přejmenování, mazání, kopírování

```python
p.rename("novy_nazev.txt")
p.unlink()                  # smaž soubor

# Kopírování — pathlib nemá; použij shutil
import shutil
shutil.copy("a.txt", "b.txt")
shutil.copytree("src", "dst")
shutil.rmtree("staré")
```

---

## 🎯 Příklady

### Najdi všechny obrázky

```python
obrazky = list(Path("fotky").rglob("*.jpg"))
```

### Statistika souboru

```python
p.stat().st_size          # velikost v bytech
p.stat().st_mtime         # čas poslední úpravy
```

### Sloučení relativní a absolutní

```python
absolutni = (cwd / "data" / "neco.txt").resolve()
```

---

## 🆚 Pathlib vs os.path

```python
# os.path styl
os.path.join("a", "b", "c.txt")         # "a/b/c.txt"
os.path.exists("/tmp")
os.path.basename(p)
os.path.splitext(p)[1]

# Pathlib styl
Path("a") / "b" / "c.txt"
Path("/tmp").exists()
p.name
p.suffix
```

Pathlib = vždycky hezčí. Používej ho. 🎉

---

## ✏️ Cvičení

1. **Domov:** Vypiš všechny soubory ve své domovské složce.
2. **Glob:** Najdi všechny `.py` soubory v projektu (rekurzivně).
3. **Velikost:** Spočítej součet velikostí všech souborů ve složce.
4. **Read/Write:** Přečti `data.txt`, převeď na velká písmena, ulož jako `data_velke.txt`.
5. **Stem suffix:** Funkce co rename všechny `.jpg` na `.jpeg`.
