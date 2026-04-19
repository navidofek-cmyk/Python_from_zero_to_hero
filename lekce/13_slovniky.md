# Lekce 13: Slovníky (`dict`)

## 📖 Co je slovník?

Slovník je jako **opravdový slovník** nebo **telefonní seznam**: máš **klíč** (heslo, jméno) a k němu **hodnotu** (definici, číslo).

```python
osoba = {
    "jmeno": "Eliška",
    "vek": 10,
    "mesto": "Praha",
}

print(osoba["jmeno"])    # Eliška
```

- Klíč → hodnota
- Klíč musí být **neměnný** (string, číslo, tuple — ne list!)
- Hodnota může být cokoliv

---

## 🔧 Hlavní operace

```python
osoba["email"] = "el@example.com"   # přidá nebo přepíše
osoba["vek"] = 11                    # změní

del osoba["mesto"]                   # smaže klíč
osoba.pop("email", None)             # smaže a vrátí (None když není)

"jmeno" in osoba                     # True (kontrola existence)
len(osoba)                           # počet klíčů
```

### Bezpečné čtení s `.get()`

```python
osoba["telefon"]              # ❌ KeyError! Klíč neexistuje
osoba.get("telefon")          # None  (žádný pád)
osoba.get("telefon", "—")     # "—"   (default hodnota)
```

---

## 🔁 Procházení

```python
for klic in osoba:
    print(klic)               # jen klíče

for klic, hodnota in osoba.items():
    print(f"{klic}: {hodnota}")

osoba.keys()                  # všechny klíče
osoba.values()                # všechny hodnoty
osoba.items()                 # páry (klíč, hodnota)
```

---

## 🎁 `setdefault` — vytvoř, pokud neexistuje

```python
pocty = {}
slovo = "ahoj"
pocty.setdefault(slovo, 0)
pocty[slovo] += 1
```

Místo `if klic not in dict: dict[klic] = ...`

(Ještě líp viz `defaultdict` v lekci 17.)

---

## ✨ Dict comprehension

Stejně jako u seznamů:

```python
ctverce = {x: x*x for x in range(1, 6)}
# {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

# Inverze (klíče <-> hodnoty)
inverze = {v: k for k, v in osoba.items()}
```

---

## 🔀 Spojení slovníků

```python
a = {"x": 1, "y": 2}
b = {"y": 99, "z": 3}

# Python 3.9+ — operátor |
spojeno = a | b           # {"x": 1, "y": 99, "z": 3}  (b vyhrává)

# Update — mění a
a.update(b)               # a se změní

# Rozbalení **
spojeno = {**a, **b}      # alternativa
```

---

## 🪆 Vnořené slovníky

```python
trida = {
    "Eliška": {"vek": 10, "predmet": "matematika"},
    "Jan":    {"vek": 11, "predmet": "čeština"},
}

print(trida["Eliška"]["vek"])    # 10
```

---

## 📊 Klasický příklad — počítání slov

```python
text = "ahoj svete ahoj kamarade svete svete"
slova = text.split()

pocty = {}
for slovo in slova:
    pocty[slovo] = pocty.get(slovo, 0) + 1

print(pocty)    # {'ahoj': 2, 'svete': 3, 'kamarade': 1}
```

---

## ✏️ Cvičení

1. **Telefoní seznam:** Vyrob slovník 5 jmen → telefonních čísel. Přidej jedno, smaž jedno, vypiš jedno.
2. **Procházení:** Pro každého ve slovníku vypiš `Jméno: Eliška, Telefon: 123`.
3. **Bezpečně:** Zeptej se uživatele na jméno a vypiš telefon. Když ho neznáš, vypiš `"neznámý"`.
4. **Počítání:** Spočítej, kolikrát se v textu opakuje každé písmeno.
5. **Inverze:** Vyrob slovník `{1: "jedna", 2: "dva", 3: "tři"}`. Vyrob k němu inverzi.
