# Lekce 61: `try`/`except`/`else`/`finally`

## ⚠️ Co je výjimka?

**Výjimka** je „chyba“ — něco šlo špatně a program by jinak spadnul. Místo pádu **chytíš** výjimku a rozhodneš, co dál.

```python
try:
    x = int(input("Číslo: "))
    vysledek = 10 / x
except ValueError:
    print("To není číslo!")
except ZeroDivisionError:
    print("Nuly se dělit nedá!")
```

---

## 🔧 Plná struktura

```python
try:
    riskantni_akce()
except SomeError as e:
    # když přijde výjimka
    print(f"Chyba: {e}")
except (TypeError, ValueError):
    # víc typů najednou
    print("Něco jiného")
except Exception as e:
    # cokoli (poslední záchrana)
    print(f"Něco se stalo: {e}")
else:
    # když NEPŘIJDE výjimka
    print("Vše v pořádku")
finally:
    # VŽDYCKY (i při výjimce, i bez)
    print("Úklid")
```

### Pořadí matters

```python
try: ...
except Exception: ...     # ❌ tohle by chytlo VŠE
except ValueError: ...    # ← už se nikdy nespustí
```

Speciální výjimky **PRVNÍ**, obecné **POSLEDNÍ**.

---

## 🌳 Hierarchie výjimek

```
BaseException
 ├── SystemExit
 ├── KeyboardInterrupt           ← Ctrl+C
 ├── GeneratorExit
 └── Exception                    ← chytej tohle (ne BaseException)
      ├── ArithmeticError
      │    └── ZeroDivisionError
      ├── LookupError
      │    ├── IndexError
      │    └── KeyError
      ├── ValueError
      ├── TypeError
      ├── FileNotFoundError
      └── ...
```

**Pravidlo:** chytej `Exception`, ne `BaseException` (jinak chytíš i Ctrl+C).

---

## 🎯 Nejčastější výjimky

| Výjimka | Kdy |
|---|---|
| `ValueError` | Špatná hodnota — `int("abc")` |
| `TypeError` | Špatný typ — `"a" + 1` |
| `KeyError` | Chybí klíč ve dict |
| `IndexError` | Index mimo seznam |
| `FileNotFoundError` | Soubor neexistuje |
| `PermissionError` | Není oprávnění |
| `ZeroDivisionError` | Dělení nulou |
| `AttributeError` | Atribut neexistuje |
| `ImportError` | Modul se nedá importovat |
| `RuntimeError` | Cokoli jiného za běhu |

---

## 🚫 Anti-vzory

### ❌ Bare except

```python
try:
    ...
except:                      # nikdy nevíš, co chytáš
    pass
```

Chytíš i `KeyboardInterrupt` — uživatel nemůže ukončit program!

### ❌ Polykání výjimek

```python
try:
    riskantni()
except Exception:
    pass                     # tiše ignoruje VŠE
```

Skryješ chyby, debugging noční můra.

### ✅ Specifické except

```python
try:
    riskantni()
except FileNotFoundError:
    return "default"
```

Chytej **jen to, co umíš zpracovat**.

---

## 🎯 `else` vs `try`

```python
# ❌ Špatně — vše v try
try:
    soubor = open("a.txt")
    obsah = soubor.read()
    soubor.close()
    zpracuj(obsah)            # ← když tady padne, chytí to except!
except FileNotFoundError:
    ...

# ✅ Lépe — jen to riskantní v try
try:
    soubor = open("a.txt")
except FileNotFoundError:
    ...
else:
    obsah = soubor.read()
    soubor.close()
    zpracuj(obsah)
```

---

## 🧯 `finally` — úklid

```python
soubor = None
try:
    soubor = open("a.txt")
    ...
finally:
    if soubor:
        soubor.close()           # vždy se zavolá
```

Většinou ale lepší použít `with` (lekce 46):
```python
with open("a.txt") as soubor:
    ...
# automatický zavření
```

---

## ✏️ Cvičení

1. **Bezpečný int:** Funkce `bezpecne_int(text, default=0)` co vrátí int nebo default.
2. **Dělení:** Zachyť `ZeroDivisionError` i `TypeError`.
3. **Soubor:** Otevři neexistující soubor a hezky to zpracuj.
4. **Else:** Napiš příklad s `try/except/else/finally` — všechny větve.
5. **Anti-vzor:** Najdi v nějakém starém kódu „bare except“ a oprav ho.
