# Lekce 101: SOLID v Pythonu

## 🎯 Co je SOLID?

SOLID je 5 principů pro psaní udržitelného OOP kódu. Python je dynamický jazyk — některé principy se uplatňují jinak než v Javě, ale myšlenky platí vždy.

---

## S — Single Responsibility Principle (SRP)

> Třída/funkce má mít **jeden důvod ke změně**.

```python
# ❌ Špatně — třída dělá příliš mnoho
class Objednavka:
    def pridej_polozku(self, polozka): ...
    def vypocti_cenu(self): ...
    def uloz_do_db(self): ...       # I/O závisí na DB
    def posli_email(self): ...      # závisí na SMTP

# ✅ Správně — každá třída má jednu odpovědnost
class Objednavka:
    def pridej_polozku(self, polozka): ...
    def vypocti_cenu(self): ...

class ObjednavkaRepo:
    def uloz(self, obj: Objednavka): ...

class EmailNotifikace:
    def posli_potvrzeni(self, obj: Objednavka): ...
```

---

## O — Open/Closed Principle (OCP)

> Kód má být **otevřený pro rozšíření, uzavřený pro modifikaci**.

```python
# ❌ Špatně — každý nový typ vyžaduje změnu funkce
def vypocti_slevu(typ_zakaznika: str, cena: float) -> float:
    if typ_zakaznika == "vip":
        return cena * 0.8
    elif typ_zakaznika == "student":
        return cena * 0.9
    return cena

# ✅ Správně — nový typ = nová třída, funkce se nemění
from abc import ABC, abstractmethod

class Sleva(ABC):
    @abstractmethod
    def aplikuj(self, cena: float) -> float: ...

class VipSleva(Sleva):
    def aplikuj(self, cena: float) -> float:
        return cena * 0.8

class StudentSleva(Sleva):
    def aplikuj(self, cena: float) -> float:
        return cena * 0.9

def vypocti_cenu(cena: float, sleva: Sleva) -> float:
    return sleva.aplikuj(cena)
```

**Pythonic alternativa** — funkce jako strategie:

```python
from typing import Callable

SlevaFn = Callable[[float], float]

vip_sleva: SlevaFn = lambda cena: cena * 0.8
student_sleva: SlevaFn = lambda cena: cena * 0.9

def vypocti_cenu(cena: float, sleva: SlevaFn) -> float:
    return sleva(cena)
```

---

## L — Liskov Substitution Principle (LSP)

> Podtřídu lze **vždy nahradit** nadtřídou bez změny chování programu.

```python
# ❌ Porušení LSP — čtverec je geometricky čtverec, ale ne jako podtřída obdélníku
class Obdelnik:
    def __init__(self, w: float, h: float):
        self.w, self.h = w, h

    def obsah(self) -> float:
        return self.w * self.h

class Ctverec(Obdelnik):
    def __init__(self, strana: float):
        super().__init__(strana, strana)

    @property  # type: ignore
    def w(self): return self._w

    @w.setter
    def w(self, v):           # nastavení w změní i h — překvapení!
        self._w = self._h = v

# ✅ Správně — samostatné třídy se společným protokolem
from typing import Protocol

class Tvar(Protocol):
    def obsah(self) -> float: ...

class Obdelnik:
    def __init__(self, w: float, h: float):
        self.w, self.h = w, h
    def obsah(self) -> float:
        return self.w * self.h

class Ctverec:
    def __init__(self, strana: float):
        self.strana = strana
    def obsah(self) -> float:
        return self.strana ** 2
```

---

## I — Interface Segregation Principle (ISP)

> Klient nemá být nucen záviset na metodách, které **nepoužívá**.

```python
# ❌ Tlustý protokol — ne každá třída umí vše
class Pracovnik(Protocol):
    def pracuj(self) -> None: ...
    def jez(self) -> None: ...
    def spi(self) -> None: ...

class Robot:
    def pracuj(self) -> None: print("pracuji")
    def jez(self) -> None: raise NotImplementedError   # robot nejí!
    def spi(self) -> None: raise NotImplementedError

# ✅ Tenké protokoly — každý implementuje jen co umí
class Pracujici(Protocol):
    def pracuj(self) -> None: ...

class Zivi(Protocol):
    def jez(self) -> None: ...
    def spi(self) -> None: ...

class Robot:
    def pracuj(self) -> None: print("pracuji")

class Clovek:
    def pracuj(self) -> None: print("pracuji")
    def jez(self) -> None: print("jím")
    def spi(self) -> None: print("spím")
```

---

## D — Dependency Inversion Principle (DIP)

> Závislost na **abstrakcích**, ne na konkrétních implementacích.

```python
# ❌ Špatně — vysokoúrovňový modul závisí na konkrétní DB
class UzivatelService:
    def __init__(self):
        self.db = MySQLDatabase()   # přibito natvrdo

    def najdi(self, id: int):
        return self.db.query(f"SELECT * FROM users WHERE id={id}")

# ✅ Správně — závisíme na rozhraní, konkrétní impl. se injectuje
from typing import Protocol

class UzivatelRepo(Protocol):
    def najdi(self, id: int) -> dict: ...

class UzivatelService:
    def __init__(self, repo: UzivatelRepo):
        self.repo = repo            # dependency injection

    def najdi(self, id: int) -> dict:
        return self.repo.najdi(id)

# V testech: FakeRepo(); v produkci: MySQLRepo()
class FakeRepo:
    def najdi(self, id: int) -> dict:
        return {"id": id, "jmeno": "Test"}

service = UzivatelService(FakeRepo())
```

---

## 🐍 SOLID a Python — kdy "pythonic" vyhrává

| Princip | Java přístup | Pythonic přístup |
|---------|-------------|-----------------|
| OCP | abstraktní třída | funkce / Protocol |
| LSP | dědičnost | duck typing |
| ISP | rozhraní | Protocol (strukturální) |
| DIP | IoC container | prostý parametr / closure |

Python preferuje **Protocol** (strukturální typování) před `ABC` — nemusíš explicitně dědit, stačí implementovat správné metody.

---

## 📝 Shrnutí

- **S** — jedna odpovědnost, jeden důvod ke změně
- **O** — rozšiřuj přidáváním, ne upravováním
- **L** — podtřída nesmí překvapit
- **I** — malé protokoly > jeden velký
- **D** — záviset na abstrakci, injektovat konkrétní impl.

---

## 🏋️ Cvičení

1. Refaktoruj `Objednavka` z příkladu SRP — přidej metodu `to_dict()` a rozhodni, kam patří.
2. Přidej nový typ slevy `SeniorSleva(20 %)` bez změny funkce `vypocti_cenu`.
3. Napiš `DatabaseRepo` a `InMemoryRepo` implementující stejný `Protocol` a použij je v `UzivatelService`.
