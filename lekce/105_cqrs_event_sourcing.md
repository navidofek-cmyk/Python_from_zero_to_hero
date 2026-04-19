# Lekce 105: CQRS a Event Sourcing

## CQRS — Command Query Responsibility Segregation

CQRS odděluje **zápis** (Command) od **čtení** (Query):

- **Command** — změní stav systému, vrací potvrzení nebo nic
- **Query** — čte stav, nemění ho, vrací data

```
┌──────────┐  Command   ┌───────────────┐  události   ┌──────────────┐
│  Klient  │ ─────────> │ Command Model │ ──────────> │  Event Store │
│          │            │  (zapisuje)   │             │              │
│          │  Query     ┌───────────────┐  projekce   │              │
│          │ <───────── │  Query Model  │ <────────── │              │
└──────────┘            │   (čte)       │             └──────────────┘
```

---

## Event Sourcing

Místo ukládání **aktuálního stavu** ukládáme **sled událostí**. Stav se vždy rekonstruuje přehráním událostí od začátku.

```
Tradiční způsob:   uložit { saldo: 500 }
Event Sourcing:    [VkladVlozen(300), VkladVlozen(400), VyberProveden(200)]
                   → přehraj → saldo = 500
```

Výhody:
- Úplná auditní stopa — víme **co** a **kdy** se stalo
- Lze přehrát historii a vytvořit nové projekce
- Přirozené pro CQRS — Command generuje událost, Query čte projekci

---

## EventStore v Pythonu

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid

@dataclass(frozen=True)
class Udalost:
    typ: str
    agregat_id: str
    data: dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cas: datetime = field(default_factory=datetime.now)

class EventStore:
    def __init__(self) -> None:
        self._log: list[Udalost] = []

    def uloz(self, udalost: Udalost) -> None:
        self._log.append(udalost)

    def nacti(self, agregat_id: str) -> list[Udalost]:
        return [u for u in self._log if u.agregat_id == agregat_id]

    def vsechny(self) -> list[Udalost]:
        return list(self._log)
```

---

## Aggregate s Event Sourcing

Stav agregátu vzniká přehráváním událostí přes `apply_*` metody.

```python
@dataclass
class BankovniUcet:
    id: str
    saldo: float = 0.0
    uzavreno: bool = False

    @classmethod
    def z_udalosti(cls, id: str, udalosti: list[Udalost]) -> "BankovniUcet":
        ucet = cls(id=id)
        for u in udalosti:
            ucet._aplikuj(u)
        return ucet

    def _aplikuj(self, udalost: Udalost) -> None:
        match udalost.typ:
            case "UcetOtevren":
                self.saldo = udalost.data["pocatecni_vklad"]
            case "VkladVlozen":
                self.saldo += udalost.data["castka"]
            case "VyberProveden":
                self.saldo -= udalost.data["castka"]
            case "UcetUzavren":
                self.uzavreno = True
```

---

## Commands a CommandHandlers

```python
@dataclass(frozen=True)
class VlozVklad:
    ucet_id: str
    castka: float

@dataclass(frozen=True)
class ProvedVyber:
    ucet_id: str
    castka: float

class BankovniUcetCommandHandler:
    def __init__(self, store: EventStore) -> None:
        self._store = store

    def _nacti_ucet(self, id: str) -> BankovniUcet:
        udalosti = self._store.nacti(id)
        if not udalosti:
            raise KeyError(f"Účet {id!r} neexistuje")
        return BankovniUcet.z_udalosti(id, udalosti)

    def handle_vloz_vklad(self, cmd: VlozVklad) -> None:
        ucet = self._nacti_ucet(cmd.ucet_id)
        if ucet.uzavreno:
            raise ValueError("Účet je uzavřen")
        self._store.uloz(Udalost(
            typ="VkladVlozen",
            agregat_id=cmd.ucet_id,
            data={"castka": cmd.castka},
        ))

    def handle_proved_vyber(self, cmd: ProvedVyber) -> None:
        ucet = self._nacti_ucet(cmd.ucet_id)
        if ucet.saldo < cmd.castka:
            raise ValueError(f"Nedostatek prostředků: saldo={ucet.saldo}")
        self._store.uloz(Udalost(
            typ="VyberProveden",
            agregat_id=cmd.ucet_id,
            data={"castka": cmd.castka},
        ))
```

---

## Projekce (Read Model)

Projekce transformuje historii událostí do formy vhodné pro dotazy.

```python
@dataclass
class StavUctuProjekcee:
    ucet_id: str
    saldo: float = 0.0
    pocet_transakci: int = 0
    posledni_pohyb: datetime | None = None

class StavUctuProjektor:
    def __init__(self, store: EventStore) -> None:
        self._store = store

    def projekce(self, ucet_id: str) -> StavUctuProjekcee:
        stav = StavUctuProjekcee(ucet_id=ucet_id)
        for u in self._store.nacti(ucet_id):
            if u.typ == "UcetOtevren":
                stav.saldo = u.data["pocatecni_vklad"]
                stav.pocet_transakci += 1
            elif u.typ == "VkladVlozen":
                stav.saldo += u.data["castka"]
                stav.pocet_transakci += 1
            elif u.typ == "VyberProveden":
                stav.saldo -= u.data["castka"]
                stav.pocet_transakci += 1
            stav.posledni_pohyb = u.cas
        return stav
```

---

## Idempotence

Command nebo Handler je **idempotentní** pokud vícenásobné spuštění se stejnými daty má stejný výsledek jako jednorázové.

```python
class IdempotentniEventStore:
    def __init__(self) -> None:
        self._log: list[Udalost] = []
        self._zpracovana_ids: set[str] = set()

    def uloz(self, udalost: Udalost) -> bool:
        """Vrátí False pokud událost již byla uložena (deduplication)."""
        if udalost.id in self._zpracovana_ids:
            return False   # idempotentní — ignorujeme duplikát
        self._zpracovana_ids.add(udalost.id)
        self._log.append(udalost)
        return True
```

---

## Shrnutí

| Koncept | Popis |
|---------|-------|
| **Command** | Mění stav, vrací nic nebo potvrzení |
| **Query** | Čte stav, nemění ho |
| **Event** | Neměnný záznam toho, co se stalo |
| **EventStore** | Append-only log událostí |
| **Projekce** | Agregace událostí do read modelu |
| **Idempotence** | Opakování → stejný výsledek |

---

## Cvičení

1. Přidej Command `UzavriUcet` a handler, který vygeneruje událost `UcetUzavren`.
2. Vytvoř projekci `HistorieTransakci` která vrátí seznam `(typ, castka, cas)` pro daný účet.
3. Implementuj snapshot mechanismus: po 10 událostech ulož snapshot stavu, aby se nemuselo přehrávat od začátku.
4. Přidej do `IdempotentniEventStore` metodu `zpracovano(id)` a napiš test duplikátního vložení.
