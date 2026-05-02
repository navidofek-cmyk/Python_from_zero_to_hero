# Lekce 138: DuckDB — analytická databáze

DuckDB je **embedded OLAP databáze** — běží přímo v procesu Pythonu (žádný server). Extrémně rychlá pro analytické dotazy nad velkými datasety. Ideální náhrada za pandas pro agregace.

---

## 🚀 Instalace

```bash
uv add duckdb

# Volitelně pro integraci s pandas/polars
uv add pandas pyarrow polars
```

---

## 🔌 Připojení

```python
import duckdb

# In-memory databáze (zmizí po ukončení)
con = duckdb.connect()

# Persistentní soubor
con = duckdb.connect("moje_data.duckdb")

# Context manager
with duckdb.connect("data.duckdb") as con:
    con.execute("SELECT 42").fetchone()

# Sdílené připojení (read-only přístup z více procesů)
con_ro = duckdb.connect("data.duckdb", read_only=True)
```

---

## 📊 Základní SQL

```python
import duckdb

con = duckdb.connect()

# Vytvoření tabulky
con.execute("""
    CREATE TABLE produkty (
        id INTEGER PRIMARY KEY,
        nazev VARCHAR,
        cena DECIMAL(10, 2),
        kategorie VARCHAR,
        prodano INTEGER
    )
""")

# Vkládání dat
con.execute("""
    INSERT INTO produkty VALUES
    (1, 'Laptop', 25000, 'Elektronika', 150),
    (2, 'Myš', 500, 'Elektronika', 800),
    (3, 'Stůl', 8000, 'Nábytek', 200),
    (4, 'Židle', 5000, 'Nábytek', 350),
    (5, 'Monitor', 12000, 'Elektronika', 400)
""")

# Dotaz
vysledky = con.execute("""
    SELECT kategorie,
           COUNT(*) as pocet,
           SUM(cena * prodano) as trzby,
           AVG(cena) as prumerna_cena
    FROM produkty
    GROUP BY kategorie
    ORDER BY trzby DESC
""").fetchall()

for radek in vysledky:
    print(radek)
```

---

## 🐼 Integrace s pandas

```python
import duckdb
import pandas as pd

con = duckdb.connect()

# DataFrame přímo jako tabulka v SQL!
df = pd.DataFrame({
    "jmeno": ["Anna", "Bob", "Carol", "Dan"],
    "vek": [30, 25, 35, 28],
    "plat": [80000, 60000, 95000, 70000],
    "oddeleni": ["IT", "Marketing", "IT", "HR"]
})

# DuckDB vidí df jako tabulku — bez kopírování dat
vysledek = con.execute("""
    SELECT oddeleni,
           COUNT(*) as pocet,
           AVG(plat) as prumer_plat,
           MAX(plat) as max_plat
    FROM df
    GROUP BY oddeleni
    ORDER BY prumer_plat DESC
""").df()   # vrátí DataFrame!

print(vysledek)

# Výsledek zpět do DataFrame
df_filtr = con.execute("SELECT * FROM df WHERE vek > 27").df()
```

---

## 📁 Přímé dotazy nad soubory

```python
# CSV soubor — bez načtení do paměti!
con.execute("""
    SELECT * FROM 'data/*.csv'
    WHERE vek > 18
    LIMIT 100
""").df()

# Parquet soubor (velmi rychlé)
con.execute("SELECT COUNT(*) FROM 'velky_dataset.parquet'").fetchone()

# JSON soubor
con.execute("SELECT * FROM 'data.json'").df()

# Více souborů najednou (glob)
con.execute("SELECT * FROM 'log_2024_*.parquet'").df()

# Vzdálené soubory (S3, HTTP)
con.execute("""
    SELECT * FROM 'https://example.com/data.parquet'
    LIMIT 10
""").df()
```

---

## 🚀 Window funkce

```python
con.execute("""
    SELECT
        jmeno,
        oddeleni,
        plat,
        AVG(plat) OVER (PARTITION BY oddeleni) as prumer_oddeleni,
        RANK() OVER (PARTITION BY oddeleni ORDER BY plat DESC) as poradi,
        LAG(plat, 1) OVER (ORDER BY plat) as predchozi_plat,
        SUM(plat) OVER (ORDER BY plat ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as kumulativni
    FROM df
    ORDER BY oddeleni, poradi
""").df()
```

---

## 📈 Pokročilá analytika

```python
import duckdb
import pandas as pd
import numpy as np

con = duckdb.connect()

# Generuj časovou řadu
df_casova = pd.DataFrame({
    "datum": pd.date_range("2024-01-01", periods=365, freq="D"),
    "trzby": np.random.normal(10000, 2000, 365).clip(0),
    "naklady": np.random.normal(7000, 1500, 365).clip(0),
})

# Měsíční agregace s klouzavým průměrem
vysledek = con.execute("""
    SELECT
        DATE_TRUNC('month', datum) as mesic,
        SUM(trzby) as mesicni_trzby,
        SUM(naklady) as mesicni_naklady,
        SUM(trzby) - SUM(naklady) as zisk,
        AVG(SUM(trzby)) OVER (
            ORDER BY DATE_TRUNC('month', datum)
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) as klouzavy_prumer_3m
    FROM df_casova
    GROUP BY DATE_TRUNC('month', datum)
    ORDER BY mesic
""").df()

print(vysledek)
```

---

## 🔄 DuckDB vs pandas

```python
import time
import duckdb
import pandas as pd
import numpy as np

# Vygeneruj velký dataset
n = 5_000_000
df = pd.DataFrame({
    "kategorie": np.random.choice(["A", "B", "C", "D"], n),
    "hodnota": np.random.randn(n),
    "datum": pd.date_range("2020-01-01", periods=n, freq="s"),
})

# pandas
start = time.perf_counter()
vysledek_pandas = df.groupby("kategorie")["hodnota"].agg(["mean", "std", "count"])
cas_pandas = time.perf_counter() - start

# DuckDB
con = duckdb.connect()
start = time.perf_counter()
vysledek_duck = con.execute("""
    SELECT kategorie,
           AVG(hodnota) as mean,
           STDDEV(hodnota) as std,
           COUNT(*) as count
    FROM df
    GROUP BY kategorie
""").df()
cas_duck = time.perf_counter() - start

print(f"pandas: {cas_pandas:.3f}s")
print(f"DuckDB: {cas_duck:.3f}s")
print(f"DuckDB je {cas_pandas/cas_duck:.1f}× rychlejší")
```

---

## 🔗 Integrace s Polars

```python
import duckdb
import polars as pl

# Polars DataFrame → DuckDB
df_pl = pl.DataFrame({
    "a": [1, 2, 3],
    "b": ["x", "y", "z"]
})

con = duckdb.connect()
vysledek = con.execute("SELECT * FROM df_pl WHERE a > 1").pl()  # vrátí Polars DataFrame
```

---

## 🏗️ Typy a funkce

```python
# DuckDB má bohaté typy
con.execute("""
    CREATE TABLE udalosti (
        id INTEGER,
        cas TIMESTAMPTZ,
        metadata JSON,
        pole INTEGER[],
        lokace STRUCT(lat DOUBLE, lon DOUBLE)
    )
""")

# JSON funkce
con.execute("""
    SELECT json_extract('{"a": {"b": 1}}', '$.a.b')
""").fetchone()

# Array funkce
con.execute("SELECT list_sum([1, 2, 3, 4, 5])").fetchone()  # 15
con.execute("SELECT list_sort([3, 1, 4, 1, 5])").fetchone()

# String funkce
con.execute("SELECT regexp_extract('hello world 123', '\\d+')").fetchone()
```

---

## 📤 Export dat

```python
# Do CSV
con.execute("COPY produkty TO 'export.csv' (HEADER, DELIMITER ',')")

# Do Parquet (komprimovaný, velmi rychlý)
con.execute("COPY produkty TO 'export.parquet' (FORMAT PARQUET)")

# Do JSON
con.execute("COPY (SELECT * FROM produkty) TO 'export.json'")

# Zpět do pandas
df = con.execute("SELECT * FROM produkty").df()

# Zpět do seznam slovníků
radky = con.execute("SELECT * FROM produkty").fetchdf().to_dict("records")
```

---

## 🎯 Kdy použít DuckDB

| Případ | DuckDB | pandas | PostgreSQL |
|--------|--------|--------|-----------|
| Analytika na lokálních datech | ✅ nejlepší | ✅ | ❌ overkill |
| Data větší než RAM | ✅ streaming | ❌ | ✅ |
| Dotazy nad CSV/Parquet | ✅ přímé | nutno načíst | nutno importovat |
| OLTP (transakce) | ❌ | ❌ | ✅ |
| Sdílená DB (více uživatelů) | ❌ | ❌ | ✅ |
| Window funkce | ✅ | složitější | ✅ |
| Rychlost agregací | ✅ | pomalejší | ✅ |

---

## ✏️ Cvičení

1. Stáhni CSV dataset (např. Titanic z Kaggle), načti ho přes DuckDB a spusť 5 analytických dotazů.
2. Porovnej výkon pandas vs DuckDB na datasetu 1M řádků — skupinová agregace.
3. Vytvoř časovou řadu prodejů a spočítej klouzavý průměr za 7 dní pomocí window funkce.
4. Načti více CSV souborů najednou přes glob (`*.csv`) a vytvoř souhrnný report.
5. Exportuj výsledek dotazu do Parquet a znovu ho načti — porovnej velikost s CSV.
