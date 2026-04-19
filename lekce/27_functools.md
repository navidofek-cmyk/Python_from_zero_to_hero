# Lekce 27: `functools` — kouzla nad funkcemi

`functools` je modul plný **užitečných nástrojů pro funkce**. Hlavní hvězdy:

```python
from functools import lru_cache, partial, reduce, singledispatch, wraps
```

---

## 💾 `lru_cache` — paměť výsledků

Některé výpočty jsou drahé. `@lru_cache` si **zapamatuje výsledek** pro daný vstup a podruhé už ho jen vytáhne.

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

print(fib(100))   # mžiknutí oka, jinak by to trvalo věčnost
```

**LRU** = Least Recently Used — když cache překročí `maxsize`, vyhodí nejstarší. `maxsize=None` = bez limitu.

V Python 3.9+ máš jednodušší `@cache`:
```python
from functools import cache

@cache
def fib(n): ...
```

---

## 🪛 `partial` — zafixování argumentů

```python
from functools import partial

def mocnina(zaklad, exponent):
    return zaklad ** exponent

ctverec = partial(mocnina, exponent=2)
krychle = partial(mocnina, exponent=3)

print(ctverec(5))     # 25
print(krychle(5))     # 125
```

`partial(funkce, x=10)` vrátí novou funkci, kde je `x` napevno `10`.

Hodí se, když musíš funkci poslat někam (jako callback) ale potřebuješ ji předkonfigurovat:

```python
button = Button(callback=partial(odesli_zpravu, prijemce="bob"))
```

---

## ➡️ `reduce` — sbal seznam do jedné hodnoty

```python
from functools import reduce

reduce(lambda a, b: a + b, [1, 2, 3, 4])    # 10  (jako sum)
reduce(lambda a, b: a * b, [1, 2, 3, 4])    # 24  (faktoriál!)
reduce(max, [3, 1, 4, 1, 5, 9])              # 9
```

Jak funguje:
1. Vezme první dva: `f(1, 2) = 3`
2. Pak výsledek + třetí: `f(3, 3) = 6`
3. ...až do konce.

V praxi `sum`, `max`, `min` jsou často lepší. `reduce` se hodí na vlastní operace.

---

## 🍴 `singledispatch` — funkce, co se chová jinak podle typu

```python
from functools import singledispatch

@singledispatch
def vykresli(co):
    print(f"Něco neznámého: {co}")

@vykresli.register
def _(co: int):
    print(f"Číslo: {co}")

@vykresli.register
def _(co: str):
    print(f"Text: {co!r}")

@vykresli.register
def _(co: list):
    print(f"Seznam o {len(co)} prvcích")

vykresli(42)        # Číslo: 42
vykresli("ahoj")    # Text: 'ahoj'
vykresli([1, 2])    # Seznam o 2 prvcích
```

Jako kdybys měl jednu vstupní bránu a podle typu balíku ho přepošlou jinam.

---

## 🎁 `wraps` (rekapitulace)

Vždycky používej v dekorátorech (lekce 26).

---

## 🔄 `functools.cache` vs `lru_cache`

| | `lru_cache(maxsize=N)` | `cache` |
|---|---|---|
| Limit | ano | ne |
| Vyhazuje staré | ano | ne |
| Verze | všechny | 3.9+ |
| Pro malé úkoly | ✅ | ✅ |
| Pro velké | ✅ (omezuje paměť) | ⚠️ (může nabobtnat) |

---

## ✏️ Cvičení

1. **Cache fib:** Napiš `fib(n)` rekurzivně. Spočítej `fib(35)` bez cache (trvá!) a pak s `@cache` (mžik).
2. **Partial:** Vyrob `partial` z `print` co vždycky tiskne s `sep="-"`.
3. **Reduce součin:** Spočítej součin čísel od 1 do 10 pomocí `reduce`.
4. **Singledispatch:** Napiš funkci `popis(co)` co popíše různě `int`, `str`, `list`, `dict`.
5. **Cached funkce:** Vyrob funkci `pocet_pismen(text)` s `@cache`. Zkontroluj přes `pocet_pismen.cache_info()` kolik bylo zásahů.
