# Program — Lekce 159: Lekce 159: Pokročilý type system

Patří k lekci [Lekce 159: Pokročilý type system](../159_advanced_types.md).

## Jak spustit

```bash
python3 programy/l159_advanced_types.py
```

## Zdrojový kód

### `l159_advanced_types.py`

```py
"""Lekce 159 — Pokročilý type system: TypeVar, Literal, Protocol, Annotated.

Spuštění:
    uv run l159_advanced_types.py
"""

from typing import TypeVar, Generic, Literal, TypeGuard, Annotated, Callable, overload
from typing import Protocol, runtime_checkable, ParamSpec
from pydantic import BaseModel, Field
import functools


T = TypeVar("T")
S = TypeVar("S")
P = ParamSpec("P")
R = TypeVar("R")


# TypeVar + Generic
class Zasobnik(Generic[T]):
    def __init__(self): self._data: list[T] = []
    def push(self, item: T) -> None: self._data.append(item)
    def pop(self) -> T: return self._data.pop()
    def __len__(self): return len(self._data)
    def __repr__(self): return f"Zasobnik({self._data})"


# Literal
Smer = Literal["north", "south", "east", "west"]
HttpStatus = Literal[200, 201, 400, 404, 500]

def pohyb(smer: Smer) -> str:
    return f"Jdu na {smer}"

def status_zprava(s: HttpStatus) -> str:
    zpravy = {200: "OK", 201: "Created", 400: "Bad Request", 404: "Not Found", 500: "Server Error"}
    return zpravy.get(s, "Unknown")


# TypeGuard
def je_str_seznam(val: list) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)

def zpracuj(data: list) -> str:
    if je_str_seznam(data):
        return ", ".join(data)
    return str(sum(x for x in data if isinstance(x, int)))


# Protocol
@runtime_checkable
class Comparable(Protocol):
    def __lt__(self, other) -> bool: ...

def seradˇ(items: list[Comparable]) -> list[Comparable]:
    return sorted(items)


# Annotated + Pydantic
class Produkt(BaseModel):
    nazev: Annotated[str, Field(min_length=1, max_length=100)]
    cena: Annotated[float, Field(gt=0)]
    mnozstvi: Annotated[int, Field(ge=0)]
    kategorie: Literal["elektronika", "nabytek", "obleceni"]


# ParamSpec — typování dekorátorů
def loguj(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"  → {func.__name__}({args}, {kwargs})")
        result = func(*args, **kwargs)
        print(f"  ← {result}")
        return result
    return wrapper


# Overload
@overload
def prevod(x: int) -> str: ...
@overload
def prevod(x: str) -> int: ...
def prevod(x):
    if isinstance(x, int): return str(x)
    return len(x)


def main():
    print("=" * 50)
    print("  🔧 Pokročilý type system Demo")
    print("=" * 50)

    print("\n=== Generic Zasobnik ===")
    z: Zasobnik[int] = Zasobnik()
    for i in [3, 1, 4]: z.push(i)
    print(f"  Zasobnik: {z}")
    print(f"  Pop: {z.pop()}")

    print("\n=== Literal types ===")
    print(f"  pohyb('north') = {pohyb('north')}")
    print(f"  status_zprava(404) = {status_zprava(404)}")

    print("\n=== TypeGuard ===")
    print(f"  zpracuj(['a','b','c']) = {zpracuj(['a','b','c'])}")
    print(f"  zpracuj([1,2,3]) = {zpracuj([1,2,3])}")

    print("\n=== Protocol + Comparable ===")
    class Teplota:
        def __init__(self, v): self.v = v
        def __lt__(self, o): return self.v < o.v
        def __repr__(self): return f"{self.v}°C"
    teploty = [Teplota(25), Teplota(18), Teplota(30)]
    print(f"  Seřazeno: {seradˇ(teploty)}")
    print(f"  isinstance check: {isinstance(teploty[0], Comparable)}")

    print("\n=== Pydantic Annotated ===")
    p = Produkt(nazev="Laptop", cena=25000, mnozstvi=5, kategorie="elektronika")
    print(f"  {p}")
    try:
        Produkt(nazev="", cena=-1, mnozstvi=5, kategorie="elektronika")
    except Exception as e:
        print(f"  Validace zachytila: {type(e).__name__}")

    print("\n=== ParamSpec dekorátor ===")
    @loguj
    def secti(a: int, b: int) -> int: return a + b
    secti(3, 4)

    print("\n=== Overload ===")
    a: str = prevod(42)
    b: int = prevod("hello")
    print(f"  prevod(42) = {a!r} (str)")
    print(f"  prevod('hello') = {b} (int)")

    print("\n✅ Demo dokončeno!")
    print("Tip: spusť mypy --strict l159_advanced_types.py")


if __name__ == "__main__":
    main()

```
