# Lekce 102: Návrhové vzory pythonicky

## 🎯 Co jsou návrhové vzory?

Návrhové vzory jsou osvědčená řešení opakujících se problémů. V Pythonu je often implementujeme jinak než v Javě — díky duck typingu, funkcím jako first-class objects a modulovému systému.

---

## 1. Strategy — přes funkce

Místo hierarchie tříd stačí předat funkci.

```python
from typing import Callable

Sorter = Callable[[list], list]

def bubble_sort(data: list) -> list: ...
def quick_sort(data: list) -> list: ...

def zpracuj(data: list, sorter: Sorter) -> list:
    return sorter(data)

zpracuj([3, 1, 2], sorted)          # vestavěný sorted jako strategie
zpracuj([3, 1, 2], bubble_sort)
```

---

## 2. Singleton — přes modul

Python modul je singleton ze své podstaty — importuje se jednou.

```python
# config.py  ← toto JE singleton
DEBUG = False
DB_URL = "sqlite:///app.db"

# použití
import config
config.DEBUG = True
```

Pokud potřebuješ třídu:

```python
class _Config:
    debug: bool = False

config = _Config()   # jediná instance v modulu
```

---

## 3. Factory — přes `__init_subclass__`

```python
class Tvar:
    _registry: dict[str, type] = {}

    def __init_subclass__(cls, typ: str, **kw):
        super().__init_subclass__(**kw)
        Tvar._registry[typ] = cls

    @classmethod
    def vytvor(cls, typ: str, **kw) -> "Tvar":
        if typ not in cls._registry:
            raise ValueError(f"Neznámý typ: {typ}")
        return cls._registry[typ](**kw)

class Kruh(Tvar, typ="kruh"):
    def __init__(self, r: float): self.r = r
    def __repr__(self): return f"Kruh(r={self.r})"

class Ctverec(Tvar, typ="ctverec"):
    def __init__(self, a: float): self.a = a
    def __repr__(self): return f"Ctverec(a={self.a})"

t = Tvar.vytvor("kruh", r=5)     # → Kruh(r=5)
```

---

## 4. Observer — přes callable seznam

```python
from typing import Callable

class Udalost:
    def __init__(self):
        self._posluchaci: list[Callable] = []

    def prihlas(self, fn: Callable) -> None:
        self._posluchaci.append(fn)

    def odprihlas(self, fn: Callable) -> None:
        self._posluchaci.remove(fn)

    def spust(self, *args, **kwargs) -> None:
        for fn in self._posluchaci:
            fn(*args, **kwargs)

# použití
on_login = Udalost()
on_login.prihlas(lambda uzivatel: print(f"Přihlášen: {uzivatel}"))
on_login.prihlas(lambda uzivatel: print(f"[LOG] login: {uzivatel}"))
on_login.spust("Anna")
```

---

## 5. State — přes třídy stavů

```python
from __future__ import annotations
from abc import ABC, abstractmethod

class Stav(ABC):
    @abstractmethod
    def zpracuj(self, kontext: "Objednavka") -> None: ...

class Cekajici(Stav):
    def zpracuj(self, obj: "Objednavka") -> None:
        print("Objednávka schválena")
        obj.stav = Schvalena()

class Schvalena(Stav):
    def zpracuj(self, obj: "Objednavka") -> None:
        print("Objednávka odeslána")
        obj.stav = Odeslana()

class Odeslana(Stav):
    def zpracuj(self, obj: "Objednavka") -> None:
        print("Objednávka již odeslána, nelze pokračovat")

class Objednavka:
    def __init__(self):
        self.stav: Stav = Cekajici()

    def dalsi_krok(self) -> None:
        self.stav.zpracuj(self)
```

---

## 6. Visitor — přes `singledispatch`

Místo dvojité dispatch hierarchie stačí `functools.singledispatch`.

```python
from functools import singledispatch

class Cislo:
    def __init__(self, h: float): self.h = h

class Text:
    def __init__(self, s: str): self.s = s

@singledispatch
def tiskni(uzel):
    raise TypeError(f"Neznámý typ: {type(uzel)}")

@tiskni.register
def _(uzel: Cislo) -> None:
    print(f"Číslo: {uzel.h}")

@tiskni.register
def _(uzel: Text) -> None:
    print(f"Text: '{uzel.s}'")

tiskni(Cislo(42))   # → Číslo: 42
tiskni(Text("hi"))  # → Text: 'hi'
```

---

## 🐍 Pythonic shrnutí vzorů

| Vzor | Java způsob | Python způsob |
|------|------------|---------------|
| Strategy | rozhraní + třídy | funkce / lambda |
| Singleton | privátní konstruktor | modul nebo instance v modulu |
| Factory | factory třída | `__init_subclass__` / dict |
| Observer | interface + seznam | seznam callable |
| State | abstraktní třída | abstraktní třída (stejné) |
| Visitor | dvojitá dispatch | `singledispatch` |

---

## 📝 Shrnutí

- Python funkce jsou first-class — Strategy, Command, Callback jsou triviální
- Moduly jsou přirozené singletony
- `__init_subclass__` umožňuje self-registraci tříd (Factory bez registrace ručně)
- `singledispatch` nahrazuje Visitor pattern elegantně

---

## 🏋️ Cvičení

1. Přidej do Factory vzoru typ `"trojuhelnik"` bez změny třídy `Tvar`.
2. Rozšiř Observer — přidej prioritu posluchačům (vyšší priorita = dříve zavolán).
3. Implementuj State vzor pro semafor: `Cervena → Zelena → Oranzova → Cervena`.
