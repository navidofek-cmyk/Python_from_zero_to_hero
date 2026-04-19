# Lekce 67: Moduly a `import` systém

## 📦 Co je modul?

**Modul** = jeden Python soubor (`*.py`). Každý soubor je modul. **Balíček** = složka s moduly + `__init__.py`.

---

## 🛠️ Způsoby importu

```python
import math                           # celý modul
math.sqrt(4)

from math import sqrt, pi             # konkrétní jména
sqrt(4)

from math import sqrt as druha_odm    # alias
import math as m                       # alias modulu

from math import *                    # ❌ NEDĚLEJ — zaplaví namespace
```

---

## 🗺️ `sys.path` — kde Python hledá

```python
import sys
print(sys.path)
# ['', '/usr/lib/python3.12', '...']
```

Python prohledává v pořadí. Když najde modul, použije první.

---

## 📁 Balíček (package)

```
muj_balicek/
├── __init__.py          ← označuje složku jako balíček
├── modul_a.py
├── modul_b.py
└── pod_balicek/
    ├── __init__.py
    └── modul_c.py
```

```python
import muj_balicek.modul_a
from muj_balicek import modul_a
from muj_balicek.pod_balicek import modul_c
```

---

## 🆕 Namespace packages (bez `__init__.py`)

Python 3.3+ umí balíčky bez `__init__.py` — hodí se na **rozdělené** balíčky napříč adresáři. Zvláštní použití (pluginy, rozšíření).

Pro většinu případů: **napiš si `__init__.py`**, byť prázdný.

---

## 🎯 Co dát do `__init__.py`?

### Prázdný

```python
# nic — jen označení balíčku
```

### Re-export (zjednodušení API)

```python
# muj_balicek/__init__.py
from .modul_a import DulezitaTrida
from .modul_b import dulezita_funkce

__all__ = ["DulezitaTrida", "dulezita_funkce"]
```

Uživatel pak dělá:
```python
from muj_balicek import DulezitaTrida    # bez .modul_a
```

### `__all__` — kontrola `from x import *`

```python
__all__ = ["funkce_a", "funkce_b"]    # jen tyhle se exportují
```

---

## 🔧 `__init__.py` vs konvence

V moderním Pythonu doporučuju:
- Mít `__init__.py` (i prázdný)
- Re-exportovat veřejné API
- Nepřemíchávat moc logiky

---

## ⚠️ `from X import *` past

```python
from muj_balicek import *    # importuje co?
```

- Když je `__all__`, importuje to.
- Když není, importuje vše bez `_`.
- **Nikdy nedělej v knihovnách!** Zaplaví namespace.

---

## ✏️ Cvičení

1. **Vyrob balíček:** Vytvoř složku `pomocnici/` s `__init__.py`. Přidej `matematika.py` s funkcí `nasob(a, b)`. Importuj ji.
2. **Re-export:** V `__init__.py` udělej `from .matematika import nasob`. Importuj `from pomocnici import nasob`.
3. **Sys.path:** Vypiš `sys.path` — kde tvůj Python hledá moduly?
4. **Alias:** Importuj `numpy` (nebo `math`) jako `np` a něco vypiš.
