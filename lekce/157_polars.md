# Lekce 157: Polars — rychlejší pandas

Polars je DataFrame knihovna v Rustu — **5–50× rychlejší** než pandas, lazy evaluation, SIMD optimalizace, nulové kopírování.

---

## 🚀 Instalace

```bash
uv add polars
# S volitelnou podporou:
uv add "polars[numpy,pandas,xlsx2csv,connectorx]"
```

---

## 📊 Základy — Series a DataFrame

```python
import polars as pl
import numpy as np

# Series
s = pl.Series("hodnoty", [1, 2, 3, 4, 5])
print(s)
print(f"dtype: {s.dtype}, sum: {s.sum()}, mean: {s.mean()}")

# DataFrame
df = pl.DataFrame({
    "jmeno": ["Anna", "Bob", "Carol", "Dan", "Eva"],
    "vek": [30, 25, 35, 28, 32],
    "plat": [80000, 60000, 95000, 70000, 88000],
    "oddeleni": ["IT", "Marketing", "IT", "HR", "IT"],
    "aktivni": [True, True, True, False, True],
})
print(df)
print(df.dtypes)
```

---

## 🔍 Výběr a filtrování

```python
# Výběr sloupců
print(df.select(["jmeno", "plat"]))
print(df.select(pl.col("jmeno"), pl.col("plat") * 1.1))

# Filtrování
print(df.filter(pl.col("vek") > 28))
print(df.filter((pl.col("oddeleni") == "IT") & (pl.col("plat") > 75000)))

# Řazení
print(df.sort("plat", descending=True))
print(df.sort(["oddeleni", "plat"], descending=[False, True]))

# Head / tail / sample
print(df.head(3))
print(df.sample(3, seed=42))
```

---

## 🔄 Transformace

```python
# Přidání sloupce
df2 = df.with_columns([
    (pl.col("plat") * 1.15).alias("plat_po_pridavku"),
    pl.col("vek").cast(pl.Float32).alias("vek_float"),
    pl.when(pl.col("plat") > 80000).then("senior").otherwise("junior").alias("level"),
])
print(df2)

# Rename
df3 = df.rename({"jmeno": "name", "vek": "age"})

# Drop
df4 = df.drop(["aktivni"])

# Map / apply
df5 = df.with_columns(
    pl.col("jmeno").str.to_uppercase().alias("jmeno_velke"),
    pl.col("plat").map_elements(lambda x: f"{x:,} Kč", return_dtype=pl.Utf8).alias("plat_str"),
)
print(df5.select(["jmeno_velke", "plat_str"]))
```

---

## 📈 Agregace a GroupBy

```python
# GroupBy
skupiny = (
    df.group_by("oddeleni")
    .agg([
        pl.count().alias("pocet"),
        pl.col("plat").mean().alias("prumer_plat"),
        pl.col("plat").max().alias("max_plat"),
        pl.col("vek").mean().alias("prumer_vek"),
    ])
    .sort("prumer_plat", descending=True)
)
print("\nGrupBy oddělení:")
print(skupiny)

# GroupBy + transformace (jak window funkce)
df_s_rank = df.with_columns(
    pl.col("plat").rank(descending=True).over("oddeleni").alias("rank_v_oddeleni")
)
print("\nRank v oddělení:")
print(df_s_rank.sort(["oddeleni", "rank_v_oddeleni"]))
```

---

## ⚡ Lazy API — klíč k výkonu

```python
# Lazy = dotaz se nespustí dokud nezavoláš .collect()
# Polars optimalizuje celý dotaz najednou (predicate pushdown, projection pushdown)

lazy_dotaz = (
    pl.scan_csv("data.csv")   # čte jen co potřebuje
    .filter(pl.col("vek") > 25)
    .group_by("oddeleni")
    .agg(pl.col("plat").mean())
    .sort("plat", descending=True)
)
print("\nLazy dotaz (query plan):")
print(lazy_dotaz.explain())  # zobrazí plán bez spuštění

# Spuštění
# vysledek = lazy_dotaz.collect()

# Na DataFrame
lazy = df.lazy()
result = (
    lazy
    .filter(pl.col("aktivni"))
    .select(["jmeno", "plat", "oddeleni"])
    .with_columns(pl.col("plat").rank(descending=True).alias("rank"))
    .collect()
)
print("\nLazy výsledek:")
print(result)
```

---

## 🔗 Joins

```python
oddeleni_df = pl.DataFrame({
    "oddeleni": ["IT", "Marketing", "HR"],
    "vedouci": ["Karel", "Jana", "Petr"],
    "budget": [500000, 200000, 150000],
})

# Inner join
print("\nInner join:")
print(df.join(oddeleni_df, on="oddeleni", how="inner"))

# Left join
print("\nLeft join:")
print(df.join(oddeleni_df, on="oddeleni", how="left"))
```

---

## 🪟 Window funkce

```python
df_window = df.with_columns([
    pl.col("plat").mean().over("oddeleni").alias("prumer_oddeleni"),
    pl.col("plat").rank(descending=True).over("oddeleni").alias("rank"),
    (pl.col("plat") - pl.col("plat").mean().over("oddeleni")).alias("odchylka"),
])
print("\nWindow funkce:")
print(df_window)
```

---

## 📁 I/O — CSV, Parquet, JSON

```python
import tempfile, os

with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
    cesta_csv = f.name
with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
    cesta_parquet = f.name

# Zápis
df.write_csv(cesta_csv)
df.write_parquet(cesta_parquet)

# Čtení
df_csv = pl.read_csv(cesta_csv)
df_parquet = pl.read_parquet(cesta_parquet)
print(f"\nCSV načteno: {df_csv.shape}")
print(f"Parquet načteno: {df_parquet.shape}")

# Parquet je ~5× menší a ~10× rychlejší k načtení
import os
print(f"CSV velikost:     {os.path.getsize(cesta_csv):,} B")
print(f"Parquet velikost: {os.path.getsize(cesta_parquet):,} B")
os.unlink(cesta_csv); os.unlink(cesta_parquet)
```

---

## ⏱️ Srovnání výkonu: Polars vs pandas

```python
import time

n = 1_000_000
data = {
    "kategorie": np.random.choice(["A","B","C","D"], n),
    "hodnota": np.random.randn(n),
    "podkat": np.random.choice(["X","Y","Z"], n),
}

# pandas
import pandas as pd
df_pd = pd.DataFrame(data)
start = time.perf_counter()
_ = df_pd.groupby(["kategorie","podkat"])["hodnota"].agg(["mean","std","count"])
t_pd = time.perf_counter() - start

# Polars
df_pl = pl.DataFrame(data)
start = time.perf_counter()
_ = (df_pl.group_by(["kategorie","podkat"])
     .agg([pl.col("hodnota").mean(), pl.col("hodnota").std(), pl.col("hodnota").count()]))
t_pl = time.perf_counter() - start

print(f"\nSrovnání ({n:,} řádků, GroupBy):")
print(f"  pandas: {t_pd*1000:.0f}ms")
print(f"  Polars: {t_pl*1000:.0f}ms")
if t_pd > 0: print(f"  Zrychlení: {t_pd/t_pl:.1f}×")
```

---

## 🎯 Kdy Polars, kdy pandas

| | Polars | pandas |
|---|--------|--------|
| Rychlost | ✅ 5–50× rychlejší | baseline |
| Paměť | ✅ efektivnější | více kopií |
| Lazy eval | ✅ | ❌ |
| API zralost | roste | ✅ zavedené |
| Ekosystém | roste | ✅ bohatý |
| ML integrace | přes Arrow | ✅ přímá |
| Velká data | ✅ | omezené |

---

## ✏️ Cvičení

1. Načti Titanic CSV, spočítej přežití podle pohlaví a třídy — Polars vs pandas benchmark.
2. Implementuj **klouzavý průměr 7 dní** na časové řadě pomocí Polars window funkcí.
3. Zpracuj 10M řádků CSV souboru přes Lazy API — porovnej spotřebu paměti s pandas.
4. Napiš `scan_parquet` dotaz s `predicate pushdown` — ověř v `.explain()`.
5. Konvertuj existující pandas pipeline na Polars — změř zrychlení.
