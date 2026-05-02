# Program — Lekce 108: Lekce 108: Konzistence dat — Saga, Outbox, transakční messaging

Patří k lekci [Lekce 108: Konzistence dat — Saga, Outbox, transakční messaging](../108_konzistence_dat.md).

## Jak spustit

```bash
python3 programy/l108_konzistence_dat.py
```

## Zdrojový kód

### `l108_konzistence_dat.py`

```py
"""Lekce 108 — Konzistence dat: Saga pattern, Outbox pattern, transakční messaging."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# ── Simulace mikroslužeb ──────────────────────────────────────────────────────

class PlatebniSluzba:
    """Simuluje platební mikroslužbu."""

    def __init__(self) -> None:
        self._platby: dict[str, float] = {}
        self.selhavej_pri: set[str] = set()  # pro testování selhání

    def zpracuj_platbu(self, objednavka_id: str, castka: float) -> str:
        if objednavka_id in self.selhavej_pri:
            raise RuntimeError(f"Platba selhala pro objednávku {objednavka_id}")
        platba_id = str(uuid.uuid4())[:8]
        self._platby[objednavka_id] = castka
        print(f"  [PlatebniSluzba] Platba {castka:.2f} Kč zpracována (id={platba_id})")
        return platba_id

    def vrat_platbu(self, objednavka_id: str) -> None:
        if objednavka_id in self._platby:
            castka = self._platby.pop(objednavka_id)
            print(f"  [PlatebniSluzba] KOMPENZACE: platba {castka:.2f} Kč vrácena")
        else:
            print(f"  [PlatebniSluzba] Kompenzace: platba pro {objednavka_id} nenalezena")


class SkladovaSluzba:
    """Simuluje skladovou mikroslužbu."""

    def __init__(self, zasoby: dict[str, int]) -> None:
        self._zasoby = dict(zasoby)
        self._rezervace: dict[str, list[tuple[str, int]]] = {}
        self.selhavej_pri: set[str] = set()

    def rezervuj(self, objednavka_id: str, polozky: list[tuple[str, int]]) -> None:
        if objednavka_id in self.selhavej_pri:
            raise RuntimeError(f"Sklad nedostupný pro objednávku {objednavka_id}")
        for nazev, mnozstvi in polozky:
            dostupne = self._zasoby.get(nazev, 0)
            if dostupne < mnozstvi:
                raise ValueError(f"Nedostatečné zásoby: {nazev} (dostupné={dostupne}, požadováno={mnozstvi})")
        for nazev, mnozstvi in polozky:
            self._zasoby[nazev] -= mnozstvi
        self._rezervace[objednavka_id] = polozky
        print(f"  [SkladovaSluzba] Rezervováno pro objednávku {objednavka_id}: {polozky}")

    def zrus_rezervaci(self, objednavka_id: str) -> None:
        polozky = self._rezervace.pop(objednavka_id, [])
        for nazev, mnozstvi in polozky:
            self._zasoby[nazev] = self._zasoby.get(nazev, 0) + mnozstvi
        print(f"  [SkladovaSluzba] KOMPENZACE: rezervace {objednavka_id} zrušena, zásoby obnoveny")

    def zasoby(self) -> dict[str, int]:
        return dict(self._zasoby)


class EmailovaSluzba:
    """Simuluje e-mailovou mikroslužbu."""

    def __init__(self) -> None:
        self._odeslane: list[str] = []
        self.selhavej_pri: set[str] = set()

    def posli_potvrzeni(self, objednavka_id: str, email: str) -> None:
        if objednavka_id in self.selhavej_pri:
            raise RuntimeError(f"E-mail selhal pro objednávku {objednavka_id}")
        self._odeslane.append(objednavka_id)
        print(f"  [EmailovaSluzba] Potvrzení odesláno na {email}")

    def odvolej_potvrzeni(self, objednavka_id: str) -> None:
        if objednavka_id in self._odeslane:
            self._odeslane.remove(objednavka_id)
        print(f"  [EmailovaSluzba] KOMPENZACE: odesláno zrušení objednávky {objednavka_id}")


# ── Saga: Orchestration-based ─────────────────────────────────────────────────

@dataclass
class VysledekSagy:
    uspech: bool
    objednavka_id: str
    chyba: str | None = None
    platba_id: str | None = None


class ObjednavkaSaga:
    """
    Orchestration-based Saga: koordinuje lokální transakce přes 3 mikroslužby.
    Při selhání spustí kompenzační transakce v opačném pořadí.
    """

    def __init__(
        self,
        platebni: PlatebniSluzba,
        sklad: SkladovaSluzba,
        email: EmailovaSluzba,
    ) -> None:
        self._platba = platebni
        self._sklad = sklad
        self._email = email

    def proved(
        self,
        objednavka_id: str,
        castka: float,
        polozky: list[tuple[str, int]],
        email_zakaznika: str,
    ) -> VysledekSagy:
        """
        Kroky:
          1. Rezervuj sklad
          2. Zpracuj platbu         (kompenzace: vrát platbu)
          3. Pošli potvrzovací e-mail (kompenzace: odvolej potvrzení)
        """
        print(f"  [Saga] Spouštím sagu pro objednávku {objednavka_id}")
        sklad_rezervovano = False
        platba_id: str | None = None

        # Krok 1: Rezervace skladu
        try:
            self._sklad.rezervuj(objednavka_id, polozky)
            sklad_rezervovano = True
        except Exception as exc:
            return VysledekSagy(False, objednavka_id, chyba=f"Sklad: {exc}")

        # Krok 2: Platba
        try:
            platba_id = self._platba.zpracuj_platbu(objednavka_id, castka)
        except Exception as exc:
            print(f"  [Saga] Krok 2 selhal — spouštím kompenzaci...")
            if sklad_rezervovano:
                self._sklad.zrus_rezervaci(objednavka_id)
            return VysledekSagy(False, objednavka_id, chyba=f"Platba: {exc}")

        # Krok 3: E-mail
        try:
            self._email.posli_potvrzeni(objednavka_id, email_zakaznika)
        except Exception as exc:
            print(f"  [Saga] Krok 3 selhal — spouštím kompenzaci...")
            self._platba.vrat_platbu(objednavka_id)
            self._sklad.zrus_rezervaci(objednavka_id)
            return VysledekSagy(False, objednavka_id, chyba=f"E-mail: {exc}")

        print(f"  [Saga] Saga úspěšně dokončena")
        return VysledekSagy(True, objednavka_id, platba_id=platba_id)


# ── Outbox pattern ────────────────────────────────────────────────────────────

@dataclass
class OutboxZprava:
    id: str
    typ: str
    payload: dict[str, Any]
    status: str = "PENDING"
    pocet_pokusu: int = 0
    cas_vytvoreni: datetime = field(default_factory=datetime.now)
    cas_odeslani: datetime | None = None


class OutboxStore:
    """Simulace outbox tabulky — součást stejné DB jako business data."""

    def __init__(self) -> None:
        self._zpravy: list[OutboxZprava] = []

    def pridej(self, typ: str, payload: dict[str, Any]) -> OutboxZprava:
        zprava = OutboxZprava(id=str(uuid.uuid4()), typ=typ, payload=payload)
        self._zpravy.append(zprava)
        return zprava

    def cekajici(self, limit: int = 10) -> list[OutboxZprava]:
        return [z for z in self._zpravy if z.status == "PENDING"][:limit]

    def neuspesne(self, max_pokusu: int = 3) -> list[OutboxZprava]:
        return [z for z in self._zpravy if z.pocet_pokusu >= max_pokusu and z.status != "SENT"]

    def oznac_odeslano(self, id: str) -> None:
        for z in self._zpravy:
            if z.id == id:
                z.status = "SENT"
                z.cas_odeslani = datetime.now()

    def oznac_selhani(self, id: str) -> None:
        for z in self._zpravy:
            if z.id == id:
                z.pocet_pokusu += 1
                if z.pocet_pokusu >= 3:
                    z.status = "FAILED"

    def souhrn(self) -> dict[str, int]:
        from collections import Counter
        c = Counter(z.status for z in self._zpravy)
        return dict(c)


class SimulovanyMessageBroker:
    """Simulace message brokera (Kafka, RabbitMQ)."""

    def __init__(self, pravdepodobnost_uspechu: float = 0.8) -> None:
        self._p = pravdepodobnost_uspechu
        self._prijate: list[dict[str, Any]] = []
        self._pocitadlo = 0

    def posli(self, zprava: OutboxZprava) -> None:
        import random
        self._pocitadlo += 1
        if random.random() > self._p:
            raise ConnectionError(f"Broker nedostupný (pokus #{self._pocitadlo})")
        self._prijate.append({"typ": zprava.typ, "payload": zprava.payload})

    def prijate_zpravy(self) -> list[dict[str, Any]]:
        return list(self._prijate)


class OutboxPoller:
    """
    Čte čekající zprávy z outboxu a posílá je do brokera.
    At-least-once: při selhání brokera se zpráva odešle znovu.
    """

    def __init__(self, outbox: OutboxStore, broker: SimulovanyMessageBroker) -> None:
        self._outbox = outbox
        self._broker = broker

    def zpracuj_davku(self, limit: int = 10) -> tuple[int, int]:
        """Zpracuje dávku čekajících zpráv. Vrátí (úspěšné, neúspěšné)."""
        zpravy = self._outbox.cekajici(limit)
        uspesne = neuspesne = 0

        for zprava in zpravy:
            try:
                self._broker.posli(zprava)
                self._outbox.oznac_odeslano(zprava.id)
                uspesne += 1
                print(f"  [Poller] Odesláno: {zprava.typ} (id={zprava.id[:8]}...)")
            except ConnectionError as exc:
                self._outbox.oznac_selhani(zprava.id)
                neuspesne += 1
                print(f"  [Poller] Selhání: {exc} — pokus #{zprava.pocet_pokusu + 1}")

        return uspesne, neuspesne


# ── Idempotentní příjemce zpráv ───────────────────────────────────────────────

class IdempotentniPrijemce:
    """At-least-once + deduplication = de-facto exactly-once."""

    def __init__(self) -> None:
        self._zpracovane_ids: set[str] = set()
        self._zpracovane_zpravy: list[dict[str, Any]] = []

    def zpracuj(self, zprava: dict[str, Any]) -> bool:
        zprava_id = zprava.get("id", "")
        if zprava_id in self._zpracovane_ids:
            print(f"  [Příjemce] Duplikát {zprava_id[:8]}... ignorován")
            return False
        self._zpracovane_ids.add(zprava_id)
        self._zpracovane_zpravy.append(zprava)
        print(f"  [Příjemce] Zpracována zpráva: {zprava.get('typ', '?')}")
        return True


# ── Demo ──────────────────────────────────────────────────────────────────────

def main() -> None:
    import random
    random.seed(123)

    print("=== Konzistence dat: Saga + Outbox demo ===\n")

    # Inicializace simulovaných mikroslužeb
    platba = PlatebniSluzba()
    sklad = SkladovaSluzba({"Notebook": 5, "Myš": 20, "Klávesnice": 10})
    email_svc = EmailovaSluzba()
    saga = ObjednavkaSaga(platba, sklad, email_svc)

    print("--- Saga: úspěšná objednávka ---")
    vysledek = saga.proved(
        objednavka_id="OBJ-001",
        castka=26_300.0,
        polozky=[("Notebook", 1), ("Myš", 2)],
        email_zakaznika="anna@example.com",
    )
    print(f"  Výsledek: {'OK' if vysledek.uspech else 'CHYBA'} | platba_id={vysledek.platba_id}")
    print(f"  Zásoby: {sklad.zasoby()}")

    print("\n--- Saga: selhání v kroku 'Platba' → kompenzace skladu ---")
    platba.selhavej_pri.add("OBJ-002")
    zasoby_pred = sklad.zasoby()
    vysledek2 = saga.proved(
        objednavka_id="OBJ-002",
        castka=800.0,
        polozky=[("Klávesnice", 2)],
        email_zakaznika="bob@example.com",
    )
    print(f"  Výsledek: {'OK' if vysledek2.uspech else 'CHYBA — ' + str(vysledek2.chyba)}")
    print(f"  Zásoby před: {zasoby_pred}")
    print(f"  Zásoby po:   {sklad.zasoby()} (sklad obnoven ✓)")

    print("\n--- Saga: selhání e-mailu → kompenzace platby + skladu ---")
    email_svc.selhavej_pri.add("OBJ-003")
    vysledek3 = saga.proved(
        objednavka_id="OBJ-003",
        castka=500.0,
        polozky=[("Myš", 1)],
        email_zakaznika="cyril@example.com",
    )
    print(f"  Výsledek: {'OK' if vysledek3.uspech else 'CHYBA — ' + str(vysledek3.chyba)}")

    print("\n--- Outbox pattern ---")
    outbox = OutboxStore()
    broker = SimulovanyMessageBroker(pravdepodobnost_uspechu=0.6)
    poller = OutboxPoller(outbox, broker)

    # Simulace: "atomicky" uložíme data + přidáme do outboxu
    for i in range(5):
        oid = f"OBJ-{100+i:03d}"
        # V reálu: db.uloz(objednavka) + outbox.pridej(...) v jedné transakci
        outbox.pridej("ObjednavkaVytvorena", {"objednavka_id": oid, "castka": 500.0 * i})
    print(f"  Přidáno {len(outbox.cekajici())} zpráv do outboxu")

    print("\n  Poller — první dávka:")
    ok1, err1 = poller.zpracuj_davku()
    print(f"  Úspěšné: {ok1}, Neúspěšné: {err1}")

    print("\n  Poller — druhá dávka (retry selhání):")
    ok2, err2 = poller.zpracuj_davku()
    print(f"  Úspěšné: {ok2}, Neúspěšné: {err2}")

    print(f"\n  Souhrn outboxu: {outbox.souhrn()}")
    print(f"  Broker přijal: {len(broker.prijate_zpravy())} zpráv")

    print("\n--- Idempotentní příjemce (at-least-once → exactly-once) ---")
    prijemce = IdempotentniPrijemce()
    zprava_id = str(uuid.uuid4())
    zprava = {"id": zprava_id, "typ": "ObjednavkaVytvorena", "payload": {"id": "OBJ-001"}}

    print("  Zpracování zprávy 3× (at-least-once simulace):")
    for _ in range(3):
        prijemce.zpracuj(zprava)

    print(f"\n  Celkem skutečně zpracováno: {len(prijemce._zpracovane_zpravy)} (ne 3)")


if __name__ == "__main__":
    main()

```
