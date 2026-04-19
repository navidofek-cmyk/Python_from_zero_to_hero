# Projekt 1: Hádej číslo 🎯

Mini-projekt po **sekci I (Základy)**. Použité koncepty:

- proměnné, typy (lekce 3, 4)
- f-stringy (lekce 5)
- vstup/výstup (lekce 7)
- podmínky `if/elif/else` (lekce 8)
- smyčky `while`, `for...else` (lekce 9)
- typové hinty, docstringy (lekce 10)
- náhoda — `random.randint`

## Jak spustit

```bash
python3 hra.py
# nebo
uv run hra.py
```

## Co se v něm naučíš

- Strukturovat malý program do funkcí
- Validovat vstup (`isdigit()`)
- Smyčka `while True` + `break`
- `for/else` pro hodnocení podle počtu pokusů
- Hrát si znova ve smyčce

## Jak ho rozšířit (cvičení)

1. Přidej **úrovně obtížnosti** (snadné 1–50, těžké 1–500).
2. Přidej **omezený počet pokusů** — když ho překročíš, prohraješ.
3. Po každé hře si **uloží rekord** do souboru `rekordy.txt`.
4. Zkus to **obrátit** — ty si myslíš číslo a robot hádá (binární vyhledávání).
