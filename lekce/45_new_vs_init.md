# Lekce 45: `__new__` vs `__init__`

## 🥚 Dvoufázová tvorba

Když napíšeš `Pes("Rex")`, Python udělá:

1. **`__new__`** — vyrobí prázdnou instanci (alokuje paměť)
2. **`__init__`** — naplní ji daty

Většinou tě zajímá jen `__init__`. `__new__` se používá zřídka.

```python
class Pes:
    def __new__(cls, *args, **kwargs):
        print(f"__new__ s {args}")
        instance = super().__new__(cls)
        return instance

    def __init__(self, jmeno):
        print(f"__init__ s {jmeno}")
        self.jmeno = jmeno


Pes("Rex")
# __new__ s ('Rex',)
# __init__ s Rex
```

---

## 🎯 Kdy použít `__new__`?

### 1. Singleton (jediná instance)

```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


a = Singleton()
b = Singleton()
print(a is b)    # True
```

(Pythončtěji se to dělá modulem nebo class atributem, ale tohle je klasika.)

### 2. Immutable třídy dědící od int/str/tuple

`__init__` u `tuple`/`str`/`int` **nic nedělá** — musíš pracovat s `__new__`.

```python
class Vek(int):
    def __new__(cls, hodnota):
        if hodnota < 0:
            raise ValueError("Záporný věk")
        return super().__new__(cls, hodnota)


v = Vek(25)
print(v + 5)    # 30 (chová se jako int)
```

### 3. Vrácení jiné instance / typu

```python
class Tvar:
    def __new__(cls, **kwargs):
        if cls is Tvar:    # když voláš Tvar(...) přímo, vrať podtřídu
            if "polomer" in kwargs:
                return Kruh(kwargs["polomer"])
            elif "a" in kwargs:
                return Obdelnik(kwargs["a"], kwargs["b"])
        return super().__new__(cls)

class Kruh(Tvar): ...
class Obdelnik(Tvar): ...

t = Tvar(polomer=5)   # vrátí Kruh
```

(Tomu se říká **factory**.)

---

## 🚫 Pasti

### `__new__` musí vrátit instanci

Když nevrátí instanci `cls`, `__init__` se vůbec nezavolá:

```python
class A:
    def __new__(cls):
        return "ahoj"        # ne instance!

    def __init__(self):
        print("__init__")    # NIKDY nezavolá

a = A()
print(a)     # "ahoj"  (jen string!)
```

### Pozor na argumenty

`__new__` dostává stejné argumenty jako `__init__`. Když jeden přijme jiné, padne:

```python
class A:
    def __new__(cls, x):       # ← bere x
        return super().__new__(cls)

    def __init__(self, x, y):  # ← bere x, y
        ...

A(1, 2)   # __new__ dostane (1, 2) — přebytek!
```

---

## ✏️ Cvičení

1. **Singleton:** Implementuj přes `__new__`.
2. **Vek (int):** Třída co dědí od `int`, vyhodí ValueError pro záporné.
3. **Cache:** Třída `Bod(x, y)` co cachuje instance ve slovníku — `Bod(1, 2) is Bod(1, 2)`.
4. **Logger:** `__new__` co vypíše „Vyrábím X“ pro každou instanci.
