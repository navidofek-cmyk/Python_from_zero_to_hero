# Lekce 43: Deskriptory

## 🎯 Co je deskriptor?

**Deskriptor** je objekt s metodami `__get__`, `__set__` (a/nebo `__delete__`), který **kontroluje přístup k atributu** v jiné třídě.

To je to **kouzlo, na kterém staví `@property`, `@classmethod`, `@staticmethod`** a SQLAlchemy ORM atributy.

```python
class Validator:
    def __init__(self, min_hodnota: int):
        self.min_hodnota = min_hodnota

    def __set_name__(self, owner, name):
        self._jmeno = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self._jmeno]

    def __set__(self, instance, hodnota):
        if hodnota < self.min_hodnota:
            raise ValueError(f"{self._jmeno} musí být >= {self.min_hodnota}")
        instance.__dict__[self._jmeno] = hodnota


class Osoba:
    vek = Validator(0)
    skore = Validator(0)


o = Osoba()
o.vek = 25       # OK
o.skore = -5     # ❌ ValueError
```

---

## 🔌 `__get__`, `__set__`, `__delete__`

```python
class D:
    def __get__(self, instance, owner):
        # instance = objekt na kterém čteš (nebo None u třídy)
        # owner = třída
        ...

    def __set__(self, instance, hodnota):
        ...

    def __delete__(self, instance):
        ...
```

A bonus `__set_name__(self, owner, name)` — Python ti řekne, jak se atribut jmenuje.

---

## 🧠 Jak to vlastně funguje?

Když napíšeš `o.x`, Python kontroluje:
1. Je `x` **data deskriptor** (má `__set__` nebo `__delete__`) ve **třídě**? → použij ho.
2. Je `x` v `o.__dict__`? → vrať to.
3. Je `x` **non-data deskriptor** (má jen `__get__`) ve třídě? → použij ho.
4. Je `x` jako obyčejný atribut třídy? → vrať to.
5. Jinak → `__getattr__` nebo `AttributeError`.

`@property` je deskriptor s `__get__`, `__set__`, `__delete__`. Proto funguje.

---

## 🎯 Reálný příklad: typed atributy

```python
class TypedField:
    def __init__(self, expected_type):
        self.expected_type = expected_type

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(f"{self.name} musí být {self.expected_type.__name__}")
        instance.__dict__[self.name] = value


class Pes:
    jmeno = TypedField(str)
    vek = TypedField(int)


rex = Pes()
rex.jmeno = "Rex"
rex.vek = 5
rex.vek = "pět"   # ❌ TypeError
```

To samé dělá Pydantic, SQLAlchemy, Django ORM, ale samozřejmě sofistikovaněji.

---

## ✏️ Cvičení

1. **PositiveInt:** Deskriptor co povolí jen kladná celá čísla.
2. **TypedField:** Implementuj jako výše. Otestuj.
3. **Logger:** Deskriptor co loguje každé čtení a zápis.
4. **Property bez @property:** Implementuj „celsius/fahrenheit“ z lekce 34, ale jako deskriptor.
