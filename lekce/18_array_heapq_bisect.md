# Lekce 18: `array`, `heapq`, `bisect`

## 📏 `array` — efektivní pole stejného typu

`list` umí cokoliv (čísla, texty, mix). Ale je velký. **`array`** je úsporný, ale jen pro jeden typ čísla.

```python
from array import array

cisla = array("i", [1, 2, 3, 4])    # "i" = int (4 byty)
cisla.append(5)
print(cisla)                          # array('i', [1, 2, 3, 4, 5])
```

Typové kódy: `"i"` (int), `"f"` (float), `"d"` (double), `"b"` (signed byte) atd.

V praxi pro velká čísla raději **NumPy** (lekce 98). `array` je takový `list` na dietě.

---

## ⛰️ `heapq` — prioritní fronta (halda)

**Halda** je struktura, kde rychle dostaneš **nejmenší prvek**. Jako kornout zmrzliny — odkrojíš vrch, zbytek se sám srovná.

```python
import heapq

h = []
heapq.heappush(h, 5)
heapq.heappush(h, 1)
heapq.heappush(h, 3)
heapq.heappush(h, 2)

print(h)                       # [1, 2, 3, 5]   (vnitřní reprezentace, ne zcela seřazená!)
print(heapq.heappop(h))        # 1   (vždy nejmenší)
print(heapq.heappop(h))        # 2
```

### N nejmenších/největších

```python
cisla = [5, 7, 1, 9, 3, 2, 8]
heapq.nsmallest(3, cisla)      # [1, 2, 3]
heapq.nlargest(3, cisla)       # [9, 8, 7]
```

Pro pár prvků z velkého seznamu **rychlejší** než `sorted()[:n]`.

### Prioritní fronta s čím-co

```python
fronta = []
heapq.heappush(fronta, (1, "důležité"))
heapq.heappush(fronta, (3, "počká"))
heapq.heappush(fronta, (2, "středně"))

while fronta:
    print(heapq.heappop(fronta))
# (1, 'důležité'), (2, 'středně'), (3, 'počká')
```

---

## 🎯 `bisect` — vyhledávání v seřazeném seznamu

Rychlé hledání **kam patří** prvek v seřazeném seznamu (binárním půlením).

```python
import bisect

s = [1, 3, 5, 7, 9]

bisect.bisect_left(s, 4)      # 2   (kam by patřila 4)
bisect.bisect_right(s, 5)     # 3   (kam patří za existující 5)

bisect.insort(s, 4)           # vloží na správné místo
print(s)                       # [1, 3, 4, 5, 7, 9]
```

### Klasické použití — známkování

```python
hranice = [40, 60, 75, 90]      # 4, 3, 2, 1
znamky = ["F", "D", "C", "B", "A"]

def znamka(skore: int) -> str:
    return znamky[bisect.bisect_left(hranice, skore)]

print(znamka(85))    # "B"
print(znamka(45))    # "D"
```

---

## ✏️ Cvičení

1. **Halda:** Vytvoř haldu z `[5, 2, 8, 1, 9, 3]` a postupně vyhazuj — vzniká seřazená posloupnost.
2. **Top 3:** Z velkého seznamu náhodných čísel vyber 3 největší pomocí `nlargest`.
3. **Prioritní úkoly:** Vyrob frontu úkolů s prioritami a zpracovávej je.
4. **Známkování:** Použij `bisect` na známkování — uživatel zadá body a dostane známku.
5. **Insort:** Vyrob prázdný seznam. Postupně do něj přidávej náhodná čísla pomocí `insort`. Na konci by měl být seřazený.
