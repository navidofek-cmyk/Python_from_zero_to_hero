"""Lekce 151 — Neuronové sítě od nuly (NumPy).

Spuštění:
    uv run --with numpy l151_neural_networks_scratch.py
"""

import numpy as np
import time


# ── Aktivační funkce ────────────────────────────────���─────────────────────────

def sigmoid(z): return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))
def sigmoid_d(z): s = sigmoid(z); return s * (1 - s)
def relu(z): return np.maximum(0, z)
def relu_d(z): return (z > 0).astype(float)
def tanh_d(z): return 1 - np.tanh(z)**2
def softmax(z):
    e = np.exp(z - np.max(z, axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)

AKT = {"relu": (relu, relu_d), "sigmoid": (sigmoid, sigmoid_d),
       "tanh": (np.tanh, tanh_d), "linear": (lambda x: x, lambda x: np.ones_like(x))}


# ── Vrstva ────────────────────────────────────────────────────────────────────

class Vrstva:
    def __init__(self, n_in, n_out, akt="relu"):
        scale = np.sqrt(2/n_in) if akt == "relu" else np.sqrt(1/n_in)
        self.W = np.random.randn(n_in, n_out) * scale
        self.b = np.zeros((1, n_out))
        self.dW = np.zeros_like(self.W)
        self.db = np.zeros_like(self.b)
        self._f, self._fd = AKT[akt]
        self.vstup = self.z = self.a = None

    def forward(self, x):
        self.vstup = x
        self.z = x @ self.W + self.b
        self.a = self._f(self.z)
        return self.a

    def backward(self, grad):
        delta = grad * self._fd(self.z)
        self.dW = self.vstup.T @ delta
        self.db = delta.sum(axis=0, keepdims=True)
        return delta @ self.W.T


# ── Optimalizátory ─────────────────────────────────���────────────────────────���─

class Adam:
    def __init__(self, lr=0.001, b1=0.9, b2=0.999, eps=1e-8):
        self.lr, self.b1, self.b2, self.eps, self.t = lr, b1, b2, eps, 0
        self.m, self.v = {}, {}

    def krok(self, vrstvy):
        self.t += 1
        for i, vr in enumerate(vrstvy):
            if i not in self.m:
                self.m[i] = {p: np.zeros_like(getattr(vr, p)) for p in ["W","b"]}
                self.v[i] = {p: np.zeros_like(getattr(vr, p)) for p in ["W","b"]}
            for p in ["W","b"]:
                g = getattr(vr, f"d{p}")
                self.m[i][p] = self.b1*self.m[i][p] + (1-self.b1)*g
                self.v[i][p] = self.b2*self.v[i][p] + (1-self.b2)*g**2
                mh = self.m[i][p]/(1-self.b1**self.t)
                vh = self.v[i][p]/(1-self.b2**self.t)
                getattr(vr, p)[:] -= self.lr*mh/(np.sqrt(vh)+self.eps)


# ── Síť ───────────────────────────────────────────────────────────────────────

class NeuronSit:
    def __init__(self, vrstvy): self.vrstvy = vrstvy

    def forward(self, x):
        for v in self.vrstvy: x = v.forward(x)
        return x

    def backward(self, grad):
        for v in reversed(self.vrstvy): grad = v.backward(grad)

    def params(self): return sum(v.W.size + v.b.size for v in self.vrstvy)


def mse(p, y): return float(np.mean((p-y)**2))
def mse_d(p, y): return 2*(p-y)/y.size
def bce(p, y, e=1e-15):
    p = np.clip(p, e, 1-e)
    return float(-np.mean(y*np.log(p)+(1-y)*np.log(1-p)))
def bce_d(p, y, e=1e-15):
    p = np.clip(p, e, 1-e)
    return (p-y)/(p*(1-p)*y.size)


def trenuj(sit, X, y, opt, epochy=1000, bs=32, loss_fn=mse, loss_d=mse_d, verbose=True):
    hist, n = [], X.shape[0]
    for ep in range(epochy):
        idx = np.random.permutation(n)
        X_s, y_s = X[idx], y[idx]
        ep_loss = 0.0
        for s in range(0, n, bs):
            Xb, yb = X_s[s:s+bs], y_s[s:s+bs]
            pred = sit.forward(Xb)
            ep_loss += loss_fn(pred, yb) * len(Xb)
            sit.backward(loss_d(pred, yb))
            opt.krok(sit.vrstvy)
        ep_loss /= n
        hist.append(ep_loss)
        if verbose and ep % 200 == 0:
            print(f"  Epocha {ep:4d}: loss={ep_loss:.6f}")
    return hist


# ── Demo ──────────────────────────────────────────────────────────────────────

def demo_xor():
    print("\n=== XOR (nelineárně separabilní) ===")
    X = np.array([[0,0],[0,1],[1,0],[1,1]], dtype=float)
    y = np.array([[0],[1],[1],[0]], dtype=float)
    np.random.seed(42)
    sit = NeuronSit([Vrstva(2,8,"relu"), Vrstva(8,4,"relu"), Vrstva(4,1,"sigmoid")])
    opt = Adam(lr=0.01)
    trenuj(sit, X, y, opt, epochy=2000, bs=4, loss_fn=bce, loss_d=bce_d, verbose=True)
    pred = sit.forward(X)
    print("\n  Výsledky:")
    for inp, yhat, ytrue in zip(X, pred.flatten(), y.flatten()):
        ok = "✅" if abs(yhat-ytrue) < 0.5 else "❌"
        print(f"  {ok} {inp} → {yhat:.4f} (správně: {ytrue})")


def demo_klasifikace():
    print("\n=== Binární klasifikace (moons dataset) ===")
    try:
        from sklearn.datasets import make_moons
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler
        X, y = make_moons(n_samples=500, noise=0.2, random_state=42)
        X = StandardScaler().fit_transform(X)
        y = y.reshape(-1, 1).astype(float)
    except ImportError:
        # fallback — náhodná data
        np.random.seed(42)
        X = np.random.randn(200, 2)
        y = (X[:,0]**2 + X[:,1]**2 < 1).reshape(-1,1).astype(float)

    X_tr, X_te, y_tr, y_te = X[:400], X[400:], y[:400], y[400:]
    np.random.seed(0)
    sit = NeuronSit([Vrstva(2,16,"relu"), Vrstva(16,8,"relu"), Vrstva(8,1,"sigmoid")])
    opt = Adam(lr=0.005)
    trenuj(sit, X_tr, y_tr, opt, epochy=500, bs=32, loss_fn=bce, loss_d=bce_d, verbose=False)

    pred_te = sit.forward(X_te)
    acc = np.mean((pred_te > 0.5).flatten() == y_te.flatten())
    print(f"  Test accuracy: {acc:.1%}")


def demo_aktivace():
    print("\n=== Srovnání aktivačních funkcí ===")
    z = np.linspace(-3, 3, 7)
    print(f"  z =       {z}")
    print(f"  ReLU =    {relu(z).round(2)}")
    print(f"  Sigmoid = {sigmoid(z).round(3)}")
    print(f"  Tanh =    {np.tanh(z).round(3)}")


def main():
    print("=" * 50)
    print("  🧠 Neuronové sítě od nuly (NumPy)")
    print("=" * 50)
    demo_aktivace()
    demo_xor()
    demo_klasifikace()
    print("\n✅ Demo dokončeno!")


if __name__ == "__main__":
    main()
