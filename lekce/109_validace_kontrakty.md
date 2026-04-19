# Lekce 109: Validace a kontrakty — Pydantic v2

## Co je Pydantic?

Pydantic je knihovna pro validaci dat pomocí Python type hints. Verze 2 (2023+) je přepsaná v Rustu — výrazně rychlejší.

```bash
pip install pydantic
```

---

## Základní BaseModel

```python
from pydantic import BaseModel, Field
from datetime import datetime

class Uzivatel(BaseModel):
    id: int
    jmeno: str
    email: str
    vytvoreno: datetime = Field(default_factory=datetime.now)
```

```python
# Vytvoření z dict
u = Uzivatel(id=1, jmeno="Anna", email="anna@example.com")
print(u.model_dump())          # → {'id': 1, 'jmeno': 'Anna', ...}
print(u.model_dump_json())     # → JSON string
```

---

## Field — omezení hodnot

```python
from pydantic import BaseModel, Field

class Produkt(BaseModel):
    id: int
    nazev: str = Field(min_length=2, max_length=200)
    cena: float = Field(gt=0, description="Cena v Kč bez DPH")
    sleva: float = Field(default=0.0, ge=0.0, le=100.0)
    ean: str = Field(pattern=r"^\d{13}$")

# Při chybě: pydantic.ValidationError s detailním popisem
```

Parametry `Field`:
- `gt`, `ge`, `lt`, `le` — větší/menší než
- `min_length`, `max_length` — délka stringu/listu
- `pattern` — regex
- `default`, `default_factory`
- `description` — pro JSON Schema / OpenAPI

---

## field_validator

```python
from pydantic import BaseModel, field_validator

class Registrace(BaseModel):
    jmeno: str
    email: str
    heslo: str

    @field_validator("email")
    @classmethod
    def email_musi_byt_firemni(cls, v: str) -> str:
        if not v.endswith("@firma.cz"):
            raise ValueError("Povoleny jsou pouze e-maily @firma.cz")
        return v.lower()   # normalizace

    @field_validator("heslo")
    @classmethod
    def heslo_dostatecne_silne(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Heslo musí mít alespoň 8 znaků")
        if not any(c.isdigit() for c in v):
            raise ValueError("Heslo musí obsahovat číslici")
        return v
```

---

## model_validator — křížová validace

```python
from pydantic import BaseModel, model_validator
from datetime import date

class Rezervace(BaseModel):
    od: date
    do: date
    pocet_hostu: int = Field(ge=1, le=10)
    dite: bool = False

    @model_validator(mode="after")
    def datum_od_musi_byt_drive(self) -> "Rezervace":
        if self.do <= self.od:
            raise ValueError("Datum odjezdu musí být po datu příjezdu")
        return self

    @model_validator(mode="after")
    def dite_potrebuje_dospeleho(self) -> "Rezervace":
        if self.dite and self.pocet_hostu < 2:
            raise ValueError("Dítě musí mít doprovod — počet hostů ≥ 2")
        return self
```

---

## Nested modely a List/Optional

```python
from pydantic import BaseModel
from typing import Annotated

class Adresa(BaseModel):
    ulice: str
    mesto: str
    psc: str

class Zakaznik(BaseModel):
    id: int
    jmeno: str
    adresa: Adresa | None = None
    tagy: list[str] = []

# Validace vnořených modelů funguje automaticky
z = Zakaznik(
    id=1,
    jmeno="Anna",
    adresa={"ulice": "Náměstí 1", "mesto": "Praha", "psc": "12000"},
)
print(z.adresa.mesto)   # → Praha
```

---

## JSON Schema generování

```python
import json

schema = Produkt.model_json_schema()
print(json.dumps(schema, ensure_ascii=False, indent=2))
# Výstup: plné JSON Schema včetně description, min/max, pattern...
```

JSON Schema se automaticky používá v FastAPI pro OpenAPI dokumentaci.

---

## Schema Evolution

```python
# V1 → V2: přidání nepovinného pole = zpětně kompatibilní
class UzivatelV1(BaseModel):
    id: int
    email: str

class UzivatelV2(BaseModel):
    id: int
    email: str
    telefon: str | None = None   # non-breaking: nepovinné

# Breaking change — vyžaduje novou API verzi:
class UzivatelV3(BaseModel):
    id: int
    email: str
    telefon: str | None = None
    prijmeni: str    # breaking: povinné nové pole
```

---

## model_config — nastavení chování

```python
from pydantic import BaseModel, ConfigDict

class OrmModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,    # ORM mode (SQLAlchemy objekty)
        populate_by_name=True,   # alias i jméno atributu
        str_strip_whitespace=True,   # automatické strip()
        frozen=True,             # neměnné (jako frozen dataclass)
    )
```

---

## Shrnutí

| Funkce | Popis |
|--------|-------|
| `BaseModel` | Základní validovatelný datový model |
| `Field(gt=0, ...)` | Omezení hodnoty, popis pro schema |
| `@field_validator` | Validace jednoho pole |
| `@model_validator` | Křížová validace přes více polí |
| `model_dump()` | Serializace na dict |
| `model_dump_json()` | Serializace na JSON string |
| `model_json_schema()` | Generování JSON Schema |
| `ConfigDict` | Nastavení chování modelu |

---

## Cvičení

1. Vytvoř model `Objednavka` s validací: `datum_doruceni` musí být v budoucnosti, `polozky` nesmí být prázdné.
2. Přidej `field_validator` pro `PSC` — musí mít formát `NNN NN` nebo `NNNNN`.
3. Vygeneruj JSON Schema pro model `Zakaznik` a vypiš ho jako hezký JSON.
4. Zkus načíst model z SQLAlchemy objektu pomocí `model_validate(db_row, from_attributes=True)`.
