# Program — Lekce 101: Lekce 101: SOLID v Pythonu

Patří k lekci [Lekce 101: SOLID v Pythonu](../101_solid.md).

## Jak spustit

```bash
python3 programy/l101_solid.py
```

## Zdrojový kód

### `l101_solid.py`

```py
"""Lekce 101 — SOLID v Pythonu."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Protocol


# ── S: Single Responsibility ──────────────────────────────────────────────────

class Objednavka:
    def __init__(self):
        self._polozky: list[str] = []

    def pridej(self, polozka: str) -> None:
        self._polozky.append(polozka)

    def vypocti_cenu(self) -> float:
        return float(len(self._polozky) * 100)

    def __repr__(self):
        return f"Objednavka({self._polozky})"


class ObjednavkaRepo:
    def uloz(self, obj: Objednavka) -> None:
        print(f"[DB] uloženo: {obj}")


class EmailNotifikace:
    def posli_potvrzeni(self, obj: Objednavka) -> None:
        print(f"[EMAIL] potvrzení pro {obj}")


# ── O: Open/Closed ────────────────────────────────────────────────────────────

SlevaFn = Callable[[float], float]

vip_sleva:     SlevaFn = lambda c: c * 0.8
student_sleva: SlevaFn = lambda c: c * 0.9
bez_slevy:     SlevaFn = lambda c: c


def vypocti_cenu(cena: float, sleva: SlevaFn) -> float:
    return sleva(cena)


# ── L: Liskov Substitution ────────────────────────────────────────────────────

class Tvar(Protocol):
    def obsah(self) -> float: ...


class Obdelnik:
    def __init__(self, w: float, h: float):
        self.w, self.h = w, h

    def obsah(self) -> float:
        return self.w * self.h


class Ctverec:
    def __init__(self, strana: float):
        self.strana = strana

    def obsah(self) -> float:
        return self.strana ** 2


def vytiskni_obsah(tvar: Tvar) -> None:
    print(f"  obsah = {tvar.obsah():.1f}")


# ── I: Interface Segregation ──────────────────────────────────────────────────

class Pracujici(Protocol):
    def pracuj(self) -> None: ...


class Zivi(Protocol):
    def jez(self) -> None: ...


class Robot:
    def pracuj(self) -> None:
        print("  Robot: pracuji")


class Clovek:
    def pracuj(self) -> None:
        print("  Člověk: pracuji")

    def jez(self) -> None:
        print("  Člověk: jím")


# ── D: Dependency Inversion ───────────────────────────────────────────────────

class UzivatelRepo(Protocol):
    def najdi(self, id: int) -> dict: ...
    def uloz(self, uzivatel: dict) -> None: ...


class InMemoryRepo:
    def __init__(self):
        self._data: dict[int, dict] = {}

    def najdi(self, id: int) -> dict:
        return self._data.get(id, {})

    def uloz(self, uzivatel: dict) -> None:
        self._data[uzivatel["id"]] = uzivatel
        print(f"  [InMemory] uložen: {uzivatel}")


class UzivatelService:
    def __init__(self, repo: UzivatelRepo):
        self.repo = repo

    def registruj(self, id: int, jmeno: str) -> None:
        self.repo.uloz({"id": id, "jmeno": jmeno})

    def najdi(self, id: int) -> dict:
        return self.repo.najdi(id)


# ── Demo ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=== S: Single Responsibility ===")
    obj = Objednavka()
    obj.pridej("kniha")
    obj.pridej("tužka")
    ObjednavkaRepo().uloz(obj)
    EmailNotifikace().posli_potvrzeni(obj)

    print("\n=== O: Open/Closed ===")
    cena = 1000.0
    for nazev, sleva in [("VIP", vip_sleva), ("student", student_sleva), ("bez", bez_slevy)]:
        print(f"  {nazev}: {vypocti_cenu(cena, sleva):.0f} Kč")

    print("\n=== L: Liskov Substitution ===")
    tvary: list[Tvar] = [Obdelnik(4, 5), Ctverec(3)]
    for t in tvary:
        vytiskni_obsah(t)

    print("\n=== I: Interface Segregation ===")
    for pracovnik in [Robot(), Clovek()]:
        pracovnik.pracuj()

    print("\n=== D: Dependency Inversion ===")
    service = UzivatelService(InMemoryRepo())
    service.registruj(1, "Anna")
    print(f"  nalezen: {service.najdi(1)}")
    print(f"  neexistuje: {service.najdi(99)}")


if __name__ == "__main__":
    main()

```
