# Lekce 41: `dataclasses`

## 🎁 Co je dataclass?

**Dataclass** je třída zaměřená **hlavně na držení dat**. Místo psaní celého boilerplatu (`__init__`, `__repr__`, `__eq__`, ...) ti je **Python vygeneruje**.

### Bez dataclass — bolavě

```python
class Pes:
    def __init__(self, jmeno: str, vek: int):
        self.jmeno = jmeno
        self.vek = vek

    def __repr__(self):
        return f"Pes(jmeno={self.jmeno!r}, vek={self.vek})"

    def __eq__(self, other):
        if not isinstance(other, Pes):
            return NotImplemented
        return (self.jmeno, self.vek) == (other.jmeno, other.vek)
```

### S dataclass — krása

```python
from dataclasses import dataclass

@dataclass
class Pes:
    jmeno: str
    vek: int


rex = Pes("Rex", 5)
print(rex)                    # Pes(jmeno='Rex', vek=5)
rex == Pes("Rex", 5)          # True
```

Ušetříš 10+ řádků! Anotace typů jsou **povinné** — bez nich dataclass nepozná atribut.

---

## ⚙️ Možnosti `@dataclass`

```python
@dataclass(
    init=True,         # generovat __init__? (default True)
    repr=True,         # __repr__?
    eq=True,           # __eq__?
    order=False,       # __lt__, __le__, ...? (často chceš True)
    frozen=False,      # neměnné? (jako tuple)
    slots=False,       # __slots__? (Python 3.10+)
    kw_only=False,     # všechny argumenty jen jako keyword? (3.10+)
)
class X: ...
```

### `frozen=True` — neměnný (immutable)

```python
@dataclass(frozen=True)
class Bod:
    x: int
    y: int

p = Bod(1, 2)
p.x = 99    # ❌ FrozenInstanceError
hash(p)     # funguje (dá se použít v setu/dict)
```

### `slots=True` — efektivní

```python
@dataclass(slots=True)
class Pes:
    jmeno: str
    vek: int
# Generuje __slots__ → úspora paměti
```

### `order=True` — porovnatelné

```python
@dataclass(order=True)
class Verze:
    major: int
    minor: int

Verze(1, 5) < Verze(2, 0)    # True
```

---

## 🎚️ `field()` — pokročilá kontrola

```python
from dataclasses import dataclass, field

@dataclass
class Inventar:
    nazev: str
    polozky: list[str] = field(default_factory=list)   # ❗ NE list=[]!
    sklad: dict = field(default_factory=dict)
    id: int = field(default=0, repr=False)             # neukazovat v repr
    interne: str = field(default="", compare=False)    # neporovnávat
```

⚠️ **Mutable default jen přes `default_factory`!** (Stejná past jako u funkcí.)

---

## 🪄 `__post_init__` — co po inicializaci

```python
@dataclass
class Osoba:
    jmeno: str
    prijmeni: str
    cele_jmeno: str = field(init=False)

    def __post_init__(self):
        self.cele_jmeno = f"{self.jmeno} {self.prijmeni}"

o = Osoba("Eliška", "Nováková")
print(o.cele_jmeno)    # "Eliška Nováková"
```

---

## 📊 Konverze

```python
from dataclasses import asdict, astuple

@dataclass
class Pes:
    jmeno: str
    vek: int

rex = Pes("Rex", 5)
asdict(rex)    # {'jmeno': 'Rex', 'vek': 5}
astuple(rex)   # ('Rex', 5)
```

---

## 🆚 Dataclass vs NamedTuple vs dict vs Pydantic

| | dict | NamedTuple | dataclass | Pydantic BaseModel |
|---|---|---|---|---|
| Syntax | `{}` | jednoduchá | hezká | hezká |
| Typové anotace | ne | ano | ano | ano |
| Validace dat | ne | ne | ne | **ano** |
| Mutable | ano | ne | volitelné | ano |
| Rychlost | nejvíc | rychlé | rychlé | pomalejší |
| Konverze (JSON) | ano | ne | ručně | **automaticky** |

**Doporučení:**
- Vnitřní data, malé typy → `@dataclass`
- API/JSON, validace → `pydantic`
- Heterogeny → `dict`

---

## 🎯 Praktický příklad

```python
@dataclass(frozen=True, slots=True)
class Adresa:
    ulice: str
    mesto: str
    psc: str

@dataclass
class Uzivatel:
    jmeno: str
    email: str
    adresy: list[Adresa] = field(default_factory=list)
    aktivni: bool = True

u = Uzivatel("Eliška", "el@example.com")
u.adresy.append(Adresa("Hlavní 1", "Praha", "11000"))
print(u)
```

---

## ✏️ Cvičení

1. **Pes:** Předělej `Pes` z lekce 31 na dataclass.
2. **Frozen:** Vyrob `Bod(x, y)` jako `frozen=True` a strč do setu.
3. **Order:** `Studium(prumer, jmeno)` s `order=True`. Seřaď seznam studií podle průměru.
4. **Default factory:** `Tym` s `clenove: list[str]` přes `default_factory`.
5. **Post init:** `Obdelnik(a, b)` s automaticky spočítanou `obsah` v `__post_init__`.
