"""Lekce 105 — CQRS a Event Sourcing."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# ── Event Store ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Udalost:
    typ: str
    agregat_id: str
    data: dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cas: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"[{self.typ}] agregat={self.agregat_id} data={self.data}"


class EventStore:
    """Append-only log událostí s podporou idempotence."""

    def __init__(self) -> None:
        self._log: list[Udalost] = []
        self._zpracovana_ids: set[str] = set()

    def uloz(self, udalost: Udalost) -> bool:
        """Uloží událost. Vrátí False pro duplikát (idempotentní)."""
        if udalost.id in self._zpracovana_ids:
            print(f"  [STORE] Duplikát ignorován: {udalost.id[:8]}...")
            return False
        self._zpracovana_ids.add(udalost.id)
        self._log.append(udalost)
        return True

    def nacti(self, agregat_id: str) -> list[Udalost]:
        return [u for u in self._log if u.agregat_id == agregat_id]

    def vsechny(self) -> list[Udalost]:
        return list(self._log)

    def __len__(self) -> int:
        return len(self._log)


# ── Agregát: BankovniUcet ─────────────────────────────────────────────────────

@dataclass
class BankovniUcet:
    """Stav rekonstruovaný z událostí — žádná DB, jen přehrání logu."""

    id: str
    saldo: float = 0.0
    uzavreno: bool = False
    verze: int = 0

    @classmethod
    def z_udalosti(cls, id: str, udalosti: list[Udalost]) -> BankovniUcet:
        ucet = cls(id=id)
        for u in udalosti:
            ucet._aplikuj(u)
        return ucet

    def _aplikuj(self, udalost: Udalost) -> None:
        """Čistá funkce: aplikuje jednu událost na stav."""
        match udalost.typ:
            case "UcetOtevren":
                self.saldo = udalost.data["pocatecni_vklad"]
            case "VkladVlozen":
                self.saldo += udalost.data["castka"]
            case "VyberProveden":
                self.saldo -= udalost.data["castka"]
            case "UcetUzavren":
                self.uzavreno = True
        self.verze += 1

    def __str__(self) -> str:
        stav = "uzavřen" if self.uzavreno else "aktivní"
        return f"Účet {self.id[:8]}... | saldo={self.saldo:.2f} Kč | {stav} | v{self.verze}"


# ── Commands ──────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class OtevriUcet:
    ucet_id: str
    pocatecni_vklad: float


@dataclass(frozen=True)
class VlozVklad:
    ucet_id: str
    castka: float


@dataclass(frozen=True)
class ProvedVyber:
    ucet_id: str
    castka: float


@dataclass(frozen=True)
class UzavriUcet:
    ucet_id: str
    duvod: str = ""


# ── Command Handler ───────────────────────────────────────────────────────────

class BankovniUcetCommandHandler:
    """Zpracovává Commands — mění stav přes EventStore."""

    def __init__(self, store: EventStore) -> None:
        self._store = store

    def _nacti(self, ucet_id: str) -> BankovniUcet:
        udalosti = self._store.nacti(ucet_id)
        if not udalosti:
            raise KeyError(f"Účet {ucet_id[:8]}... neexistuje")
        return BankovniUcet.z_udalosti(ucet_id, udalosti)

    def otevri_ucet(self, cmd: OtevriUcet) -> None:
        if self._store.nacti(cmd.ucet_id):
            raise ValueError("Účet již existuje")
        if cmd.pocatecni_vklad < 0:
            raise ValueError("Počáteční vklad nesmí být záporný")
        self._store.uloz(Udalost(
            typ="UcetOtevren",
            agregat_id=cmd.ucet_id,
            data={"pocatecni_vklad": cmd.pocatecni_vklad},
        ))

    def vloz_vklad(self, cmd: VlozVklad) -> None:
        ucet = self._nacti(cmd.ucet_id)
        if ucet.uzavreno:
            raise ValueError("Účet je uzavřen")
        if cmd.castka <= 0:
            raise ValueError("Vklad musí být kladný")
        self._store.uloz(Udalost(
            typ="VkladVlozen",
            agregat_id=cmd.ucet_id,
            data={"castka": cmd.castka},
        ))

    def proved_vyber(self, cmd: ProvedVyber) -> None:
        ucet = self._nacti(cmd.ucet_id)
        if ucet.uzavreno:
            raise ValueError("Účet je uzavřen")
        if cmd.castka <= 0:
            raise ValueError("Výběr musí být kladný")
        if ucet.saldo < cmd.castka:
            raise ValueError(f"Nedostatek prostředků: saldo={ucet.saldo:.2f}, požadováno={cmd.castka:.2f}")
        self._store.uloz(Udalost(
            typ="VyberProveden",
            agregat_id=cmd.ucet_id,
            data={"castka": cmd.castka},
        ))

    def uzavri_ucet(self, cmd: UzavriUcet) -> None:
        ucet = self._nacti(cmd.ucet_id)
        if ucet.uzavreno:
            raise ValueError("Účet je již uzavřen")
        self._store.uloz(Udalost(
            typ="UcetUzavren",
            agregat_id=cmd.ucet_id,
            data={"duvod": cmd.duvod, "konecne_saldo": ucet.saldo},
        ))


# ── Query Modely (Projekce) ───────────────────────────────────────────────────

@dataclass
class StavUctuView:
    ucet_id: str
    saldo: float
    uzavreno: bool
    pocet_transakci: int
    posledni_pohyb: datetime | None


@dataclass
class TransakceView:
    typ: str
    castka: float
    cas: datetime
    saldo_po: float


class BankovniUcetQueryHandler:
    """Zpracovává Queries — čte stav z projekcí, nikdy nemění EventStore."""

    def __init__(self, store: EventStore) -> None:
        self._store = store

    def stav_uctu(self, ucet_id: str) -> StavUctuView:
        udalosti = self._store.nacti(ucet_id)
        if not udalosti:
            raise KeyError(f"Účet neexistuje")
        saldo = 0.0
        uzavreno = False
        pocet = 0
        posledni = None
        for u in udalosti:
            if u.typ == "UcetOtevren":
                saldo = u.data["pocatecni_vklad"]
                pocet += 1
            elif u.typ == "VkladVlozen":
                saldo += u.data["castka"]
                pocet += 1
            elif u.typ == "VyberProveden":
                saldo -= u.data["castka"]
                pocet += 1
            elif u.typ == "UcetUzavren":
                uzavreno = True
            posledni = u.cas
        return StavUctuView(ucet_id, saldo, uzavreno, pocet, posledni)

    def historie_transakci(self, ucet_id: str) -> list[TransakceView]:
        udalosti = self._store.nacti(ucet_id)
        transakce = []
        saldo = 0.0
        for u in udalosti:
            if u.typ == "UcetOtevren":
                saldo = u.data["pocatecni_vklad"]
                transakce.append(TransakceView("Otevření", saldo, u.cas, saldo))
            elif u.typ == "VkladVlozen":
                saldo += u.data["castka"]
                transakce.append(TransakceView("Vklad", u.data["castka"], u.cas, saldo))
            elif u.typ == "VyberProveden":
                saldo -= u.data["castka"]
                transakce.append(TransakceView("Výběr", -u.data["castka"], u.cas, saldo))
            elif u.typ == "UcetUzavren":
                transakce.append(TransakceView("Uzavření", 0.0, u.cas, saldo))
        return transakce


# ── Demo ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=== CQRS + Event Sourcing demo ===\n")

    store = EventStore()
    cmd = BankovniUcetCommandHandler(store)
    qry = BankovniUcetQueryHandler(store)

    ucet_id = str(uuid.uuid4())

    print("--- Commands: operace s účtem ---")
    cmd.otevri_ucet(OtevriUcet(ucet_id, pocatecni_vklad=10_000.0))
    print(f"  Účet otevřen, vklad: 10 000 Kč")

    cmd.vloz_vklad(VlozVklad(ucet_id, castka=5_000.0))
    print(f"  Vložen vklad: 5 000 Kč")

    cmd.proved_vyber(ProvedVyber(ucet_id, castka=3_000.0))
    print(f"  Proveden výběr: 3 000 Kč")

    cmd.vloz_vklad(VlozVklad(ucet_id, castka=2_000.0))
    print(f"  Vložen vklad: 2 000 Kč")

    cmd.proved_vyber(ProvedVyber(ucet_id, castka=1_500.0))
    print(f"  Proveden výběr: 1 500 Kč")

    print("\n--- Query: aktuální stav ---")
    stav = qry.stav_uctu(ucet_id)
    print(f"  Saldo:        {stav.saldo:.2f} Kč")
    print(f"  Transakcí:    {stav.pocet_transakci}")
    print(f"  Uzavřen:      {stav.uzavreno}")
    print(f"  Posl. pohyb:  {stav.posledni_pohyb:%H:%M:%S}")  # type: ignore[union-attr]

    print("\n--- Query: historie transakcí ---")
    for t in qry.historie_transakci(ucet_id):
        smer = "+" if t.castka >= 0 else ""
        print(f"  {t.typ:12s} {smer}{t.castka:8.2f} Kč  → saldo: {t.saldo_po:.2f} Kč")

    print("\n--- Rekonstrukce stavu z událostí ---")
    udalosti = store.nacti(ucet_id)
    ucet = BankovniUcet.z_udalosti(ucet_id, udalosti)
    print(f"  {ucet}")
    print(f"  Celkem událostí v logu: {len(store)}")

    print("\n--- Ochrana před přečerpáním ---")
    try:
        cmd.proved_vyber(ProvedVyber(ucet_id, castka=999_999.0))
    except ValueError as exc:
        print(f"  Správná chyba: {exc}")

    print("\n--- Idempotence: duplikátní událost ---")
    duplicitni = Udalost(
        typ="VkladVlozen",
        agregat_id=ucet_id,
        data={"castka": 100.0},
        id=store.vsechny()[-1].id,   # stejné id jako poslední událost
    )
    vysledek = store.uloz(duplicitni)
    print(f"  Duplikát uložen: {vysledek}  (False = správně ignorován)")
    stav2 = qry.stav_uctu(ucet_id)
    print(f"  Saldo se nezměnilo: {stav2.saldo:.2f} Kč")

    print("\n--- Uzavření účtu ---")
    cmd.uzavri_ucet(UzavriUcet(ucet_id, duvod="Na žádost klienta"))
    stav3 = qry.stav_uctu(ucet_id)
    print(f"  Uzavřen: {stav3.uzavreno}")

    try:
        cmd.vloz_vklad(VlozVklad(ucet_id, castka=100.0))
    except ValueError as exc:
        print(f"  Operace na uzavřeném účtu: {exc}")


if __name__ == "__main__":
    main()
