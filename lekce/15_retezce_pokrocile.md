# Lekce 15: Řetězce do hloubky

## 🔤 Pokročilé metody

```python
"ahoj svete".title()           # "Ahoj Svete"
"ahoj svete".capitalize()      # "Ahoj svete"
"AhOj".swapcase()              # "aHoJ"
"   ahoj   ".strip()           # "ahoj"
"---ahoj---".strip("-")        # "ahoj"
"abc".ljust(10, "*")           # "abc*******"
"abc".rjust(10, "*")           # "*******abc"
"abc".center(10, "*")          # "***abc****"
"abc".zfill(5)                 # "00abc"
```

---

## 🔍 Hledání

```python
"ahoj svete".find("svete")     # 5  (index, -1 když není)
"ahoj svete".index("svete")    # 5  (jako find, ale CHYBA když není)
"ahoj ahoj ahoj".count("ahoj") # 3
"ahoj".startswith("ah")        # True
"ahoj".endswith(("oj", "ek"))  # True (může brát tuple!)
```

---

## ✂️ Rozdělování a spojování

```python
"a,b,c".split(",")              # ["a", "b", "c"]
"a,b,c".split(",", 1)           # ["a", "b,c"]   (max 1 split)
"a\nb\nc".splitlines()          # ["a", "b", "c"]
"  ahoj  svete  ".split()       # ["ahoj", "svete"]  (whitespace)

",".join(["a", "b", "c"])       # "a,b,c"
"-".join("ahoj")                # "a-h-o-j"
```

---

## 🔄 `translate` a `maketrans`

Hromadná záměna znaků:

```python
tabulka = str.maketrans("aeiou", "AEIOU")
"ahoj svete".translate(tabulka)
# "AhOj svEtE"

# Smazání znaků
tabulka = str.maketrans("", "", "aeiou")
"ahoj svete".translate(tabulka)
# "hj svt"
```

---

## 🎨 `format` a `format_map`

Před érou f-stringů se používalo `format`:

```python
"Ahoj {jmeno}, je ti {vek}".format(jmeno="Eliška", vek=10)

# format_map bere přímo slovník
data = {"jmeno": "Eliška", "vek": 10}
"Ahoj {jmeno}, je ti {vek}".format_map(data)
```

F-stringy jsou lepší, ale `format_map` je užitečný, když ti někdo pošle slovník.

---

## 📑 `string.Template` — bezpečné šablony

Pro texty od uživatele (kde nechceš spouštět kód f-stringu):

```python
from string import Template

t = Template("Ahoj $jmeno, máš $body bodů.")
print(t.substitute(jmeno="Eliška", body=42))
```

`$jmeno` se nahradí, ale **žádné výrazy** jako u f-stringů.

---

## 🔠 Kontrola obsahu

```python
"abc".isalpha()       # True (jen písmena)
"123".isdigit()       # True (jen čísla)
"abc123".isalnum()    # True (písmena nebo čísla)
"   ".isspace()       # True (jen mezery)
"ABC".isupper()       # True
"abc".islower()       # True
"Ahoj Svete".istitle()# True
```

---

## 🌍 Kódování

```python
text = "Příšerně"
bytes_utf8 = text.encode("utf-8")    # → b'P\xc5\x99\xc3\xad\xc5\xa1ern\xc4\x9b'
zpet = bytes_utf8.decode("utf-8")    # → "Příšerně"
```

Vždycky pracuj s UTF-8. Jiná kódování (latin-2, cp1250) jsou pro starožitnosti.

---

## ✏️ Cvičení

1. **Title case:** Z textu `"ahoj svete jak se mas"` udělej `"Ahoj Svete Jak Se Mas"`.
2. **Vlastní cenzor:** Napiš funkci, která v textu nahradí písmena `aeiou` hvězdičkami pomocí `translate`.
3. **CSV řádek:** Z tuple `("Eliška", 10, "Praha")` udělej CSV řádek (`"Eliška,10,Praha"`).
4. **Šablona:** Použij `string.Template` na vyrobení dopisu („Milý $jmeno, …“).
5. **Validace:** Napiš funkci `je_pin(text)`, která vrátí True, pokud je `text` čtyřciferné číslo (jen `isdigit` + `len`).
