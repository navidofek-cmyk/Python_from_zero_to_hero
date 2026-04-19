# Lekce 50: Protokoly a `typing.Protocol` (strukturální typování)

## 🦆 Duck typing s typovou kontrolou

Python tradičně dělá **duck typing**: „Když to chodí jako kachna a kváká jako kachna, je to kachna.“ Jenže typový checker (mypy) vidí jen jména typů.

**Protocol** spojuje obojí: **strukturální typování s typovou kontrolou**.

---

## 🔥 Příklad

```python
from typing import Protocol

class MaJmeno(Protocol):
    jmeno: str

    def predstav_se(self) -> str: ...


class Pes:                      # nedědí od MaJmeno!
    def __init__(self, jmeno):
        self.jmeno = jmeno
    def predstav_se(self) -> str:
        return f"Pes {self.jmeno}"

class Robot:
    def __init__(self, jmeno):
        self.jmeno = jmeno
    def predstav_se(self) -> str:
        return f"R2-{self.jmeno}"


def pozdrav(x: MaJmeno) -> None:
    print(x.predstav_se())


pozdrav(Pes("Rex"))      # ✅ funguje (Pes "vypadá" jako MaJmeno)
pozdrav(Robot("D2"))     # ✅ funguje
```

`Pes` ani `Robot` nedědí od `MaJmeno` — stačí, že **mají správné metody/atributy**. mypy to ověří.

---

## 🆚 Protocol vs ABC

| | ABC | Protocol |
|---|---|---|
| Dědičnost | Nutná | Není potřeba |
| Kontrola | Při vytvoření instance | Při typové kontrole (mypy) |
| Runtime check | Ano | Volitelně přes `@runtime_checkable` |
| Pythoničnost | Klasické OOP | Modernější, volnější |

---

## 🏃 `@runtime_checkable`

Standardně Protocol funguje jen pro mypy. Když chceš `isinstance` za běhu:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class MaJmeno(Protocol):
    def predstav_se(self) -> str: ...


isinstance(Pes("R"), MaJmeno)    # True (kontroluje JEN existence metody!)
```

⚠️ Runtime check **nekontroluje signatury** — jen jestli metoda existuje.

---

## 📚 Protokoly ze stdlib

`collections.abc` má fakticky protokoly (i když implementačně jsou ABC):

```python
from collections.abc import Iterable, Sized, Hashable

def soucet(x: Iterable[int]) -> int:
    return sum(x)

# Funguje na list, tuple, set, generator, ...
```

Anotuj **schopnostmi**, ne konkrétními typy:
- `Iterable[T]` místo `list[T]`
- `Mapping[K, V]` místo `dict[K, V]`
- `Sequence[T]` (indexovatelné, len) místo `list[T]`

---

## 🎯 Praktický příklad

```python
from typing import Protocol

class JsonSerializable(Protocol):
    def to_json(self) -> str: ...


def uloz(obj: JsonSerializable, soubor: str) -> None:
    with open(soubor, "w") as f:
        f.write(obj.to_json())


# Cokoli s metodou to_json projde — žádná dědičnost.
```

---

## ✏️ Cvičení

1. **Plav protokol:** Protocol `Plovak` s metodou `plav() -> None`. Implementuj `Ryba` a `Lod` (bez dědičnosti).
2. **Comparable:** Protocol s `__lt__`. Funkce `min_z(seznam: list[Comparable]) -> Comparable`.
3. **Sized:** Funkce `vypis_velikost(co: Sized)` co vypíše `len(co)`. Otestuj na list, str, dict.
4. **Runtime checkable:** Vyrob Protocol se `@runtime_checkable` a otestuj `isinstance`.
