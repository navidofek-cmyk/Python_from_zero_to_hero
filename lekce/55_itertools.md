# Lekce 55: `itertools` — kouzla s iterátory

`itertools` má **šuplík plný hotových iterátorů**. Naučíš se je a změní ti život.

```python
import itertools as it
```

---

## ♾️ Nekonečné

```python
it.count(10)            # 10, 11, 12, 13, ...
it.count(0, 2)          # 0, 2, 4, 6, ...

it.cycle("ABC")         # A, B, C, A, B, C, ...

it.repeat("ahoj", 3)    # ahoj, ahoj, ahoj
it.repeat("forever")    # ahoj, ahoj, ... navždy
```

---

## 🔗 `chain` — spojení

```python
list(it.chain([1,2], [3,4], [5]))     # [1, 2, 3, 4, 5]
list(it.chain.from_iterable([[1,2],[3,4]]))   # [1, 2, 3, 4] — zploštění
```

---

## 🎯 `islice` — slice na iterátoru

```python
list(it.islice(it.count(), 5))       # [0, 1, 2, 3, 4]
list(it.islice(range(20), 2, 10, 2)) # [2, 4, 6, 8]
```

`slice` ale na generátoru — bez vyrábění seznamu.

---

## 📊 `groupby` — seskupení

```python
data = [("ovoce", "jablko"), ("ovoce", "banán"), ("zelenina", "mrkev")]

for klic, skupina in it.groupby(data, key=lambda x: x[0]):
    print(f"{klic}: {[v for _, v in skupina]}")
# ovoce: ['jablko', 'banán']
# zelenina: ['mrkev']
```

⚠️ Funguje **jen na seřazená** data! Pokud nejsou seřazená, použij `sorted` první.

---

## 🪞 `tee` — duplikuj iterátor

```python
a, b = it.tee([1, 2, 3, 4, 5])
list(a)   # [1, 2, 3, 4, 5]
list(b)   # [1, 2, 3, 4, 5]   (i podruhé)
```

Užitečné, když chceš jeden iterátor projít víckrát.

---

## 🎲 Kombinatorika

```python
list(it.product([1,2], "AB"))            # [(1,'A'), (1,'B'), (2,'A'), (2,'B')]
list(it.permutations([1,2,3], 2))        # všechny dvojice s pořadím
list(it.combinations([1,2,3,4], 2))      # bez pořadí: (1,2), (1,3), (1,4), (2,3), ...
list(it.combinations_with_replacement([1,2,3], 2))  # i s opakováním
```

---

## ✂️ `dropwhile`, `takewhile`

```python
list(it.takewhile(lambda x: x < 5, [1, 2, 3, 4, 5, 4, 3]))
# [1, 2, 3, 4]   (bere dokud podmínka platí)

list(it.dropwhile(lambda x: x < 5, [1, 2, 3, 4, 5, 4, 3]))
# [5, 4, 3]      (přeskočí dokud platí, pak bere zbytek)
```

---

## 🎁 `accumulate` — průběžný součet

```python
list(it.accumulate([1, 2, 3, 4]))       # [1, 3, 6, 10]
list(it.accumulate([3,1,4,1,5], max))   # [3, 3, 4, 4, 5]
```

---

## 📦 `zip_longest`

Klasický `zip` se zastaví u nejkratšího. `zip_longest` ne:

```python
list(it.zip_longest([1,2,3], "AB", fillvalue="-"))
# [(1, 'A'), (2, 'B'), (3, '-')]
```

---

## 🌈 `pairwise` (3.10+)

```python
list(it.pairwise([1, 2, 3, 4, 5]))
# [(1,2), (2,3), (3,4), (4,5)]
```

Sliding window dvojic.

---

## ✏️ Cvičení

1. **Cycle:** Pomocí `cycle` vyrob barevný gradient — opakuj `["red", "green", "blue"]` pro 10 prvků.
2. **Combinations:** Vypiš všechny dvojice ze seznamu jmen.
3. **Groupby:** Skupinka slov podle prvního písmene (po seřazení).
4. **Pairwise:** Vyrob seznam rozdílů sousedních čísel `[1,3,7,12,20]` → `[2,4,5,8]`.
5. **Accumulate:** Spočítej kumulativní součet měsíčních příjmů (12 čísel).
