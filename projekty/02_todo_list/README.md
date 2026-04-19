# Projekt 2: TODO list s ukládáním 📋

Mini-projekt po **sekci II (Datové struktury)**.

## Co je v něm použito

- **list** úkolů (lekce 11)
- **dict** pro každý úkol s klíči `text`, `hotovo`, `priorita` (lekce 13)
- **sorted** s `key=lambda` na řazení podle stavu a priority (lekce 20)
- **enumerate** na číslování (lekce 20)
- **JSON** pro ukládání mezi spuštěními
- **pathlib** na práci se souborem

## Jak spustit

```bash
python3 todo.py
```

Úkoly se ukládají do `ukoly.json` ve stejné složce.

## Jak ho rozšířit

1. Přidej **kategorie** (práce, škola, doma) a filtrování podle nich.
2. **Termín** úkolu (datum) a řazení podle něj.
3. **Statistika**: kolik úkolů hotovo, kolik zbývá, % dokončení.
4. **Více seznamů** — uživatel si může mít víc todo listů.
5. **Export** do CSV, aby se to dalo otevřít v Excelu.
