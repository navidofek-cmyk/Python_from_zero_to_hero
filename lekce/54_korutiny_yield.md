# Lekce 54: Generátorové korutiny — `send`, `throw`, `close`

## 📨 Generátor co i přijímá

Klasický generátor jen **vysílá** přes `yield`. Ale `yield` umí i **přijímat**.

```python
def echo():
    while True:
        prijato = yield     # čeká, až někdo pošle
        print(f"Přijal: {prijato}")


g = echo()
next(g)           # nutné — "rozjedeš" generátor až k prvnímu yield
g.send("ahoj")    # → Přijal: ahoj
g.send("svete")   # → Přijal: svete
```

---

## ⚡ `send(hodnota)` — pošle hodnotu k `yield`

```python
def soucet():
    celkem = 0
    while True:
        x = yield celkem
        celkem += x


g = soucet()
print(next(g))       # 0
print(g.send(10))    # 10
print(g.send(5))     # 15
print(g.send(3))     # 18
```

---

## 💥 `throw(typ_vyjimky)` — pošle výjimku dovnitř

```python
def gen():
    try:
        while True:
            x = yield
            print(x)
    except ValueError:
        print("Někdo mi poslal ValueError!")


g = gen()
next(g)
g.send(1)
g.throw(ValueError)
```

---

## 🔒 `close()` — ukončí generátor

```python
def gen():
    try:
        while True:
            yield
    except GeneratorExit:
        print("Konec, uklízím...")


g = gen()
next(g)
g.close()
# → Konec, uklízím...
```

---

## 🆚 Generator korutiny vs `async`/`await`

Tohle byly **původní korutiny** (Python 2.5+). V moderním Pythonu (3.5+) používáme **`async`/`await`** (lekce 56) — je to čistší a podporuje `await`.

Generator korutiny vidíš ještě v některých starších knihovnách. Většinou je nahrazují async verze.

---

## ✏️ Cvičení

1. **Echo:** Vyrob jako výše.
2. **Průměr:** Korutina co dostává čísla a vrací průběžný průměr.
3. **Sběrač:** Korutina co dostává položky a po `close()` vrátí seznam.
4. **Filter:** Korutina co dostává čísla a vrací jen sudá.
