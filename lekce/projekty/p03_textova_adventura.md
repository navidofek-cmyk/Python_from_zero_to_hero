# Projekt 3: Textová adventura

Mini-projekt po **sekci III (Funkce)**. Prozkoumej les, jezero, louku a jeskyni. Sebere předměty a otevři truhlu zlatým klíčem.

**Použité koncepty:** funkce (21–22), dekorátory (26), closure (25), `functools.wraps` (27), dispatch slovník.

## Jak spustit

```bash
python3 projekty/03_textova_adventura/adventura.py
```

Příkazy: `rozhled`, `jdi <smer>`, `vezmi <předmět>`, `inv`, `konec`.

## Zdrojový kód — `adventura.py`

```python
"""Mini-projekt po sekci III: Textová adventura.

Procvičuje: funkce, *args/**kwargs, closure, dekorátory, dataclass-like
slovníky, dispatch.
"""

import random
from functools import wraps


def loguj_akci(funkce):
    @wraps(funkce)
    def obalka(stav, *args, **kwargs):
        print(f"\n📍 [{funkce.__name__.upper()}]")
        return funkce(stav, *args, **kwargs)
    return obalka


@loguj_akci
def rozhled(stav: dict) -> None:
    mistnost = stav["mistnost"]
    print(MISTNOSTI[mistnost]["popis"])
    if predmety := MISTNOSTI[mistnost].get("predmety"):
        print(f"Vidíš tu: {', '.join(predmety)}")


@loguj_akci
def jdi(stav: dict, smer: str) -> None:
    sousede = MISTNOSTI[stav["mistnost"]].get("sousede", {})
    if smer in sousede:
        stav["mistnost"] = sousede[smer]
        print(f"🚶 Jdeš na {smer}.")
        rozhled(stav)
    else:
        print(f"⛔ Tudy ne ({smer}).")


@loguj_akci
def vezmi(stav: dict, predmet: str) -> None:
    predmety = MISTNOSTI[stav["mistnost"]].setdefault("predmety", [])
    if predmet in predmety:
        predmety.remove(predmet)
        stav["inventar"].append(predmet)
        print(f"🎒 Vzal jsi: {predmet}")
    else:
        print(f"❌ Tady žádný {predmet} není.")


@loguj_akci
def inventar(stav: dict) -> None:
    if not stav["inventar"]:
        print("🎒 Nic nemáš.")
    else:
        print(f"🎒 Máš: {', '.join(stav['inventar'])}")


MISTNOSTI = {
    "les": {
        "popis": "🌲 Stojíš v hustém lese. Zní tu ptáčci.",
        "sousede": {"sever": "jezero", "jih": "louka"},
        "predmety": ["klacek", "kámen"],
    },
    "louka": {
        "popis": "🌼 Krásná louka plná květin.",
        "sousede": {"sever": "les", "vychod": "jeskyne"},
        "predmety": ["květina"],
    },
    "jezero": {
        "popis": "💧 Modré jezero. Něco se v něm zatřpytilo.",
        "sousede": {"jih": "les"},
        "predmety": ["zlatý klíč"],
    },
    "jeskyne": {
        "popis": "🕳️ Tmavá jeskyně. Slyšíš funění.",
        "sousede": {"zapad": "louka"},
        "predmety": ["truhla"],
    },
}

PRIKAZY = {
    "rozhled": rozhled,
    "r": rozhled,
    "jdi": jdi,
    "vezmi": vezmi,
    "inv": inventar,
    "inventar": inventar,
}


def hraj() -> None:
    stav = {"mistnost": "les", "inventar": []}
    print("=" * 40)
    print("    🗡️  TEXTOVÁ ADVENTURA")
    print("=" * 40)
    print("Příkazy: rozhled, jdi <smer>, vezmi <předmět>, inv, konec")
    rozhled(stav)

    while True:
        akce = input("\n> ").strip().lower().split()
        if not akce:
            continue
        if akce[0] == "konec":
            print("👋 Konec dobrodružství.")
            break

        prikaz = PRIKAZY.get(akce[0])
        if prikaz is None:
            print(f"❓ Neznámý příkaz: {akce[0]}")
            continue
        try:
            prikaz(stav, *akce[1:])
        except TypeError:
            print(f"⚠️  Špatné argumenty pro {akce[0]}.")

        # Vítězství
        if "zlatý klíč" in stav["inventar"] and "truhla" in stav["inventar"]:
            print("\n🏆 VÍTĚZSTVÍ! Otevřel jsi truhlu zlatým klíčem!")
            break


if __name__ == "__main__":
    hraj()
```
