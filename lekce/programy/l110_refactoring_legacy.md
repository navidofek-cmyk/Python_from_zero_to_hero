# Program — Lekce 110: Lekce 110: Refactoring legacy Pythonu

Patří k lekci [Lekce 110: Refactoring legacy Pythonu](../110_refactoring_legacy.md).

## Jak spustit

```bash
python3 programy/l110_refactoring_legacy.py
```

## Zdrojový kód

### `l110_refactoring_legacy.py`

```py
"""Lekce 110 — Refactoring legacy Pythonu: Strangler Fig, charakterizační testy, typizace."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, cast

if TYPE_CHECKING:
    pass  # sem by šly cyklické importy jen pro mypy


# ── Legacy kód (před refactoringem) ──────────────────────────────────────────

def vypocti_cenu_legacy(data, config):
    """
    LEGACY funkce — bez typů, bez testů, špatně čitelná.
    Nesmíme změnit chování, dokud nemáme charakterizační testy!
    """
    if not data:
        return 0
    cena = data.get("cena", 0)
    mnozstvi = data.get("mnozstvi", 1)
    kategorie = data.get("kategorie", "")
    sleva = config.get("sleva", 0) if config else 0

    # Tajemná logika bez dokumentace
    if kategorie == "PREMIUM":
        cena = cena * 1.15
    elif kategorie == "SALE":
        cena = cena * 0.8
    if mnozstvi >= 10:
        sleva = max(sleva, 5)
    if mnozstvi >= 100:
        sleva = max(sleva, 15)

    vysledek = cena * mnozstvi * (1 - sleva / 100)
    return round(vysledek, 2)


class LegacyObjednavkaService:
    """
    LEGACY třída — přibité závislosti, nečitelná, netestovatelná.
    """

    def __init__(self):
        # Závislost přibita natvrdo — v testech nelze nahradit
        self._db: dict[int, dict] = {}   # simulace DB
        self._seq = 0
        self._log_cesta = "/tmp/legacy.log"  # soubor přibit natvrdo

    def vytvor_objednavku(self, zakaznik_id, polozky):
        if not polozky:
            return None
        self._seq += 1
        celkem = sum(p["cena"] * p["mnozstvi"] for p in polozky)
        objednavka = {
            "id": self._seq,
            "zakaznik_id": zakaznik_id,
            "polozky": polozky,
            "celkem": celkem,
        }
        self._db[self._seq] = objednavka
        # self._zapis_log(f"Vytvořena objednávka {self._seq}")  # zakomentováno pro demo
        return self._seq

    def najdi(self, id):
        return self._db.get(id)


# ── Fáze 1: Charakterizační testy ────────────────────────────────────────────

def spust_charakterizacni_testy() -> None:
    """
    Zachycuje AKTUÁLNÍ chování legacy kódu.
    Testy říkají "co kód dělá", ne "co by měl dělat".
    Chrání nás při refactoringu — výsledky musí zůstat stejné.
    """
    # Zachycené vstupy a výstupy (golden master)
    testovane_pripady = [
        # (popis, vstup, config, ocekavany_vysledek)
        ("Základní cena",          {"cena": 100.0, "mnozstvi": 1, "kategorie": ""},        {},              100.0),
        ("Premium kategorie",      {"cena": 100.0, "mnozstvi": 1, "kategorie": "PREMIUM"}, {},              115.0),
        ("SALE kategorie",         {"cena": 100.0, "mnozstvi": 1, "kategorie": "SALE"},    {},               80.0),
        ("Hromadná sleva ≥10",     {"cena": 100.0, "mnozstvi": 10, "kategorie": ""},       {},              950.0),
        ("Hromadná sleva ≥100",    {"cena": 100.0, "mnozstvi": 100, "kategorie": ""},      {},            8500.0),
        ("Config sleva",           {"cena": 100.0, "mnozstvi": 5, "kategorie": ""},        {"sleva": 20},   400.0),
        ("Prázdný vstup",          {},                                                      {},                  0),
    ]

    print("  Charakterizační testy:")
    vse_ok = True
    for popis, vstup, config, ocekavano in testovane_pripady:
        vysledek = vypocti_cenu_legacy(vstup, config)
        ok = vysledek == ocekavano
        if not ok:
            vse_ok = False
        status = "✓" if ok else "✗"
        print(f"    {status} {popis:30s} → {vysledek} (očekáváno: {ocekavano})")

    print(f"  Výsledek: {'VŠECHNY PROŠLY' if vse_ok else 'SELHÁNÍ — nesmíme refaktorovat!'}")


# ── Fáze 2: Postupná typizace ─────────────────────────────────────────────────

# Fáze 2a: Any — alespoň mypy vidí parametry
def vypocti_cenu_typed_v1(data: Any, config: Any) -> Any:
    """Přechod fáze 1 — Any, ale alespoň mypy ví o parametrech."""
    return vypocti_cenu_legacy(data, config)


# Fáze 2b: Konkrétní dict typy
def vypocti_cenu_typed_v2(
    data: dict[str, Any],
    config: dict[str, float],
) -> float:
    """Přechod fáze 2 — konkrétní typy."""
    return float(vypocti_cenu_legacy(data, config))


# Fáze 2c: Vlastní dataclasses — nejčistší
@dataclass(frozen=True)
class VstupCeny:
    cena: float
    mnozstvi: int
    kategorie: str = ""


@dataclass(frozen=True)
class KonfiguraceCen:
    sleva: float = 0.0


def vypocti_cenu(vstup: VstupCeny, config: KonfiguraceCen = KonfiguraceCen()) -> float:
    """
    NOVÁ, čistá funkce — plně typovaná, testovatelná, dokumentovaná.
    Chování identické s legacy (ověřeno charakterizačními testy).
    """
    cena = vstup.cena
    sleva = config.sleva

    # Cenová kategorie
    if vstup.kategorie == "PREMIUM":
        cena *= 1.15
    elif vstup.kategorie == "SALE":
        cena *= 0.8

    # Hromadné slevy
    if vstup.mnozstvi >= 100:
        sleva = max(sleva, 15.0)
    elif vstup.mnozstvi >= 10:
        sleva = max(sleva, 5.0)

    return round(cena * vstup.mnozstvi * (1 - sleva / 100), 2)


# ── Fáze 3: Dependency Injection ─────────────────────────────────────────────

class ObjednavkaDatabase(Protocol):
    """PORT — definuje co DB musí umět."""
    def uloz(self, objednavka: dict[str, Any]) -> int: ...
    def najdi(self, id: int) -> dict[str, Any] | None: ...


class Logger(Protocol):
    """PORT pro logování."""
    def log(self, zprava: str) -> None: ...


@dataclass
class Objednavka:
    id: int
    zakaznik_id: int
    polozky: list[dict[str, Any]]
    celkem: float


class ObjednavkaService:
    """
    REFACTORED třída — závislosti injectované, testovatelná, typovaná.
    """

    def __init__(self, db: ObjednavkaDatabase, logger: Logger) -> None:
        self._db = db
        self._logger = logger

    def vytvor_objednavku(
        self,
        zakaznik_id: int,
        polozky: list[dict[str, Any]],
    ) -> Objednavka | None:
        if not polozky:
            self._logger.log("Pokus o vytvoření prázdné objednávky")
            return None

        celkem = sum(
            float(p["cena"]) * int(p["mnozstvi"])
            for p in polozky
        )
        zaznam: dict[str, Any] = {
            "zakaznik_id": zakaznik_id,
            "polozky": polozky,
            "celkem": celkem,
        }
        objednavka_id = self._db.uloz(zaznam)
        self._logger.log(f"Vytvořena objednávka id={objednavka_id}, celkem={celkem:.2f} Kč")

        return Objednavka(
            id=objednavka_id,
            zakaznik_id=zakaznik_id,
            polozky=polozky,
            celkem=celkem,
        )

    def najdi(self, id: int) -> Objednavka | None:
        zaznam = self._db.najdi(id)
        if zaznam is None:
            return None
        return Objednavka(
            id=cast(int, zaznam["id"]),
            zakaznik_id=cast(int, zaznam["zakaznik_id"]),
            polozky=cast(list[dict[str, Any]], zaznam["polozky"]),
            celkem=cast(float, zaznam["celkem"]),
        )


# Testovací adaptéry (Fake implementace)
class FakeDatabase:
    def __init__(self) -> None:
        self._store: dict[int, dict[str, Any]] = {}
        self._seq = 0

    def uloz(self, objednavka: dict[str, Any]) -> int:
        self._seq += 1
        zaznam = {**objednavka, "id": self._seq}
        self._store[self._seq] = zaznam
        return self._seq

    def najdi(self, id: int) -> dict[str, Any] | None:
        return self._store.get(id)


class FakeLogger:
    def __init__(self) -> None:
        self.zaznamy: list[str] = []

    def log(self, zprava: str) -> None:
        self.zaznamy.append(zprava)
        print(f"  [LOG] {zprava}")


# ── Strangler Fig pattern ─────────────────────────────────────────────────────

class StranglerProxy:
    """
    Přepíná mezi legacy a novým kódem.
    V produkci: feature flag z konfigurace, postupně zvyšuj %.
    """

    def __init__(
        self,
        legacy: LegacyObjednavkaService,
        novy: ObjednavkaService,
        pouzit_novy: bool = False,
    ) -> None:
        self._legacy = legacy
        self._novy = novy
        self._pouzit_novy = pouzit_novy
        self._prepnuti: list[str] = []

    def vytvor_objednavku(
        self,
        zakaznik_id: int,
        polozky: list[dict[str, Any]],
    ) -> Any:
        impl = "NOVÝ" if self._pouzit_novy else "LEGACY"
        self._prepnuti.append(impl)
        print(f"  [Strangler] Použita implementace: {impl}")

        if self._pouzit_novy:
            return self._novy.vytvor_objednavku(zakaznik_id, polozky)
        else:
            return self._legacy.vytvor_objednavku(zakaznik_id, polozky)

    def prepni_na_novy(self) -> None:
        self._pouzit_novy = True
        print("  [Strangler] Přepnuto na novou implementaci")

    def statistiky(self) -> dict[str, int]:
        from collections import Counter
        return dict(Counter(self._prepnuti))


# ── Demo ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=== Refactoring legacy Pythonu demo ===\n")

    print("--- 1. Charakterizační testy (Golden Master) ---")
    spust_charakterizacni_testy()

    print("\n--- 2. Ověření nové funkce vs. legacy ---")
    testovane_pripady = [
        ({"cena": 100.0, "mnozstvi": 1,   "kategorie": "PREMIUM"}, {}),
        ({"cena": 100.0, "mnozstvi": 10,  "kategorie": ""},        {}),
        ({"cena": 100.0, "mnozstvi": 100, "kategorie": "SALE"},    {"sleva": 10}),
    ]
    vse_ok = True
    for data, config in testovane_pripady:
        legacy_vysledek = vypocti_cenu_legacy(data, config)
        novy_vstup = VstupCeny(
            cena=data["cena"],
            mnozstvi=data["mnozstvi"],
            kategorie=data.get("kategorie", ""),
        )
        novy_config = KonfiguraceCen(sleva=float(config.get("sleva", 0)))
        novy_vysledek = vypocti_cenu(novy_vstup, novy_config)
        shoda = legacy_vysledek == novy_vysledek
        if not shoda:
            vse_ok = False
        print(f"  {'✓' if shoda else '✗'} legacy={legacy_vysledek} nový={novy_vysledek} {data}")
    print(f"  Chování identické: {'ANO' if vse_ok else 'NE — nutno opravit!'}")

    print("\n--- 3. Dependency Injection — testování bez DB ---")
    fake_db = FakeDatabase()
    fake_log = FakeLogger()
    service = ObjednavkaService(fake_db, fake_log)

    obj = service.vytvor_objednavku(
        zakaznik_id=42,
        polozky=[
            {"nazev": "Notebook", "cena": 25000.0, "mnozstvi": 1},
            {"nazev": "Myš",      "cena": 500.0,   "mnozstvi": 2},
        ],
    )
    if obj:
        print(f"  Objednávka vytvořena: id={obj.id}, celkem={obj.celkem:.2f} Kč")

    nalezena = service.najdi(1)
    print(f"  Nalezena: id={nalezena.id if nalezena else None}")

    empty = service.vytvor_objednavku(42, [])
    print(f"  Prázdné položky: {empty}")
    print(f"  Log záznamy: {len(fake_log.zaznamy)}")

    print("\n--- 4. Strangler Fig pattern ---")
    legacy_svc = LegacyObjednavkaService()
    novy_svc = ObjednavkaService(FakeDatabase(), FakeLogger())
    proxy = StranglerProxy(legacy_svc, novy_svc, pouzit_novy=False)

    polozky = [{"nazev": "Produkt", "cena": 100.0, "mnozstvi": 1}]

    # Fáze 1: používáme legacy
    proxy.vytvor_objednavku(1, polozky)
    proxy.vytvor_objednavku(2, polozky)

    # Fáze 2: přepneme na nový kód
    proxy.prepni_na_novy()
    proxy.vytvor_objednavku(3, polozky)
    proxy.vytvor_objednavku(4, polozky)

    print(f"  Statistiky přepnutí: {proxy.statistiky()}")

    print("\n--- 5. typing.cast a TYPE_CHECKING ---")
    # cast říká mypy "věř mi" — za běhu nic nedělá
    raw_data: object = {"klic": "hodnota"}
    typed_data = cast(dict[str, str], raw_data)  # mypy věří, runtime = noop
    print(f"  cast() výsledek (runtime = noop): {typed_data}")

    # TYPE_CHECKING — import jen pro mypy, ne za běhu
    print(f"  TYPE_CHECKING hodnota za běhu: {TYPE_CHECKING}  (vždy False)")

    print("\n--- Doporučený postup refactoringu ---")
    kroky = [
        "1. Napiš charakterizační testy (Golden Master)",
        "2. Přidej závislosti přes DI tam kde chybí",
        "3. Typizuj postupně: None → Any → dict → dataclass",
        "4. Extrahuj malé, testovatelné funkce/třídy",
        "5. Strangler Fig: nový kód vedle starého, feature flag",
        "6. Smaž legacy jakmile pokrytí = 100 %",
    ]
    for krok in kroky:
        print(f"  {krok}")


if __name__ == "__main__":
    main()

```
