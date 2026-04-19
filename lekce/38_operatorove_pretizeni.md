# Lekce 38: Operátorové přetížení

Pokračování dunderu — teď **aritmetické a indexové operátory**.

## ➕ Aritmetika — `__add__`, `__sub__`, ...

```python
class Vektor:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        return Vektor(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vektor(self.x - other.x, self.y - other.y)

    def __mul__(self, skalar):
        return Vektor(self.x * skalar, self.y * skalar)

    def __repr__(self):
        return f"Vektor({self.x}, {self.y})"


a = Vektor(1, 2)
b = Vektor(3, 4)
print(a + b)        # Vektor(4, 6)
print(a - b)        # Vektor(-2, -2)
print(a * 3)        # Vektor(3, 6)
```

| Operátor | Metoda |
|---|---|
| `+` | `__add__` |
| `-` | `__sub__` |
| `*` | `__mul__` |
| `/` | `__truediv__` |
| `//` | `__floordiv__` |
| `%` | `__mod__` |
| `**` | `__pow__` |
| `-x` | `__neg__` |
| `abs(x)` | `__abs__` |

### Pravostranné — když je tvůj objekt vpravo

```python
3 * a    # → int.__mul__(3, a) selže → Vektor.__rmul__(a, 3)
```

Implementuj `__rmul__` aby `3 * a` fungovalo:

```python
def __rmul__(self, skalar):
    return self * skalar
```

### In-place — `+=`, `*=`

```python
def __iadd__(self, other):
    self.x += other.x
    self.y += other.y
    return self
```

Bez `__iadd__` Python použije `__add__` a vyrobí novou instanci.

---

## 🗂️ Indexace — `__getitem__`, `__setitem__`, `__delitem__`

```python
class Matice:
    def __init__(self):
        self._data = {}

    def __getitem__(self, klic):
        # klic může být cokoli — i tuple (i, j)!
        return self._data.get(klic, 0)

    def __setitem__(self, klic, hodnota):
        self._data[klic] = hodnota

    def __delitem__(self, klic):
        del self._data[klic]


m = Matice()
m[1, 2] = 99      # 2D indexace!
print(m[1, 2])    # 99
print(m[5, 5])    # 0
del m[1, 2]
```

`__getitem__` umožňuje i **slicing**:
```python
def __getitem__(self, klic):
    if isinstance(klic, slice):
        ...
```

---

## 📏 Porovnávací bonus

Místo psaní 6 metod použij `@total_ordering`:

```python
from functools import total_ordering

@total_ordering
class Verze:
    def __init__(self, major, minor):
        self.major = major
        self.minor = minor

    def __eq__(self, other):
        return (self.major, self.minor) == (other.major, other.minor)

    def __lt__(self, other):
        return (self.major, self.minor) < (other.major, other.minor)


Verze(1, 5) <= Verze(2, 0)    # True (i bez psaní __le__!)
```

---

## 🌗 Bitové operátory

```python
__and__       # &
__or__        # |
__xor__       # ^
__lshift__    # <<
__rshift__    # >>
__invert__    # ~
```

`pathlib.Path` používá `/`: `Path("a") / "b"`.

---

## 🎨 Praktický příklad — Peníze

```python
class Penize:
    def __init__(self, castka, mena="CZK"):
        self.castka = castka
        self.mena = mena

    def __add__(self, other):
        if self.mena != other.mena:
            raise ValueError("Nelze sčítat různé měny")
        return Penize(self.castka + other.castka, self.mena)

    def __mul__(self, n):
        return Penize(self.castka * n, self.mena)

    def __repr__(self):
        return f"{self.castka} {self.mena}"


cena = Penize(100) + Penize(50)
print(cena * 3)       # 450 CZK
```

---

## ✏️ Cvičení

1. **Vektor:** Implementuj `Vektor` s `+`, `-`, `*` (skalárem), `__repr__`, `__eq__`.
2. **Peníze:** Třída `Penize` co umí sčítat (jen stejné měny) a násobit číslem.
3. **Polynom:** Třída `Polynom` co umí `+` a `*` polynomy.
4. **Indexace:** Třída `MyList` obalující list, ale s tím, že `[-1]` vrací `None` místo posledního prvku.
5. **Total ordering:** Implementuj `Verze(major, minor, patch)` s `@total_ordering`.
