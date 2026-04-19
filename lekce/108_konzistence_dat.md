# Lekce 108: Konzistence dat — Saga, Outbox, transakční messaging

## Problém distribuované konzistence

V monolitu jedna DB transakce zajistí konzistenci. V mikroslužbách každá služba má svou DB — nelze použít jednu transakci přes více služeb.

```
Objednávka OK → Sklad odečten → Platba provedena
                  ↑ co když tady selžeme?
Objednávka existuje, ale sklad nebyl odečten → NEKONZISTENTNÍ STAV
```

---

## Saga pattern

**Saga** je sekvence lokálních transakcí koordinovaných přes zprávy nebo orchestrátor. Každá lokální transakce má **kompenzační transakci** (undo).

### Choreography-based Saga

Každá služba poslouchá události a reaguje na ně.

```
Order Service → [OrderCreated] → Payment Service
                                → [PaymentProcessed] → Inventory Service
                                                      → [InventoryReserved] → Order Service
                                                                            → [OrderConfirmed]
```

Výhody: jednoduchá, žádný centrální orchestrátor
Nevýhody: těžko sledovatelná, cyklické závislosti

### Orchestration-based Saga

Centrální orchestrátor (saga manager) řídí tok.

```python
class ObjednavkaSaga:
    def __init__(self, platebn_svc, sklad_svc):
        self._platba = platebn_svc
        self._sklad = sklad_svc

    def proved(self, objednavka_id: str, castka: float, polozky: list) -> bool:
        # Krok 1: rezervovat sklad
        try:
            self._sklad.rezervuj(objednavka_id, polozky)
        except Exception:
            return False  # nic k kompenzaci

        # Krok 2: zpracovat platbu
        try:
            self._platba.zpracuj(objednavka_id, castka)
        except Exception:
            self._sklad.zrus_rezervaci(objednavka_id)  # kompenzace!
            return False

        return True
```

---

## Outbox pattern

**Problém**: uložit do DB a zároveň poslat zprávu do message brokera atomicky.

```
Špatně:
  1. COMMIT do DB ✓
  2. Pošli zprávu... crash → zpráva ztracena ✗

Taky špatně:
  1. Pošli zprávu... ✓
  2. COMMIT do DB... crash → zpráva poslána, ale data v DB nejsou ✗
```

**Outbox pattern**:
1. V rámci jedné DB transakce: ulož data + ulož zprávu do tabulky `outbox`
2. Separátní proces (poller) čte `outbox` a posílá zprávy
3. Po potvrzení odeslání označí záznam jako odeslaný

```
DB transakce:
  INSERT INTO orders ...
  INSERT INTO outbox (payload, status) VALUES ('{"typ":"OrderCreated"...}', 'PENDING')

Outbox Poller:
  SELECT * FROM outbox WHERE status = 'PENDING' LIMIT 10
  FOR EACH:
    Pošli do message brokera
    UPDATE outbox SET status = 'SENT'
```

---

## Implementace Outbox v Pythonu (simulace)

```python
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class OutboxZprava:
    id: str
    typ: str
    payload: dict
    status: str = "PENDING"
    cas: datetime = field(default_factory=datetime.now)
    odeslan_v: datetime | None = None

class OutboxStore:
    def __init__(self) -> None:
        self._zpravy: list[OutboxZprava] = []

    def pridej(self, typ: str, payload: dict) -> OutboxZprava:
        zprava = OutboxZprava(id=str(uuid.uuid4()), typ=typ, payload=payload)
        self._zpravy.append(zprava)
        return zprava

    def cekajici(self) -> list[OutboxZprava]:
        return [z for z in self._zpravy if z.status == "PENDING"]

    def oznac_odeslano(self, id: str) -> None:
        for z in self._zpravy:
            if z.id == id:
                z.status = "SENT"
                z.odeslan_v = datetime.now()
```

---

## At-least-once vs. Exactly-once

| Záruka | Popis | Implementace |
|--------|-------|--------------|
| **At-most-once** | Zpráva může být ztracena, ne duplicitní | Fire & forget |
| **At-least-once** | Zpráva dorazí, ale možná víckrát | Retry + idempotentní příjemce |
| **Exactly-once** | Zpráva dorazí přesně jednou | Distribuované transakce nebo idempotence + deduplication |

Kafka, RabbitMQ nabízejí **at-least-once**. Exactly-once je prakticky nemožné bez kompromisů.

**Řešení**: at-least-once + **idempotentní příjemce** = de-facto exactly-once.

---

## Transakční messaging — tři záruky

```python
# Producent s outbox:
def vytvor_objednavku(objednavka: Objednavka, outbox: OutboxStore) -> None:
    # Atomická operace (v reálu jedna DB transakce):
    db.uloz(objednavka)
    outbox.pridej("ObjednavkaVytvorena", {"id": objednavka.id, ...})
    # Commit — buď oboje, nebo nic

# Konzument s deduplication:
def zpracuj_zprávu(zprava: dict, zpracovano_ids: set) -> None:
    if zprava["id"] in zpracovano_ids:
        return   # duplikát — ignorovat
    zpracovano_ids.add(zprava["id"])
    # ... zpracování
```

---

## Shrnutí

| Pattern | Problém | Řešení |
|---------|---------|--------|
| **Saga** | Distribuovaná transakce přes více DB | Lokální transakce + kompenzace |
| **Outbox** | Atomicky DB + message broker | Zapsat do DB, poller odešle |
| **Idempotence** | At-least-once delivery | Deduplication na příjemci |

---

## Cvičení

1. Rozšiř `ObjednavkaSaga` o třetí krok: odeslání potvrzovacího e-mailu s kompenzací.
2. Implementuj `OutboxPoller` který každých N sekund zpracuje čekající zprávy.
3. Přidej do `OutboxStore` metodu `neuspesne()` která vrátí zprávy s více než 3 pokusy odeslání.
4. Simuluj scenář kde Outbox Poller selže uprostřed — jak zajistit, že zprávy nebudou ztraceny?
