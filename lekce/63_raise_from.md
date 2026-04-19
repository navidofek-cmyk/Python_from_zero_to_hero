# Lekce 63: `raise from`, řetězení výjimek

## 🔗 `raise X from Y` — když chyba vznikla z jiné

```python
try:
    int("abc")
except ValueError as e:
    raise RuntimeError("Špatný vstup") from e
```

V tracebacku uvidíš obě:

```
ValueError: invalid literal for int() with base 10: 'abc'

The above exception was the direct cause of the following exception:

RuntimeError: Špatný vstup
```

---

## 🆚 `from` vs implicitní řetězení

Bez `from` Python přidá automatický kontext (jen jiné formulace):

```python
try:
    int("abc")
except ValueError:
    raise RuntimeError("Špatný vstup")
# "During handling of the above exception, another exception occurred"
```

S `from` říkáš: „**tohle je důsledek toho.**“

---

## 🚫 `raise X from None` — schovej původní

```python
try:
    int("abc")
except ValueError:
    raise RuntimeError("Špatný vstup") from None
```

V tracebacku se původní `ValueError` **neobjeví**. Užitečné, když chceš čistý error pro uživatele knihovny.

---

## 🪟 `__cause__` a `__context__`

```python
try:
    raise RuntimeError("vnější") from ValueError("vnitřní")
except RuntimeError as e:
    print(e.__cause__)        # ValueError('vnitřní')
    print(e.__context__)      # totéž (s from i tady)
```

- `__cause__` = explicitní `from`
- `__context__` = automatické (bez `from`)

---

## 🎯 Best practice

✅ **Použij `from`** když překládáš jednu výjimku na jinou:
```python
except DatabaseError as e:
    raise UserNotFoundError(id) from e
```

✅ **Použij `from None`** když chceš schovat detaily:
```python
except DatabaseError:
    raise UserNotFoundError(id) from None
```

❌ **Nepoužívej `raise` bez ošetření** — ztratíš stack:
```python
try:
    risk()
except Exception:
    raise Exception("něco")    # ❌ zbytečné
# Lépe:
    raise                       # ← znovu vyhoď ORIGINÁL
```

---

## ✏️ Cvičení

1. **From:** Funkce co převede `KeyError` na `UserNotFoundError` přes `raise from`.
2. **From None:** Schovej technické detaily — uživatel vidí jen čistou chybu.
3. **Cause:** Vypiš `e.__cause__` po chytnutí.
4. **Re-raise:** Bez `from` jen znovu vyhodíš (`raise`).
