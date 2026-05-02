"""Lekce 157 — Polars: rychlá DataFrame knihovna.

Spuštění:
    uv run --with polars,numpy l157_polars.py
"""

import time
import numpy as np

try:
    import polars as pl
except ImportError:
    print("Nainstaluj: uv add polars")
    raise


def main():
    print("=" * 50)
    print("  🐻‍❄️ Polars Demo")
    print("=" * 50)

    df = pl.DataFrame({
        "jmeno": ["Anna","Bob","Carol","Dan","Eva","Frank","Grace"],
        "vek": [30,25,35,28,32,27,41],
        "plat": [80000,60000,95000,70000,88000,65000,110000],
        "oddeleni": ["IT","Marketing","IT","HR","IT","Marketing","IT"],
    })
    print("\n=== DataFrame ===")
    print(df)

    print("\n=== Filtrování + transformace ===")
    vysledek = (
        df
        .filter(pl.col("vek") > 27)
        .with_columns([
            (pl.col("plat") * 1.1).alias("plat_s_bonusem"),
            pl.when(pl.col("plat") > 80000).then("senior").otherwise("junior").alias("level"),
        ])
        .sort("plat", descending=True)
    )
    print(vysledek)

    print("\n=== GroupBy ===")
    skupiny = (
        df.group_by("oddeleni")
        .agg([
            pl.count().alias("pocet"),
            pl.col("plat").mean().alias("prumer_plat"),
            pl.col("plat").max().alias("max_plat"),
        ])
        .sort("prumer_plat", descending=True)
    )
    print(skupiny)

    print("\n=== Lazy API ===")
    lazy = (
        df.lazy()
        .filter(pl.col("oddeleni") == "IT")
        .with_columns(pl.col("plat").rank(descending=True).alias("rank"))
        .sort("rank")
    )
    print("Query plan:")
    print(lazy.explain())
    print("\nVýsledek:")
    print(lazy.collect())

    # Benchmark vs pandas
    print("\n=== Benchmark: Polars vs pandas ===")
    n = 500_000
    data = {
        "kat": np.random.choice(["A","B","C","D"], n),
        "val": np.random.randn(n),
    }

    try:
        import pandas as pd
        df_pd = pd.DataFrame(data)
        start = time.perf_counter()
        _ = df_pd.groupby("kat")["val"].agg(["mean","std","count"])
        t_pd = time.perf_counter()-start

        df_pl = pl.DataFrame(data)
        start = time.perf_counter()
        _ = df_pl.group_by("kat").agg([pl.col("val").mean(), pl.col("val").std(), pl.col("val").count()])
        t_pl = time.perf_counter()-start

        print(f"  pandas: {t_pd*1000:.1f}ms")
        print(f"  Polars: {t_pl*1000:.1f}ms")
        if t_pl > 0: print(f"  Zrychlení: {t_pd/t_pl:.1f}×")
    except ImportError:
        print("  pandas není nainstalovaný — přeskoč benchmark")

    print("\n✅ Demo dokončeno!")


if __name__ == "__main__":
    main()
