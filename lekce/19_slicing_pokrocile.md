# Lekce 19: Slicing pokročile

## ✂️ Plná syntaxe slice

`[start:stop:step]` — tři čísla. Všechna jsou volitelná.

```python
s = "ABCDEFGHIJ"
s[2:7]        # "CDEFG"     2..6
s[::2]        # "ACEGI"     každý druhý
s[::3]        # "ADGJ"
s[::-1]       # "JIHGFEDCBA" pozpátku
s[8:2:-1]     # "IHGFED"     pozpátku úsek
s[:5:2]       # "ACE"
```

---

## 📝 Přiřazení do slice (jen list)

Pomocí slice můžeš **měnit kus seznamu naráz**.

```python
seznam = [1, 2, 3, 4, 5]

seznam[1:3] = [20, 30, 40]      # nahradí pozice 1..2 třemi prvky
print(seznam)                    # [1, 20, 30, 40, 4, 5]

seznam[::2] = ["a", "b", "c"]   # přepiš každý druhý
print(seznam)                    # ['a', 20, 'b', 40, 'c', 5]

seznam[1:3] = []                 # smaže úsek
```

Pro každý druhý prvek **musí** sedět délka.

---

## 🪟 `slice` jako objekt

`s[1:5:2]` je vlastně zkratka pro `s[slice(1, 5, 2)]`. Slice si můžeš uložit do proměnné:

```python
prvni_pet = slice(0, 5)
kazdy_druhy = slice(None, None, 2)

s = "ABCDEFGHIJ"
s[prvni_pet]      # "ABCDE"
s[kazdy_druhy]    # "ACEGI"
```

Užitečné, když ten samý slice používáš víckrát.

---

## 🌈 Ekvivalence

| Zápis | Co to dělá |
|---|---|
| `s[:]` | celá kopie |
| `s[::-1]` | obrácená kopie |
| `s[:n]` | prvních `n` |
| `s[-n:]` | posledních `n` |
| `s[:-n]` | bez posledních `n` |
| `s[n:]` | od `n` dál |
| `s[::2]` | každý druhý |

---

## 🪆 Slicing 2D (numpy přesahuje)

`list[i][j]` musíš ručně. NumPy umí `arr[2:5, 1:3]` (lekce 98).

---

## ⚠️ Slice je shovívavý

Když řekneš příliš velké číslo, **nespadne** — jen ti vrátí, co má:

```python
s = "abc"
s[10:100]    # ""    (žádný IndexError!)
s[100]       # ❌ IndexError
```

---

## ✏️ Cvičení

1. **Pozpátku:** Otoč string `"Příšerně žluťoučký kůň"` pomocí `[::-1]`.
2. **Každé třetí:** Z `range(30)` udělej list a vyber každé třetí číslo.
3. **Prostřední úsek:** Ze seznamu 100 čísel vyber prostředních 10.
4. **Slice nahrazení:** Vyrob seznam `[1, 2, 3, 4, 5, 6]`. Nahraď první 3 prvky `[10, 20]`. Jak se změní délka?
5. **Slice objekt:** Vyrob proměnnou `kazdy_treti = slice(None, None, 3)`. Použij ji na 3 různých seznamech.
