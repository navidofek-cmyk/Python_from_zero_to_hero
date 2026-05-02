# Lekce 159: Pokročilý type system

Python's type system je mocnější než se zdá. Správné typování zachytí chyby při vývoji, ne v produkci.

---

## 🔧 TypeVar a Generic

```python
from typing import TypeVar, Generic, Callable, Iterable

T = TypeVar("T")
S = TypeVar("S")

def prvni(sekvence: list[T]) -> T:
    return sekvence[0]

prvni([1, 2, 3])        # int
prvni(["a", "b"])        # str
prvni([1, "mix"])        # int | str


class Zasobnik(Generic[T]):
    def __init__(self) -> None:
        self._data: list[T] = []

    def push(self, item: T) -> None:
        self._data.append(item)

    def pop(self) -> T:
        return self._data.pop()

    def __len__(self) -> int:
        return len(self._data)


z: Zasobnik[int] = Zasobnik()
z.push(1)
z.push(2)
print(z.pop())   # 2


# Bounded TypeVar — omezení na podtřídy
from numbers import Number
N = TypeVar("N", bound=Number)

def scitej(a: N, b: N) -> N:
    return a + b   # type: ignore

print(scitej(1, 2))       # int
print(scitej(1.5, 2.5))   # float
```

---

## 🏷️ Literal — přesné hodnoty

```python
from typing import Literal

Smer = Literal["north", "south", "east", "west"]
Status = Literal[200, 201, 400, 404, 500]

def pohyb(smer: Smer) -> str:
    return f"Jdu na {smer}"

pohyb("north")   # OK
# pohyb("up")    # mypy chyba!

def zpracuj_odpoved(status: Status) -> str:
    if status == 200: return "OK"
    if status == 404: return "Not Found"
    return "Chyba"
```

---

## 🛡️ TypeGuard — zúžení typů

```python
from typing import TypeGuard


def je_string_seznam(val: list) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)


def zpracuj(data: list[str | int]) -> None:
    if je_string_seznam(data):
        # mypy ví, že data je list[str]
        print(", ".join(data))
    else:
        print(sum(x for x in data if isinstance(x, int)))


# TypeGuard pro přesné narrowing
from typing import Union

def je_int(val: Union[int, str]) -> TypeGuard[int]:
    return isinstance(val, int)

x: int | str = 42
if je_int(x):
    print(x + 1)   # mypy ví, že x je int
```

---

## 📝 Annotated — metadata k typům

```python
from typing import Annotated
from dataclasses import dataclass


# Validační metadata
Kladne = Annotated[int, "musí být > 0"]
Email = Annotated[str, "musí být platný email"]
Procento = Annotated[float, "0.0 až 1.0"]


@dataclass
class Uzivatel:
    jmeno: str
    vek: Annotated[int, "18-150"]
    email: Email
    skore: Annotated[float, "0.0-1.0"]


# Pydantic Annotated validace (v praxi)
from pydantic import BaseModel, Field

class Produkt(BaseModel):
    nazev: Annotated[str, Field(min_length=1, max_length=100)]
    cena: Annotated[float, Field(gt=0, le=1_000_000)]
    mnozstvi: Annotated[int, Field(ge=0)]
    kategorie: Literal["elektronika", "nabytek", "obleceni"]


p = Produkt(nazev="Laptop", cena=25000, mnozstvi=5, kategorie="elektronika")
print(p)
```

---

## ⚙️ ParamSpec — typování dekorátorů

```python
from typing import ParamSpec, Callable, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def loguj(func: Callable[P, R]) -> Callable[P, R]:
    """Dekorátor, který zachovává signaturu funkce."""
    import functools

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Volám {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Hotovo {func.__name__}")
        return result
    return wrapper


@loguj
def secti(a: int, b: int) -> int:
    return a + b


# mypy ví, že secti(a: int, b: int) -> int
vysledek = secti(1, 2)
print(f"Výsledek: {vysledek}")
```

---

## 🔄 Protocol — strukturální subtyping

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Comparable(Protocol):
    def __lt__(self, other: "Comparable") -> bool: ...
    def __gt__(self, other: "Comparable") -> bool: ...


@runtime_checkable
class Renderable(Protocol):
    def render(self) -> str: ...


def seradˇ(items: list[Comparable]) -> list[Comparable]:
    return sorted(items)


class Teplota:
    def __init__(self, hodnota: float): self.hodnota = hodnota
    def __lt__(self, other: "Teplota") -> bool: return self.hodnota < other.hodnota
    def __gt__(self, other: "Teplota") -> bool: return self.hodnota > other.hodnota
    def __repr__(self): return f"{self.hodnota}°C"


teploty = [Teplota(25), Teplota(18), Teplota(30)]
print(seradˇ(teploty))
print(isinstance(teploty[0], Comparable))   # True (runtime_checkable)
```

---

## 🏗️ TypedDict — slovníky se schématem

```python
from typing import TypedDict, NotRequired, Required


class Adresa(TypedDict):
    ulice: str
    mesto: str
    psc: str


class Uzivatel2(TypedDict):
    id: int
    jmeno: str
    email: str
    adresa: NotRequired[Adresa]   # volitelné pole


def zpracuj_uzivatele(u: Uzivatel2) -> str:
    return f"{u['jmeno']} <{u['email']}>"


uzivatel: Uzivatel2 = {"id": 1, "jmeno": "Anna", "email": "anna@test.com"}
print(zpracuj_uzivatele(uzivatel))
```

---

## 🔁 Overload — přetížení funkcí

```python
from typing import overload


@overload
def zpracuj(x: int) -> str: ...
@overload
def zpracuj(x: str) -> int: ...
@overload
def zpracuj(x: list[int]) -> list[str]: ...

def zpracuj(x):
    if isinstance(x, int): return str(x)
    if isinstance(x, str): return len(x)
    return [str(i) for i in x]


a: str = zpracuj(42)       # mypy ví: str
b: int = zpracuj("hello")  # mypy ví: int
c: list[str] = zpracuj([1, 2, 3])
print(a, b, c)
```

---

## ✏️ Cvičení

1. Napíš generický `Result[T, E]` typ (jako v Rustu) — `Ok(T)` nebo `Err(E)`.
2. Implementuj `Paginator[T]` generickou třídu pro stránkování libovolných dat.
3. Použij `Annotated` + Pydantic pro validaci REST API requestu s vlastními validátory.
4. Napiš type-safe `EventEmitter[T]` kde T je TypedDict události.
5. Zkontroluj existující projekt pomocí `mypy --strict` — oprav všechny chyby.
