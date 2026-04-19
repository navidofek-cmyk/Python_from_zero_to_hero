# Lekce 79: Regulární výrazy (`re`)

## 🎯 Co je regex?

**Regex** = vzor pro hledání v textu. Mocný, ale **náročný na čtení**.

```python
import re

re.search(r"\d+", "Mám 42 jablek")    # Match object: '42'
re.findall(r"\d+", "1, 2, 3, 4")       # ['1', '2', '3', '4']
re.sub(r"\d+", "X", "1 a 2")           # 'X a X'
re.split(r"\s+", "ahoj   svete")       # ['ahoj', 'svete']
```

**Vždy `r"..."`** (raw string) — vyhneš se interpretaci backslashů.

---

## 📋 Hlavní symboly

| Symbol | Význam |
|---|---|
| `\d` | číslice (0–9) |
| `\D` | NEčíslice |
| `\w` | písmeno/číslice/_ |
| `\W` | NEpísmeno |
| `\s` | whitespace |
| `\S` | NE-whitespace |
| `.` | jakýkoli znak (kromě \n) |
| `^` | začátek řetězce |
| `$` | konec |
| `\b` | hranice slova |

### Kvantifikátory

| Symbol | Význam |
|---|---|
| `*` | 0 nebo víc |
| `+` | 1 nebo víc |
| `?` | 0 nebo 1 |
| `{n}` | přesně n |
| `{n,m}` | n až m |

### Speciální

| Symbol | Význam |
|---|---|
| `[abc]` | jeden z a, b, c |
| `[^abc]` | NE a, b, c |
| `[a-z]` | rozsah |
| `(...)` | skupina |
| `a|b` | a nebo b |

---

## 🛠️ Hlavní funkce

```python
re.match(vzor, text)      # od ZAČÁTKU
re.search(vzor, text)     # kdekoliv (první výskyt)
re.findall(vzor, text)    # všechny výskyty (list)
re.finditer(vzor, text)   # iterator Match objektů
re.sub(vzor, nahrada, text)
re.split(vzor, text)
```

### Match object

```python
m = re.search(r"(\d+)-(\d+)", "číslo 12-34 tady")
m.group()       # '12-34'    (celá match)
m.group(1)      # '12'       (první skupina)
m.group(2)      # '34'
m.groups()      # ('12', '34')
m.start(), m.end()
```

---

## 🏷️ Pojmenované skupiny

```python
m = re.search(r"(?P<jmeno>\w+) (?P<vek>\d+)", "Anna 12")
m.group("jmeno")    # 'Anna'
m.group("vek")      # '12'
m.groupdict()       # {'jmeno': 'Anna', 'vek': '12'}
```

---

## 📝 `re.VERBOSE` — čitelný regex

```python
vzor = re.compile(r"""
    (\d{4})        # rok
    -
    (\d{2})        # měsíc
    -
    (\d{2})        # den
""", re.VERBOSE)

vzor.match("2026-04-18")
```

Komentáře a whitespace se ignorují.

---

## ⚡ `re.compile` — pro opakované použití

```python
vzor = re.compile(r"\d+")
for radek in soubor:
    if vzor.search(radek):
        ...
```

Rychlejší, když ten samý regex používáš víckrát.

---

## 🎯 Praktické příklady

### Email validace (jednoduchá)

```python
EMAIL = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
EMAIL.match("ahoj@example.com")    # Match
EMAIL.match("ne_email")             # None
```

### Najdi všechny URL

```python
URL = re.compile(r"https?://\S+")
URL.findall(text)
```

### Telefon

```python
TELEFON = re.compile(r"^\+?\d{3}[ -]?\d{3}[ -]?\d{3}$")
```

---

## 🚨 Pasti

1. **`*` a `+` jsou greedy** — chytí co nejvíc. Pro non-greedy: `*?`, `+?`.
2. **`re.match` matchuje od začátku** — pro „kdekoli“ použij `re.search`.
3. **Raw string** `r"..."` — vždy.
4. **Pro HTML/XML/JSON** **NEPOUŽÍVEJ** regex. Použij parser (`bs4`, `lxml`, `json`).

---

## ✏️ Cvičení

1. **Najdi čísla:** V textu „Mám 5 jablek a 12 hrušek a 3 banány“ vytáhni všechna čísla.
2. **Email:** Validuj emaily ze seznamu.
3. **PSČ:** Najdi všechna česká PSČ (5 cifer, někdy s mezerou).
4. **Sub:** Nahraď všechna telefoní čísla v textu řetězcem `XXX`.
5. **Skupiny:** Z `"2026-04-18"` vytáhni rok, měsíc, den jako pojmenované skupiny.
