# Lekce 52: Generátory s `yield`

## ⚡ Co je generátor?

**Generátor** je funkce, která místo `return` používá `yield`. **Pamatuje si stav** mezi voláními.

```python
def odpocet(od: int):
    while od >= 0:
        yield od         # ← „pošli ven a počkej“
        od -= 1


for i in odpocet(3):
    print(i)
# 3, 2, 1, 0
```

Tohle je **mnohem kratší** než vlastní iterátor z lekce 51!

---

## 🔍 Jak to funguje

Když zavoláš `odpocet(3)`, **funkce se NEVYKONÁ** — vrátí ti **generátorový objekt**.

```python
g = odpocet(3)
print(g)              # <generator object ...>

next(g)               # 3   ← teď se kód spustí až po první yield
next(g)               # 2
next(g)               # 1
next(g)               # 0
next(g)               # ❌ StopIteration
```

Kód mezi `yield` se spustí až **mezi voláními `next`**.

---

## 💎 Proč generátory?

### 1. Líné vyhodnocení (lazy)

```python
def cisla():
    n = 0
    while True:
        yield n          # nekonečně!
        n += 1

# Žádný problém s pamětí — nepočítá se nic, dokud nevoláš
for x in cisla():
    if x > 5:
        break
    print(x)
```

### 2. Úspora paměti

```python
# ❌ Drahé — vyrobí celý seznam
suma = sum([x*x for x in range(10_000_000)])

# ✅ Generátor — počítá za pochodu
suma = sum(x*x for x in range(10_000_000))
```

### 3. Streamování dat

```python
def cti_radky(soubor):
    with open(soubor) as f:
        for radek in f:
            yield radek.strip()

# Pracuje i s 10GB souborem — nenačte vše do paměti
for r in cti_radky("velky.txt"):
    zpracuj(r)
```

---

## 🎯 Generator expression — výraz

Místo `[...]` použij `(...)`:

```python
ctverce = (x*x for x in range(10))   # generátor
```

V argumentu funkce nemusíš vnitřní závorky:
```python
sum(x*x for x in range(10))
```

---

## 🔧 Užitečný trik — pipeline

Můžeš generátory **řetězit**:

```python
def cisla():
    for i in range(100):
        yield i

def jen_suda(it):
    for x in it:
        if x % 2 == 0:
            yield x

def na_druhou(it):
    for x in it:
        yield x * x


for x in na_druhou(jen_suda(cisla())):
    print(x)
```

Každý generátor zpracovává prvek po prvku — žádné mezivýsledky v paměti!

---

## 🎁 `return` v generátoru

`return` v generátoru znamená `StopIteration`:

```python
def gen():
    yield 1
    yield 2
    return            # konec
    yield 3           # nikdy

list(gen())   # [1, 2]
```

---

## ✏️ Cvičení

1. **Odpocet generátor:** Naprogramuj odpocet pomocí `yield`.
2. **Fibonacci generátor:** Generátor co vrací fibonacciho čísla donekonečna.
3. **Pipeline:** Vyrob generátor čísel, filtr lichých, mocnina.
4. **Velký soubor:** Generátor co čte řádky souboru.
5. **Sliding window:** Generátor co vrací tuple `(prev, current)` při procházení seznamu.
