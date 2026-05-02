# Projekt 5: Mini ORM / validátor

Mini-projekt po **sekci V (Pokročilé OOP)**. Vlastní micro-ORM s validačními deskriptory — deklaruj model jako třídu a ORM validuje a ukládá záznamy.

**Použité koncepty:** deskriptory (43), `__init_subclass__` (44), metatřídy (44), dynamické třídy (49), Protocol (50).

## Jak spustit

```bash
python3 projekty/05_mini_orm/orm.py
```

## Ukázka použití

```python
class Pes(Model):
    jmeno = StringField(min_delka=1)
    vek = IntField(min_hodnota=0, max_hodnota=30)

rex = Pes(jmeno="Rex", vek=5)
rex.uloz()
print(Pes.vse())   # [Pes(jmeno='Rex', vek=5)]
```

## Zdrojový kód — `orm.py`

```python
"""Mini-projekt po sekci V: Mini ORM/validátor.

Procvičuje: deskriptory, __init_subclass__, dataclass, dynamické třídy,
Protocol, dunder metody.
"""

from typing import Any, ClassVar


class Field:
    """Základní deskriptor."""

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        self.validuj(value)
        instance.__dict__[self.name] = value

    def validuj(self, value): ...


class StringField(Field):
    def __init__(self, min_delka: int = 0, max_delka: int = 1000):
        self.min_delka = min_delka
        self.max_delka = max_delka

    def validuj(self, value):
        if not isinstance(value, str):
            raise TypeError(f"{self.name}: musí být string")
        if not (self.min_delka <= len(value) <= self.max_delka):
            raise ValueError(f"{self.name}: délka {len(value)} mimo rozsah")


class IntField(Field):
    def __init__(self, min_hodnota: int = -(10**9), max_hodnota: int = 10**9):
        self.min_hodnota = min_hodnota
        self.max_hodnota = max_hodnota

    def validuj(self, value):
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{self.name}: musí být int")
        if not (self.min_hodnota <= value <= self.max_hodnota):
            raise ValueError(f"{self.name}: {value} mimo rozsah")


class Model:
    """Bázová třída pro modely."""

    _registr: ClassVar[dict[str, list]] = {}
    _pole: ClassVar[list[str]] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Model._registr[cls.__name__] = []
        cls._pole = [k for k, v in cls.__dict__.items() if isinstance(v, Field)]

    def __init__(self, **kwargs):
        for nazev in self._pole:
            if nazev not in kwargs:
                raise ValueError(f"Chybí {nazev}")
            setattr(self, nazev, kwargs[nazev])

    def uloz(self) -> None:
        Model._registr[type(self).__name__].append(self)

    @classmethod
    def vse(cls) -> list:
        return Model._registr.get(cls.__name__, [])

    def to_dict(self) -> dict[str, Any]:
        return {p: getattr(self, p) for p in self._pole}

    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.to_dict().items())
        return f"{type(self).__name__}({attrs})"


# === Použití ===

class Pes(Model):
    jmeno = StringField(min_delka=1, max_delka=20)
    vek = IntField(min_hodnota=0, max_hodnota=30)


class Auto(Model):
    znacka = StringField(min_delka=2)
    rok = IntField(min_hodnota=1900, max_hodnota=2030)


def main() -> None:
    Pes(jmeno="Rex", vek=5).uloz()
    Pes(jmeno="Bonzo", vek=3).uloz()
    Auto(znacka="Škoda", rok=2020).uloz()

    print("🐕 Psi:")
    for p in Pes.vse():
        print(f"  {p}")

    print("\n🚗 Auta:")
    for a in Auto.vse():
        print(f"  {a}")

    try:
        Pes(jmeno="X" * 30, vek=5)
    except ValueError as e:
        print(f"\n❌ Validace: {e}")

    try:
        Pes(jmeno="A", vek=-1)
    except ValueError as e:
        print(f"❌ Validace: {e}")

    try:
        Pes(jmeno=123, vek=5)
    except TypeError as e:
        print(f"❌ Validace: {e}")


if __name__ == "__main__":
    main()
```
