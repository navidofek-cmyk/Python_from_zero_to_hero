# Lekce 154: Transformers a Attention mechanismus

Transformers (2017, "Attention Is All You Need") revolucionizovaly NLP a dnes pohánějí GPT, BERT, LLaMA. Vychází z lekce 151–152.

---

## 🧠 Intuice Attention

```
"Banka na řece" vs "banka pro peníze"

Attention říká: při zpracování slova "banka" se dívej na ostatní slova
a přiřaď jim váhy — "řece" dostane vysokou váhu, "peníze" nízkou.

Query  = co hledám?
Key    = co nabízím?
Value  = co předám dál?

Attention(Q,K,V) = softmax(QKᵀ / √dₖ) · V
```

---

## 🔢 Scaled Dot-Product Attention

```python
import numpy as np


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    e = np.exp(x - x.max(axis=axis, keepdims=True))
    return e / e.sum(axis=axis, keepdims=True)


def scaled_dot_product_attention(
    Q: np.ndarray,  # (batch, heads, seq, d_k)
    K: np.ndarray,
    V: np.ndarray,
    mask: np.ndarray = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Vrátí (výstup, attention_weights).
    Q, K, V: (..., seq_len, d_k)
    """
    d_k = Q.shape[-1]
    # Skóre: Q·Kᵀ / √d_k
    scores = Q @ K.swapaxes(-2, -1) / np.sqrt(d_k)

    # Kauzální maska (pro dekodér — nevidí budoucnost)
    if mask is not None:
        scores = np.where(mask == 0, -1e9, scores)

    weights = softmax(scores)
    return weights @ V, weights


# Příklad
batch, seq, d_k = 1, 5, 8
np.random.seed(42)
Q = np.random.randn(batch, seq, d_k)
K = np.random.randn(batch, seq, d_k)
V = np.random.randn(batch, seq, d_k)

out, weights = scaled_dot_product_attention(Q, K, V)
print(f"Attention output shape: {out.shape}")
print(f"Attention weights (první věta):\n{weights[0].round(3)}")
```

---

## 🔀 Multi-Head Attention

```python
class MultiHeadAttention:
    """Multi-Head Attention od nuly."""

    def __init__(self, d_model: int, num_heads: int):
        assert d_model % num_heads == 0
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        # Projekční matice
        scale = np.sqrt(2.0 / d_model)
        self.W_Q = np.random.randn(d_model, d_model) * scale
        self.W_K = np.random.randn(d_model, d_model) * scale
        self.W_V = np.random.randn(d_model, d_model) * scale
        self.W_O = np.random.randn(d_model, d_model) * scale

    def split_heads(self, x: np.ndarray) -> np.ndarray:
        """(batch, seq, d_model) → (batch, heads, seq, d_k)"""
        batch, seq, _ = x.shape
        x = x.reshape(batch, seq, self.num_heads, self.d_k)
        return x.transpose(0, 2, 1, 3)

    def forward(self, Q: np.ndarray, K: np.ndarray, V: np.ndarray,
                mask: np.ndarray = None) -> np.ndarray:
        batch = Q.shape[0]

        # Lineární projekce
        Q_proj = (Q @ self.W_Q).reshape(batch, -1, self.num_heads, self.d_k).transpose(0,2,1,3)
        K_proj = (K @ self.W_K).reshape(batch, -1, self.num_heads, self.d_k).transpose(0,2,1,3)
        V_proj = (V @ self.W_V).reshape(batch, -1, self.num_heads, self.d_k).transpose(0,2,1,3)

        # Attention pro každou hlavu
        attn_out, _ = scaled_dot_product_attention(Q_proj, K_proj, V_proj, mask)

        # Spoj hlavy a projektuj
        attn_out = attn_out.transpose(0, 2, 1, 3).reshape(batch, -1, self.d_model)
        return attn_out @ self.W_O
```

---

## 📍 Positional Encoding

Transformers nezná pořadí slov — musíme ho přidat.

```python
def positional_encoding(max_seq: int, d_model: int) -> np.ndarray:
    """Sinusoidální poziční kódování."""
    pe = np.zeros((max_seq, d_model))
    position = np.arange(max_seq)[:, np.newaxis]
    div_term = np.exp(np.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))

    pe[:, 0::2] = np.sin(position * div_term)
    pe[:, 1::2] = np.cos(position * div_term)
    return pe


pe = positional_encoding(50, 64)
print(f"\nPositional encoding shape: {pe.shape}")
print(f"První token, první 8 dimenzí: {pe[0, :8].round(3)}")
```

---

## 🏗️ Feed-Forward + Layer Norm + Transformer blok

```python
def layer_norm(x: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    mean = x.mean(axis=-1, keepdims=True)
    std = x.std(axis=-1, keepdims=True)
    return (x - mean) / (std + eps)


def feed_forward(x: np.ndarray, W1: np.ndarray, W2: np.ndarray,
                  b1: np.ndarray, b2: np.ndarray) -> np.ndarray:
    """FFN(x) = max(0, xW1+b1)W2+b2  —  d_model → d_ff → d_model"""
    return np.maximum(0, x @ W1 + b1) @ W2 + b2


class TransformerBlok:
    def __init__(self, d_model: int, num_heads: int, d_ff: int):
        self.attn = MultiHeadAttention(d_model, num_heads)
        scale = np.sqrt(2.0 / d_model)
        self.W1 = np.random.randn(d_model, d_ff) * scale
        self.b1 = np.zeros((1, d_ff))
        self.W2 = np.random.randn(d_ff, d_model) * scale
        self.b2 = np.zeros((1, d_model))

    def forward(self, x: np.ndarray, mask: np.ndarray = None) -> np.ndarray:
        # Self-attention + residual
        attn = self.attn.forward(x, x, x, mask)
        x = layer_norm(x + attn)
        # FFN + residual
        ff = feed_forward(x, self.W1, self.W2, self.b1, self.b2)
        return layer_norm(x + ff)


# Demo
np.random.seed(0)
blok = TransformerBlok(d_model=64, num_heads=4, d_ff=256)
x = np.random.randn(1, 10, 64)  # (batch=1, seq=10, d_model=64)
out = blok.forward(x)
print(f"\nTransformer blok: {x.shape} → {out.shape}")
```

---

## 🤗 Hugging Face Transformers v praxi

```python
# pip install transformers torch
from transformers import pipeline, AutoTokenizer, AutoModel
import torch

# 1. Pipeline — nejjednodušší
# classifier = pipeline("sentiment-analysis")
# result = classifier("I love Python!")
# print(result)  # [{'label': 'POSITIVE', 'score': 0.999}]

# 2. Tokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
tokens = tokenizer("Hello, how are you?", return_tensors="pt")
print(f"\nTokeny: {tokens['input_ids']}")
print(f"Dekódováno: {tokenizer.decode(tokens['input_ids'][0])}")

# 3. Embeddingy
# model = AutoModel.from_pretrained("bert-base-uncased")
# with torch.no_grad():
#     output = model(**tokens)
# embeddings = output.last_hidden_state  # (1, seq_len, 768)
```

---

## 🎯 Causal mask pro dekodér

```python
def kauzalni_maska(seq_len: int) -> np.ndarray:
    """Dolní trojúhelník — dekodér nevidí budoucí tokeny."""
    return np.tril(np.ones((seq_len, seq_len)))


maska = kauzalni_maska(5)
print("\nKauzální maska (5×5):")
print(maska.astype(int))
```

---

## ✏️ Cvičení

1. Implementuj **cross-attention** — Q pochází z dekodéru, K a V z enkodéru.
2. Přidej **dropout** do attention vah (regularizace).
3. Napiš minimální **tokenizer** — BPE (Byte Pair Encoding) od nuly.
4. Implementuj **Rotary Position Embedding (RoPE)** — používá LLaMA.
5. Natrénuj malý Transformer na predikci dalšího znaku v sekvenci.
