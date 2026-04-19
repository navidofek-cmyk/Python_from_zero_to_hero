# Lekce 20: Iterace — `enumerate`, `zip`, `reversed`, `sorted`

Tyhle čtyři funkce **změní život** každého Pythonisty. Naučí se je milovat.

---

## 🔢 `enumerate` — index i hodnota najednou

❌ **Začátečnický** styl:
```python
ovoce = ["jablko", "banán", "hruška"]
for i in range(len(ovoce)):
    print(i, ovoce[i])
```

✅ **Pythonský** styl:
```python
for i, ovo in enumerate(ovoce):
    print(i, ovo)
```

Můžeš začít od jiného čísla:
```python
for i, ovo in enumerate(ovoce, start=1):
    print(f"{i}. {ovo}")    # 1. jablko, 2. banán, ...
```

---

## 🤐 `zip` — spojení dvou (a víc) seznamů

```python
jmena = ["Anna", "Bob", "Cyril"]
veky =  [10, 11, 12]

for jmeno, vek in zip(jmena, veky):
    print(f"{jmeno} ({vek})")
```

Můžeš spojit i víc:
```python
mesta = ["Praha", "Brno", "Plzeň"]
for j, v, m in zip(jmena, veky, mesta):
    print(j, v, m)
```

### Pozor — `zip` se zastaví u nejkratšího!

```python
list(zip([1,2,3,4,5], ["a","b","c"]))
# [(1,'a'), (2,'b'), (3,'c')]   (4, 5 přeskočeno!)
```

Když chceš výjimku při různé délce:
```python
list(zip(a, b, strict=True))   # Python 3.10+
```

### Vyrobit slovník ze dvou seznamů

```python
dict(zip(jmena, veky))    # {"Anna": 10, "Bob": 11, "Cyril": 12}
```

### Transpozice (kouzlo!)

```python
matice = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
list(zip(*matice))
# [(1, 4, 7), (2, 5, 8), (3, 6, 9)]
```

---

## 🔄 `reversed` — pozpátku

```python
for x in reversed([1, 2, 3]):
    print(x)
# 3, 2, 1

for znak in reversed("ahoj"):
    print(znak)
```

Funguje na seznamech, n-ticích, řetězcích, range. **NE** na slovnících bez převodu.

---

## 📊 `sorted` — seřazení

```python
sorted([3, 1, 2])              # [1, 2, 3]
sorted([3, 1, 2], reverse=True) # [3, 2, 1]
sorted("ahoj")                  # ['a', 'h', 'j', 'o']
```

### `key` — seřaď podle čeho?

```python
slova = ["pes", "kočka", "myš", "slon"]
sorted(slova, key=len)         # ['pes', 'myš', 'slon', 'kočka']

# Podle posledního písmene
sorted(slova, key=lambda s: s[-1])

# Podle ne-rozlišování velkých/malých
sorted(["Banán", "ananas", "Citron"], key=str.lower)
```

### Seřazení slovníků/dataclassů

```python
osoby = [
    {"jmeno": "Anna", "vek": 12},
    {"jmeno": "Bob",  "vek": 10},
]

sorted(osoby, key=lambda o: o["vek"])
# Bob první (mladší)
```

### Více kritérií najednou

```python
# Nejdřív podle věku, pak podle jména
sorted(osoby, key=lambda o: (o["vek"], o["jmeno"]))
```

---

## 🎁 `any` a `all` — bonus

```python
any([False, False, True])    # True (aspoň jedno True)
all([True, True, False])     # False (musí být všechny True)

# S generátorem (pythonské):
any(x > 10 for x in cisla)
all(x > 0 for x in cisla)
```

---

## ✏️ Cvičení

1. **Číslovaný seznam:** Vypiš seznam svých koníčků s čísly: `1. čtení, 2. fotbal, ...`.
2. **Tabulka:** Máš `jmena` a `veky`. Pomocí `zip` vyrob slovník a vypiš tabulku.
3. **Seřaď slova podle délky:** Z věty vyrob seznam slov a seřaď je podle délky.
4. **Top 3 nejstarší:** Máš seznam slovníků s lidmi. Vypiš 3 nejstarší.
5. **Pozpátku v páru:** Pomocí `reversed` a `enumerate` vypiš seznam pozpátku s pořadovým číslem **od konce**.
6. **All/Any:** Zjisti, jestli jsou všechna čísla v seznamu kladná. Pak: jestli aspoň jedno je sudé.
