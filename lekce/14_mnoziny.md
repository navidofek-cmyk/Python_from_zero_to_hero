# Lekce 14: Množiny (`set`, `frozenset`)

## 🎒 Co je množina?

**Set** je jako **pytlík kuliček bez pořadí, kde každá kulička je tam jen jednou**.

- ❌ žádné duplikáty
- ❌ žádné pořadí (nemůžeš `set[0]`)
- ✅ super rychlé hledání („je to v pytlíku?“)

```python
ovoce = {"jablko", "banán", "hruška"}
ovoce2 = set(["jablko", "jablko", "banán"])  # → {'jablko', 'banán'}
prazdna = set()    # ⚠️ {} je prázdný DICT, ne set!
```

---

## ⚡ Hlavní operace

```python
s = {1, 2, 3}

s.add(4)              # přidá
s.discard(99)         # smaže (bez chyby, když není)
s.remove(99)          # smaže (CHYBA, když není)
s.pop()               # vyhodí náhodný prvek

3 in s                # True   (super rychlé!)
len(s)                # 3
```

---

## ➕ Matematické operace

Sety umí to, co se v matice učí jako **operace s množinami**.

```python
A = {1, 2, 3, 4}
B = {3, 4, 5, 6}

A | B    # sjednocení: {1, 2, 3, 4, 5, 6}
A & B    # průnik:     {3, 4}
A - B    # rozdíl:     {1, 2}
A ^ B    # symetrický rozdíl: {1, 2, 5, 6}  (co je v jednom ale ne v obou)
```

Slovní verze: `A.union(B)`, `A.intersection(B)`, `A.difference(B)`, `A.symmetric_difference(B)`.

### Podmnožina/nadmnožina

```python
{1, 2}.issubset({1, 2, 3})        # True
{1, 2, 3}.issuperset({1, 2})      # True
{1}.isdisjoint({2, 3})            # True (žádný společný prvek)
```

---

## ✨ Set comprehension

```python
ctverce = {x*x for x in range(-5, 6)}
# {0, 1, 4, 9, 16, 25}   (žádné duplikáty!)
```

---

## 🧊 `frozenset` — zamknutý set

Stejné jako set, ale **neměnný**. Můžeš ho použít jako klíč ve slovníku nebo jako prvek v jiném setu.

```python
fs = frozenset([1, 2, 3])
# fs.add(4)   ❌ AttributeError
```

---

## 🎯 Časté použití

### Odstranit duplikáty ze seznamu

```python
seznam = [1, 2, 2, 3, 3, 3, 4]
unik = list(set(seznam))      # [1, 2, 3, 4]  (pořadí ale neručené!)

# Když chceš zachovat pořadí (Python 3.7+):
unik = list(dict.fromkeys(seznam))    # [1, 2, 3, 4]
```

### Najít společné věci

```python
moji_kamaradi = {"Anna", "Petr", "Eva"}
tvoji_kamaradi = {"Petr", "Eva", "Tom"}

spolecni = moji_kamaradi & tvoji_kamaradi   # {"Petr", "Eva"}
```

---

## ⚠️ Co set NEMŮŽE obsahovat

Pouze **neměnné** věci (hashable). Ne seznamy, ne slovníky.

```python
{[1, 2], [3, 4]}      # ❌ TypeError! list není hashable
{(1, 2), (3, 4)}      # ✅ tuple jsou OK
```

---

## ✏️ Cvičení

1. **Bez duplikátů:** Máš `cisla = [1, 2, 2, 3, 3, 3, 4, 5, 5]`. Vyrob seznam unikátních hodnot.
2. **Společné koníčky:** Máš dva sety koníčků dvou kamarádů. Vypiš co mají společné, co jen první, co jen druhý.
3. **Anagram?** Napiš funkci `je_anagram(a, b)`, která vrátí `True`, pokud jsou slova složená ze stejných písmen. (Hint: `set(a) == set(b)`. Ale pozor na duplikáty — možná lepší `sorted`.)
4. **Unikátní písmena:** Spočítej, kolik unikátních písmen má text.
5. **Slovní fotbal:** Máš seznam slov. Najdi slova, jejichž první písmeno je stejné jako poslední písmeno předchozího (slovní fotbal).
