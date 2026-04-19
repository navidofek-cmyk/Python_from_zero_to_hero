# Lekce 25: Closure a `nonlocal`

## 🔒 Co je closure?

**Closure** = **funkce, která si pamatuje proměnné z místa, kde byla definovaná**, i když ji voláš jinde.

Představ si: **dáš funkci do kapsy** a ona si v té kapse drží svůj okolní svět.

```python
def vyrob_pricitac(o_kolik):
    def pridej(x):
        return x + o_kolik         # ← závisí na o_kolik z venku!
    return pridej

pricti_5 = vyrob_pricitac(5)
pricti_10 = vyrob_pricitac(10)

print(pricti_5(100))    # 105
print(pricti_10(100))   # 110
```

`pricti_5` si **pamatuje**, že `o_kolik = 5`, i když `vyrob_pricitac` už dávno doběhla.

---

## 🔍 Jak to vidět

```python
print(pricti_5.__closure__)
# (<cell at 0x...: int object at 0x...>,)

print(pricti_5.__closure__[0].cell_contents)   # 5
```

---

## ✏️ `nonlocal` — měnění zvenku

Defaultně **nemůžeš** měnit proměnnou z vnější funkce:

```python
def pocitadlo():
    n = 0
    def zvyseni():
        n += 1                    # ❌ UnboundLocalError
        return n
    return zvyseni
```

Musíš to říct přes `nonlocal`:

```python
def pocitadlo():
    n = 0
    def zvyseni():
        nonlocal n               # „n je z vnější funkce, NE nová lokální“
        n += 1
        return n
    return zvyseni

c = pocitadlo()
print(c())   # 1
print(c())   # 2
print(c())   # 3
```

### Rozdíl:
- `global x` → x je z modulu
- `nonlocal x` → x je z **vnější funkce** (ne modul!)

---

## 🎁 K čemu closure?

### 1. Tovární funkce (vyrábějí jiné funkce)

```python
def vyrob_validator(min_delka):
    def validuj(text):
        return len(text) >= min_delka
    return validuj

validuj_heslo = vyrob_validator(8)
validuj_pin = vyrob_validator(4)
```

### 2. Schování stavu (alternativa k třídám)

```python
def banka(zustatek=0):
    def vloz(castka):
        nonlocal zustatek
        zustatek += castka
        return zustatek
    def vyber(castka):
        nonlocal zustatek
        zustatek -= castka
        return zustatek
    return vloz, vyber

vloz, vyber = banka(100)
print(vloz(50))    # 150
print(vyber(30))   # 120
```

### 3. Dekorátory (lekce 26 — postavené na closure!)

---

## ⚠️ Past s pozdním vyhodnocením

```python
funkce = [lambda: i for i in range(3)]
print([f() for f in funkce])   # [2, 2, 2]   ← Cože?!
```

Lambdy se dívají na `i` **až když jsou volané** — a v tu chvíli je `i = 2` (poslední hodnota).

**Oprava** přes default argument:
```python
funkce = [lambda i=i: i for i in range(3)]
print([f() for f in funkce])   # [0, 1, 2]   ✅
```

Default je vyhodnocen **při definici**, ne až při volání.

---

## ✏️ Cvičení

1. **Pricitac:** Vyrob `vyrob_nasobic(faktor)` a otestuj `*2`, `*10`, `*100`.
2. **Pocitadlo:** Vytvoř funkci, která vrací postupně 1, 2, 3, 4...
3. **Banka:** Rozšiř příklad výše o `zustatek_funkce`, která vrátí aktuální stav.
4. **Past:** Vyzkoušej past s lambdami a oprav ji.
5. **Validator:** Vyrob `vyrob_kontrola_rozsahu(min, max)` co vrací funkci `kontrola(x)` testující jestli je `x` mezi.
