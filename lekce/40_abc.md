# Lekce 40: Abstraktní třídy (`abc`)

## 🚧 Co je abstraktní třída?

**Abstraktní třída** je **plán, který nelze postavit přímo** — musíš ho dodědit a doplnit.

Příklad: `Zvire` je abstraktní, `Pes`/`Kocka` jsou konkrétní. Abstraktní třída říká: „Každé moje dítě musí mít metodu `zvuk()`.“

```python
from abc import ABC, abstractmethod

class Zvire(ABC):
    @abstractmethod
    def zvuk(self) -> str:
        ...                              # tělo nemusíš psát

class Pes(Zvire):
    def zvuk(self) -> str:
        return "Haf!"

class Kocka(Zvire):
    pass                                  # ❌ chybí zvuk!

z = Zvire()      # ❌ TypeError — abstraktní třídu nelze instantiovat
p = Pes()        # ✅ OK
k = Kocka()      # ❌ TypeError — chybí abstract metoda zvuk
```

- `ABC` (Abstract Base Class) = označí třídu jako abstraktní
- `@abstractmethod` = označí metodu jako povinnou pro děti

---

## 🎯 K čemu to je?

### 1. Vynucení rozhraní

Když řekneš „každý plugin musí mít metody `start`, `stop`, `status`“, abstraktní třída tě donutí to dodržet.

```python
class Plugin(ABC):
    @abstractmethod
    def start(self): ...

    @abstractmethod
    def stop(self): ...

    @abstractmethod
    def status(self) -> str: ...
```

### 2. Dokumentace záměru

Když vidíš `class X(ABC)`, hned víš, že je to **plán pro odvozené**, ne hotová věc.

### 3. Polymorfismus s typovou kontrolou

Můžeš anotovat `def zpracuj(z: Zvire)` a víš, že každé `Zvire` má `zvuk()`.

---

## 🛠️ Abstraktní vlastnosti a classmethods

```python
class Tvar(ABC):
    @property
    @abstractmethod
    def obsah(self) -> float:
        ...

    @classmethod
    @abstractmethod
    def jednotkova(cls):
        ...
```

Pořadí: `@abstractmethod` **dolů**, ostatní dekorátory nad ním.

---

## ⚖️ ABC vs Protocol (lekce 50)

| ABC | Protocol |
|---|---|
| Musíš **explicitně dědit** | Stačí, když máš metody |
| Klasické OOP | Duck typing s typovou kontrolou |
| Kontrola při vytvoření | Kontrola při použití (mypy) |
| Funguje za běhu | Hlavně typová kontrola |

```python
# ABC — musíš dědit
class Pes(Zvire):
    ...

# Protocol — stačí mít metody
class Zvuk(Protocol):
    def zvuk(self) -> str: ...

class Pes:    # nedědí, ale "vypadá" jako Zvuk
    def zvuk(self): return "Haf!"
```

V moderním Pythonu jsou **Protocoly** často hezčí (volnější, „pythoničtější“).

---

## 🎯 Užitečné ABC ze stdlib

```python
from collections.abc import Iterable, Iterator, Mapping, Sized

isinstance([1,2,3], Iterable)     # True
isinstance({"a":1}, Mapping)      # True
```

Když napíšeš funkci, která jen **iteruje** přes vstup, anotuj jí jako `Iterable`, ne `list`.

```python
def soucet(cisla: Iterable[int]) -> int:
    return sum(cisla)
```

---

## ✏️ Cvičení

1. **Tvar:** Abstraktní `Tvar` s `obsah()` a `obvod()`. Konkrétní `Kruh`, `Obdelnik`.
2. **Plugin:** ABC `Plugin` s `start`, `stop`, `status`. Vyrob 2 konkrétní pluginy.
3. **Zaměstnanec:** ABC `Zamestnanec` s `vypocti_plat()`. `Hodinovy(hodiny, sazba)` a `Mesicni(plat)`.
4. **Test ABC:** Zkus instantiovat abstraktní třídu — co se stane?
5. **Iterable:** Napiš funkci `soucet(cisla: Iterable[int]) -> int`. Otestuj na list, tuple, generator.
