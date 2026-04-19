# Lekce 53: `yield from` — delegování generátorů

## 🪆 Co dělá `yield from`?

Místo psaní smyčky:

```python
def vse(seznam):
    for x in seznam:
        yield x
```

Můžeš:

```python
def vse(seznam):
    yield from seznam
```

Stejné chování, ale **kratší a rychlejší**.

---

## 🔗 Skládání generátorů

```python
def cisla_1_10():
    yield from range(1, 11)

def cisla_20_30():
    yield from range(20, 31)

def vsechna():
    yield from cisla_1_10()
    yield from cisla_20_30()


print(list(vsechna()))
# [1, 2, ..., 10, 20, ..., 30]
```

---

## 🌳 Procházení stromu

```python
def vsechny_polozky(strom):
    for prvek in strom:
        if isinstance(prvek, list):
            yield from vsechny_polozky(prvek)   # rekurze
        else:
            yield prvek


strom = [1, [2, [3, 4], 5], 6, [7, [8, 9]]]
print(list(vsechny_polozky(strom)))
# [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

---

## 🔄 Procházení adresáře

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

(V moderním Pythonu raději `pathlib.Path.rglob`.)

---

## 🎯 `yield from` umí víc — předává `send`/`throw`

V plné formě umí předávat `send()` hodnoty a výjimky vnitřnímu generátoru. Pro běžné použití to neřeš — funguje to.

---

## ✏️ Cvičení

1. **Spojení:** Vyrob `spoj_vse(*generators)` co spojí víc generátorů přes `yield from`.
2. **Strom:** Procházej vnořený seznam — všechny prvky.
3. **Přílohy:** Funkce co projde adresář a vrátí všechny PDF soubory.
4. **Čísla:** Generátor `cisla_az_do(n)` co spojí `range(0, n)` a `range(0, -n, -1)`.
