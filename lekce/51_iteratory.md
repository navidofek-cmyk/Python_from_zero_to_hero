# Lekce 51: Iterátory

## 🚂 Co je iterátor?

**Iterátor** = něco, z čeho můžeš brát hodnoty **jednu po druhé** přes `next()`. Když dojde, vyhodí `StopIteration`.

```python
seznam = [1, 2, 3]
it = iter(seznam)        # iterátor

next(it)    # 1
next(it)    # 2
next(it)    # 3
next(it)    # ❌ StopIteration
```

`for` smyčka pod kapotou dělá přesně tohle.

---

## 🔄 Iterable vs iterator

| | Iterable | Iterator |
|---|---|---|
| Co je | „Dá se z toho iterovat“ | „Aktuálně iteruje“ |
| Příklady | list, tuple, set, dict, str | výsledek `iter(x)`, generátor |
| Metoda | `__iter__` | `__iter__` + `__next__` |

```python
[1, 2, 3]              # iterable (NE iterator)
iter([1, 2, 3])        # iterator
```

---

## 🛠️ Vlastní iterátor

```python
class Odpocet:
    def __init__(self, od: int):
        self.od = od

    def __iter__(self):
        self.aktualni = self.od
        return self                  # iterátor jsem já

    def __next__(self):
        if self.aktualni < 0:
            raise StopIteration
        x = self.aktualni
        self.aktualni -= 1
        return x


for i in Odpocet(3):
    print(i)
# 3, 2, 1, 0
```

---

## 🎯 Iterable bez stavu

Když chceš, aby `for` šel **vícekrát**, oddělíš iterable od iteratoru:

```python
class Range:
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return Iterator(self.n)


class Iterator:
    def __init__(self, n):
        self.i = 0
        self.n = n

    def __iter__(self):
        return self

    def __next__(self):
        if self.i >= self.n:
            raise StopIteration
        x = self.i
        self.i += 1
        return x


r = Range(3)
list(r)   # [0, 1, 2]
list(r)   # [0, 1, 2]   (znovu od začátku)
```

V praxi to ale řeší **generátory** (lekce 52) mnohem elegantněji.

---

## 🎨 Užitečné funkce s iterátory

```python
iter([1,2,3])            # iterator z iterable
next(it)                 # další prvek
next(it, default)        # další nebo default (když StopIteration)

list(it)                 # vyčerpá do seznamu
sum(it), max(it), min(it)
```

---

## 🪜 Iterace v zákulisí

```python
for x in seznam:
    ...

# Je v podstatě:

it = iter(seznam)
while True:
    try:
        x = next(it)
    except StopIteration:
        break
    ...
```

---

## ✏️ Cvičení

1. **Odpocet:** Implementuj jako výše.
2. **Sudá:** Iterátor co vrací sudá čísla od 0.
3. **Cyklický:** Iterátor co donekonečna opakuje seznam.
4. **Iter + next:** Z manuálně iteruj seznam pomocí `iter` a `next`.
