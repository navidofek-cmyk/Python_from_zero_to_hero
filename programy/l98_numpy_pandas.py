"""Lekce 98 — NumPy + pandas + matplotlib demo.

Vyžaduje:
    pip install numpy pandas matplotlib
"""

import time


def demo_numpy() -> None:
    import numpy as np
    arr = np.random.randn(1_000_000)
    print(f"NumPy 1M čísel:")
    print(f"  mean: {arr.mean():.4f}")
    print(f"  std:  {arr.std():.4f}")
    print(f"  max:  {arr.max():.4f}")

    # Vektorizace vs Python
    start = time.perf_counter()
    pure = sum(x * x for x in arr.tolist())
    cas_pure = time.perf_counter() - start

    start = time.perf_counter()
    np_sum = (arr ** 2).sum()
    cas_np = time.perf_counter() - start

    print(f"  pure Python: {cas_pure:.3f}s")
    print(f"  NumPy:       {cas_np:.3f}s ({cas_pure/cas_np:.0f}× rychlejší)")


def demo_pandas() -> None:
    import pandas as pd

    df = pd.DataFrame({
        "trida": ["A", "A", "B", "B", "C"],
        "jmeno": ["Anna", "Bob", "Cyril", "Dana", "Eva"],
        "skore": [85, 92, 78, 95, 88],
    })

    print("\nDataFrame:")
    print(df)

    print("\nPrůměr podle třídy:")
    print(df.groupby("trida")["skore"].mean())


def main() -> None:
    try:
        demo_numpy()
        demo_pandas()
    except ImportError as e:
        print(f"❌ Chybí: {e.name}. Nainstaluj: pip install numpy pandas")


if __name__ == "__main__":
    main()
