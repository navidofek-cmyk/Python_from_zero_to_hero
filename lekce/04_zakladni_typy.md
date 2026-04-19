# Lekce 4: Základní typy — int, float, bool, complex

## 🎒 Typy = druhy krabic

Ne každá krabice umí totéž. Krabice s **čísly** umí počítat, krabice se **slovy** ne (aspoň ne normálně). V Pythonu máš tyhle základní typy:

| Typ | Česky | Příklad |
|---|---|---|
| `int` | celé číslo | `42`, `-7`, `0` |
| `float` | desetinné číslo | `3.14`, `-0.5` |
| `bool` | ano/ne (pravda/nepravda) | `True`, `False` |
| `complex` | komplexní číslo (pro matiku) | `2 + 3j` |

Typ zjistíš přes `type()`:

```python
type(42)       # <class 'int'>
type(3.14)     # <class 'float'>
type(True)     # <class 'bool'>
```

---

## 🔢 `int` — celá čísla bez limitu!

Python nemá žádný limit na velikost celého čísla. Vážně!

```python
obrovske = 2 ** 1000   # dvojka na tisícinu
print(obrovske)         # vypíše 302 cifer dlouhé číslo 🤯
```

Základní operace:

```python
5 + 3     # 8  sčítání
10 - 4    # 6  odčítání
6 * 7     # 42 násobení
10 / 3    # 3.3333... (vždycky float!)
10 // 3   # 3 (celočíselné dělení — zaokrouhlí dolů)
10 % 3    # 1 (zbytek po dělení)
2 ** 10   # 1024 (umocnění)
```

---

## 🌊 `float` — desetinná čísla (a jejich podivnost)

```python
0.1 + 0.2   # 0.30000000000000004  ← Ne, nezbláznil ses!
```

Proč? Počítač ukládá desetinná čísla v **binární soustavě** (jenom 0 a 1) a některá desetinná čísla se do ní nevejdou přesně. Je to, jako kdybys chtěl do šuplíku narvat kruh — vždycky tam zbyde malá mezera.

Když potřebuješ **přesná desetinná čísla** (třeba peníze!), použij `Decimal`:

```python
from decimal import Decimal
Decimal("0.1") + Decimal("0.2")   # Decimal("0.3")  ✅
```

---

## ✅ `bool` — pravda nebo nepravda

Dvě hodnoty: `True` a `False` (s velkým písmenem!).

```python
mam_hlad = True
je_sobota = False
```

Zajímavost: `bool` je vlastně **specialní druh `int`**. `True` je 1, `False` je 0.

```python
True + True   # 2  🤨
```

---

## 🌀 `complex` — komplexní čísla

Pro matematiku. Používá `j` místo `i`:

```python
z = 2 + 3j
z.real   # 2.0
z.imag   # 3.0
```

Pokud nevíš, k čemu to je — nevadí, jen vědět že to existuje.

---

## 🔄 Převody mezi typy

```python
int("42")       # 42 (ze slova na číslo)
float("3.14")   # 3.14
str(42)         # "42" (z čísla na slovo)
bool(0)         # False
bool(1)         # True
bool("")        # False (prázdný text = nepravda)
bool("ahoj")    # True
int(3.9)        # 3 (UŘÍZNE desetinnou část, nezaokrouhlí!)
round(3.9)      # 4 (TOHLE zaokrouhluje)
```

---

## ✏️ Cvičení

1. **Kalkulačka:** Spočítej `17 // 5`, `17 % 5`, `17 / 5`. Vysvětli, co je rozdíl mezi `//` a `/`.
2. **Velké číslo:** Spočítej `2 ** 100`. Kolik má číslic? (Nápověda: `len(str(2**100))`.)
3. **Float podivnost:** Zkus `0.1 + 0.2 == 0.3`. Co vrátí? Proč?
4. **Převod:** Zeptej se uživatele na věk (`input`) a vypiš „Za 5 let ti bude X.“ Pozor — `input` vrací text, musíš ho převést na `int`!
