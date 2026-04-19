"""Mini-projekt po sekci II: TODO list s ukládáním.

Procvičuje: list, dict, slovníkové klíče, slicing, sorted, JSON.

Spuštění:
    python3 todo.py
"""

import json
from pathlib import Path

DATABAZE = Path("ukoly.json")


def nacti() -> list[dict]:
    if not DATABAZE.exists():
        return []
    return json.loads(DATABAZE.read_text(encoding="utf-8"))


def uloz(ukoly: list[dict]) -> None:
    DATABAZE.write_text(
        json.dumps(ukoly, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def vypis(ukoly: list[dict]) -> None:
    if not ukoly:
        print("📭 Žádné úkoly! Užij si volno.")
        return

    serazene = sorted(ukoly, key=lambda u: (u["hotovo"], -u["priorita"]))
    print()
    for i, u in enumerate(serazene, 1):
        znak = "✅" if u["hotovo"] else "⬜"
        hvezdy = "⭐" * u["priorita"]
        print(f"  {i}. {znak} [{hvezdy:5s}] {u['text']}")
    print()


def pridej(ukoly: list[dict]) -> None:
    text = input("Co je třeba udělat? ").strip()
    if not text:
        print("⚠️  Prázdný úkol nepřidám.")
        return
    pri = input("Priorita 1–3 (Enter = 1): ").strip()
    priorita = int(pri) if pri.isdigit() and 1 <= int(pri) <= 3 else 1
    ukoly.append({"text": text, "hotovo": False, "priorita": priorita})
    print("➕ Přidáno.")


def hotovo(ukoly: list[dict]) -> None:
    vypis(ukoly)
    cislo = input("Číslo úkolu (od 1): ").strip()
    if not cislo.isdigit():
        return
    idx = int(cislo) - 1
    if 0 <= idx < len(ukoly):
        ukoly[idx]["hotovo"] = not ukoly[idx]["hotovo"]
        print("🎉 Změněno.")


def smaz(ukoly: list[dict]) -> None:
    vypis(ukoly)
    cislo = input("Smazat úkol číslo: ").strip()
    if cislo.isdigit():
        idx = int(cislo) - 1
        if 0 <= idx < len(ukoly):
            ukoly.pop(idx)
            print("🗑️  Smazáno.")


def main() -> None:
    ukoly = nacti()
    print("=" * 40)
    print("       📋 MŮJ TODO LIST")
    print("=" * 40)

    akce = {
        "v": ("Vypsat", vypis),
        "p": ("Přidat", pridej),
        "h": ("Hotovo/nehotovo", hotovo),
        "s": ("Smazat", smaz),
    }

    while True:
        print("\nMožnosti:")
        for k, (jmeno, _) in akce.items():
            print(f"  {k}) {jmeno}")
        print("  q) Konec")

        volba = input("Volba: ").strip().lower()
        if volba == "q":
            break
        if volba in akce:
            _, funkce = akce[volba]
            if funkce is vypis:
                funkce(ukoly)
            else:
                funkce(ukoly)
                uloz(ukoly)
        else:
            print("⚠️  Neznámá volba.")

    print("\nUloženo do", DATABAZE.absolute())


if __name__ == "__main__":
    main()
