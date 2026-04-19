# Lekce 9: Smyčky — `for` a `while`

## 🔁 Co je smyčka?

Smyčka je **opakování**. Místo abys napsal stejný kód 10×, řekneš robotovi: „Udělej tohle 10×.“

Python má dvě:
- **`for`** — opakuj **pro každou věc** v něčem (seznam, text, čísla…).
- **`while`** — opakuj **dokud** platí podmínka.

---

## 🚂 `for` — pro každého

```python
for ovoce in ["jablko", "banán", "hruška"]:
    print(f"Mám rád {ovoce}.")
```

Robot si vezme jednu věc po druhé a přečte tělo smyčky.

### `range()` — kouzlo na čísla

```python
for i in range(5):       # 0, 1, 2, 3, 4   (5 NE!)
    print(i)

for i in range(1, 6):    # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2):  # 0, 2, 4, 6, 8 (krok 2)
    print(i)

for i in range(10, 0, -1): # 10, 9, 8 ... 1 (pozadu)
    print(i)
```

### Procházení textu

```python
for znak in "Ahoj":
    print(znak)
# A
# h
# o
# j
```

---

## ⏳ `while` — dokud platí

```python
energie = 5
while energie > 0:
    print(f"Energie: {energie}")
    energie -= 1
print("Vyčerpáno!")
```

**Pozor!** Pokud zapomeneš měnit podmínku, máš **nekonečnou smyčku** 🔄♾️ — robot bude točit donekonečna a budeš muset stisknout `Ctrl+C` ho zastavit.

```python
while True:
    print("Pomóóóc!")  # ❌ NIKDY nepřestane
```

---

## ✋ `break` — vyskoč ven

```python
for i in range(100):
    if i == 5:
        break       # vyskoč ven HNED
    print(i)
# 0, 1, 2, 3, 4
```

## ⏭️ `continue` — přeskoč na další

```python
for i in range(5):
    if i == 2:
        continue    # přeskoč zbytek tohoto kola
    print(i)
# 0, 1, 3, 4   (2 chybí)
```

---

## 🎁 `else` na smyčkách — bonus věc

`else` se na konci smyčky spustí **pokud smyčka neskončila přes `break`**.

```python
for cislo in [1, 2, 3, 4]:
    if cislo == 5:
        print("Našel jsem pětku")
        break
else:
    print("Pětku jsem nenašel.")
# → Pětku jsem nenašel.
```

Užitečné při hledání — pokud smyčkou projdeš celou bez nálezu, `else` to oznámí.

---

## 🌀 Vnořené smyčky

```python
for i in range(3):
    for j in range(3):
        print(f"({i},{j})", end=" ")
    print()
# (0,0) (0,1) (0,2)
# (1,0) (1,1) (1,2)
# (2,0) (2,1) (2,2)
```

---

## ✏️ Cvičení

1. **Násobilka:** Vypiš násobilku 7 (od 1×7 do 10×7).
2. **Součet:** Spočítej součet čísel od 1 do 100. (Bonus: porovnej s `sum(range(1, 101))`.)
3. **Hra na hádání:** Robot si vybere číslo (`import random; tajne = random.randint(1, 100)`). Uživatel hádá ve `while`, dokud netrefí. Po každém pokusu mu napiš „víc“ nebo „míň“.
4. **FizzBuzz** (klasika!): Pro čísla 1 až 30 vypiš samotné číslo. Ale když je dělitelné 3, napiš „Fizz“. Když 5, napiš „Buzz“. Když oběma, „FizzBuzz“.
5. **Hvězdičkový trojúhelník:** Vypiš trojúhelník z hvězdiček, výška 5: `*`, `**`, `***`, `****`, `*****`.
