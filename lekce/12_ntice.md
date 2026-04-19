# Lekce 12: N-tice (`tuple`)

## 🔒 Co je n-tice?

**Tuple** je jako **seznam, ale zamčený na klíč**. Když ho jednou vyrobíš, **nemůžeš ho měnit**.

```python
souradnice = (50.08, 14.42)   # Praha
barva_rgb = (255, 100, 50)
prazdna = ()
jednoprvkova = (42,)           # ⚠️ čárka je nutná!
```

Bez závorek to taky funguje (čárky stačí):
```python
bod = 5, 7     # tuple (5, 7)
```

---

## 🤔 K čemu n-tice, když mám seznamy?

1. **Bezpečnost** — víš, že nikdo nezmění obsah.
2. **Rychlost** — tuple jsou trošku rychlejší.
3. **Klíč ve slovníku** — list nemůže být klíčem ve `dict`/`set`, tuple ano.
4. **Vícenásobné návraty** z funkcí.

```python
def min_max(cisla):
    return min(cisla), max(cisla)   # vrací tuple

a, b = min_max([3, 1, 4, 1, 5])     # rozbalení
```

---

## 📦 Packing / unpacking — balení a rozbalení

### Packing (zabalení)
```python
osoba = "Eliška", 10, "Praha"   # tuple ze tří věcí
```

### Unpacking (rozbalení)
```python
jmeno, vek, mesto = osoba
print(jmeno)   # Eliška
```

Musí **sedět počet**! Jinak chyba.

### Hvězdička `*` — sbírá zbytek
```python
prvni, *zbytek = [1, 2, 3, 4, 5]
# prvni=1, zbytek=[2, 3, 4, 5]

prvni, *stred, posledni = [1, 2, 3, 4, 5]
# prvni=1, stred=[2, 3, 4], posledni=5
```

### Záměna proměnných (klasický trik!)
```python
a, b = 1, 2
a, b = b, a    # vyměnili jsme je BEZ pomocné proměnné! ✨
```

---

## 🏷️ `namedtuple` — tuple s nálepkami

Obyčejný tuple je `(50.08, 14.42)`. Ale co je první? Co druhé? Pomůže `namedtuple`:

```python
from collections import namedtuple

Bod = namedtuple("Bod", ["x", "y"])
p = Bod(50.08, 14.42)

print(p.x, p.y)        # 50.08 14.42
print(p[0])            # i jako tuple to funguje
```

V moderním Pythonu místo toho často používáme `dataclass` (lekce 41) nebo `NamedTuple`:

```python
from typing import NamedTuple

class Bod(NamedTuple):
    x: float
    y: float
```

---

## 🛠️ Operace s tuple

```python
t = (1, 2, 3)
len(t)           # 3
2 in t           # True
t + (4, 5)       # (1, 2, 3, 4, 5)  (nová tuple, t se nemění)
t * 3            # (1, 2, 3, 1, 2, 3, 1, 2, 3)
t[0]             # 1
t.count(2)       # 1
t.index(3)       # 2
```

Žádné `append`, `remove`, `pop` — tuple je neměnná!

---

## ⚠️ Drobnosti

- `()` je prázdná tuple, `(5)` je jen číslo 5 v závorkách! Pro tuple s jedním prvkem **musíš čárku**: `(5,)`.
- I když nemůžeš měnit tuple, **můžeš měnit její vnitřek**, pokud je proměnný:
  ```python
  t = ([1, 2], [3, 4])
  t[0].append(99)     # ✅ funguje! Měníš seznam UVNITŘ.
  t[0] = [9, 9]       # ❌ TypeError! Měníš samotnou tuple.
  ```

---

## ✏️ Cvičení

1. **Souřadnice:** Vyrob tuple `(x, y)` souřadnice tvého města. Rozbal do dvou proměnných.
2. **Záměna:** Vyrob `a = "ahoj"`, `b = "svete"`. Vyměň je jedním řádkem.
3. **Funkce vracející tuple:** Napiš funkci `ctverec(strana)`, která vrátí tuple `(obvod, obsah)`.
4. **Hvězdička:** Máš seznam známek `[1, 2, 3, 4, 5]`. Rozbal tak, aby `prvni` mělo 1, `posledni` 5 a `stred` zbytek.
5. **NamedTuple:** Vytvoř `NamedTuple` `Pes` s atributy `jmeno`, `vek`, `plemeno`. Vyrob několik psů a vypiš je.
