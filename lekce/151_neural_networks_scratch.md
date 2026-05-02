# Lekce 151: Neuronové sítě od nuly

Implementace neuronové sítě **bez frameworku** — čistý Python + NumPy. Pochopení základů je klíčové před použitím PyTorche nebo TensorFlow.

---

## 🧠 Biologická inspirace

```
Neuron:  vstupy → váhy → součet → aktivace → výstup
Vrstva:  matice vah W, vektor biasů b
Síť:     vstup → [skrytá vrstva 1] → ... → [výstupní vrstva]

Dopředný průchod (forward pass):
    z = W · x + b      ← lineární kombinace
    a = f(z)           ← aktivační funkce
```

---

## 🔢 Aktivační funkce

```python
import numpy as np
from typing import Callable


def sigmoid(z: np.ndarray) -> np.ndarray:
    """σ(z) = 1 / (1 + e^(-z))  — výstup (0, 1)"""
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))

def sigmoid_deriv(z: np.ndarray) -> np.ndarray:
    s = sigmoid(z)
    return s * (1 - s)

def relu(z: np.ndarray) -> np.ndarray:
    """ReLU(z) = max(0, z)  — nejpopulárnější pro skryté vrstvy"""
    return np.maximum(0, z)

def relu_deriv(z: np.ndarray) -> np.ndarray:
    return (z > 0).astype(float)

def tanh(z: np.ndarray) -> np.ndarray:
    return np.tanh(z)

def tanh_deriv(z: np.ndarray) -> np.ndarray:
    return 1 - np.tanh(z)**2

def leaky_relu(z: np.ndarray, alpha: float = 0.01) -> np.ndarray:
    return np.where(z > 0, z, alpha * z)

def leaky_relu_deriv(z: np.ndarray, alpha: float = 0.01) -> np.ndarray:
    return np.where(z > 0, 1.0, alpha)

def softmax(z: np.ndarray) -> np.ndarray:
    """Softmax pro multi-class výstup — výstupy se sčítají na 1."""
    e = np.exp(z - np.max(z, axis=1, keepdims=True))  # numerická stabilita
    return e / e.sum(axis=1, keepdims=True)
```

---

## 📉 Ztrátové funkce (Loss)

```python
def mse(y_pred: np.ndarray, y_true: np.ndarray) -> float:
    """Mean Squared Error — pro regresi."""
    return float(np.mean((y_pred - y_true)**2))

def mse_deriv(y_pred: np.ndarray, y_true: np.ndarray) -> np.ndarray:
    return 2 * (y_pred - y_true) / y_true.size

def binary_crossentropy(y_pred: np.ndarray, y_true: np.ndarray, eps=1e-15) -> float:
    """BCE — pro binární klasifikaci."""
    y_pred = np.clip(y_pred, eps, 1 - eps)
    return float(-np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred)))

def binary_crossentropy_deriv(y_pred: np.ndarray, y_true: np.ndarray, eps=1e-15) -> np.ndarray:
    y_pred = np.clip(y_pred, eps, 1 - eps)
    return (y_pred - y_true) / (y_pred * (1 - y_pred) * y_true.size)

def categorical_crossentropy(y_pred: np.ndarray, y_true: np.ndarray, eps=1e-15) -> float:
    """CCE — pro multi-class klasifikaci (one-hot y_true)."""
    y_pred = np.clip(y_pred, eps, 1)
    return float(-np.mean(np.sum(y_true * np.log(y_pred), axis=1)))
```

---

## 🏗️ Vrstva a síť

```python
from dataclasses import dataclass, field


@dataclass
class Vrstva:
    n_vstupy: int
    n_neuronu: int
    aktivace: str = "relu"

    def __post_init__(self):
        # He inicializace (pro ReLU), Xavier pro sigmoid/tanh
        scale = np.sqrt(2.0 / self.n_vstupy) if self.aktivace == "relu" else np.sqrt(1.0 / self.n_vstupy)
        self.W = np.random.randn(self.n_vstupy, self.n_neuronu) * scale
        self.b = np.zeros((1, self.n_neuronu))
        # Gradienty
        self.dW = np.zeros_like(self.W)
        self.db = np.zeros_like(self.b)
        # Cache pro backprop
        self.vstup: np.ndarray = None
        self.z: np.ndarray = None
        self.a: np.ndarray = None

    @property
    def _aktivace_fn(self):
        return {"relu": relu, "sigmoid": sigmoid, "tanh": tanh,
                "leaky_relu": leaky_relu, "linear": lambda x: x}[self.aktivace]

    @property
    def _aktivace_deriv(self):
        return {"relu": relu_deriv, "sigmoid": sigmoid_deriv, "tanh": tanh_deriv,
                "leaky_relu": leaky_relu_deriv, "linear": lambda x: np.ones_like(x)}[self.aktivace]

    def forward(self, x: np.ndarray) -> np.ndarray:
        self.vstup = x
        self.z = x @ self.W + self.b
        self.a = self._aktivace_fn(self.z)
        return self.a

    def backward(self, grad_vystup: np.ndarray) -> np.ndarray:
        """Vrátí gradient pro předchozí vrstvu."""
        delta = grad_vystup * self._aktivace_deriv(self.z)
        self.dW = self.vstup.T @ delta
        self.db = np.sum(delta, axis=0, keepdims=True)
        return delta @ self.W.T


class NeuronSit:
    def __init__(self, vrstvy: list[Vrstva]):
        self.vrstvy = vrstvy

    def forward(self, x: np.ndarray) -> np.ndarray:
        for v in self.vrstvy:
            x = v.forward(x)
        return x

    def backward(self, grad: np.ndarray) -> None:
        for v in reversed(self.vrstvy):
            grad = v.backward(grad)

    def parametry(self):
        return sum(v.W.size + v.b.size for v in self.vrstvy)
```

---

## ⚙️ Optimalizátory

```python
class SGD:
    def __init__(self, lr: float = 0.01, momentum: float = 0.0):
        self.lr = lr
        self.momentum = momentum
        self._velocity: dict = {}

    def krok(self, vrstvy: list[Vrstva]) -> None:
        for i, v in enumerate(vrstvy):
            if i not in self._velocity:
                self._velocity[i] = {"W": np.zeros_like(v.W), "b": np.zeros_like(v.b)}
            vel = self._velocity[i]
            vel["W"] = self.momentum * vel["W"] - self.lr * v.dW
            vel["b"] = self.momentum * vel["b"] - self.lr * v.db
            v.W += vel["W"]
            v.b += vel["b"]


class Adam:
    """Adaptivní optimalizátor — nejčastěji používaný v praxi."""
    def __init__(self, lr: float = 0.001, beta1: float = 0.9,
                 beta2: float = 0.999, eps: float = 1e-8):
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps
        self.t = 0
        self._m: dict = {}
        self._v: dict = {}

    def krok(self, vrstvy: list[Vrstva]) -> None:
        self.t += 1
        for i, vrstva in enumerate(vrstvy):
            if i not in self._m:
                self._m[i] = {"W": np.zeros_like(vrstva.W), "b": np.zeros_like(vrstva.b)}
                self._v[i] = {"W": np.zeros_like(vrstva.W), "b": np.zeros_like(vrstva.b)}
            for p in ["W", "b"]:
                g = getattr(vrstva, f"d{p}")
                self._m[i][p] = self.beta1 * self._m[i][p] + (1 - self.beta1) * g
                self._v[i][p] = self.beta2 * self._v[i][p] + (1 - self.beta2) * g**2
                m_hat = self._m[i][p] / (1 - self.beta1**self.t)
                v_hat = self._v[i][p] / (1 - self.beta2**self.t)
                getattr(vrstva, p)[:] -= self.lr * m_hat / (np.sqrt(v_hat) + self.eps)
```

---

## 🏋️ Trénink — XOR problém

XOR není lineárně separabilní — vyžaduje skrytou vrstvu.

```python
def trenuj(
    sit: NeuronSit,
    X: np.ndarray,
    y: np.ndarray,
    optimizer,
    epochy: int = 1000,
    batch_size: int = 32,
    verbose: bool = True,
) -> list[float]:
    loss_history = []
    n = X.shape[0]

    for epocha in range(epochy):
        # Mini-batch shuffle
        idx = np.random.permutation(n)
        X_sh, y_sh = X[idx], y[idx]
        epoch_loss = 0.0

        for start in range(0, n, batch_size):
            Xb = X_sh[start:start+batch_size]
            yb = y_sh[start:start+batch_size]

            # Forward
            y_pred = sit.forward(Xb)

            # Loss
            epoch_loss += mse(y_pred, yb) * len(Xb)

            # Backward
            grad = mse_deriv(y_pred, yb)
            sit.backward(grad)

            # Update
            optimizer.krok(sit.vrstvy)

        epoch_loss /= n
        loss_history.append(epoch_loss)

        if verbose and epocha % 200 == 0:
            print(f"  Epocha {epocha:4d}: loss={epoch_loss:.6f}")

    return loss_history


# XOR dataset
X_xor = np.array([[0,0],[0,1],[1,0],[1,1]], dtype=float)
y_xor = np.array([[0],[1],[1],[0]], dtype=float)

np.random.seed(42)
sit = NeuronSit([
    Vrstva(2, 8, "relu"),
    Vrstva(8, 4, "relu"),
    Vrstva(4, 1, "sigmoid"),
])
opt = Adam(lr=0.01)
print(f"Parametrů: {sit.parametry()}")

history = trenuj(sit, X_xor, y_xor, opt, epochy=2000, batch_size=4, verbose=True)

print("\nXOR predikce po tréninku:")
pred = sit.forward(X_xor)
for inp, yhat, ytrue in zip(X_xor, pred.flatten(), y_xor.flatten()):
    print(f"  {inp} → {yhat:.4f} (správně: {ytrue})")
```

---

## 📊 Batch normalizace

```python
class BatchNorm:
    """Normalizace aktivací v dávce — urychluje trénink."""
    def __init__(self, n_features: int, eps: float = 1e-8, momentum: float = 0.1):
        self.gamma = np.ones((1, n_features))   # scale
        self.beta = np.zeros((1, n_features))    # shift
        self.eps = eps
        self.momentum = momentum
        self.running_mean = np.zeros((1, n_features))
        self.running_var = np.ones((1, n_features))
        # Cache
        self._x_norm = None
        self._mean = None
        self._var = None
        self._x = None

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        if training:
            self._x = x
            self._mean = x.mean(axis=0, keepdims=True)
            self._var = x.var(axis=0, keepdims=True)
            self._x_norm = (x - self._mean) / np.sqrt(self._var + self.eps)
            self.running_mean = (1-self.momentum)*self.running_mean + self.momentum*self._mean
            self.running_var = (1-self.momentum)*self.running_var + self.momentum*self._var
        else:
            self._x_norm = (x - self.running_mean) / np.sqrt(self.running_var + self.eps)
        return self.gamma * self._x_norm + self.beta
```

---

## 🎯 Přehled vrstev a aktivací

| Aktivace | Rozsah | Problém | Kdy použít |
|----------|--------|---------|------------|
| ReLU | [0, ∞) | dying neurons | skryté vrstvy (nejčastější) |
| Leaky ReLU | (-∞, ∞) | — | náhrada za ReLU |
| Sigmoid | (0, 1) | vanishing gradient | výstup (binární klas.) |
| Tanh | (-1, 1) | vanishing gradient | RNN, skryté vrstvy |
| Softmax | (0, 1) Σ=1 | — | výstup (multi-class) |
| Linear | (-∞, ∞) | — | výstupní vrstva (regrese) |

---

## ✏️ Cvičení

1. Implementuj **Dropout** vrstvu — při tréninku náhodně nuluje neurony, při inferenci škáluje.
2. Přidej **L1 a L2 regularizaci** — penalizace velkých vah v loss funkci.
3. Natrénuj síť na **Moon dataset** (sklearn) — 2-class, nelineárně separabilní.
4. Implementuj **learning rate scheduler** — snižuj LR po každých N epochách (step decay).
5. Vizualizuj **decision boundary** v 2D pomocí matplotlib — vykresli oblasti klasifikace.
