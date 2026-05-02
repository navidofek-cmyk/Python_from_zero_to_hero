# Program — Lekce 138: Lekce 138: DuckDB — analytická databáze

Patří k lekci [Lekce 138: DuckDB — analytická databáze](../138_duckdb.md).

## Jak spustit

```bash
python3 programy/l138_duckdb.py
```

## Zdrojový kód

### `l138_duckdb.py`

```py
"""Lekce 138 — DuckDB: analytická databáze.

Spuštění:
    uv run --with duckdb,pandas,numpy l138_duckdb.py
"""

import time

try:
    import duckdb
    import pandas as pd
    import numpy as np
except ImportError:
    print("Nainstaluj: uv add duckdb pandas numpy")
    raise


def demo_zakladni():
    print("\n=== Základní SQL ===")
    con = duckdb.connect()

    con.execute("""
        CREATE TABLE produkty (
            id INTEGER,
            nazev VARCHAR,
            cena DECIMAL(10,2),
            kategorie VARCHAR,
            prodano INTEGER
        )
    """)

    con.execute("""
        INSERT INTO produkty VALUES
        (1, 'Laptop',   25000, 'Elektronika', 150),
        (2, 'Myš',        500, 'Elektronika', 800),
        (3, 'Stůl',      8000, 'Nábytek',     200),
        (4, 'Židle',     5000, 'Nábytek',     350),
        (5, 'Monitor',  12000, 'Elektronika', 400),
        (6, 'Skříň',    15000, 'Nábytek',     100),
        (7, 'Klávesnice', 800, 'Elektronika', 600)
    """)

    vysledek = con.execute("""
        SELECT kategorie,
               COUNT(*) as pocet_produktu,
               SUM(cena * prodano) as trzby,
               AVG(cena) as prumerna_cena
        FROM produkty
        GROUP BY kategorie
        ORDER BY trzby DESC
    """).df()

    print(vysledek.to_string(index=False))
    return con


def demo_pandas_integrace(con):
    print("\n=== Integrace s pandas ===")

    df = pd.DataFrame({
        "jmeno": ["Anna", "Bob", "Carol", "Dan", "Eva"],
        "vek": [30, 25, 35, 28, 32],
        "plat": [80000, 60000, 95000, 70000, 88000],
        "oddeleni": ["IT", "Marketing", "IT", "HR", "IT"]
    })

    # DuckDB vidí df přímo — bez kopírování
    vysledek = con.execute("""
        SELECT oddeleni,
               COUNT(*) as pocet,
               ROUND(AVG(plat), 0) as prumer_plat,
               MAX(plat) as max_plat,
               MIN(plat) as min_plat
        FROM df
        GROUP BY oddeleni
        ORDER BY prumer_plat DESC
    """).df()

    print("Statistiky platů:")
    print(vysledek.to_string(index=False))

    # Filtrování
    it_tym = con.execute("SELECT jmeno, plat FROM df WHERE oddeleni = 'IT' ORDER BY plat DESC").df()
    print(f"\nIT tým: {it_tym['jmeno'].tolist()}")


def demo_window_funkce(con):
    print("\n=== Window funkce ===")

    df_prodeje = pd.DataFrame({
        "mesic": range(1, 13),
        "trzby": [45000, 38000, 52000, 61000, 55000, 70000,
                  68000, 72000, 65000, 80000, 95000, 110000]
    })

    vysledek = con.execute("""
        SELECT
            mesic,
            trzby,
            ROUND(AVG(trzby) OVER (
                ORDER BY mesic
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ), 0) as klouzavy_prumer_3m,
            ROUND(trzby - LAG(trzby, 1) OVER (ORDER BY mesic), 0) as zmena,
            RANK() OVER (ORDER BY trzby DESC) as poradi
        FROM df_prodeje
        ORDER BY mesic
    """).df()

    print(vysledek.to_string(index=False))


def demo_rychlost():
    print("\n=== Srovnání rychlosti: pandas vs DuckDB ===")

    n = 1_000_000
    print(f"Dataset: {n:,} řádků")

    df = pd.DataFrame({
        "kategorie": np.random.choice(["A", "B", "C", "D"], n),
        "hodnota": np.random.randn(n),
        "podkategorie": np.random.choice(["X", "Y", "Z"], n),
    })

    # pandas
    start = time.perf_counter()
    _ = df.groupby(["kategorie", "podkategorie"])["hodnota"].agg(["mean", "std", "count"])
    cas_pandas = time.perf_counter() - start

    # DuckDB
    con = duckdb.connect()
    start = time.perf_counter()
    _ = con.execute("""
        SELECT kategorie, podkategorie,
               AVG(hodnota) as mean,
               STDDEV(hodnota) as std,
               COUNT(*) as count
        FROM df
        GROUP BY kategorie, podkategorie
    """).df()
    cas_duck = time.perf_counter() - start

    print(f"  pandas: {cas_pandas*1000:.0f}ms")
    print(f"  DuckDB: {cas_duck*1000:.0f}ms")
    if cas_duck > 0:
        print(f"  DuckDB je {cas_pandas/cas_duck:.1f}× rychlejší")


def demo_csv_dotaz():
    print("\n=== Přímé dotazy nad soubory ===")

    import tempfile, os

    # Vytvoř dočasné CSV
    df = pd.DataFrame({
        "jmeno": [f"Osoba_{i}" for i in range(100)],
        "vek": np.random.randint(18, 70, 100),
        "mesto": np.random.choice(["Praha", "Brno", "Ostrava"], 100),
    })

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        df.to_csv(f.name, index=False)
        cesta = f.name

    con = duckdb.connect()
    vysledek = con.execute(f"""
        SELECT mesto, COUNT(*) as pocet, ROUND(AVG(vek), 1) as prumer_vek
        FROM read_csv_auto('{cesta}')
        GROUP BY mesto
        ORDER BY pocet DESC
    """).df()

    print("Statistiky z CSV souboru:")
    print(vysledek.to_string(index=False))
    os.unlink(cesta)


def main():
    print("=" * 50)
    print("  🦆 DuckDB Demo")
    print("=" * 50)

    con = demo_zakladni()
    demo_pandas_integrace(con)
    demo_window_funkce(con)
    demo_csv_dotaz()
    demo_rychlost()

    print("\n✅ Demo dokončeno!")


if __name__ == "__main__":
    main()

```
