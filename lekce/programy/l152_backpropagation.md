# Program — Lekce 152: Lekce 152: Backpropagation — od nuly

Patří k lekci [Lekce 152: Backpropagation — od nuly](../152_backpropagation.md).

## Jak spustit

```bash
python3 programy/l152_backpropagation.py
```

## Zdrojový kód

### `l152_backpropagation.py`

```py
"""Lekce 152 — Backpropagation: vlastní autograd engine.

Spuštění:
    uv run --with numpy l152_backpropagation.py
"""

import numpy as np


# ── Tensor s autogradem ───────────────────────────────────────────────────────

class Tensor:
    def __init__(self, data, _deti=(), _op=""):
        self.data = np.array(data, dtype=float)
        self.grad = np.zeros_like(self.data)
        self._back = lambda: None
        self._deti = set(_deti)
        self._op = _op

    def __repr__(self): return f"Tensor(shape={self.data.shape}, op={self._op!r})"

    def __add__(self, o):
        o = o if isinstance(o, Tensor) else Tensor(o)
        out = Tensor(self.data + o.data, (self, o), "+")
        def back(): self.grad += out.grad; o.grad += out.grad
        out._back = back; return out

    def __mul__(self, o):
        o = o if isinstance(o, Tensor) else Tensor(o)
        out = Tensor(self.data * o.data, (self, o), "*")
        def back(): self.grad += o.data * out.grad; o.grad += self.data * out.grad
        out._back = back; return out

    def __matmul__(self, o):
        o = o if isinstance(o, Tensor) else Tensor(o)
        out = Tensor(self.data @ o.data, (self, o), "@")
        def back():
            self.grad += out.grad @ o.data.T
            o.grad += self.data.T @ out.grad
        out._back = back; return out

    def __pow__(self, exp):
        out = Tensor(self.data**exp, (self,), f"**{exp}")
        def back(): self.grad += exp * self.data**(exp-1) * out.grad
        out._back = back; return out

    def __sub__(self, o): return self + (-1 * o)
    def __neg__(self): return self * -1
    def __radd__(self, o): return self + o
    def __rmul__(self, o): return self * o
    def __rsub__(self, o): return Tensor(o) - self
    def __truediv__(self, o): return self * Tensor(o)**-1

    def relu(self):
        out = Tensor(np.maximum(0, self.data), (self,), "relu")
        def back(): self.grad += (out.data > 0) * out.grad
        out._back = back; return out

    def sigmoid(self):
        s = 1/(1+np.exp(-self.data))
        out = Tensor(s, (self,), "sigmoid")
        def back(): self.grad += s*(1-s)*out.grad
        out._back = back; return out

    def tanh(self):
        t = np.tanh(self.data)
        out = Tensor(t, (self,), "tanh")
        def back(): self.grad += (1-t**2)*out.grad
        out._back = back; return out

    def exp(self):
        e = np.exp(self.data)
        out = Tensor(e, (self,), "exp")
        def back(): self.grad += e*out.grad
        out._back = back; return out

    def log(self):
        out = Tensor(np.log(self.data+1e-15), (self,), "log")
        def back(): self.grad += out.grad/(self.data+1e-15)
        out._back = back; return out

    def sum(self, axis=None, keepdims=False):
        out = Tensor(self.data.sum(axis=axis, keepdims=keepdims), (self,), "sum")
        def back():
            if axis is None: self.grad += out.grad * np.ones_like(self.data)
            else: self.grad += np.broadcast_to(
                np.expand_dims(out.grad, axis) if not keepdims else out.grad,
                self.data.shape)
        out._back = back; return out

    def mean(self): return self.sum() * (1.0/self.data.size)

    def backward(self):
        topo, vis = [], set()
        def build(t):
            if t not in vis:
                vis.add(t)
                for d in t._deti: build(d)
                topo.append(t)
        build(self)
        self.grad = np.ones_like(self.data)
        for t in reversed(topo): t._back()


# ── NN vrstva s Tensory ───────────────────────────────────────────────────────

class TVrstva:
    def __init__(self, n_in, n_out):
        scale = np.sqrt(2/n_in)
        self.W = Tensor(np.random.randn(n_in, n_out)*scale)
        self.b = Tensor(np.zeros((1, n_out)))

    def __call__(self, x): return (x @ self.W) + self.b
    def params(self): return [self.W, self.b]
    def nuluj(self):
        for p in self.params(): p.grad = np.zeros_like(p.data)


class TSit:
    def __init__(self, konfig):
        self.vrstvy, self.akts = [], []
        for i in range(len(konfig)-1):
            self.vrstvy.append(TVrstva(konfig[i][0], konfig[i+1][0]))
            self.akts.append(konfig[i+1][1])

    def __call__(self, x):
        for vr, akt in zip(self.vrstvy, self.akts):
            x = vr(x)
            if akt == "relu": x = x.relu()
            elif akt == "sigmoid": x = x.sigmoid()
        return x

    def params(self): return [p for v in self.vrstvy for p in v.params()]
    def nuluj(self):
        for v in self.vrstvy: v.nuluj()


# ── Gradient check ────────────────────────────────────────────────────────────

def gradient_check(sit, X_np, y_np, h=1e-5):
    def loss_fn(params=None):
        sit.nuluj()
        X = Tensor(X_np); y = Tensor(y_np)
        pred = sit(X)
        diff = pred - y
        return (diff * diff).mean()

    # Analytický gradient
    L = loss_fn()
    L.backward()
    analyticke = {i: p.grad.copy() for i, p in enumerate(sit.params())}

    # Numerický gradient
    numericke = {}
    for i, p in enumerate(sit.params()):
        numericke[i] = np.zeros_like(p.data)
        for idx in np.ndindex(p.data.shape):
            orig = p.data[idx]
            p.data[idx] = orig + h
            lp = loss_fn().data.item()
            p.data[idx] = orig - h
            lm = loss_fn().data.item()
            p.data[idx] = orig
            numericke[i][idx] = (lp - lm) / (2*h)

    print("\nGradient check:")
    for i in analyticke:
        err = np.max(np.abs(analyticke[i]-numericke[i]))
        rel = err/(np.max(np.abs(analyticke[i]))+1e-8)
        ok = "✅" if rel < 1e-4 else "❌"
        print(f"  {ok} param_{i}: max_abs={err:.2e}, rel={rel:.2e}")


# ── Vizualizace grafu ─────────────────────────────────────────────────────────

def tiskni_graf(t, prefix="", posledni=True):
    konektor = "└── " if posledni else "├── "
    prodlouzeni = "    " if posledni else "│   "
    op = f"[{t._op}]" if t._op else "[data]"
    print(f"{prefix}{konektor}{op} shape={t.data.shape}")
    deti = list(t._deti)
    for i, d in enumerate(deti):
        tiskni_graf(d, prefix+prodlouzeni, i==len(deti)-1)


def main():
    print("=" * 50)
    print("  🔄 Backpropagation — vlastní autograd")
    print("=" * 50)

    # Základní autograd
    print("\n=== Základní derivace ===")
    x = Tensor(np.array([[2.0]]))
    y = (x * x * x) + (Tensor(2.0) * x * x) - x + Tensor(1.0)
    y.backward()
    print(f"  f(x) = x³+2x²-x+1 při x=2")
    print(f"  f'(x) = 3x²+4x-1 = {3*4+8-1} (analyticky)")
    print(f"  f'(x) = {x.grad.flatten()[0]:.1f} (autograd)")

    # Výpočetní graf
    print("\n=== Výpočetní graf ===")
    a = Tensor(np.array([[1.,2.]]))
    b = Tensor(np.array([[3.],[4.]]))
    c = (a @ b).relu()
    d = c.mean()
    tiskni_graf(d)

    # XOR trénink
    print("\n=== XOR s vlastním autogradem ===")
    np.random.seed(42)
    X_xor = np.array([[0,0],[0,1],[1,0],[1,1]], dtype=float)
    y_xor = np.array([[0],[1],[1],[0]], dtype=float)

    sit = TSit([(2,""), (8,"relu"), (4,"relu"), (1,"sigmoid")])
    lr = 0.05

    for ep in range(1500):
        sit.nuluj()
        X = Tensor(X_xor); y = Tensor(y_xor)
        pred = sit(X)
        eps = 1e-15
        pred_c = Tensor(np.clip(pred.data, eps, 1-eps))
        loss = -(y * pred_c.log() + (Tensor(1.0)-y) * (Tensor(1.0)-pred_c).log()).mean()
        loss.backward()
        for p in sit.params(): p.data -= lr * p.grad
        if ep % 300 == 0:
            print(f"  Epocha {ep:4d}: loss={loss.data.flat[0]:.6f}")

    print("\n  XOR predikce:")
    pred = sit(Tensor(X_xor))
    for inp, yhat, ytrue in zip(X_xor, pred.data.flatten(), y_xor.flatten()):
        ok = "✅" if abs(yhat-ytrue) < 0.5 else "❌"
        print(f"  {ok} {inp} → {yhat:.4f}")

    # Gradient check na malé síti
    np.random.seed(7)
    mala = TSit([(2,""), (3,"relu"), (1,"sigmoid")])
    X_t = np.random.randn(4, 2)
    y_t = np.random.rand(4, 1)
    gradient_check(mala, X_t, y_t)

    print("\n✅ Demo dokončeno!")


if __name__ == "__main__":
    main()

```
