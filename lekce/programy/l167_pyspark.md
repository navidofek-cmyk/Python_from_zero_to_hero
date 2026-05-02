# Program — Lekce 167: Lekce 167: PySpark — distribuovaná analytika

Patří k lekci [Lekce 167: PySpark — distribuovaná analytika](../167_pyspark.md).

## Jak spustit

```bash
python3 programy/l167_pyspark.py
```

## Zdrojový kód

### `l167_pyspark.py`

```py
"""Lekce 167 — PySpark: distribuovaná analytika.

Spuštění (vyžaduje Java):
    uv run --with pyspark l167_pyspark.py
"""

import time


def demo_bez_sparku():
    print("=" * 50)
    print("  ⚡ PySpark Architektura Demo")
    print("=" * 50)
    print("""
PySpark = Python API pro Apache Spark

Architektura:
  Driver (Python) → SparkContext → Worker 1
                                 → Worker 2
                                 → Worker N

RDD = Resilient Distributed Dataset
  - immutabilní kolekce partitionovaná přes cluster
  - lazy evaluation — transformace se neprovádí hned

DataFrame = RDD s pojmenovanými sloupci (jako SQL)
  - optimalizovaný Catalyst query planner
  - Tungsten execution engine

Klíčové koncepty:
  Transformation (lazy): map, filter, groupBy, join
  Action (triggers execution): count, collect, show, write

Kdy PySpark vs alternativy:
  < 1 GB   → pandas/Polars (rychlejší na jednom stroji)
  1-100 GB → DuckDB nebo Polars (lazy)
  > 100 GB → PySpark (cluster)
  Streaming → Spark Structured Streaming nebo Kafka
""")


try:
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    import warnings
    warnings.filterwarnings("ignore")

    def demo_spark():
        print("\n=== SparkSession ===")
        spark = (SparkSession.builder
                 .appName("KurzDemo")
                 .master("local[2]")
                 .config("spark.driver.memory", "1g")
                 .config("spark.sql.shuffle.partitions", "4")
                 .getOrCreate())
        spark.sparkContext.setLogLevel("ERROR")
        print(f"  Spark {spark.version} spuštěn")

        print("\n=== DataFrame operace ===")
        data = [
            (1,"Anna","IT",80000), (2,"Bob","Marketing",60000),
            (3,"Carol","IT",95000), (4,"Dan","HR",70000), (5,"Eva","IT",88000),
        ]
        df = spark.createDataFrame(data, ["id","jmeno","oddeleni","plat"])
        df.show()

        print("Filtrování a transformace:")
        (df.filter(F.col("plat") > 75000)
           .withColumn("bonus", F.col("plat") * 0.1)
           .select("jmeno", "plat", "bonus")
           .show())

        print("GroupBy:")
        (df.groupBy("oddeleni")
           .agg(F.count("*").alias("pocet"), F.avg("plat").alias("prumer"))
           .show())

        print("\n=== SQL ===")
        df.createOrReplaceTempView("zamestnanci")
        spark.sql("""
            SELECT oddeleni, COUNT(*) pocet, MAX(plat) max_plat
            FROM zamestnanci
            GROUP BY oddeleni
            ORDER BY max_plat DESC
        """).show()

        print("\n=== RDD Word Count ===")
        text_rdd = spark.sparkContext.parallelize([
            "python je skvely jazyk",
            "spark je distribuovany system",
            "python spark analytika",
        ])
        wc = (text_rdd.flatMap(lambda l: l.split())
                      .map(lambda w: (w, 1))
                      .reduceByKey(lambda a, b: a+b)
                      .sortBy(lambda x: x[1], ascending=False))
        print("  Word count:", wc.collect())

        spark.stop()
        print("\n✅ Spark demo dokončeno!")

    demo_spark()

except ImportError:
    print("\nPySpark není dostupný.")
    print("Instalace: uv add pyspark  (vyžaduje Java 8/11/17)")


def main():
    demo_bez_sparku()


if __name__ == "__main__":
    main()

```
