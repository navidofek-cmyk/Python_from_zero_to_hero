# Lekce 17: `collections` — speciální struktury

Modul `collections` má **šuplík plný šikovných nástrojů** pro práci s daty.

```python
from collections import deque, Counter, defaultdict, OrderedDict, ChainMap
```

---

## 🚊 `deque` — rychlá fronta z obou stran

`list` je super, ale **vkládání na začátek** je pomalé (musí všechno posunout). `deque` (čti „dek“) je rychlý z obou stran.

```python
from collections import deque

fronta = deque(["a", "b", "c"])
fronta.append("d")           # vpravo
fronta.appendleft("0")       # vlevo
fronta.pop()                 # vyhodí zprava
fronta.popleft()             # vyhodí zleva
```

Hodí se na **fronty** (FIFO) a **historii** s limitem:

```python
historie = deque(maxlen=5)   # drží jen posledních 5
for i in range(10):
    historie.append(i)
print(historie)              # deque([5, 6, 7, 8, 9], maxlen=5)
```

---

## 🔢 `Counter` — počítadlo

Spočítá ti, kolikrát se co opakuje. Dříve jsi to dělal ručně — teď za tebe.

```python
from collections import Counter

slova = "ahoj svete ahoj ahoj svete kamarade".split()
c = Counter(slova)
# Counter({'ahoj': 3, 'svete': 2, 'kamarade': 1})

c.most_common(2)             # [('ahoj', 3), ('svete', 2)]
c["ahoj"]                    # 3
c["neexistuje"]              # 0  (žádný KeyError!)
```

Aritmetika mezi countery:

```python
a = Counter("aabbc")
b = Counter("abcc")
a + b      # Counter({'a': 3, 'b': 3, 'c': 3})
a - b      # Counter({'a': 1, 'b': 1})
a & b      # průnik
a | b      # sjednocení (max)
```

---

## 🎁 `defaultdict` — slovník s defaultem

Klasický `dict` ti hodí `KeyError`, když klíč nemá. `defaultdict` ti místo toho **automaticky vytvoří** defaultní hodnotu.

```python
from collections import defaultdict

# Group by
zviratka = [("savec", "pes"), ("pták", "vrabec"), ("savec", "kočka")]
podle_skupiny = defaultdict(list)
for skupina, jmeno in zviratka:
    podle_skupiny[skupina].append(jmeno)

# defaultdict(list, {'savec': ['pes', 'kočka'], 'pták': ['vrabec']})
```

Místo:
```python
if skupina not in d:
    d[skupina] = []
d[skupina].append(jmeno)
```

Podobné s číslem:
```python
pocty = defaultdict(int)   # default 0
pocty["a"] += 1
```

---

## 📜 `OrderedDict`

V dnešních dnech je obyčejný `dict` v Pythonu **garantovaně ve vkládacím pořadí** (od 3.7). `OrderedDict` měl tuhle vlastnost dřív. Pořád má pár extra metod:

```python
from collections import OrderedDict
od = OrderedDict([("a", 1), ("b", 2)])
od.move_to_end("a")          # přesune na konec
od.move_to_end("a", last=False)  # přesune na začátek
```

Pro většinu věcí stačí obyčejný `dict`.

---

## 🔗 `ChainMap` — řetězec slovníků

Zkombinuje víc slovníků do jednoho pohledu (bez kopírování).

```python
from collections import ChainMap

defaulty = {"barva": "červená", "velikost": "M"}
uzivatel = {"barva": "modrá"}

config = ChainMap(uzivatel, defaulty)
print(config["barva"])      # "modrá"   (z prvního)
print(config["velikost"])   # "M"       (default)
```

Skvělé pro **konfigurace**: uživatel přebijí default.

---

## ✏️ Cvičení

1. **Counter:** Spočítej, kolikrát se v dlouhém textu opakuje každé slovo. Vypiš top 5.
2. **Defaultdict:** Máš seznam dvojic `(město, jméno)`. Vyrob slovník `{město: [seznam_jmen]}` pomocí `defaultdict(list)`.
3. **Deque historie:** Implementuj historii posledních 10 příkazů. Po 11. příkazu se ten první ztratí.
4. **ChainMap:** Vyrob 3 slovníky (CLI argumenty, environment, defaulty) a najdi hodnotu napříč nimi.
5. **Top písmena:** Pomocí `Counter` zjisti, jaké písmeno je v textu nejčastější.
