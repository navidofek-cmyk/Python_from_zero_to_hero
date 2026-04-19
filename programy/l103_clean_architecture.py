"""Lekce 103 — Hexagonal / Ports & Adapters / Clean Architecture."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


# ── Domain — entity ───────────────────────────────────────────────────────────

@dataclass
class Uzivatel:
    """Doménová entita — má identitu (id), validuje svůj stav."""

    id: int
    jmeno: str
    email: str
    vytvoreno: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not self.email or "@" not in self.email:
            raise ValueError(f"Neplatný e-mail: {self.email!r}")
        if not self.jmeno.strip():
            raise ValueError("Jméno nesmí být prázdné")

    def zmen_email(self, novy: str) -> None:
        if "@" not in novy:
            raise ValueError(f"Neplatný e-mail: {novy!r}")
        self.email = novy


# ── Application — porty (Protocol) ───────────────────────────────────────────

class UzivatelRepository(Protocol):
    """PORT — definuje co infrastruktura musí umět. Žádný import DB!"""

    def najdi_podle_id(self, id: int) -> Uzivatel | None: ...
    def uloz(self, uzivatel: Uzivatel) -> None: ...
    def seznam(self) -> list[Uzivatel]: ...


# ── Application — DTO a use cases ────────────────────────────────────────────

@dataclass(frozen=True)
class RegistraceVstupu:
    jmeno: str
    email: str


@dataclass(frozen=True)
class RegistraceVystupu:
    id: int
    jmeno: str
    email: str


class RegistraceUzivateleUseCase:
    """Use case: zaregistruje nového uživatele, závisí jen na Portu."""

    def __init__(self, repo: UzivatelRepository) -> None:
        self._repo = repo
        self._next_id = 1

    def execute(self, vstup: RegistraceVstupu) -> RegistraceVystupu:
        # doménové pravidlo: unikátní e-mail
        duplicita = [u for u in self._repo.seznam() if u.email == vstup.email]
        if duplicita:
            raise ValueError(f"E-mail {vstup.email!r} je již registrován")

        uzivatel = Uzivatel(
            id=self._next_id,
            jmeno=vstup.jmeno,
            email=vstup.email,
        )
        self._repo.uloz(uzivatel)
        self._next_id += 1
        return RegistraceVystupu(id=uzivatel.id, jmeno=uzivatel.jmeno, email=uzivatel.email)


class NajdiUzivateleUseCase:
    """Use case: vyhledá uživatele podle id."""

    def __init__(self, repo: UzivatelRepository) -> None:
        self._repo = repo

    def execute(self, id: int) -> Uzivatel:
        uzivatel = self._repo.najdi_podle_id(id)
        if uzivatel is None:
            raise KeyError(f"Uživatel s id={id} neexistuje")
        return uzivatel


# ── Infrastructure — adaptéry ─────────────────────────────────────────────────

class InMemoryUzivatelRepository:
    """ADAPTER — in-memory implementace portu, vhodná pro testy."""

    def __init__(self) -> None:
        self._store: dict[int, Uzivatel] = {}

    def najdi_podle_id(self, id: int) -> Uzivatel | None:
        return self._store.get(id)

    def uloz(self, uzivatel: Uzivatel) -> None:
        self._store[uzivatel.id] = uzivatel

    def seznam(self) -> list[Uzivatel]:
        return list(self._store.values())


# Alternativní adapter — simulace "databázového" úložiště s log výpisy
class LogujiciRepository:
    """ADAPTER — obaluje jiný repo a loguje každou operaci (Decorator)."""

    def __init__(self, vnitrni: UzivatelRepository) -> None:
        self._vnitrni = vnitrni

    def najdi_podle_id(self, id: int) -> Uzivatel | None:
        result = self._vnitrni.najdi_podle_id(id)
        print(f"  [LOG] najdi_podle_id({id}) → {result}")
        return result

    def uloz(self, uzivatel: Uzivatel) -> None:
        print(f"  [LOG] uloz({uzivatel.jmeno!r}, id={uzivatel.id})")
        self._vnitrni.uloz(uzivatel)

    def seznam(self) -> list[Uzivatel]:
        vysledek = self._vnitrni.seznam()
        print(f"  [LOG] seznam() → {len(vysledek)} záznamů")
        return vysledek


# ── Demo ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=== Clean Architecture demo ===\n")

    # Infrastructure vrstva: vyber adapter
    zakladni_repo = InMemoryUzivatelRepository()
    repo = LogujiciRepository(zakladni_repo)   # obalíme logujícím dekorátorem

    # Application vrstva: use cases dostanou repo přes DI
    registrace_uc = RegistraceUzivateleUseCase(repo)
    najdi_uc = NajdiUzivateleUseCase(repo)

    print("--- Registrace nových uživatelů ---")
    uzivatele_data = [
        RegistraceVstupu("Anna Nováková", "anna@example.com"),
        RegistraceVstupu("Bob Svoboda", "bob@example.com"),
        RegistraceVstupu("Cyril Dvořák", "cyril@example.com"),
    ]
    vystupy = []
    for data in uzivatele_data:
        vystup = registrace_uc.execute(data)
        vystupy.append(vystup)
        print(f"  Registrován: {vystup.jmeno} (id={vystup.id})")

    print("\n--- Pokus o duplicitní e-mail ---")
    try:
        registrace_uc.execute(RegistraceVstupu("Anna2", "anna@example.com"))
    except ValueError as exc:
        print(f"  Chyba (správně): {exc}")

    print("\n--- Vyhledání uživatele ---")
    uzivatel = najdi_uc.execute(2)
    print(f"  Nalezen: {uzivatel.jmeno} <{uzivatel.email}>")

    print("\n--- Pokus o neexistujícího uživatele ---")
    try:
        najdi_uc.execute(999)
    except KeyError as exc:
        print(f"  Chyba (správně): {exc}")

    print("\n--- Změna e-mailu (doménová logika) ---")
    uzivatel.zmen_email("bob.novy@example.com")
    repo.uloz(uzivatel)
    overeni = najdi_uc.execute(2)
    print(f"  Nový e-mail: {overeni.email}")

    print("\n--- Přehled: závislosti tečou dovnitř ---")
    print("  Infrastructure (LogujiciRepo, InMemoryRepo)")
    print("    └─> Application (RegistraceUC, NajdiUC, UzivatelRepository Protocol)")
    print("          └─> Domain (Uzivatel entita)")
    print("  Domain nezná nikoho. Application nezná Infrastructure.")


if __name__ == "__main__":
    main()
