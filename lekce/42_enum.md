# Lekce 42: `Enum`, `IntEnum`, `StrEnum`, `Flag`

## 🎨 Co je Enum?

**Enum** = výčet **pojmenovaných hodnot**. Místo magických čísel/textů použiješ čitelná jména.

### Bez Enum — bolavě

```python
status = "pending"     # mohlo by být cokoliv — překlep tě nezachrání

if status == "pendingg":   # 🐛 nikdy se nespustí, ale Python neřekne
    ...
```

### S Enum — bezpečně

```python
from enum import Enum

class Status(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"

status = Status.PENDING
print(status)              # Status.PENDING
print(status.name)         # 'PENDING'
print(status.value)        # 'pending'

if status == Status.PENDING:
    ...

# Status.PENDIINGG  ❌ AttributeError při importu!
```

---

## 🔢 `IntEnum` — chová se jako int

```python
from enum import IntEnum

class Den(IntEnum):
    PONDELI = 1
    UTERY = 2
    STREDA = 3

den = Den.UTERY
den + 1                    # 3 (jako int!)
isinstance(den, int)       # True
```

Užitečné pro flagy nebo když potřebuješ kompatibilitu s knihovnou očekávající int.

---

## 📝 `StrEnum` (Python 3.11+)

```python
from enum import StrEnum

class Barva(StrEnum):
    CERVENA = "red"
    MODRA = "blue"

b = Barva.CERVENA
b.startswith("r")        # True (jako str!)
print(f"<span style='color:{b}'>")    # použije .value
```

---

## 🎌 `Flag` — bitové kombinace

Pro **kombinovatelné** vlastnosti (více najednou).

```python
from enum import Flag, auto

class Pristup(Flag):
    CIST = auto()      # 1
    PSAT = auto()      # 2
    MAZAT = auto()     # 4

# Kombinace operátory:
admin = Pristup.CIST | Pristup.PSAT | Pristup.MAZAT
host = Pristup.CIST

print(admin)                      # Pristup.CIST|PSAT|MAZAT
Pristup.PSAT in admin             # True
host & Pristup.MAZAT              # Pristup(0)  (nemá)
```

`auto()` automaticky přiřadí 1, 2, 4, 8... (mocniny dvou — pro bitové operace).

`IntFlag` umí to samé + chová se jako int.

---

## 🛠️ Metody na enum

```python
from enum import Enum

class Status(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"

# Iterace
for s in Status:
    print(s.name, s.value)

# Vyhledání podle hodnoty
Status("active")          # Status.ACTIVE

# Vyhledání podle jména
Status["ACTIVE"]          # Status.ACTIVE

# Všechny hodnoty
list(Status)              # [Status.PENDING, Status.ACTIVE, Status.DONE]
```

---

## 🎯 Vlastní metody

Enum může mít metody jako jakákoliv třída:

```python
class Den(Enum):
    PO = 1
    UT = 2
    ST = 3
    CT = 4
    PA = 5
    SO = 6
    NE = 7

    def je_vikend(self) -> bool:
        return self in {Den.SO, Den.NE}

    def cesky(self) -> str:
        nazvy = {Den.PO: "Pondělí", Den.UT: "Úterý", ...}
        return nazvy[self]


Den.SO.je_vikend()     # True
```

---

## 🎨 Praktický příklad

```python
class Priorita(IntEnum):
    NIZKA = 1
    NORMALNI = 2
    VYSOKA = 3
    KRITICKA = 4


class Stav(StrEnum):
    OTEVREN = "open"
    UZAVREN = "closed"


@dataclass
class Ticket:
    text: str
    priorita: Priorita = Priorita.NORMALNI
    stav: Stav = Stav.OTEVREN
```

---

## ⚠️ Pasti

1. **Hodnoty musí být unikátní** (jinak se duplikáty stanou aliasy).
2. **`Enum.NEEXISTUJE`** vyhodí `AttributeError` (dobře!).
3. **`Enum("X", ["A", "B"])`** funguje (funkční API).

---

## ✏️ Cvičení

1. **Status:** Enum `Status` s PENDING/ACTIVE/DONE. Vypiš všechny.
2. **Den:** `IntEnum` `Den` (1=PO až 7=NE) s metodou `je_vikend()`.
3. **Flag:** `Pristup` s CIST/PSAT/MAZAT. Vyrob admin (vše) a host (jen čtení).
4. **StrEnum:** `Barva` s `RED`, `GREEN`, `BLUE`. Použij ji v f-stringu.
5. **Z hodnoty:** Funkce co vezme text "active" a vrátí `Status.ACTIVE` (přes `Status(text)`).
