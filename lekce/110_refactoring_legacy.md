# Lekce 110: Refactoring legacy Pythonu

## Co je legacy kód?

Legacy kód = kód **bez testů** (Michael Feathers). Může být starý nebo nový — klíčové je, že ho nejde bezpečně měnit.

```
Bez testů: změníš A → možná rozbije B, C, D. Nevíš.
S testy:   změníš A → testy okamžitě řeknou co se rozbilo.
```

---

## Strangler Fig Pattern

Postupná náhrada legacy systému novým — jako fíkovník dusitel (strangler fig) obalí a postupně nahradí starý strom.

```
Fáze 1: Starý systém funguje naplno
Fáze 2: Nový systém zachytí část požadavků (proxy)
Fáze 3: Nový systém zpracuje vše, starý odstraněn

             ┌──────────────┐
Požadavek →  │    Proxy     │ → Starý systém (část A, B)
             │  (strangler) │ → Nový systém  (část C — migrovaná)
             └──────────────┘
```

```python
class LegacyCenovyKalkulator:
    """Starý, netestovatelný kód."""
    def vypocti(self, produkt_id: int, mnozstvi: int) -> float:
        # 200 řádků spaghetti kódu...
        return 0.0

class NovyCenovyKalkulator:
    """Nový, testovatelný kód."""
    def vypocti(self, produkt_id: int, mnozstvi: int) -> float:
        # čistá implementace
        return 0.0

class StranglerProxy:
    """Přepíná mezi starým a novým kódem podle feature flagu."""
    def __init__(self, legacy, novy, pouzit_novy: bool = False):
        self._legacy = legacy
        self._novy = novy
        self._pouzit_novy = pouzit_novy

    def vypocti(self, produkt_id: int, mnozstvi: int) -> float:
        if self._pouzit_novy:
            return self._novy.vypocti(produkt_id, mnozstvi)
        return self._legacy.vypocti(produkt_id, mnozstvi)
```

---

## Charakterizační testy (Golden Master)

Před refactoringem zapiš chování stávajícího kódu do testů — ne zda je správné, ale **jaké je**. Testy pak ochrání refactoring.

```python
def test_legacy_kalkulator_charakterizacni():
    """Zachycuje aktuální (byť špatné) chování — nesmí se měnit."""
    kalk = LegacyCenovyKalkulator()
    # Toto je zachycené chování — neříkáme zda je správné
    assert kalk.vypocti(1, 1) == 99.0
    assert kalk.vypocti(1, 10) == 850.0    # hromadná sleva?
    assert kalk.vypocti(999, 1) == 0.0     # neznámý produkt
```

Technika: spusť starý kód s různými vstupy a zapiš výstupy jako testy.

---

## Postupná typizace

Přidávej typy postupně — nezlomí stávající kód, ale mypy postupně odhalí chyby.

```python
# Fáze 0: bez typů (legacy)
def zpracuj(data, config):
    return data["hodnota"] * config.get("nasobitel", 1)

# Fáze 1: Any — alespoň mypy zkontroluje strukturu
from typing import Any
def zpracuj(data: Any, config: Any) -> Any:
    return data["hodnota"] * config.get("nasobitel", 1)

# Fáze 2: konkrétní typy
def zpracuj(data: dict[str, float], config: dict[str, float]) -> float:
    return data["hodnota"] * config.get("nasobitel", 1.0)

# Fáze 3: vlastní typy / dataclasses
from dataclasses import dataclass

@dataclass
class VstupniData:
    hodnota: float

@dataclass
class Konfigurace:
    nasobitel: float = 1.0

def zpracuj(data: VstupniData, config: Konfigurace) -> float:
    return data.hodnota * config.nasobitel
```

---

## typing.cast a TYPE_CHECKING

```python
from typing import cast, TYPE_CHECKING

# TYPE_CHECKING — import jen pro mypy, ne za běhu (vyhne se cyklickým importům)
if TYPE_CHECKING:
    from .slozita_trida import SlozitaTrida

# cast — řekneme mypy "věř mi, tohle je daný typ" (bez efektu za běhu)
def nacti_data(raw: object) -> dict[str, str]:
    return cast(dict[str, str], raw)  # mypy věří, runtime nijak nekontroluje
```

---

## Dependency Injection pro testovatelnost

```python
# ❌ Legacy: přibité závislosti = netestovatelné
class ObjednavkaService:
    def __init__(self):
        self.db = MySQLDatabase("prod-server")   # nelze nahradit v testech

    def vytvor(self, data: dict):
        return self.db.insert("orders", data)

# ✅ Refactored: závislosti jako parametry
from typing import Protocol

class Database(Protocol):
    def insert(self, tabulka: str, data: dict) -> int: ...

class ObjednavkaService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def vytvor(self, data: dict) -> int:
        return self.db.insert("orders", data)

# Test bez DB:
class FakeDatabase:
    def __init__(self): self._data = []
    def insert(self, tabulka, data): self._data.append(data); return len(self._data)

service = ObjednavkaService(FakeDatabase())
```

---

## Postup refactoringu legacy kódu

1. **Charakterizační testy** — zapiš co kód dělá
2. **Izoluj závislosti** — přidej DI tam kde je to nutné pro testy
3. **Typizuj postupně** — začni s `Any`, zpřesňuj
4. **Extrahuj funkce/třídy** — malé, testovatelné jednotky
5. **Strangler Fig** — nový kód vedle starého, postupně přepínej
6. **Smaž legacy** — až když testy pokrývají 100 % cest

---

## Shrnutí

| Technika | Kdy | Nástroj |
|----------|-----|---------|
| Charakterizační testy | Před každou změnou | pytest + snapshot |
| Strangler Fig | Velký refactoring / migrace | Feature flag / proxy |
| Postupná typizace | Kontinuálně | mypy + TYPE_CHECKING |
| Dependency Injection | Netestovatelné závislosti | Protocol + parametr |
| `typing.cast` | Přechodné období | typing |

---

## Cvičení

1. Napiš charakterizační test pro funkci `vypocti_cenu_legacy` z demo souboru.
2. Refaktoruj ji do čisté funkce s type hints a testy.
3. Vytvoř `StranglerProxy` která loguje, kdy se přepíná mezi legacy a novým kódem.
4. Aplikuj DI na třídu která čte konfiguraci ze souboru — jak ji zpřístupnit pro testy?
