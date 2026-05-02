# Program — Lekce 154: Lekce 154: Transformers a Attention mechanismus

Patří k lekci [Lekce 154: Transformers a Attention mechanismus](../154_transformers_attention.md).

## Jak spustit

```bash
python3 programy/l154_transformers_attention.py
```

## Zdrojový kód

### `l154_transformers_attention.py`

```py
"""Lekce 154 — Transformers a Attention mechanismus.

Spuštění:
    uv run --with numpy l154_transformers_attention.py
"""

import numpy as np


def softmax(x, axis=-1):
    e = np.exp(x - x.max(axis=axis, keepdims=True))
    return e / e.sum(axis=axis, keepdims=True)


def scaled_dot_product_attention(Q, K, V, mask=None):
    d_k = Q.shape[-1]
    scores = Q @ K.swapaxes(-2, -1) / np.sqrt(d_k)
    if mask is not None:
        scores = np.where(mask == 0, -1e9, scores)
    weights = softmax(scores)
    return weights @ V, weights


def positional_encoding(max_seq, d_model):
    pe = np.zeros((max_seq, d_model))
    pos = np.arange(max_seq)[:, None]
    div = np.exp(np.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
    pe[:, 0::2] = np.sin(pos * div)
    pe[:, 1::2] = np.cos(pos * div)
    return pe


def kauzalni_maska(n):
    return np.tril(np.ones((n, n)))


def main():
    print("=" * 50)
    print("  🤖 Transformers & Attention Demo")
    print("=" * 50)

    np.random.seed(42)
    batch, seq, d_k = 1, 5, 8
    Q = np.random.randn(batch, seq, d_k)
    K = np.random.randn(batch, seq, d_k)
    V = np.random.randn(batch, seq, d_k)

    out, weights = scaled_dot_product_attention(Q, K, V)
    print(f"\nAttention výstup: {out.shape}")
    print(f"Attention weights (řádek 0):\n{weights[0].round(3)}")

    maska = kauzalni_maska(seq)
    out_m, weights_m = scaled_dot_product_attention(Q, K, V, maska)
    print(f"\nS kauzální maskou — weights[0,0]:\n{weights_m[0,0].round(3)}")
    print("→ Pozice 0 vidí jen pozici 0 (budoucnost maskována)")

    pe = positional_encoding(10, 16)
    print(f"\nPositional encoding shape: {pe.shape}")
    print(f"První token, dim 0-7: {pe[0, :8].round(3)}")
    print(f"Druhý token, dim 0-7: {pe[1, :8].round(3)}")

    print("\n✅ Demo dokončeno!")
    print("Pro plný Transformer: uv add transformers torch")


if __name__ == "__main__":
    main()

```
