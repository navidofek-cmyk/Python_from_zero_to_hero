# Lekce 37: Dunder metody

## 🎭 Co jsou dunder metody?

**Dunder** = **D**ouble **UNDER**score, „dvojité podtržítko“ → metody jako `__init__`, `__str__`, `__eq__`. Říká se jim taky **magické metody**.

Python je volá automaticky při různých operacích. Ty jen určuješ **jak se má tvoje třída chovat**.

---

## 🖼️ `__repr__` a `__str__` — textová podoba

```python
class Pes:
    def __init__(self, jmeno):
        self.jmeno = jmeno

    def __repr__(self):
        # Pro vývojáře — přesný popis (často: jak by se to dalo recreate)
        return f"Pes({self.jmeno!r})"

    def __str__(self):
        # Pro uživatele — hezky čitelný
        return f"Pejsek {self.jmeno}"


rex = Pes("Rex")
print(rex)         # používá __str__: "Pejsek Rex"
print(repr(rex))   # používá __repr__: "Pes('Rex')"
[rex]              # v seznamech se používá __repr__
```

**Pravidlo**: Vždy implementuj **aspoň `__repr__`**. `__str__` je bonus.

---

## ⚖️ Porovnání — `__eq__`, `__lt__`, atd.

```python
class Bod:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, other):
        if not isinstance(other, Bod):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)


Bod(1, 2) == Bod(1, 2)    # True
Bod(1, 2) < Bod(2, 0)     # True
sorted([Bod(3,3), Bod(1,1), Bod(2,2)])   # funguje díky __lt__
```

| Metoda | Operátor |
|---|---|
| `__eq__` | `==` |
| `__ne__` | `!=` (často generované z `__eq__`) |
| `__lt__` | `<` |
| `__le__` | `<=` |
| `__gt__` | `>` |
| `__ge__` | `>=` |

**Tip**: Použij `@functools.total_ordering` — z `__eq__` + `__lt__` ti dogeneruje zbytek.

---

## #️⃣ `__hash__` — hashovatelnost

Aby objekt mohl být klíčem ve `dict` nebo prvkem v `set`, musí mít `__hash__`.

```python
class Bod:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)
    def __hash__(self):
        return hash((self.x, self.y))

s = {Bod(1, 2), Bod(1, 2)}    # jen JEDEN bod (jsou rovné)
```

⚠️ **Pravidlo**: Když přepíšeš `__eq__`, **musíš** přepsat i `__hash__` (jinak ti Python nastaví `None` = neměnný).

Pravidlo hashe: pokud `a == b`, tak `hash(a) == hash(b)`.

---

## 📏 `__len__`, `__bool__`

```python
class Vozik:
    def __init__(self):
        self.polozky = []

    def __len__(self):
        return len(self.polozky)

    def __bool__(self):
        return len(self.polozky) > 0

v = Vozik()
len(v)      # 0
bool(v)     # False
if not v:
    print("Vozík je prázdný")
```

Bez `__bool__` se použije `__len__` (0 = False).

---

## 🔁 `__iter__`, `__next__` — iterace

```python
class Odpocet:
    def __init__(self, od):
        self.od = od

    def __iter__(self):
        self.aktualni = self.od
        return self

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

(Více v lekci 51.)

---

## 🚪 `__contains__` — operátor `in`

```python
class Skupina:
    def __init__(self, lide):
        self.lide = lide

    def __contains__(self, kdo):
        return kdo in self.lide

s = Skupina(["Anna", "Bob"])
"Anna" in s        # True
```

---

## 🏃 `__call__` — volání instance jako funkce

```python
class Pricitac:
    def __init__(self, kolik):
        self.kolik = kolik

    def __call__(self, x):
        return x + self.kolik

p = Pricitac(10)
p(5)         # 15  ← jako funkce!
```

---

## 🎯 Plný seznam (zkráceně)

| Metoda | K čemu |
|---|---|
| `__init__` | konstruktor |
| `__del__` | destruktor (málokdy potřebné) |
| `__repr__`, `__str__` | text |
| `__eq__`, `__lt__`, ... | porovnání |
| `__hash__` | hashovatelnost |
| `__len__`, `__bool__` | délka, pravdivost |
| `__iter__`, `__next__` | iterace |
| `__contains__` | `in` |
| `__call__` | `()` |
| `__add__`, `__mul__`, ... | aritmetika (lekce 38) |
| `__getitem__`, `__setitem__` | `[]` (lekce 38) |
| `__enter__`, `__exit__` | `with` (lekce 46) |

---

## ✏️ Cvičení

1. **Repr + str:** Třída `Kniha(nazev, autor)` s `__repr__` a `__str__`.
2. **Eq:** Implementuj `__eq__` pro `Bod(x, y)`.
3. **Hash:** Přidej `__hash__` aby šel `Bod` použít v setu.
4. **Total ordering:** Použij `@functools.total_ordering` na `Verze(major, minor, patch)`.
5. **Call:** Třída `Stopky` co po každém volání vrátí čas od posledního volání.
