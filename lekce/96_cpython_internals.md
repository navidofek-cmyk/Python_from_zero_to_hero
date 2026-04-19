# Lekce 96: CPython internals — bytecode, GC, refcounting

## 🤖 Jak Python opravdu funguje

Python (CPython) tvůj kód **nevykonává přímo**. Nejdřív ho **zkompiluje do bytecode**, ten pak interpretuje virtuální stroj.

```
zdroj.py → bytecode (.pyc) → CPython VM → výsledek
```

---

## 🔍 `dis` — vidíš bytecode

```python
import dis

def secti(a, b):
    return a + b

dis.dis(secti)
```

Výstup:
```
  2     RESUME                   0
  3     LOAD_FAST                a
        LOAD_FAST                b
        BINARY_OP                0 (+)
        RETURN_VALUE
```

To jsou **instrukce virtuálního stroje** Pythonu. Užitečné pro pochopení rychlosti.

---

## 🗑️ Garbage collector

CPython má **dva mechanismy**:

### 1. Reference counting

Každý objekt má počítadlo. Když klesne na 0 → smazat.

```python
a = [1, 2, 3]    # refcount(list) = 1
b = a            # refcount = 2
del b            # refcount = 1
del a            # refcount = 0 → smazáno
```

### 2. Garbage collector (pro cykly)

Reference counting **selže na cyklech**:
```python
a = []
b = []
a.append(b)
b.append(a)        # cyklus, oba mají refcount 1 ale nikdo zvenku je nedrží
```

Python má **cyklický GC** který tohle uklidí.

```python
import gc

gc.collect()       # ručně spustit
gc.disable()       # vypnout (rychlejší, ale leak)
gc.enable()
gc.get_count()
```

---

## ⚖️ `weakref` — slabé reference

Reference, která **nezvyšuje refcount**:

```python
import weakref

class Velka: pass

obj = Velka()
ref = weakref.ref(obj)

print(ref())       # <__main__.Velka object>
del obj
print(ref())       # None — automaticky vyčištěno
```

Užitečné pro cache, observers, parent references.

---

## 🏗️ Objektová struktura

V CPython **všechno je `PyObject`** — i čísla a stringy. Každý má:
- typ
- refcount
- vlastní data

To znamená, že `int(42)` zabere ~28 bytů (ne 8). Proto je NumPy/array efektivnější.

---

## ⚡ Optimizace v CPython 3.11+

CPython 3.11+ přinesl **„Faster CPython“** projekt:
- Specialized adaptive interpreter
- Inline caches
- Lepší startup
- Subinterpreters

3.13 přinesl free-threaded build (lekce 87).

---

## 🎯 Praktické důsledky

1. **Lokální proměnné jsou rychlejší** než globální (LOAD_FAST vs LOAD_GLOBAL).
2. **Atribut lookup je drahý** — cachuj v hot loopu.
3. **Drobná čísla jsou cached** (-5 až 256) — `is` na nich funguje.
4. **Stringy se internují** v některých případech.
5. **Cyklické reference fungují, ale GC je drahý** — vyhni se kde to jde.

---

## 🔬 `sys` introspekce

```python
import sys

sys.getrefcount(obj)         # počet referencí
sys.getsizeof(obj)            # velikost v bytech
sys.intern("ahoj")            # internuj string
```

---

## ✏️ Cvičení

1. **Dis:** Zkus `dis.dis()` na svou funkci. Co vidíš?
2. **Refcount:** Vypiš `sys.getrefcount` před/po přiřazení.
3. **Cycle:** Vyrob cyklus, pak `gc.collect()`.
4. **Weakref:** Vyrob weakref a sleduj kdy ho objekt přežije.
5. **Sizeof:** Změř velikost `int`, `str`, `list`, `dict`.
