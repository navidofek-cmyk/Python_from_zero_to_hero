# Lekce 98: Datové analýzy — NumPy a pandas

## 🔢 NumPy — pole čísel

```bash
pip install numpy
```

```python
import numpy as np

a = np.array([1, 2, 3, 4, 5])
b = np.arange(10)              # 0..9
c = np.linspace(0, 1, 11)      # 0, 0.1, 0.2, ... 1.0
d = np.zeros((3, 3))           # matice 3x3 nul
e = np.random.rand(100)        # 100 náhodných

# Vektorizace
a * 2                           # [2, 4, 6, 8, 10]
a + 100                         # [101, 102, ...]
a > 3                           # [False, ..., True]
a.sum(), a.mean(), a.std()
a.reshape(5, 1)
```

**100× rychlejší** než pure Python pro velká pole.

---

## 📊 pandas — tabulky

```bash
pip install pandas
```

```python
import pandas as pd

# DataFrame ze slovníku
df = pd.DataFrame({
    "jmeno": ["Anna", "Bob", "Cyril"],
    "vek": [10, 11, 12],
    "skore": [85, 92, 78],
})

# Z CSV
df = pd.read_csv("data.csv")
df = pd.read_excel("data.xlsx")

# Filtrování
mladsi = df[df["vek"] < 12]

# Agregace
df.groupby("trida")["skore"].mean()

# Nový sloupec
df["skore_pct"] = df["skore"] / df["skore"].max() * 100

# Export
df.to_csv("vystup.csv", index=False)
df.to_parquet("data.parquet")
```

---

## 📈 matplotlib — grafy

```bash
pip install matplotlib
```

```python
import matplotlib.pyplot as plt

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.plot(x, y)
plt.xlabel("x")
plt.ylabel("sin(x)")
plt.title("Sinus")
plt.savefig("graf.png")
plt.show()
```

---

## 🚀 Polars (alternativa pandas)

`polars` je modernější, **rychlejší** alternativa pandas (Rust pod kapotou):

```python
import polars as pl

df = pl.read_csv("data.csv")
df.filter(pl.col("vek") < 12).group_by("trida").agg(pl.col("skore").mean())
```

V 2026 trend: pro nové projekty zvaž **Polars**.

---

## 🎯 Stack pro data

| Úloha | Knihovna |
|---|---|
| Pole čísel | NumPy |
| Tabulky | pandas / polars |
| Vizualizace | matplotlib, seaborn, plotly |
| ML | scikit-learn |
| Hluboké učení | PyTorch / JAX |
| Notebooks | Jupyter, marimo |

---

## ✏️ Cvičení

1. **NumPy:** Vyrob pole 1000 náhodných čísel, spočítej mean, std, max.
2. **Pandas:** Načti CSV, filtruj, sumarizuj.
3. **Plot:** Vykresli sinusovku.
4. **Polars:** Předělej pandas příklad do Polars, srovnej rychlost.
