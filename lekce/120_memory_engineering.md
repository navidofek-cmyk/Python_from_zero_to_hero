# Lekce 120: Memory Engineering

Správa paměti v Pythonu je automatická (garbage collector), ale to neznamená, že nemusíme myslet na memory leaks, zbytečnou alokaci nebo fragmentaci.

---

## `sys.getsizeof` — velikost objektu

`sys.getsizeof` vrátí velikost objektu v bytech — **pouze přímou alokaci**, ne rekurzivně.

```python
import sys

print(sys.getsizeof(42))           # int: ~28 bytů
print(sys.getsizeof("ahoj"))       # str: 53 bytů
print(sys.getsizeof([1, 2, 3]))    # list: 88 bytů (jen kontejner!)
print(sys.getsizeof((1, 2, 3)))    # tuple: 72 bytů

# Pozor: getsizeof nepočítá obsah kontejneru
seznam = [list(range(1000)) for _ in range(100)]
print(sys.getsizeof(seznam))       # Malé číslo! Jen pointerů
```

Rekurzivní výpočet:

```python
import sys
from collections.abc import Iterable

def deep_sizeof(obj: object, navstivene: set[int] | None = None) -> int:
    """Rekurzivní sizeof — počítá i obsah kontejnerů."""
    if navstivene is None:
        navstivene = set()
    obj_id = id(obj)
    if obj_id in navstivene:
        return 0
    navstivene.add(obj_id)
    velikost = sys.getsizeof(obj)
    if isinstance(obj, dict):
        velikost += sum(deep_sizeof(k, navstivene) + deep_sizeof(v, navstivene)
                        for k, v in obj.items())
    elif isinstance(obj, Iterable) and not isinstance(obj, (str, bytes)):
        velikost += sum(deep_sizeof(i, navstivene) for i in obj)
    return velikost
```

---

## `tracemalloc` — sledování alokací

`tracemalloc` je **stdlib** modul pro sledování alokací paměti. Ukáže kde se paměť alokuje.

```python
import tracemalloc

tracemalloc.start()

# Kód, který chceme sledovat
data = [{"klic": i, "hodnota": "x" * 100} for i in range(10_000)]

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")

print("Top 5 alokací:")
for stat in top_stats[:5]:
    print(stat)

tracemalloc.stop()
```

Porovnání dvou snapshotů (detekce leaku):

```python
import tracemalloc

tracemalloc.start()
snap1 = tracemalloc.take_snapshot()

# Simulace leaku
leaky_cache: list[bytes] = []
for _ in range(1000):
    leaky_cache.append(b"data" * 1000)

snap2 = tracemalloc.take_snapshot()
top_diff = snap2.compare_to(snap1, "lineno")

print("Největší nárůst alokací:")
for stat in top_diff[:3]:
    print(stat)
```

---

## `weakref` — slabé reference

Normální reference zabrání garbage collectoru uvolnit objekt. Slabá reference (weak reference) tuto překážku nevytváří.

```python
import weakref
import gc

class Tezky:
    def __init__(self, nazev: str) -> None:
        self.nazev = nazev

    def __del__(self) -> None:
        print(f"{self.nazev} byl uvolněn z paměti")

# Normální reference — objekt žije
obj = Tezky("A")
silna = obj
del obj           # Objekt stále žije (silna ho drží)
del silna         # Teprve teď je uvolněn

# Slabá reference — nepřekáží GC
obj2 = Tezky("B")
slaba = weakref.ref(obj2)
print(slaba())    # <__main__.Tezky object>
del obj2
gc.collect()
print(slaba())    # None — objekt byl uvolněn
```

`WeakValueDictionary` — cache bez leaku:

```python
import weakref

class Dokument:
    def __init__(self, id_: int) -> None:
        self.id_ = id_

cache: weakref.WeakValueDictionary[int, Dokument] = weakref.WeakValueDictionary()

doc = Dokument(1)
cache[1] = doc
print(cache.get(1))   # Dokument

del doc
import gc; gc.collect()
print(cache.get(1))   # None — automaticky odstraněn z cache
```

---

## Memory Leaks — časté vzory

| Vzor | Příčina | Řešení |
|---|---|---|
| Globální seznam/dict | Přidávání bez mazání | Bounded cache, LRU |
| Cyklické reference s `__del__` | GC neumí uvolnit | Přerušit cyklus, `weakref` |
| Closure drží velká data | Funkce uzavírá proměnnou | Předat jako argument |
| Thread-local storage | Vlákno nikdy neskončí | `threading.local()` s čištěním |
| Callback registrace | Event listener nikdy odhlášen | Weak callbacks |

```python
# Problém: closure drží celý seznam
def udelej_funkci(data: list[int]) -> object:
    # 'data' je uzavřena — GC ho neuvolní dokud funkce žije
    def fn() -> int:
        return sum(data)
    return fn

# Řešení: předat jen to, co potřebujeme
def udelej_funkci_ok(data: list[int]) -> object:
    soucet = sum(data)   # Vypočítáme hned, data neudrží
    def fn() -> int:
        return soucet
    return fn
```

---

## `__slots__` — úspora paměti

Bez `__slots__` každá instance třídy má slovník `__dict__` (~200 bytů navíc).

```python
import sys

class BezSlots:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

class SeSlots:
    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

a = BezSlots(1, 2)
b = SeSlots(1, 2)

print(f"BezSlots: {sys.getsizeof(a)} B + {sys.getsizeof(a.__dict__)} B (dict)")
print(f"SeSlots:  {sys.getsizeof(b)} B (žádný dict)")
```

Při milionech instancí je rozdíl výrazný.

---

## Object Graph analýza s `gc`

```python
import gc

# Najít všechny instance konkrétní třídy
class Muj:
    pass

a = Muj()
b = Muj()

gc.collect()
instance = [obj for obj in gc.get_objects() if isinstance(obj, Muj)]
print(f"Živých instancí Muj: {len(instance)}")

# Detekce cyklů
gc.set_debug(gc.DEBUG_LEAK)
gc.collect()
```

---

## Shrnutí

- `sys.getsizeof` měří přímou velikost — pro kontejnery nestačí, použij rekurzivní verzi
- `tracemalloc` (stdlib) ukáže kde se alokuje — klíčové pro ladění leaků
- `weakref` umožňuje cache bez zadržování objektů
- `__slots__` ušetří ~200 B na instanci — vyplatí se při milionech objektů
- Časté leaky: globální cache bez limitu, uzavřené proměnné v closure, neodhlášené callbacky

---

## Cvičení

1. Pomocí `tracemalloc` změř, kolik paměti alokuje 100 000 instancí třídy s `__slots__` vs bez.
2. Napiš třídu `BoundedCache` — maximálně 100 položek, při přeplnění vymaže nejstarší.
3. Simuluj memory leak (přidávání do globálního seznamu), detekuj ho pomocí dvou snapshotů `tracemalloc`.
4. Implementuj weak-callback systém: registrace callbacků jako slabých referencí, automatické odhlášení.
