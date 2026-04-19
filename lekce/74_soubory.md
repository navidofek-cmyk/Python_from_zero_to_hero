# Lekce 74: Práce se soubory

## 📂 `with open()` — základ

```python
with open("data.txt") as f:
    obsah = f.read()           # celý soubor jako string
```

`with` zaručuje **automatické zavření** — i při výjimce.

---

## 🎚️ Módy otevření

| Mód | Význam |
|---|---|
| `"r"` | Read (default) |
| `"w"` | Write — **přepíše** |
| `"a"` | Append — připojí na konec |
| `"x"` | Exclusive — vytvoř, **selže pokud existuje** |
| `"r+"` | Read + write |
| `"b"` | Binary (přidej k r/w/a: `"rb"`, `"wb"`) |
| `"t"` | Text (default) |

```python
open("a.txt")          # rt = read text
open("a.png", "rb")    # read binary
open("a.txt", "w")     # write text (přepíše!)
open("a.txt", "a")     # append
```

---

## 📜 Čtení po řádcích

```python
# ❌ Nepoužívej pro velké soubory
text = f.read()

# ✅ Lepší pro velké soubory — řádek po řádku
for radek in f:
    print(radek.strip())

# Všechny řádky najednou
radky = f.readlines()           # list of strings

# Po jednom řádku
radek = f.readline()
```

---

## ✍️ Psaní

```python
with open("vystup.txt", "w", encoding="utf-8") as f:
    f.write("Ahoj\n")
    f.write("Svete\n")
    f.writelines(["a\n", "b\n", "c\n"])
```

`write` **NEpřidává** newline! Musíš `\n` sám.

---

## 🌍 Kódování — UTF-8 vždy

```python
open("a.txt", encoding="utf-8")              # explicitně!
open("a.txt", encoding="utf-8", errors="replace")  # nahradí špatné znaky ?
```

**Default kódování** závisí na systému (Linux UTF-8, Windows často cp1252). **Vždy** uváděj explicitně.

Python 3.15+ bude UTF-8 výchozí všude.

---

## 🔧 Binární soubory

```python
with open("foto.png", "rb") as f:
    data = f.read()             # bytes

with open("kopie.png", "wb") as f:
    f.write(data)
```

---

## 💧 Pathlib alternativa

Pro krátké operace (lekce 73):

```python
from pathlib import Path

text = Path("data.txt").read_text(encoding="utf-8")
Path("vystup.txt").write_text("ahoj", encoding="utf-8")
```

---

## ⏱️ Buffered/unbuffered

`open` má parametr `buffering`. Default = OS optimalizovaný buffer. Většinou neřeš.

Pro **okamžité psaní** (logy, streaming):

```python
open("log.txt", "w", buffering=1)    # line-buffered
```

---

## 🎯 Časté chyby

❌ Bez `with`:
```python
f = open("a.txt")
data = f.read()
# ZAPOMNĚLS f.close() — leak!
```

❌ Otevření jen na čtení a snaha psát:
```python
with open("a.txt") as f:    # default = "r"
    f.write("...")           # ❌ io.UnsupportedOperation
```

❌ Bez encoding:
```python
open("a.txt")    # ⚠️ závisí na OS — buggy na Windows!
```

---

## ✏️ Cvičení

1. **Read:** Přečti soubor, vypiš počet řádků a slov.
2. **Append:** Přidej řádek do logu (`"a"` mód).
3. **Binary copy:** Zkopíruj obrázek bez `shutil`.
4. **Po řádcích:** Spočítej řádky velkého souboru BEZ `read()` (pouze for ... in f).
5. **Encoding:** Přečti soubor s diakritikou v UTF-8 i s wrong encoding (`encoding="ascii"`) a vyzkoušej co se stane.
