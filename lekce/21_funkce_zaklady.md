# Lekce 21: Definice funkcí

## 🍳 Co je funkce?

Funkce je **opakovatelný recept**. Napíšeš ho **jednou** a pak ho můžeš **použít kolikrát chceš**.

```python
def pozdrav(jmeno):
    print(f"Ahoj, {jmeno}!")

pozdrav("Eliška")    # Ahoj, Eliška!
pozdrav("Bob")        # Ahoj, Bob!
```

- `def` = „definuj“ (vytvoř)
- `pozdrav` = jméno funkce
- `(jmeno)` = **parametr** — co funkce dostane
- Tělo musí být **odsazené** (4 mezery)

---

## 🎁 `return` — vrácení výsledku

`print` jen vypíše. `return` **vrátí hodnotu**, kterou si můžeš uložit nebo dál použít.

```python
def secti(a, b):
    return a + b

vysledek = secti(3, 5)        # 8
print(secti(10, 20))           # 30
print(secti(secti(1, 2), 3))   # 6   (nesting)
```

### Funkce bez `return` vrací `None`

```python
def pozdrav(jmeno):
    print(f"Ahoj, {jmeno}!")

x = pozdrav("Bob")    # x je None
```

---

## 🚪 `return` ukončuje funkci

Hned jak narazí na `return`, funkce skončí. Nic dalšího se nespustí.

```python
def absolutni(x):
    if x < 0:
        return -x
    return x          # spustí se jen když nebylo to první return
```

---

## 🎚️ Argumenty vs parametry

Slovíčka:
- **Parametr** je v definici: `def secti(a, b):` → `a`, `b` jsou parametry.
- **Argument** je při volání: `secti(3, 5)` → `3`, `5` jsou argumenty.

(V praxi se používá oboje promíchaně, nedělej z toho vědu.)

---

## 📛 Pojmenované argumenty

```python
def pozdrav(jmeno, vykricnik):
    konec = "!" if vykricnik else "."
    print(f"Ahoj, {jmeno}{konec}")

pozdrav("Eliška", True)                        # poziční
pozdrav(jmeno="Eliška", vykricnik=True)        # pojmenované
pozdrav(vykricnik=True, jmeno="Eliška")        # pořadí nevadí!
pozdrav("Eliška", vykricnik=True)              # mix
```

**Pravidlo:** poziční argumenty musí být **před** pojmenovanými.

---

## 💎 Default hodnoty

```python
def pozdrav(jmeno, vykricnik=False):
    konec = "!" if vykricnik else "."
    print(f"Ahoj, {jmeno}{konec}")

pozdrav("Eliška")               # Ahoj, Eliška.
pozdrav("Bob", vykricnik=True)  # Ahoj, Bob!
```

### ⚠️ Past — nikdy neuváděj měnitelný default!

```python
def pridej(polozka, seznam=[]):     # ❌ ŠPATNĚ
    seznam.append(polozka)
    return seznam

print(pridej("a"))   # ['a']
print(pridej("b"))   # ['a', 'b']  ← Cože?!
```

Defaultní seznam je **stejná krabice** mezi voláními. Správně:

```python
def pridej(polozka, seznam=None):
    if seznam is None:
        seznam = []
    seznam.append(polozka)
    return seznam
```

---

## 🌍 Lokální vs globální proměnné

Proměnné uvnitř funkce jsou **lokální** — venku je nevidíš.

```python
def pocet():
    x = 10           # lokální
    print(x)

pocet()
print(x)             # ❌ NameError: x neexistuje
```

Globální proměnnou (definovanou venku) můžeš **číst**:

```python
zprava = "Ahoj"

def vypis():
    print(zprava)    # ✅ funguje

vypis()
```

Ale pro **změnu** globální musíš `global`:

```python
pocet = 0

def pridej():
    global pocet     # bez tohohle by to udělalo NOVOU lokální
    pocet += 1
```

(Globální proměnné jsou většinou **špatný nápad**. Raději vrať hodnotu.)

---

## ✏️ Cvičení

1. **Pozdrav:** Napiš funkci, co vezme jméno a vrátí (NE vypíše!) `f"Ahoj {jmeno}!"`.
2. **Obvod a obsah:** Funkce `obdelnik(a, b)` vrátí dvojici `(obvod, obsah)`.
3. **Default:** Funkce `nasob(a, b=10)` — když nezadáš `b`, použije 10.
4. **Past:** Vyzkoušej tu nebezpečnou funkci s `seznam=[]` — přesvědči se, že se chová divně.
5. **Faktoriál:** Napiš funkci `faktorial(n)`, která vrátí `n! = 1*2*3*...*n`.
