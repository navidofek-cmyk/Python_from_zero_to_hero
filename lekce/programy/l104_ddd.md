# Program — Lekce 104: Lekce 104: Domain-Driven Design (DDD)

Patří k lekci [Lekce 104: Domain-Driven Design (DDD)](../104_ddd.md).

## Jak spustit

```bash
python3 programy/l104_ddd.py
```

## Zdrojový kód

### `l104_ddd.py`

```py
"""Lekce 104 — Domain-Driven Design (DDD)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Protocol


# ── Value Objects ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Email:
    hodnota: str

    def __post_init__(self) -> None:
        if "@" not in self.hodnota or "." not in self.hodnota.split("@")[-1]:
            raise ValueError(f"Neplatný e-mail: {self.hodnota!r}")

    def domena(self) -> str:
        return self.hodnota.split("@")[1]

    def __str__(self) -> str:
        return self.hodnota


@dataclass(frozen=True)
class Penize:
    castka: float
    mena: str

    def __post_init__(self) -> None:
        if self.castka < 0:
            raise ValueError("Částka nemůže být záporná")

    def __add__(self, other: Penize) -> Penize:
        if self.mena != other.mena:
            raise ValueError(f"Nelze sčítat {self.mena} a {other.mena}")
        return Penize(round(self.castka + other.castka, 2), self.mena)

    def __str__(self) -> str:
        return f"{self.castka:.2f} {self.mena}"


@dataclass(frozen=True)
class Adresa:
    ulice: str
    mesto: str
    psc: str

    def __post_init__(self) -> None:
        if not self.psc.isdigit() or len(self.psc) != 5:
            raise ValueError(f"PSČ musí mít 5 číslic, dostali jsme: {self.psc!r}")

    def __str__(self) -> str:
        return f"{self.ulice}, {self.psc} {self.mesto}"


# ── Doménové události ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class DomenovaUdalost:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cas: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ObjednavkaVytvorena(DomenovaUdalost):
    objednavka_id: int = 0
    zakaznik_id: int = 0


@dataclass(frozen=True)
class ObjednavkaZaplacena(DomenovaUdalost):
    objednavka_id: int = 0
    castka: float = 0.0
    mena: str = "CZK"


@dataclass(frozen=True)
class ObjednavkaZrusena(DomenovaUdalost):
    objednavka_id: int = 0
    duvod: str = ""


# ── Entity ────────────────────────────────────────────────────────────────────

@dataclass
class Zakaznik:
    """Entita — identita přes id, rovnost podle id."""

    id: int
    jmeno: str
    email: Email
    adresa: Adresa | None = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Zakaznik):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __str__(self) -> str:
        return f"Zákazník #{self.id} {self.jmeno} <{self.email}>"


# ── Agregát: Objednávka ───────────────────────────────────────────────────────

class StavObjednavky(Enum):
    NOVA = auto()
    ZAPLACENA = auto()
    ZRUSENA = auto()

    def __str__(self) -> str:
        return self.name.capitalize()


@dataclass
class PolozkaObjednavky:
    nazev: str
    cena: Penize
    mnozstvi: int

    def celkem(self) -> Penize:
        return Penize(round(self.cena.castka * self.mnozstvi, 2), self.cena.mena)

    def __str__(self) -> str:
        return f"{self.nazev} × {self.mnozstvi} = {self.celkem()}"


@dataclass
class Objednavka:
    """Kořen agregátu — veškeré změny jdou přes jeho metody."""

    id: int
    zakaznik_id: int
    polozky: list[PolozkaObjednavky] = field(default_factory=list)
    stav: StavObjednavky = StavObjednavky.NOVA
    _udalosti: list[DomenovaUdalost] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self._udalosti.append(ObjednavkaVytvorena(
            objednavka_id=self.id,
            zakaznik_id=self.zakaznik_id,
        ))

    def pridej_polozku(self, nazev: str, cena: Penize, mnozstvi: int) -> None:
        """Invariant: nelze přidat položku do uzavřené objednávky."""
        if self.stav != StavObjednavky.NOVA:
            raise ValueError(f"Nelze přidat položku: objednávka je ve stavu {self.stav}")
        if mnozstvi <= 0:
            raise ValueError("Množství musí být kladné")
        self.polozky.append(PolozkaObjednavky(nazev, cena, mnozstvi))

    def celkova_cena(self) -> Penize:
        if not self.polozky:
            raise ValueError("Objednávka nemá žádné položky")
        celkem = self.polozky[0].celkem()
        for polozka in self.polozky[1:]:
            celkem = celkem + polozka.celkem()
        return celkem

    def zaplat(self) -> ObjednavkaZaplacena:
        """Invariant: lze zaplatit jen novou objednávku."""
        if self.stav != StavObjednavky.NOVA:
            raise ValueError(f"Nelze zaplatit: stav je {self.stav}")
        cena = self.celkova_cena()
        self.stav = StavObjednavky.ZAPLACENA
        udalost = ObjednavkaZaplacena(
            objednavka_id=self.id,
            castka=cena.castka,
            mena=cena.mena,
        )
        self._udalosti.append(udalost)
        return udalost

    def zrus(self, duvod: str = "") -> ObjednavkaZrusena:
        """Invariant: nelze zrušit zaplacenou objednávku."""
        if self.stav == StavObjednavky.ZAPLACENA:
            raise ValueError("Nelze zrušit zaplacenou objednávku")
        if self.stav == StavObjednavky.ZRUSENA:
            raise ValueError("Objednávka je již zrušena")
        self.stav = StavObjednavky.ZRUSENA
        udalost = ObjednavkaZrusena(objednavka_id=self.id, duvod=duvod)
        self._udalosti.append(udalost)
        return udalost

    def pop_udalosti(self) -> list[DomenovaUdalost]:
        """Vrátí a smaže nahromaděné události."""
        udalosti, self._udalosti = self._udalosti, []
        return udalosti


# ── Repository ────────────────────────────────────────────────────────────────

class ObjednavkaRepository(Protocol):
    def najdi(self, id: int) -> Objednavka | None: ...
    def uloz(self, obj: Objednavka) -> None: ...
    def dalsi_id(self) -> int: ...


class InMemoryObjednavkaRepository:
    def __init__(self) -> None:
        self._store: dict[int, Objednavka] = {}
        self._seq = 1

    def najdi(self, id: int) -> Objednavka | None:
        return self._store.get(id)

    def uloz(self, obj: Objednavka) -> None:
        self._store[obj.id] = obj

    def dalsi_id(self) -> int:
        id = self._seq
        self._seq += 1
        return id


# ── Doménová služba ───────────────────────────────────────────────────────────

class PrevodMen:
    """Doménová služba — logika, která nepatří jedné entitě."""

    def __init__(self, kurzy: dict[tuple[str, str], float]) -> None:
        self._kurzy = kurzy

    def prevod(self, castka: Penize, cilova_mena: str) -> Penize:
        if castka.mena == cilova_mena:
            return castka
        klic = (castka.mena, cilova_mena)
        if klic not in self._kurzy:
            raise ValueError(f"Kurz {castka.mena}/{cilova_mena} není k dispozici")
        return Penize(round(castka.castka * self._kurzy[klic], 2), cilova_mena)


# ── Demo ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=== DDD demo ===\n")

    # Value Objects — porovnání hodnotou
    print("--- Value Objects ---")
    e1 = Email("anna@example.com")
    e2 = Email("anna@example.com")
    e3 = Email("bob@example.com")
    print(f"  e1 == e2: {e1 == e2}  (stejná hodnota → True)")
    print(f"  e1 == e3: {e1 == e3}  (jiná hodnota → False)")
    print(f"  e1 je frozen: {e1.__dataclass_params__.frozen}")  # type: ignore[attr-defined]

    p1 = Penize(100.0, "CZK")
    p2 = Penize(50.0, "CZK")
    print(f"  {p1} + {p2} = {p1 + p2}")

    adresa = Adresa("Náměstí Míru 1", "Praha", "12000")
    print(f"  Adresa: {adresa}")

    print("\n--- Entity ---")
    zakaznik = Zakaznik(
        id=1,
        jmeno="Anna Nováková",
        email=Email("anna@example.com"),
        adresa=adresa,
    )
    print(f"  {zakaznik}")

    print("\n--- Agregát: Objednávka ---")
    repo = InMemoryObjednavkaRepository()

    obj = Objednavka(id=repo.dalsi_id(), zakaznik_id=zakaznik.id)
    obj.pridej_polozku("Notebook", Penize(25_000.0, "CZK"), mnozstvi=1)
    obj.pridej_polozku("Myš", Penize(500.0, "CZK"), mnozstvi=2)
    obj.pridej_polozku("Klávesnice", Penize(800.0, "CZK"), mnozstvi=1)

    print(f"  Objednávka #{obj.id}, stav: {obj.stav}")
    for polozka in obj.polozky:
        print(f"    {polozka}")
    print(f"  Celková cena: {obj.celkova_cena()}")

    repo.uloz(obj)

    # Zaplacení — vygeneruje doménovou událost
    udalost_zaplaceni = obj.zaplat()
    print(f"\n  Zaplaceno! Stav: {obj.stav}")

    # Pokus o přidání položky do zaplacené objednávky
    try:
        obj.pridej_polozku("Monitor", Penize(8000.0, "CZK"), 1)
    except ValueError as exc:
        print(f"  Správná chyba: {exc}")

    # Pokus o zrušení zaplacené objednávky
    try:
        obj.zrus("Zákazník si to rozmyslel")
    except ValueError as exc:
        print(f"  Správná chyba: {exc}")

    # Doménové události
    print("\n--- Doménové události ---")
    udalosti = obj.pop_udalosti()
    for u in udalosti:
        print(f"  [{u.__class__.__name__}] id={u.id[:8]}... cas={u.cas:%H:%M:%S}")

    # Druhá objednávka — bude zrušena
    print("\n--- Zrušení objednávky ---")
    obj2 = Objednavka(id=repo.dalsi_id(), zakaznik_id=zakaznik.id)
    obj2.pridej_polozku("Tiskárna", Penize(3000.0, "CZK"), 1)
    obj2.zrus("Test zrušení")
    print(f"  Stav: {obj2.stav}")
    for u in obj2.pop_udalosti():
        print(f"  [{u.__class__.__name__}]")

    # Doménová služba
    print("\n--- Doménová služba: převod měn ---")
    prevod = PrevodMen({("CZK", "EUR"): 0.04, ("EUR", "CZK"): 25.0})
    czk = Penize(25_800.0, "CZK")
    eur = prevod.prevod(czk, "EUR")
    print(f"  {czk} → {eur}")
    print(f"  Zpět: {prevod.prevod(eur, 'CZK')}")


if __name__ == "__main__":
    main()

```
