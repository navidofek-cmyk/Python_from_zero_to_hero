# Lekce 103: Hexagonal / Ports & Adapters / Clean Architecture

## Co je Clean Architecture?

Clean Architecture (Robert C. Martin), Hexagonal Architecture (Alistair Cockburn) a Ports & Adapters jsou různé názvy pro stejnou myšlenku:

> **Doménová logika nesmí záviset na I/O, frameworku ani databázi.**

Závislosti vždy směřují **dovnitř** — jádro (doména) nic neví o světě kolem sebe.

```
┌─────────────────────────────────────────┐
│  Infrastructure (DB, HTTP, CLI, e-mail) │
│  ┌───────────────────────────────────┐  │
│  │  Application (use cases / služby) │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │   Domain (entity, hodnoty)  │  │  │
│  │  └─────────────────────────────┘  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## Vrstvy a jejich odpovědnosti

| Vrstva | Co obsahuje | Závisí na |
|--------|-------------|-----------|
| **Domain** | Entity, Value Objects, doménová logika | nic externího |
| **Application** | Use cases, služby, porty (Protocol) | Domain |
| **Infrastructure** | Repozitáře, HTTP adaptéry, DB | Application + Domain |

---

## Ports & Adapters v Pythonu — Protocol

**Port** = rozhraní (co systém potřebuje).
**Adapter** = konkrétní implementace portu.

```python
from typing import Protocol

# PORT — definováno ve vrstvě Application
class UzivatelRepository(Protocol):
    def najdi_podle_id(self, id: int) -> "Uzivatel | None": ...
    def uloz(self, uzivatel: "Uzivatel") -> None: ...
    def seznam(self) -> list["Uzivatel"]: ...
```

```python
# ADAPTER — InMemory pro testy (vrstva Infrastructure)
class InMemoryUzivatelRepository:
    def __init__(self) -> None:
        self._store: dict[int, Uzivatel] = {}

    def najdi_podle_id(self, id: int) -> "Uzivatel | None":
        return self._store.get(id)

    def uloz(self, uzivatel: "Uzivatel") -> None:
        self._store[uzivatel.id] = uzivatel

    def seznam(self) -> list["Uzivatel"]:
        return list(self._store.values())
```

---

## Doménová entita

Entity mají identitu (id), Value Objects jsou neměnné a porovnávají se hodnotou.

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Uzivatel:
    id: int
    jmeno: str
    email: str
    vytvoreno: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not self.email or "@" not in self.email:
            raise ValueError(f"Neplatný e-mail: {self.email!r}")
        if not self.jmeno.strip():
            raise ValueError("Jméno nesmí být prázdné")
```

---

## Application service (Use Case)

Use case popisuje jednu akci uživatele systému. Závisí pouze na portech (Protocol), nikdy na konkrétních adapterech.

```python
from dataclasses import dataclass

@dataclass
class RegistraceVstupu:
    jmeno: str
    email: str

@dataclass
class RegistraceVystupu:
    id: int
    jmeno: str
    email: str

class RegistraceUzivateleUseCase:
    def __init__(self, repo: UzivatelRepository) -> None:
        self._repo = repo
        self._next_id = 1

    def execute(self, vstup: RegistraceVstupu) -> RegistraceVystupu:
        # kontrola duplicity
        existujici = [u for u in self._repo.seznam()
                      if u.email == vstup.email]
        if existujici:
            raise ValueError(f"E-mail {vstup.email!r} je již registrován")

        uzivatel = Uzivatel(
            id=self._next_id,
            jmeno=vstup.jmeno,
            email=vstup.email,
        )
        self._repo.uloz(uzivatel)
        self._next_id += 1

        return RegistraceVystupu(
            id=uzivatel.id,
            jmeno=uzivatel.jmeno,
            email=uzivatel.email,
        )
```

---

## Ukázka celého toku

```python
# Infrastructure: konkrétní repo (zde in-memory)
repo = InMemoryUzivatelRepository()

# Application: use case dostane repo přes DI
uc = RegistraceUzivateleUseCase(repo)

# Primární port (CLI, HTTP, ...) volá use case
vystup = uc.execute(RegistraceVstupu("Anna", "anna@example.com"))
print(f"Registrován: {vystup.jmeno} (id={vystup.id})")

# Sekundární port (DB adapter) je zcela zaměnitelný
# — pro testy použijeme InMemory, v produkci SqlAlchemyRepo
```

---

## Výhody Clean Architecture

| Bez CA | S Clean Architecture |
|--------|---------------------|
| Testy vyžadují DB / HTTP | Testy jsou čisté (in-memory) |
| Framework přibito | Framework se dá vyměnit |
| Doménová logika smíchaná s SQL | Doménová logika v čisté Pythonu |
| Těžká čitelnost toku | Každý use case = jeden soubor |

---

## Typická struktura projektu

```
src/
  domain/
    uzivatel.py          # entity, value objects
  application/
    ports.py             # Protocol rozhraní
    registrace_uc.py     # use case
  infrastructure/
    inmemory_repo.py     # testovací adapter
    sqlalchemy_repo.py   # produkční adapter
  entrypoints/
    cli.py               # CLI primární adapter
    api.py               # FastAPI primární adapter
```

---

## Shrnutí

- Doménová logika **nikdy** neimportuje DB, HTTP ani framework
- **Port** = Protocol (rozhraní), **Adapter** = konkrétní implementace
- Závislosti tečou dovnitř — Domain neví o Application, Application neví o Infrastructure
- Dependency Injection: use case dostane repo v konstruktoru
- Výsledkem jsou čisté, rychlé testy bez externích závislostí

---

## Cvičení

1. Přidej metodu `zmen_email(novy_email: str)` do entity `Uzivatel` s validací.
2. Vytvoř use case `NajdiUzivateleUseCase` který vrátí uživatele podle id nebo vyhodí `KeyError`.
3. Implementuj `SqliteUzivatelRepository` jako produkční adapter (použij `sqlite3` ze stdlib).
4. Napiš test, který ověří, že duplikátní e-mail vyhodí `ValueError` — bez jakékoliv databáze.
