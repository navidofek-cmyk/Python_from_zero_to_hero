# Lekce 94: Optimalizace

## 🎯 Hlavní triky

### 1. `__slots__` (lekce 39)

Pro třídy s mnoha instancemi — úspora paměti, mírné zrychlení.

### 2. Lokální proměnné

```python
# Pomalejší
for x in data:
    result.append(math.sqrt(x))

# Rychlejší (jméno se hledá lokálně)
sqrt = math.sqrt
append = result.append
for x in data:
    append(sqrt(x))
```

V hot loopu může být znát.

### 3. Comprehension > for + append

```python
# Pomalejší
result = []
for x in data:
    result.append(x * 2)

# Rychlejší
result = [x * 2 for x in data]

# Ještě rychlejší pokud nepotřebuješ list
result = (x * 2 for x in data)         # generátor
sum(x * 2 for x in data)
```

### 4. `set` / `dict` lookup místo `in list`

```python
# O(n)
if x in seznam: ...

# O(1)
if x in mnozina: ...
```

### 5. `str.join` místo `+=`

```python
# ❌ kvadratické
s = ""
for kus in kusy:
    s += kus

# ✅ lineární
s = "".join(kusy)
```

### 6. `enumerate` místo `range(len(...))`

```python
# Pomalejší + ošklivé
for i in range(len(data)):
    print(i, data[i])

# Rychlejší + hezčí
for i, x in enumerate(data):
    print(i, x)
```

---

## 🚀 NumPy vektorizace

```python
import numpy as np

# Pomalé — pure Python
ctverce = [x*x for x in range(1_000_000)]

# Rychlé — NumPy
arr = np.arange(1_000_000)
ctverce = arr ** 2
# 10–100× rychlejší
```

Pro číselné výpočty **vždy NumPy**.

---

## ⚡ Numba JIT

```bash
pip install numba
```

```python
from numba import jit

@jit(nopython=True)
def soucet(arr):
    s = 0
    for x in arr:
        s += x
    return s
```

Při prvním volání zkompiluje do nativního kódu. Pak je rychlost srovnatelná s C.

---

## 🎯 Cython, C rozšíření, PyPy

- **Cython** — Python s typy, kompiluje do C
- **PyO3** — psaní rozšíření v Rustu (lekce 95)
- **PyPy** — alternativní Python s JITem

---

## ⚠️ Co NEdělat

❌ Premature optimization
❌ Mikrooptimalizace bez měření
❌ Cache všeho (`@cache`) — paměť!
❌ Vyhnutí se pythonickému kódu kvůli teoretické rychlosti

---

## ✏️ Cvičení

1. **Comprehension vs for:** Změř rozdíl pro 1M prvků.
2. **Set vs list:** Změř `x in list_velky` vs `x in set_velky`.
3. **NumPy:** Spočítej součet čtverců 10M čísel — pure Python vs NumPy.
4. **Local var:** Změř rozdíl s lokální proměnnou v hot loopu.
