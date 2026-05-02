# Projekt 1: Hádej číslo

Mini-projekt po **sekci I (Základy)**. Robot si vybere číslo 1–100, ty ho hádáš. Po každém pokusu ti řekne „víc" nebo „míň".

**Použité koncepty:** proměnné a typy (lekce 3–4), f-stringy (5), vstup/výstup (7), podmínky (8), smyčky `while`/`for…else` (9), typové hinty (10), `random.randint`.

## Jak spustit

```bash
python3 projekty/01_hadej_cislo/hra.py
```

## Zdrojový kód — `hra.py`

```python
"""Mini-projekt po sekci I: Hádej číslo.

Robot si vybere číslo 1–100, ty ho hádáš. Po každém pokusu ti řekne
"víc" nebo "míň". Spočítá tvoje pokusy a oznámí výsledek.

Spuštění:
    python3 hra.py
nebo:
    uv run hra.py
"""

import random


def hraj(min_cislo: int = 1, max_cislo: int = 100) -> int:
    """Odehraje jedno kolo hry, vrátí počet pokusů."""
    tajne = random.randint(min_cislo, max_cislo)
    pokusy = 0

    print(f"🎲 Myslím si číslo od {min_cislo} do {max_cislo}. Hádej!")

    while True:
        odpoved = input("Tvůj tip: ").strip()
        if not odpoved.isdigit():
            print("⚠️  Zadej celé číslo.")
            continue

        tip = int(odpoved)
        pokusy += 1

        if tip < tajne:
            print("📈 Víc!")
        elif tip > tajne:
            print("📉 Míň!")
        else:
            print(f"🎉 Trefa! Číslo bylo {tajne}. Pokusů: {pokusy}")
            return pokusy


def main() -> None:
    print("=" * 40)
    print("  🎯 HÁDEJ ČÍSLO 🎯")
    print("=" * 40)

    hodnoceni = {1: "🤯 Magie!", 5: "🌟 Skvělé!", 10: "👍 Dobré"}

    while True:
        pokusy = hraj()
        for max_p, hodnoceni_text in sorted(hodnoceni.items()):
            if pokusy <= max_p:
                print(hodnoceni_text)
                break
        else:
            print("😅 Trochu pomaleji, ale dobré!")

        znova = input("\nHrát znova? (a/n): ").strip().lower()
        if znova != "a":
            print("Zatím! 👋")
            break


if __name__ == "__main__":
    main()
```

## Jak ho rozšířit

1. Přidej **úrovně obtížnosti** (snadné 1–50, těžké 1–500).
2. Přidej **omezený počet pokusů** — když ho překročíš, prohraješ.
3. Po každé hře si **uloží rekord** do souboru `rekordy.txt`.
4. Zkus to **obrátit** — ty si myslíš číslo a robot hádá (binární vyhledávání).
