# Lekce 152: Backpropagation — od nuly

Backpropagation = **zpětné šíření gradientu** pomocí chain rule. Základ každého moderního ML frameworku.

---

## 📐 Chain Rule — základ všeho

```
Máme: L(y_pred(W)) — loss závisí na váhách přes výstup

Chain rule:
  dL/dW = dL/dy_pred · dy_pred/dW

Vícevrstvá síť:
  dL/dW1 = dL/da3 · da3/dz3 · dz3/da2 · da2/dz2 · dz2/da1 · da1/dz1 · dz1/dW1

kde:
  zᵢ = Wᵢ · aᵢ₋₁ + bᵢ    (lineární kombinace)
  aᵢ = f(zᵢ)              (aktivace)
```

---

## 🔄 Výpočetní graf a autograd

Místo ručního odvozování vzorců implementujeme **automatické diferencování**.

```python
import numpy as np
from typing import Optional


class Tensor:
    """Tensor s automatickým výpočtem gradientů (jako PyTorch)."""

    def __init__(self, data: np.ndarray, _deti: tuple = (), _op: str = ""):
        self.data = np.array(data, dtype=float)
        self.grad = np.zeros_like(self.data)
        self._backward = lambda: None
        self._deti = set(_deti)
        self._op = _op

    def __repr__(self):
        return f"Tensor({self.data}, grad={self.grad})"

    def __add__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data + other.data, (self, other), "+")
        def _backward():
            self.grad += out.grad
            other.grad += out.grad
        out._backward = _backward
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data * other.data, (self, other), "*")
        def _backward():
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad
        out._backward = _backward
        return out

    def __matmul__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data @ other.data, (self, other), "@")
        def _backward():
            self.grad += out.grad @ other.data.T
            other.grad += self.data.T @ out.grad
        out._backward = _backward
        return out

    def __sub__(self, other):
        return self + (-1 * other)

    def __pow__(self, exp):
        out = Tensor(self.data**exp, (self,), f"**{exp}")
        def _backward():
            self.grad += exp * self.data**(exp-1) * out.grad
        out._backward = _backward
        return out

    def __neg__(self):
        return self * -1

    def __radd__(self, other): return self + other
    def __rmul__(self, other): return self * other
    def __rsub__(self, other): return Tensor(other) - self

    def relu(self):
        out = Tensor(np.maximum(0, self.data), (self,), "relu")
        def _backward():
            self.grad += (out.data > 0) * out.grad
        out._backward = _backward
        return out

    def sigmoid(self):
        s = 1 / (1 + np.exp(-self.data))
        out = Tensor(s, (self,), "sigmoid")
        def _backward():
            self.grad += s * (1 - s) * out.grad
        out._backward = _backward
        return out

    def log(self):
        out = Tensor(np.log(self.data + 1e-15), (self,), "log")
        def _backward():
            self.grad += (1 / (self.data + 1e-15)) * out.grad
        out._backward = _backward
        return out

    def sum(self, axis=None, keepdims=False):
        out = Tensor(self.data.sum(axis=axis, keepdims=keepdims), (self,), "sum")
        def _backward():
            if axis is None:
                self.grad += out.grad * np.ones_like(self.data)
            else:
                self.grad += np.broadcast_to(
                    np.expand_dims(out.grad, axis) if not keepdims else out.grad,
                    self.data.shape
                )
        out._backward = _backward
        return out

    def mean(self):
        return self.sum() * (1.0 / self.data.size)

    def backward(self):
        """Topologické řazení + zpětný průchod."""
        topo, navstivene = [], set()
        def build_topo(t):
            if t not in navstivene:
                navstivene.add(t)
                for dite in t._deti:
                    build_topo(dite)
                topo.append(t)
        build_topo(self)
        self.grad = np.ones_like(self.data)
        for t in reversed(topo):
            t._backward()
```

---

## 🏗️ NN vrstva s Tensory

```python
class TensorVrstva:
    def __init__(self, n_in: int, n_out: int):
        scale = np.sqrt(2.0 / n_in)
        self.W = Tensor(np.random.randn(n_in, n_out) * scale)
        self.b = Tensor(np.zeros((1, n_out)))

    def __call__(self, x: Tensor) -> Tensor:
        return (x @ self.W) + self.b

    def parametry(self) -> list[Tensor]:
        return [self.W, self.b]

    def nuluj_gradienty(self):
        for p in self.parametry():
            p.grad = np.zeros_like(p.data)


class TensorSit:
    def __init__(self, konfigurace: list[tuple[int, str]]):
        """konfigurace = [(n_neuronu, aktivace), ...]"""
        self.vrstvy = []
        self.aktivace = []
        for i in range(len(konfigurace) - 1):
            n_in = konfigurace[i][0]
            n_out = konfigurace[i+1][0]
            akt = konfigurace[i+1][1]
            self.vrstvy.append(TensorVrstva(n_in, n_out))
            self.aktivace.append(akt)

    def __call__(self, x: Tensor) -> Tensor:
        for vrstva, akt in zip(self.vrstvy, self.aktivace):
            x = vrstva(x)
            if akt == "relu":
                x = x.relu()
            elif akt == "sigmoid":
                x = x.sigmoid()
        return x

    def parametry(self) -> list[Tensor]:
        return [p for v in self.vrstvy for p in v.parametry()]

    def nuluj_gradienty(self):
        for p in self.parametry():
            p.grad = np.zeros_like(p.data)
```

---

## 🎓 Trénink s vlastním autogradem

```python
def mse_loss(pred: Tensor, true: Tensor) -> Tensor:
    diff = pred - true
    return (diff * diff).mean()


def bce_loss(pred: Tensor, true: Tensor) -> Tensor:
    eps = 1e-15
    pred_clamped = Tensor(np.clip(pred.data, eps, 1 - eps))
    return -(true * pred_clamped.log() + (Tensor(1.0) - true) * (Tensor(1.0) - pred_clamped).log()).mean()


# XOR s vlastním autogradem
np.random.seed(42)
X = Tensor(np.array([[0,0],[0,1],[1,0],[1,1]], dtype=float))
y = Tensor(np.array([[0],[1],[1],[0]], dtype=float))

sit = TensorSit([(2, ""), (8, "relu"), (4, "relu"), (1, "sigmoid")])
lr = 0.05

print("Trénink XOR s vlastním autogradem:")
for epocha in range(1000):
    sit.nuluj_gradienty()
    pred = sit(X)
    loss = bce_loss(pred, y)
    loss.backward()

    # Gradient descent krok
    for p in sit.parametry():
        p.data -= lr * p.grad

    if epocha % 200 == 0:
        print(f"  Epocha {epocha:4d}: loss={loss.data:.6f}")

print("\nXOR predikce:")
pred = sit(X)
for inp, yhat, ytrue in zip(X.data, pred.data.flatten(), y.data.flatten()):
    print(f"  {inp} → {yhat:.4f} (správně: {ytrue})")
```

---

## 🔬 Numerická verifikace gradientů

Důležitý nástroj pro ověření správnosti backpropu — porovnáme analytický gradient s numerickým.

```python
def gradient_check(f, params: list[Tensor], vstup: Tensor, h: float = 1e-5) -> dict:
    """Porovná analytické a numerické gradienty."""
    # Analytický gradient
    vystup = f(vstup)
    loss = vystup.mean()
    loss.backward()

    vysledky = {}
    for i, p in enumerate(params):
        analyticke = p.grad.copy()
        numericke = np.zeros_like(p.data)

        for idx in np.ndindex(p.data.shape):
            puvodni = p.data[idx]
            p.data[idx] = puvodni + h
            loss_plus = f(vstup).mean().data
            p.data[idx] = puvodni - h
            loss_minus = f(vstup).mean().data
            p.data[idx] = puvodni
            numericke[idx] = (loss_plus - loss_minus) / (2 * h)

        max_err = np.max(np.abs(analyticke - numericke))
        rel_err = max_err / (np.max(np.abs(analyticke)) + 1e-8)
        vysledky[f"param_{i}"] = {"max_abs": max_err, "rel": rel_err}

    return vysledky


# Verifikace na malé síti
np.random.seed(0)
mala_sit = TensorSit([(2, ""), (3, "relu"), (1, "sigmoid")])
X_test = Tensor(np.random.randn(4, 2))

vysledky = gradient_check(mala_sit, mala_sit.parametry(), X_test)
print("\nGradient check:")
for nazev, v in vysledky.items():
    ok = "✅" if v["rel"] < 1e-4 else "❌"
    print(f"  {ok} {nazev}: max_abs={v['max_abs']:.2e}, rel={v['rel']:.2e}")
```

---

## 📈 Vizualizace výpočetního grafu

```python
def tiskni_graf(tensor: Tensor, prefix: str = "", posledni: bool = True) -> None:
    """Tiskne výpočetní graf jako ASCII strom."""
    konektor = "└── " if posledni else "├── "
    prodlouzeni = "    " if posledni else "│   "
    op = f"[{tensor._op}]" if tensor._op else "[data]"
    print(f"{prefix}{konektor}{op} shape={tensor.data.shape}")
    deti = list(tensor._deti)
    for i, dite in enumerate(deti):
        tiskni_graf(dite, prefix + prodlouzeni, i == len(deti) - 1)


# Příklad
a = Tensor(np.array([[1., 2.]]))
b = Tensor(np.array([[3.], [4.]]))
c = (a @ b).relu()
d = c.mean()
print("\nVýpočetní graf:")
tiskni_graf(d)
```

---

## 🎯 Co se děje při backpropu — krok za krokem

```
Síť: x → W1 → z1 → ReLU → a1 → W2 → z2 → sigmoid → a2 → BCE loss → L

Forward:
  z1 = x @ W1 + b1
  a1 = relu(z1)
  z2 = a1 @ W2 + b2
  a2 = sigmoid(z2)
  L  = BCE(a2, y)

Backward (chain rule):
  dL/da2  = -(y/a2 - (1-y)/(1-a2)) / n
  dL/dz2  = dL/da2 · sigmoid'(z2)  = dL/da2 · a2·(1-a2)
  dL/dW2  = a1.T @ dL/dz2
  dL/db2  = sum(dL/dz2)
  dL/da1  = dL/dz2 @ W2.T
  dL/dz1  = dL/da1 · relu'(z1)  = dL/da1 · (z1 > 0)
  dL/dW1  = x.T @ dL/dz1
  dL/db1  = sum(dL/dz1)
```

---

## ✏️ Cvičení

1. Rozšiř `Tensor` o operace `exp()`, `tanh()`, `reshape()`, `transpose()`.
2. Implementuj **RMSprop** optimalizátor pomocí vlastního autograd systému.
3. Přidej **weight decay** (L2 regularizace) přímo do gradient descent kroku.
4. Napiš unit testy pro gradient check na všech operacích (`+`, `*`, `@`, `relu`, `sigmoid`).
5. Implementuj **mini-batch gradient descent** s vlastním autogradem — porovnej konvergenci s full-batch.
