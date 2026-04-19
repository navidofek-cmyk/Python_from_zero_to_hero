# Lekce 39: `__slots__` — paměť a rychlost

## 💾 Co `__slots__` dělá?

Defaultně každá instance má **slovník `__dict__`** kam si ukládá atributy. To je flexibilní (můžeš kdykoli přidat nový atribut), ale **žere paměť**.

`__slots__` říká: „Tato třída bude mít JEN tyto atributy. Žádný `__dict__`.“

```python
class Pes:
    __slots__ = ("jmeno", "vek")

    def __init__(self, jmeno, vek):
        self.jmeno = jmeno
        self.vek = vek

rex = Pes("Rex", 5)
print(rex.jmeno)         # Rex

rex.barva = "hnědá"      # ❌ AttributeError!
```

---

## 📊 Úspora paměti

```python
import sys

class S_dict:
    def __init__(self):
        self.x = 1
        self.y = 2

class S_slots:
    __slots__ = ("x", "y")
    def __init__(self):
        self.x = 1
        self.y = 2

print(sys.getsizeof(S_dict()) + sys.getsizeof(S_dict().__dict__))  
# ~280 bytů

print(sys.getsizeof(S_slots()))   
# ~48 bytů — 6x méně!
```

Při milionu instancí to dělá rozdíl několik set MB.

---

## ⚡ Rychlost

Přístup k atributům je o ~25 % rychlejší. Pro běžné aplikace nevýznamné, pro hot loop výrazné.

---

## ⚠️ Pasti

### 1. Ztratíš `__dict__`

```python
rex = Pes("Rex", 5)
rex.__dict__   # ❌ AttributeError
```

### 2. Dědičnost

Pokud rodič nemá `__slots__`, potomek má pořád `__dict__`.

```python
class Zvire:
    pass     # nemá __slots__

class Pes(Zvire):
    __slots__ = ("jmeno",)

p = Pes()
p.cokoliv = 99   # ✅ projde — kvůli rodiči!
```

Dej `__slots__` do **všech** tříd v hierarchii.

### 3. Kolize s class atributy

```python
class Pes:
    __slots__ = ("jmeno",)
    jmeno = "default"   # ❌ ValueError při importu!
```

---

## 🎁 `dataclass(slots=True)` (Python 3.10+)

Místo ručního `__slots__`:

```python
from dataclasses import dataclass

@dataclass(slots=True)
class Pes:
    jmeno: str
    vek: int
```

Mnohem hezčí. Více v lekci 41.

---

## 🎯 Kdy `__slots__` použít?

✅ Třídy se **statickým seznamem atributů** a **mnoha instancemi**.
✅ Performance kritické (hot loop, velké datasety).
✅ Domain modely (zákazníci, body, transakce).

❌ Třídy které potřebují flexibilitu (přidat libovolný atribut).
❌ Když používáš multiple inheritance s ne-slot třídami.

---

## ✏️ Cvičení

1. **Pes se sloty:** Vyrob `Pes` s `__slots__ = ("jmeno", "vek")`. Zkus přidat nový atribut.
2. **Měření:** Vytvoř 100 000 instancí třídy s/bez `__slots__` a porovnej paměť (`sys.getsizeof` nebo `tracemalloc`).
3. **Dataclass slots:** Předělej `Bod(x, y)` na `@dataclass(slots=True)`.
4. **Dědičnost:** Vyrob hierarchii kde rodič NEMÁ slots, dítě ano. Vidíš, že stejně můžeš přidat atribut?
