# Lekce 30: Anotace typů u funkcí (pokročile)

## 📝 Základ — opakování

```python
def secti(a: int, b: int) -> int:
    return a + b
```

- `a: int`, `b: int` — parametry
- `-> int` — návratový typ

---

## 📚 Komplexní typy

```python
def soucet_seznamu(cisla: list[int]) -> int:
    return sum(cisla)

def vrat_par() -> tuple[str, int]:
    return ("Eliška", 10)

def hledej(klic: str, slovnik: dict[str, int]) -> int | None:
    return slovnik.get(klic)
```

Od Pythonu 3.9 můžeš psát `list[int]`, `dict[str, int]` přímo. Ve starších verzích `from typing import List, Dict`.

---

## 🤝 `Callable` — typ pro funkci

Když očekáváš **funkci jako argument**:

```python
from typing import Callable

def aplikuj(f: Callable[[int, int], int], x: int, y: int) -> int:
    return f(x, y)

aplikuj(lambda a, b: a + b, 3, 5)    # 8
```

`Callable[[arg_typy], navrat]`:
- `Callable[[int, int], int]` = bere 2 inty, vrací int
- `Callable[..., str]` = bere cokoliv, vrací str
- `Callable[[], None]` = bere nic, vrací nic

---

## 🌐 Generika — `TypeVar`

Když chceš funkci, co funguje pro **jakýkoliv typ**, ale **konzistentně**:

```python
from typing import TypeVar

T = TypeVar("T")

def prvni(seznam: list[T]) -> T:
    return seznam[0]

prvni([1, 2, 3])           # vrátí int
prvni(["a", "b", "c"])     # vrátí str
```

Nový (3.12+) syntax:
```python
def prvni[T](seznam: list[T]) -> T:
    return seznam[0]
```

---

## 🎩 `ParamSpec` a `Concatenate` — pro dekorátory

Když chceš dekorátor, co **zachová signaturu** funkce:

```python
from typing import ParamSpec, TypeVar
from functools import wraps

P = ParamSpec("P")
R = TypeVar("R")

def loguj[**P, R](funkce: Callable[P, R]) -> Callable[P, R]:
    @wraps(funkce)
    def obalka(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Volám {funkce.__name__}")
        return funkce(*args, **kwargs)
    return obalka
```

Tohle je už pokročilé — pro běžnou práci to nepotřebuješ.

---

## ❓ `Optional` a `Union`

```python
from typing import Optional, Union

# Staré (před 3.10)
def hledej(klic: str) -> Optional[int]: ...    # int nebo None
def parse(x: Union[str, int]) -> int: ...      # str nebo int

# Nové (3.10+)
def hledej(klic: str) -> int | None: ...
def parse(x: str | int) -> int: ...
```

---

## 🏷️ Aliasy typu

```python
type Body = int                          # 3.12+
type Mapa[K, V] = dict[K, list[V]]

# Starší:
Body = int
SkoreLista = list[tuple[str, int]]

def vyhodnot(skore: SkoreLista) -> Body: ...
```

---

## 🔍 Kontrola typů přes `mypy` / `pyright`

Anotace **Python ignoruje** za běhu! Musíš použít externí nástroj:

```bash
pip install mypy
mypy muj_program.py
```

Najde ti nesedící typy ještě před spuštěním.

```python
def secti(a: int, b: int) -> int:
    return a + b

secti("ahoj", 5)   # mypy: error: Argument 1 has incompatible type "str"
```

---

## 🎯 Doporučení

✅ **Anotuj** všechny veřejné funkce a metody.
✅ **Používej** `mypy` nebo `pyright` v CI.
✅ **Začni postupně** — staré projekty není potřeba okamžitě anotovat všude.
✅ Pro **slovníky se známou strukturou** použij `TypedDict` nebo `dataclass`.

---

## ✏️ Cvičení

1. **Anotuj** všechny funkce z lekcí 21–29.
2. **Callable:** Napiš funkci `udelej_dvakrat(f: Callable[[int], int], x: int) -> int`, která vrátí `f(f(x))`.
3. **Generika:** Napiš `posledni[T](seznam: list[T]) -> T`.
4. **Mypy:** Nainstaluj `mypy` a pusť ho na svůj kód. Co to najde?
5. **Optional:** Funkce `najdi(jmeno: str, seznam: list[str]) -> int | None` co vrátí index nebo None.
