# Lekce 167: PySpark — distribuovaná analytika

Apache Spark zpracovává data na clusteru tisíců strojů. PySpark = Python API pro Spark. Pro data větší než RAM jednoho stroje.

---

## 🚀 Instalace

```bash
uv add pyspark
# Java 8/11/17 musí být nainstalována
```

---

## 🔌 SparkSession

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *
import warnings
warnings.filterwarnings("ignore")


def vytvor_spark(app_name: str = "PythonKurz", cores: int = 4) -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .master(f"local[{cores}]")           # lokálně na N jádrech
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


spark = vytvor_spark()
print(f"Spark verze: {spark.version}")
```

---

## 📊 DataFrame operace

```python
from datetime import date

# Vytvoření DataFrame
data = [
    (1, "Anna",  "IT",        80000, date(1994, 3, 15)),
    (2, "Bob",   "Marketing", 60000, date(1999, 7, 20)),
    (3, "Carol", "IT",        95000, date(1989, 1, 5)),
    (4, "Dan",   "HR",        70000, date(1996, 11, 30)),
    (5, "Eva",   "IT",        88000, date(1992, 5, 10)),
]

schema = StructType([
    StructField("id",        IntegerType(), False),
    StructField("jmeno",     StringType(),  False),
    StructField("oddeleni",  StringType(),  False),
    StructField("plat",      IntegerType(),  False),
    StructField("narozeniny",DateType(),    True),
])

df = spark.createDataFrame(data, schema)
df.show()
df.printSchema()

# Základní operace
df.select("jmeno", "plat").show()
df.filter(F.col("plat") > 75000).show()
df.orderBy(F.col("plat").desc()).show()

# Přidání sloupce
df2 = df.withColumn("vek", F.floor(F.months_between(F.current_date(), "narozeniny") / 12))
df2 = df2.withColumn("level", F.when(F.col("plat") > 85000, "senior").otherwise("junior"))
df2.show()
```

---

## 📈 Agregace

```python
# GroupBy
(df.groupBy("oddeleni")
   .agg(
       F.count("*").alias("pocet"),
       F.avg("plat").alias("prumer_plat"),
       F.max("plat").alias("max_plat"),
       F.min("plat").alias("min_plat"),
       F.sum("plat").alias("celkovy_plat"),
   )
   .orderBy("prumer_plat", ascending=False)
   .show())

# Window funkce
from pyspark.sql.window import Window

window = Window.partitionBy("oddeleni").orderBy(F.col("plat").desc())

df_rank = df.withColumn("rank", F.rank().over(window))
df_rank = df_rank.withColumn("cumsum", F.sum("plat").over(
    Window.partitionBy("oddeleni").orderBy("plat").rowsBetween(Window.unboundedPreceding, 0)
))
df_rank.show()
```

---

## 📁 I/O

```python
import tempfile, os

tmpdir = tempfile.mkdtemp()

# Zápis
df.write.parquet(f"{tmpdir}/zamestnanci.parquet", mode="overwrite")
df.write.csv(f"{tmpdir}/zamestnanci.csv", header=True, mode="overwrite")

# Čtení
df_parquet = spark.read.parquet(f"{tmpdir}/zamestnanci.parquet")
df_csv = spark.read.csv(f"{tmpdir}/zamestnanci.csv", header=True, inferSchema=True)

print(f"Parquet řádků: {df_parquet.count()}")

# Partitioning — klíčové pro výkon na velkých datech
df.write.partitionBy("oddeleni").parquet(f"{tmpdir}/partitioned/", mode="overwrite")
# Spark přečte jen relevantní partition při filtraci po oddeleni!
```

---

## 🔄 RDD — nízkoúrovňové API

```python
# RDD = Resilient Distributed Dataset
rdd = spark.sparkContext.parallelize(range(1, 1001), numSlices=8)

# Map-Reduce
soucet_ctvercu = (rdd
    .filter(lambda x: x % 2 == 0)        # jen sudá
    .map(lambda x: x**2)                   # na druhou
    .reduce(lambda a, b: a + b))           # suma

print(f"Součet čtverců sudých 1-1000: {soucet_ctvercu}")

# Word count — klasický Spark příklad
text_rdd = spark.sparkContext.parallelize([
    "python je skvěly jazyk",
    "spark je distribuovany system",
    "python spark analytika",
])

word_count = (text_rdd
    .flatMap(lambda line: line.split())
    .map(lambda word: (word, 1))
    .reduceByKey(lambda a, b: a + b)
    .sortBy(lambda x: x[1], ascending=False))

print("\nWord count:")
for slovo, pocet in word_count.collect():
    print(f"  {slovo}: {pocet}")
```

---

## ⚡ Spark SQL

```python
# Registruj jako SQL tabulku
df.createOrReplaceTempView("zamestnanci")

vysledek = spark.sql("""
    SELECT
        oddeleni,
        COUNT(*) as pocet,
        AVG(plat) as prumer_plat,
        SUM(plat) as celkovy_plat,
        MAX(plat) - MIN(plat) as rozptyl_platu
    FROM zamestnanci
    GROUP BY oddeleni
    ORDER BY prumer_plat DESC
""")
vysledek.show()

# Explain — ukaž fyzický plán
spark.sql("""
    SELECT * FROM zamestnanci
    WHERE plat > 75000
    ORDER BY plat DESC
""").explain(extended=False)
```

---

## 📊 MLlib — distribuované ML

```python
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.pipeline import Pipeline
from pyspark.ml.evaluation import BinaryClassificationEvaluator

# Přidej binární target
df_ml = df.withColumn("senior", (F.col("plat") > 80000).cast("integer"))

# Feature engineering
assembler = VectorAssembler(inputCols=["plat"], outputCol="features_raw")
scaler = StandardScaler(inputCol="features_raw", outputCol="features")
lr = LogisticRegression(featuresCol="features", labelCol="senior")

pipeline = Pipeline(stages=[assembler, scaler, lr])

train, test = df_ml.randomSplit([0.8, 0.2], seed=42)
model = pipeline.fit(train)
predictions = model.transform(test)
predictions.select("jmeno", "plat", "senior", "prediction", "probability").show()
```

---

## 🎯 Kdy PySpark

| Dataset | Nástroj |
|---------|---------|
| < 1 GB | pandas/Polars |
| 1–100 GB | Polars (lazy) nebo DuckDB |
| > 100 GB | PySpark |
| Streaming | Spark Structured Streaming |
| ML na velkých datech | Spark MLlib |

---

## ✏️ Cvičení

1. Stáhni NYC Taxi dataset (10GB+), analyzuj ho pomocí Spark — průměrné jízdné podle hodiny.
2. Implementuj **Spark Structured Streaming** — real-time processing Kafka zpráv.
3. Porovnej výkon: pandas vs DuckDB vs PySpark na 100M řádcích.
4. Napiš Spark job pro **ETL pipeline** — CSV → transformace → Parquet → SQL dotazy.
5. Trénuj Random Forest na 10M řádcích pomocí Spark MLlib.
