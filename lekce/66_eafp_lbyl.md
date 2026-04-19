# Lekce 66: EAFP vs LBYL — pythonský přístup

## 🔄 Dva přístupy

### LBYL — Look Before You Leap

„Než skočíš, podívej se.“ Klasický defensive programming:

```python
if "klic" in slovnik:
    hodnota = slovnik["klic"]
else:
    hodnota = None
```

### EAFP — Easier to Ask Forgiveness than Permission

„Jednoduší je omluvit se než žádat o povolení.“ **Pythonský styl:**

```python
try:
    hodnota = slovnik["klic"]
except KeyError:
    hodnota = None
```

---

## 🎯 Proč EAFP v Pythonu?

1. **Race condition** — mezi `if "x" in d:` a `d["x"]` se může stát cokoli (concurrent přístup, jiný thread).
2. **Ne všechno se dá zkontrolovat** dopředu (např. obsah souboru, stav DB).
3. **Idiom Pythonu** — výjimky jsou rychlé, levné.

---

## 📊 Příklady

### LBYL vs EAFP — soubor

```python
# LBYL
import os
if os.path.exists("data.txt"):
    with open("data.txt") as f:
        ...
# Mezi exists a open ho někdo může smazat!

# EAFP
try:
    with open("data.txt") as f:
        ...
except FileNotFoundError:
    ...
```

### Slovník

```python
# LBYL
if "klic" in d:
    use(d["klic"])

# EAFP
try:
    use(d["klic"])
except KeyError:
    pass

# Ještě lépe — get
hodnota = d.get("klic")
```

### Atribut

```python
# LBYL
if hasattr(obj, "metoda"):
    obj.metoda()

# EAFP
try:
    obj.metoda()
except AttributeError:
    pass
```

---

## ⚖️ Kdy LBYL?

- Když je **ověření dramaticky levnější** než operace.
- Když je **selhání běžné**, ne výjimečné.
- Při validaci uživatelského vstupu **dopředu**.

```python
if not isinstance(x, int):
    raise TypeError("musí být int")
zpracuj(x)
```

---

## 🎯 Pravidlo

> **„Výjimky jsou pro výjimečné stavy. Ale v Pythonu je to spektrum, ne dogma.“**

V praxi: **EAFP** často vyhrává čistotou, **LBYL** vítězí při validaci na hranici (vstupech).

---

## ✏️ Cvičení

1. **Slovník:** Napiš dvě verze přístupu ke klíči — LBYL i EAFP.
2. **Soubor:** Zkus otevřít, zachyť `FileNotFoundError`. Bez kontroly `exists`.
3. **Atribut:** Zkus zavolat metodu, zachyť `AttributeError`.
4. **Race demo:** Vysvětli prostě, proč LBYL může selhat při concurrent přístupu.
