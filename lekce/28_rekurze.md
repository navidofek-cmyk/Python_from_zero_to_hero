# Lekce 28: Rekurze

## 🪞 Co je rekurze?

**Rekurze** = funkce **volá sebe sama**.

Jako když si stoupneš mezi dvě zrcadla — vidíš sám sebe, který vidí sám sebe, který...

```python
def odpocet(n):
    if n <= 0:           # ❗ KAŽDÁ rekurze MUSÍ mít konec!
        print("BUM!")
        return
    print(n)
    odpocet(n - 1)       # voláš sám sebe, ale s menším číslem

odpocet(3)
# 3
# 2
# 1
# BUM!
```

---

## 🛑 Pravidlo č. 1: Konec (base case)

**Každá rekurze musí mít podmínku, kdy přestane.** Jinak nekonečno → chyba.

```python
def faktorial(n):
    if n == 0:
        return 1            # ← BASE CASE
    return n * faktorial(n - 1)

faktorial(5)    # 120
```

Jak se to vyhodnotí:
```
faktorial(5) = 5 * faktorial(4)
             = 5 * 4 * faktorial(3)
             = 5 * 4 * 3 * faktorial(2)
             = 5 * 4 * 3 * 2 * faktorial(1)
             = 5 * 4 * 3 * 2 * 1 * faktorial(0)
             = 5 * 4 * 3 * 2 * 1 * 1
             = 120
```

---

## 🌳 Klasické příklady

### Fibonacciho čísla

```python
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

⚠️ Pomalé bez cache! Lepší s `@cache`:
```python
from functools import cache

@cache
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

### Procházení vnořeného seznamu

```python
def soucet_vsech(seznam):
    celkem = 0
    for prvek in seznam:
        if isinstance(prvek, list):
            celkem += soucet_vsech(prvek)    # rekurze!
        else:
            celkem += prvek
    return celkem

soucet_vsech([1, [2, [3, [4, 5]]], 6])    # 21
```

### Procházení adresáře

```python
import os

def vsechny_soubory(slozka):
    for jmeno in os.listdir(slozka):
        cesta = os.path.join(slozka, jmeno)
        if os.path.isdir(cesta):
            yield from vsechny_soubory(cesta)
        else:
            yield cesta
```

---

## ⚠️ Limity rekurze

Python má limit hloubky (defaultně 1000):

```python
import sys
print(sys.getrecursionlimit())    # 1000
sys.setrecursionlimit(10000)       # můžeš zvýšit (opatrně!)
```

Když jdeš moc hluboko: **`RecursionError`**.

### Python NEMÁ optimalizaci ocasní rekurze

V některých jazycích se ocasní rekurze (poslední operace = volání sama sebe) nepřevede na stack frame. Python tohle **nedělá**. Proto pro hluboké rekurze raději použij smyčku.

```python
# Pythonic náhrada:
def faktorial(n):
    vysledek = 1
    for i in range(2, n + 1):
        vysledek *= i
    return vysledek
```

---

## 🧠 Rekurze vs smyčka

| | Rekurze | Smyčka |
|---|---|---|
| Čistý kód pro stromy | ✅ | ❌ těžké |
| Rychlost | ⚠️ pomalejší | ✅ |
| Paměť | ⚠️ stack | ✅ |
| Hloubka | ⚠️ limit | ✅ |

**Pravidlo:** Použij rekurzi, když je to **přirozené** (stromy, fraktály, parsování). Pro lineární opakování použij smyčku.

---

## ✏️ Cvičení

1. **Faktoriál:** Napiš rekurzivně i smyčkou. Porovnej.
2. **Mocnina:** Rekurzivně `mocnina(zaklad, exponent)` (bez `**`).
3. **Vnořený součet:** Spočítej součet všech čísel v `[1, [2, [3, [4]]], 5]`.
4. **Reverze řetězce:** Otoč řetězec rekurzivně (`""` je base case).
5. **Pascalův trojúhelník:** Vrať n-tý řádek pomocí rekurze.
