# Lekce 49: Dynamické vytváření tříd

## 🏭 `type()` jako továrna

`type()` má dva režimy:
- `type(x)` — vrátí typ objektu
- `type(jmeno, bases, attrs)` — **vyrobí novou třídu**

```python
def stekni(self):
    print(f"{self.jmeno}: Haf!")

Pes = type(
    "Pes",
    (),
    {
        "stekni": stekni,
        "__init__": lambda self, jmeno: setattr(self, "jmeno", jmeno),
    },
)

rex = Pes("Rex")
rex.stekni()       # Rex: Haf!
print(type(rex))   # <class '__main__.Pes'>
```

To je to, co Python dělá pod kapotou pro každou `class ...`.

---

## 🎯 Kdy je to užitečné?

### 1. Generování tříd ze schématu

```python
def vytvor_dataclass(jmeno: str, pola: dict[str, type]):
    annotations = pola

    def __init__(self, **kwargs):
        for f in pola:
            setattr(self, f, kwargs.get(f))

    return type(jmeno, (), {
        "__init__": __init__,
        "__annotations__": annotations,
    })


Uzivatel = vytvor_dataclass("Uzivatel", {"jmeno": str, "vek": int})
u = Uzivatel(jmeno="Anna", vek=12)
print(u.jmeno, u.vek)
```

### 2. ORM

Django nebo SQLAlchemy generují třídy z databázového schématu.

### 3. Plugins z konfigurace

Načteš YAML/JSON a podle něj postavíš třídy.

---

## 🔧 `types.new_class`

Modernější alternativa, lépe spolupracuje s metatřídami:

```python
import types

NovaTrida = types.new_class("NovaTrida", (object,), {}, lambda ns: ns.update({"x": 1}))
```

V praxi 99 % případů řeší obyčejné `type(...)`.

---

## ⚠️ Kdy NE

Pokud nemáš silný důvod (ORM, plugin systém, generátor kódu), **používej obyčejné `class`**. Dynamicky vytvořené třídy:
- jsou hůř čitelné
- nemají pomocníka v IDE
- mypy si s nimi neporadí

---

## ✏️ Cvičení

1. **Bod:** Vyrob třídu `Bod` dynamicky pomocí `type()` s atributy `x, y` a metodou `vzdalenost(other)`.
2. **Z konfigurace:** Vytvoř funkci `udelej_tridu(jmeno, atributy_dict)` co vrátí novou třídu.
3. **Auto-property:** Funkce co dostane jména polí a vyrobí třídu se settery/gettery.
