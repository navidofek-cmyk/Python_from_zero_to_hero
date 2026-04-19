# Lekce 11: Seznamy (`list`)

## 🚂 Co je seznam?

**Seznam** je **vláček s vagónky**. Můžeš tam dát cokoli: čísla, slova, jiné seznamy. A můžeš ho **měnit** — přidávat, mazat, prohazovat.

```python
ovoce = ["jablko", "banán", "hruška"]
cisla = [1, 2, 3, 4, 5]
mix = [1, "dvě", 3.0, True, [10, 20]]   # i mix typů a vnořené!
```

---

## 🔍 Přístup k vagónkům

```python
ovoce[0]    # "jablko"  (první)
ovoce[-1]   # "hruška"  (poslední)
ovoce[1:3]  # ["banán", "hruška"]   (slice)
len(ovoce)  # 3
```

---

## 🔧 Hlavní metody

```python
ovoce.append("jahoda")          # přidá na konec
ovoce.insert(0, "ananas")       # vloží na pozici 0
ovoce.remove("banán")           # smaže první výskyt
posledni = ovoce.pop()          # vyndá poslední (a vrátí ho)
ovoce.pop(0)                    # vyndá z pozice 0
ovoce.sort()                    # seřadí na místě (mění!)
ovoce.reverse()                 # otočí na místě
ovoce.index("hruška")           # vrátí pozici
ovoce.count("hruška")           # kolikrát tam je
ovoce.clear()                   # vymaže všechno
ovoce.extend([1, 2, 3])         # přidá VÍC najednou
nova = ovoce.copy()             # mělká kopie
```

### `sort` vs `sorted`

```python
cisla = [3, 1, 2]
cisla.sort()                    # ZMĚNÍ cisla → [1, 2, 3]
nova = sorted(cisla)            # NEMĚNÍ, vrátí novou
nova_obracene = sorted(cisla, reverse=True)
```

---

## ✨ List comprehension — kouzelné tvoření

Místo:
```python
ctverce = []
for x in range(1, 6):
    ctverce.append(x * x)
# [1, 4, 9, 16, 25]
```

Napiš jen jeden řádek:
```python
ctverce = [x * x for x in range(1, 6)]
```

S podmínkou (filtr):
```python
suda_ctverce = [x * x for x in range(1, 11) if x % 2 == 0]
# [4, 16, 36, 64, 100]
```

S `if/else` uvnitř (vždy něco vrátí):
```python
oznaceni = ["sudé" if x % 2 == 0 else "liché" for x in range(5)]
```

---

## ⚠️ Past s kopírováním

```python
a = [1, 2, 3]
b = a              # ❌ Tohle NENÍ kopie! Jen druhá nálepka.
b.append(4)
print(a)           # [1, 2, 3, 4]  ← změnilo se i a!

c = a.copy()       # ✅ kopie (mělká)
# nebo: c = a[:] nebo c = list(a)
```

Pro **vnořené** seznamy potřebuješ **hlubokou** kopii:
```python
import copy
hluboka = copy.deepcopy(matice)
```

---

## ⚡ Užitečné funkce

```python
sum([1, 2, 3])          # 6
max([1, 2, 3])          # 3
min([1, 2, 3])          # 1
sorted([3, 1, 2])       # [1, 2, 3]
list(reversed([1,2,3])) # [3, 2, 1]
list(range(5))          # [0, 1, 2, 3, 4]
list("abc")             # ["a", "b", "c"]
```

---

## ✏️ Cvičení

1. **Seznam na míru:** Vyrob seznam svých 5 oblíbených věcí. Přidej jednu, smaž jednu, vypiš.
2. **Sudá čísla:** Pomocí list comprehension vyrob seznam sudých čísel od 0 do 50.
3. **Délky slov:** Máš seznam slov `["pes", "kočka", "slon", "myš"]`. Vyrob seznam jejich délek.
4. **Past:** Vytvoř `a = [1, 2, 3]` a `b = a`. Změň `b[0]`. Co je v `a`? Vysvětli.
5. **Statistika:** Zeptej se na 5 čísel a vypiš jejich součet, průměr, max a min.
