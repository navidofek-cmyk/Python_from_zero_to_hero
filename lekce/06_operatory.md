# Lekce 6: Operátory

## ⚙️ Co jsou operátory?

**Operátory** jsou **znamínka**, která něco dělají s hodnotami. Jako v matice: `+`, `-`, `*`, `/`. V Pythonu jich je ale víc druhů.

---

## ➕ Aritmetické (počítání)

```python
5 + 3     # 8
5 - 3     # 2
5 * 3     # 15
5 / 3     # 1.666...  (vždy float)
5 // 3    # 1         (celočíselné, zaokrouhlí dolů)
5 % 3     # 2         (zbytek — „kolik zbude“)
5 ** 3    # 125       (mocnina: 5×5×5)
```

### Fígl s `%` — sudé/liché

```python
cislo % 2 == 0   # True když je sudé
```

---

## 🆚 Porovnávací (zjišťování)

Vracejí `True` nebo `False`.

```python
5 == 5   # True   (rovná se)
5 != 3   # True   (nerovná se)
5 > 3    # True
5 < 3    # False
5 >= 5   # True
5 <= 4   # False
```

### Python umí řetězit!

```python
0 < vek < 18    # znamená: vek > 0 AND vek < 18
```

To je jako matika v učebnici. Jiné jazyky to neumí, Python ano. 🎉

---

## 🧠 Logické (`and`, `or`, `not`)

```python
True and True     # True  (AND = obě musí být pravda)
True and False    # False
True or False     # True  (OR = stačí jedno)
not True          # False (NOT = obráceně)
```

**Přirovnání:** 
- `and` = „**a zároveň**“ (mám hlad **a zároveň** mám peníze)
- `or` = „**nebo**“ (mám deštník **nebo** mám pláštěnku)
- `not` = „**ne**“ (nemám hlad)

### Short-circuit (zkrat) — Python je líný

Když vidí `False and ...`, vůbec se nedívá na druhou stranu. Už ví, že je to `False`.

```python
def drahe():
    print("Počítám...")
    return True

False and drahe()   # "Počítám..." se NEVYPÍŠE
True or drahe()     # "Počítám..." se NEVYPÍŠE
```

Využití: bezpečné podmínky

```python
if seznam and seznam[0] == "ahoj":  # nespadne, i když je seznam prázdný
    ...
```

---

## 🔀 Ternární výraz — zkratka pro if/else

Místo:
```python
if vek >= 18:
    stav = "dospělý"
else:
    stav = "dítě"
```

Můžeš napsat jeden řádek:

```python
stav = "dospělý" if vek >= 18 else "dítě"
```

Čti: „**dospělý, když vek >= 18, jinak dítě**.“

---

## 🐭 Walrus `:=` (od Pythonu 3.8)

Přiřadí a vrátí zároveň. Vypadá jako mrož 🐭🦷🦷 (dvě tesáky).

```python
# Bez walrusu
n = len(seznam)
if n > 10:
    print(f"Dlouhý seznam, má {n} prvků")

# S walrusem — na jeden řádek
if (n := len(seznam)) > 10:
    print(f"Dlouhý seznam, má {n} prvků")
```

Hodí se hlavně ve `while`:

```python
while (radek := input()) != "stop":
    print(f"Napsals: {radek}")
```

---

## 🔧 Bitové operátory (pro pokročilé, zatím jen přehled)

Pracují s jednotlivými **bity** čísla. Zatím přeskoč, pokud nevíš co to je.

```python
5 & 3   # AND po bitech → 1
5 | 3   # OR po bitech  → 7
5 ^ 3   # XOR po bitech → 6
~5      # NOT           → -6
5 << 1  # posun vlevo   → 10  (×2)
5 >> 1  # posun vpravo  → 2   (/2, zaokr. dolů)
```

---

## 📌 Kombinované přiřazení

Zkratky:

```python
x += 1    # x = x + 1
x -= 2    # x = x - 2
x *= 3    # x = x * 3
x //= 2   # x = x // 2
```

---

## ✏️ Cvičení

1. **Sudé nebo liché?** Zeptej se na číslo a pomocí `%` zjisti, jestli je sudé nebo liché.
2. **Věková kontrola:** Uživatel zadá věk. Použij řetězené porovnání `0 < vek < 120` a pokud ne, napiš „nesmysl“.
3. **Ternární:** Ze dvou čísel vypiš to větší jedním řádkem pomocí ternárního výrazu.
4. **Walrus:** Napiš smyčku, která čte `input()` dokud uživatel nenapíše "konec". Použij `:=`.
5. **Logika:** Vytvoř proměnné `mam_pristup = True`, `je_zapnuto = False`. Zjisti pomocí `and`/`or`/`not`, jestli to můžeš použít.
