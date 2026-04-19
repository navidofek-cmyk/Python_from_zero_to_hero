# Lekce 44: Metatřídy

## 🤯 Třída třídy?

V Pythonu je **každá třída sama instancí jiné třídy** — **metatřídy**. Defaultní metatřída je `type`.

```python
class Pes: pass

print(type(Pes))         # <class 'type'>   ← Pes je instance type!
print(type(type))        # <class 'type'>   ← type je instance sám sebe!
```

Mind blown. 🤯

---

## 🏭 `type` jako továrna

```python
# Klasické vytvoření třídy:
class Pes:
    def stekni(self):
        print("Haf!")

# To samé dynamicky pomocí type:
Pes = type(
    "Pes",                                   # jméno
    (),                                      # rodiče
    {"stekni": lambda self: print("Haf!")},  # atributy
)

p = Pes()
p.stekni()    # Haf!
```

Třídy v Pythonu jsou **objekty první kategorie** — můžeš je vyrobit za běhu, předat funkci, uložit do slovníku.

---

## 🎩 Vlastní metatřída

```python
class MujMeta(type):
    def __new__(mcs, jmeno, bases, attrs):
        print(f"Vyrábím třídu {jmeno}")
        attrs["vyrobil"] = "MujMeta"
        return super().__new__(mcs, jmeno, bases, attrs)


class Pes(metaclass=MujMeta):
    pass
# výstup: Vyrábím třídu Pes

print(Pes.vyrobil)   # MujMeta
```

Metatřída ovlivní **vytváření třídy** (ne instance!).

---

## 🪶 Lehčí alternativa: `__init_subclass__`

V 99 % případů, kdy by ses dotkl metatřídy, stačí `__init_subclass__`:

```python
class Plugin:
    plugins = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin.plugins.append(cls)


class MujPlugin(Plugin): pass
class JinyPlugin(Plugin): pass

print(Plugin.plugins)   # [MujPlugin, JinyPlugin]
```

Auto-registrace pluginů, validace, modifikace třídy — vše bez metatřídy.

---

## 🚧 Kdy POUŽÍT metatřídu?

Téměř nikdy. Citát z Tima Petersa:
> „Metatřídy jsou hlubší magie, než většina uživatelů potřebuje. Pokud váháš, jestli ji potřebuješ, **nepotřebuješ ji**.“

Realita: ABCMeta, Django Model, SQLAlchemy DeclarativeBase, Pydantic — všechny vnitřně používají metatřídy.

Ale ty jako uživatel: použij `__init_subclass__`, dataclass, decorator.

---

## ✏️ Cvičení

1. **Type:** Vyrob třídu `Auto` dynamicky pomocí `type()`.
2. **Init subclass:** Vyrob registr pluginů přes `__init_subclass__`.
3. **Logování:** Metatřída co loguje vytvoření každé třídy.
4. **Validace:** Metatřída co vyžaduje aby každá podtřída měla metodu `start`.
