# Lekce 29: Funkcionální nástroje — `map`, `filter`, generátory

## 🗺️ `map` — proveď funkci na každém prvku

```python
cisla = [1, 2, 3, 4, 5]

ctverce = list(map(lambda x: x*x, cisla))
# [1, 4, 9, 16, 25]

# S existující funkcí
texty = list(map(str, cisla))         # ['1', '2', '3', '4', '5']
delky = list(map(len, ["pes", "kočka", "myš"]))    # [3, 5, 3]
```

`map` vrací **iterátor**, ne seznam. Pro seznam musíš `list(...)`.

### Víc seznamů najednou

```python
soucty = list(map(lambda a, b: a + b, [1, 2, 3], [10, 20, 30]))
# [11, 22, 33]
```

---

## 🔍 `filter` — propusť jen ty, co splňují podmínku

```python
suda = list(filter(lambda x: x % 2 == 0, range(10)))
# [0, 2, 4, 6, 8]

neprazdne = list(filter(None, ["", "ahoj", "", "svete", ""]))
# ["ahoj", "svete"]   (None = filtruj falsy)
```

---

## ✨ Comprehension — pythonský způsob

`map` a `filter` jsou OK, ale **comprehension** je v Pythonu obvykle čitelnější:

| `map`/`filter` | Comprehension |
|---|---|
| `list(map(lambda x: x*x, cisla))` | `[x*x for x in cisla]` |
| `list(filter(lambda x: x>0, cisla))` | `[x for x in cisla if x>0]` |
| `list(map(str.upper, slova))` | `[s.upper() for s in slova]` |

Comprehension umí **i transformaci, i filtr** v jedné chvíli:

```python
[x*x for x in range(20) if x % 2 == 0]
```

---

## ⚡ Generátorový výraz

Místo `[...]` použij `(...)` — vrátí **generátor** místo seznamu. **Líný** — počítá až když se ho ptáš.

```python
ctverce = (x*x for x in range(1_000_000))   # nezabere paměť!
prvni = next(ctverce)        # 0
druhy = next(ctverce)        # 1
```

Skvělé pro **velké datové sady**.

```python
# Součet bez vytváření seznamu (úspora paměti!)
sum(x*x for x in range(1_000_000))
```

(Bez závorek navíc, když je generátor jediný argument.)

---

## 🍳 Comprehension pro slovník a set

```python
# Dict comp
ctverce = {x: x*x for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Set comp
unikatni = {x*x for x in [-2, -1, 0, 1, 2]}
# {0, 1, 4}
```

---

## 🪆 Vnořené comprehension

```python
# Matice 3x3
matice = [[i*3 + j for j in range(3)] for i in range(3)]
# [[0, 1, 2], [3, 4, 5], [6, 7, 8]]

# Zploštění
matice = [[1, 2], [3, 4], [5, 6]]
ploche = [x for radek in matice for x in radek]
# [1, 2, 3, 4, 5, 6]
```

Pravidlo: čte se **zleva doprava** jako vnořené smyčky.

---

## ✏️ Cvičení

1. **Velkými:** Vyrob seznam slov velkými písmeny pomocí comprehension i `map`. Která verze čitelnější?
2. **Filtr:** Z čísel 1–100 vyber ta dělitelná 7.
3. **Generátor:** Spočítej součet čtverců prvních 10 milionů čísel BEZ vytvoření seznamu.
4. **Dict comp:** Z `["pes", "kočka", "myš"]` vyrob `{"pes": 3, "kočka": 5, "myš": 3}`.
5. **Zploštění:** Máš `[[1, 2], [3, 4], [5]]`. Vyrob `[1, 2, 3, 4, 5]`.
6. **Nested:** Vyrob násobilku 1×1 až 5×5 jako vnořený seznam.
