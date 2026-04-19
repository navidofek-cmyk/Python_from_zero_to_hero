# Lekce 5: Řetězce a f-stringy

## 🧵 Co je řetězec?

**Řetězec** (anglicky `string`) je **provázek písmenek**. Kus textu.

```python
jmeno = "Eliška"
pozdrav = 'Ahoj'
dlouhy = """Tohle je
víceřádkový text."""
```

Uvozovky můžou být `"..."` nebo `'...'` (jedno jakou si vybereš). Pro víceřádkový text použij trojité `"""..."""`.

---

## ✂️ Slicing — vykrajování z řetězce

Řetězec si představ jako **vláček s písmenky**. Každý vagónek má číslo:

```
 E   l   i   š   k   a
 0   1   2   3   4   5    ← kladná čísla zleva
-6  -5  -4  -3  -2  -1    ← záporná čísla zprava
```

```python
jmeno = "Eliška"
jmeno[0]      # "E"     první písmeno
jmeno[-1]     # "a"     poslední písmeno
jmeno[0:3]    # "Eli"   vagónky 0, 1, 2 (trojku už NE!)
jmeno[:3]     # "Eli"   od začátku
jmeno[3:]     # "ška"   do konce
jmeno[::-1]   # "akšilE" celý pozpátku
```

---

## 🛠️ Užitečné metody řetězce

```python
text = "  Ahoj Svete  "

text.strip()          # "Ahoj Svete" (ořízne mezery)
text.upper()          # "  AHOJ SVETE  "
text.lower()          # "  ahoj svete  "
text.replace("o", "0")# "  Ah0j Svete  "
text.split()          # ["Ahoj", "Svete"]   (rozdělí po mezerách)
"-".join(["a","b"])   # "a-b"                (spojí seznamem)
len(text)             # 14 (počet znaků)
"Ahoj" in text        # True (je to tam?)
text.startswith("  ") # True
text.endswith("!")    # False
```

---

## 🎩 F-stringy — kouzelné vkládání do textu

Chceš vyrobit text z proměnných. **F-string** je nejjednodušší způsob.

Před uvozovky napíšeš `f` a do `{...}` dáš, co chceš vložit:

```python
jmeno = "Eliška"
vek = 10

# 🎉 f-string — takhle se to dělá!
print(f"Ahoj {jmeno}, je ti {vek} let.")
# Ahoj Eliška, je ti 10 let.
```

### Uvnitř `{...}` můžeš **úplně cokoliv**

```python
print(f"Za rok ti bude {vek + 1}.")
print(f"Tvoje jméno má {len(jmeno)} písmen.")
print(f"Velkými: {jmeno.upper()}")
```

### Formátování čísel

```python
pi = 3.14159265
print(f"{pi:.2f}")       # 3.14      (2 desetinná místa)
print(f"{1000000:,}")    # 1,000,000 (oddělovače)
print(f"{0.75:.1%}")     # 75.0%     (jako procenta)
print(f"{42:5d}")        # "   42"   (zarovnání na 5 míst)
print(f"{42:05d}")       # "00042"   (doplnění nulami)
```

### Debugovací trik (od Pythonu 3.8)

Napiš `=` za jméno proměnné a f-string ti ji vypíše i s názvem:

```python
x = 42
print(f"{x=}")    # x=42   ← super pro ladění!
```

---

## 🧮 Escape sekvence

Speciální znaky uvnitř řetězce:

| Sekvence | Co dělá |
|---|---|
| `\n` | nový řádek |
| `\t` | tabulátor |
| `\\` | samotné zpětné lomítko |
| `\"` | uvozovka uvnitř `"..."` |

```python
print("Řádek 1\nŘádek 2")
```

### Raw řetězce (syrové)

Když nechceš, aby Python interpretoval zpětná lomítka, dej před uvozovky `r`:

```python
cesta = r"C:\Users\Eliska\soubor.txt"   # zpětná lomítka zůstanou
vzor = r"\d+"                            # pro regulární výrazy
```

---

## ✏️ Cvičení

1. **Vlastní jméno:** Ulož své jméno do proměnné. Vypiš: první písmeno, poslední písmeno, celé jméno velkými písmeny, pozpátku.
2. **Karta:** Uživatele se zeptej na jméno a věk. Vypiš: `"═══ Jméno: Eliška, Věk: 10 ═══"` pomocí f-stringu.
3. **Rozdělení:** Máš text `"banán jablko hruška"`. Rozděl ho na seznam. Pak ho spoj zpátky pomlčkami.
4. **Formát:** Vypiš číslo Pi na 4 desetinná místa a pak jako procento (třeba `3.14159` jako `314.159%`).
