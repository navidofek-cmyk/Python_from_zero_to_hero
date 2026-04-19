# Lekce 3: Proměnné, jména a dynamické typování

## 📦 Co je proměnná?

Proměnná je **nálepka nalepená na krabici**. V krabici je něco (hračka, číslo, slovo) a ty máš k té krabici papírovou nálepku se jménem.

```python
jmeno = "Eliška"
vek = 10
```

- `jmeno` je **nálepka**.
- `"Eliška"` je **věc v krabici** (objekt).
- Znaménko `=` neznamená „rovná se“! Znamená **„nalep nálepku na tuhle krabici“**.

---

## 🏷️ Jedna krabice, víc nálepek

Můžeš nalepit **víc nálepek na jednu krabici**:

```python
a = [1, 2, 3]
b = a          # b je druhá nálepka na STEJNÉ krabici
b.append(4)
print(a)       # [1, 2, 3, 4]   ← změnila se! Je to stejná krabice!
```

Když chceš **novou krabici** se stejným obsahem, musíš si udělat kopii:

```python
b = a.copy()   # teď je b jiná krabice
```

---

## 🧙 Dynamické typování

V některých jazycích musíš dopředu říct: „Tahle krabice bude na čísla.“ V Pythonu **ne**. Krabice je jen krabice — co do ní dáš, to tam je.

```python
x = 5          # teď je uvnitř číslo
x = "ahoj"     # teď je uvnitř slovo
x = [1, 2, 3]  # teď je tam seznam
```

Pythonu je to jedno — kontroluje si typ **až při použití**. Tomu se říká **dynamické typování**.

---

## 🔍 `id()`, `is` a `==`

Každá krabice má **sériové číslo** (adresu v paměti). Zjistíš ho přes `id()`:

```python
a = [1, 2, 3]
b = a
c = [1, 2, 3]

print(id(a), id(b), id(c))
# a a b mají STEJNÉ číslo (stejná krabice)
# c má jiné (jiná krabice se stejným obsahem)
```

A teď pozor na rozdíl:

- `==` se ptá: **„Mají krabice stejný obsah?“**
- `is` se ptá: **„Je to úplně ta stejná krabice?“**

```python
a == c   # True  (stejný obsah)
a is c   # False (jiné krabice)
a is b   # True  (stejná krabice)
```

**Používej `is` skoro jen na `None`:** `if x is None:`.

---

## 📝 Pravidla pro jména proměnných

- Můžou obsahovat písmena, čísla, podtržítka `_`.
- **Nesmí začínat číslem.** (`2pes` ❌)
- Jsou **case-sensitive** — `Pes` a `pes` jsou dvě různé nálepky.
- Píšeme je `takto_s_podtrzitkem` (snake_case), ne `TaktoSVelkymi` (to je pro třídy).
- Nepoužívej jména jako `list`, `dict`, `str`, `sum` — jsou to jména robotových nástrojů a přepsal bys je.

---

## ✏️ Cvičení

1. **Dvě nálepky:** Vytvoř `seznam1 = [1, 2, 3]` a `seznam2 = seznam1`. Přidej do `seznam2` číslo 4. Co je v `seznam1`? Proč?
2. **Dvě krabice:** Teď udělej `seznam3 = seznam1.copy()`. Přidej do `seznam3` číslo 5. Je to v `seznam1`?
3. **Sériová čísla:** Použij `id()` na `seznam1`, `seznam2`, `seznam3`. Které dvě mají stejné?
4. **Přejmenování:** Vytvoř krabici se svým věkem. Pak ji „přejmenuj“ na `muj_vek`. Pak do stejné nálepky dej jméno místo čísla. Funguje to?
