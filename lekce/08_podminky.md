# Lekce 8: Podmínky — `if`, `elif`, `else`

## 🍴 Rozhodování v programu

Život je plný rozhodování: „Když prší, vezmu deštník. Jinak ne.“ Programy taky.

```python
prsi = True

if prsi:
    print("Vezmu deštník!")
else:
    print("Půjdu bez.")
```

- `if` = „když“
- `else` = „jinak“
- **Dvojtečka `:` na konci** je povinná!
- **Odsazení (4 mezery)** říká, co patří do `if`. Python je na to přísný!

---

## 🪜 `elif` — víc možností za sebou

`elif` = „else if“ = „jinak když“

```python
znamka = int(input("Známka (1–5): "))

if znamka == 1:
    print("Výborně! 🌟")
elif znamka == 2:
    print("Chvalitebně 👍")
elif znamka == 3:
    print("Dobře 🙂")
elif znamka == 4:
    print("Dostatečně 😐")
else:
    print("Bohužel nedostatečně 😢")
```

Python jde **shora dolů** a první podmínku, která sedí, vykoná. Zbytek přeskočí.

---

## 🎭 Truthy a falsy — co se počítá za pravdu?

Python neomezuje `if` jen na `True`/`False`. Cokoliv můžeš strčit do `if`. Některé hodnoty se chovají jako **„nepravda“** (falsy), ostatní jako **„pravda“** (truthy).

### Falsy (počítá se za nepravdu):
- `False`
- `None`
- `0`, `0.0`, `0j`
- `""` (prázdný řetězec)
- `[]`, `{}`, `()`, `set()` (prázdné kolekce)

### Truthy (vše ostatní):
- `True`
- jakékoliv číslo různé od 0
- jakýkoliv neprázdný text/seznam/...

```python
seznam = []
if seznam:
    print("Něco v seznamu je")
else:
    print("Seznam je prázdný")   # ← tohle se vypíše
```

**Pythonický styl** — místo `if len(seznam) > 0:` piš jen `if seznam:`.

---

## 🪆 Vnořené `if` (jeden v druhém)

```python
vek = 15
ma_propusku = True

if vek >= 18:
    print("Můžeš na koncert.")
else:
    if ma_propusku:
        print("Můžeš s propustkou.")
    else:
        print("Nesmíš.")
```

Často to ale jde napsat **lépe pomocí `and`/`or`**:

```python
if vek >= 18 or ma_propusku:
    print("Můžeš")
else:
    print("Nesmíš")
```

---

## 🚨 Pozor — `=` vs `==`

```python
if x = 5:    # ❌ CHYBA! = je přiřazení
if x == 5:   # ✅ OK, == je porovnání
```

(Stará chyba začátečníků v jiných jazycích. Python ti `=` v `if` rovnou zakáže — díky bohu!)

---

## ✏️ Cvičení

1. **Sudé/liché:** Zeptej se na číslo. Vypiš „sudé“ nebo „liché“.
2. **Známkování:** Zeptej se na procenta. Vypiš známku: 90+ → 1, 75–89 → 2, 60–74 → 3, 40–59 → 4, méně → 5.
3. **Falsy:** Zeptej se na text. Když je prázdný (uživatel jen zmáčkne Enter), vypiš „nic jsi nenapsal“. Použij truthy/falsy, ne `len()`.
4. **Roční období:** Zeptej se na číslo měsíce (1–12) a vypiš roční období.
