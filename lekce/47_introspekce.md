# Lekce 47: Introspekce a monkey patching

## 🔍 Co je introspekce?

**Introspekce** = schopnost programu **dívat se na sebe sama** — zjistit, jaké třídy/funkce/atributy existují.

Python je v tomhle MISTR.

---

## 🛠️ Základní funkce

```python
type(x)          # typ objektu
isinstance(x, T) # je x instance T (nebo potomka)?
issubclass(A, B) # je A potomek B?
hasattr(x, "n")  # má atribut?
getattr(x, "n", default)   # vrať atribut (nebo default)
setattr(x, "n", v)         # nastav atribut
delattr(x, "n")            # smaž atribut

dir(x)           # všechny atributy a metody
vars(x)          # __dict__ jako slovník
id(x)            # unikátní ID (adresa v paměti)
callable(x)      # dá se zavolat?
```

---

## 🎯 Praktický `getattr`

Místo:
```python
if hasattr(obj, "akce"):
    obj.akce()
```

Můžeš:
```python
metoda = getattr(obj, "akce", None)
if metoda is not None:
    metoda()
```

Nebo dispatch podle jména:
```python
def zpracuj(akce: str, obj):
    metoda = getattr(obj, f"akce_{akce}")
    return metoda()
```

---

## 🐒 Monkey patching

**Monkey patch** = přidávání/změna metod tříd nebo modulů **za běhu**.

```python
class Pes:
    def stekni(self):
        print("Haf!")

# Přidáme metodu zvenčí — to je monkey patch
def vrti(self):
    print("Vrtí ocasem")

Pes.vrti = vrti

rex = Pes()
rex.vrti()    # Vrtí ocasem
```

Můžeš i přepsat **existující** metodu:

```python
def stekni_jinak(self):
    print("WAU!")

Pes.stekni = stekni_jinak
```

---

## ⚠️ Kdy monkey patch ano/ne

✅ **Ano**:
- Testy — náhrada `time.sleep` mockem
- Hotfix knihovny, kterou nemůžeš upravit
- Plugin systém

❌ **Ne**:
- V produkčním kódu pro „pohodlí“
- Když existuje normální cesta (dědičnost, dependency injection)

Monkey patch je **silný, ale debug noční můra** — kód se chová jinak, než vidíš v souboru.

---

## 🔧 `hasattr` past

```python
class A:
    @property
    def x(self):
        raise RuntimeError("ouch")

hasattr(A(), "x")   # False!  (hasattr spolkne výjimku)
```

V Pythonu 3 se to chová líp, ale stejně pozor.

---

## ✏️ Cvičení

1. **Dir:** Vypiš všechny metody seznamu (`dir([])`).
2. **Getattr:** Vyrob slovník `akce → funkce` pomocí `getattr(modul, jmeno)`.
3. **Monkey patch:** Přidej metodu `cele_jmeno` do `str` (vtipně).
4. **Kontrola:** Funkce `bezpecne_volej(obj, jmeno_metody, *args)` co zkontroluje `hasattr` a `callable`.
