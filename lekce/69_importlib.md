# Lekce 69: `importlib`, dynamické importy, lazy import

## 🪄 `importlib.import_module`

Když znáš jméno modulu **až za běhu**:

```python
import importlib

jmeno = "math"
modul = importlib.import_module(jmeno)
print(modul.sqrt(16))    # 4.0
```

Místo `__import__` — `import_module` je čitelnější.

---

## 🎯 Plugin systém

```python
def nacti_plugin(jmeno: str):
    return importlib.import_module(f"plugins.{jmeno}")


for jmeno in ["audio", "video", "siet"]:
    plugin = nacti_plugin(jmeno)
    plugin.start()
```

---

## 🔁 Reload modulu

```python
import importlib
importlib.reload(muj_modul)
```

Hodí se při vývoji. V produkci se vyhněte (špatně se kombinuje s referencemi).

---

## 💤 Lazy import — odlož import až na potřebu

```python
def velka_funkce():
    import numpy as np    # jen když je potřeba
    return np.array([1, 2, 3])
```

**Účel:**
- Zrychlit start aplikace
- Ušetřit paměť, když se feature nepoužije
- Vyřešit kruhový import

---

## 🎁 `__getattr__` na úrovni modulu (3.7+)

```python
# muj_balicek/__init__.py
def __getattr__(name):
    if name == "drahá_věc":
        from .drahe import VelkaVec
        return VelkaVec()
    raise AttributeError(name)


# Použití:
from muj_balicek import drahá_věc    # importuje až teď
```

Takhle to dělá NumPy, Pandas a jiné knihovny — některé submoduly jsou lazy.

---

## ✏️ Cvičení

1. **Dynamic:** Importuj `os`, `sys`, `math` přes `importlib.import_module` ve smyčce.
2. **Plugin:** Vyrob složku `pluginy/` s 2 soubory. Načti je dynamicky podle jména.
3. **Lazy:** Funkce co importuje `requests` až při prvním volání.
