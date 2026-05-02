# Program — Lekce 153: Lekce 153: PyTorch — tensory, autograd, nn.Module, MNIST

Patří k lekci [Lekce 153: PyTorch — tensory, autograd, nn.Module, MNIST](../153_pytorch.md).

## Jak spustit

```bash
python3 programy/l153_pytorch.py
```

## Zdrojový kód

### `l153_pytorch.py`

```py
"""Lekce 153 — PyTorch: tensory, autograd, MLP, CNN, MNIST.

Spuštění:
    uv run --with torch,torchvision --index-url https://download.pytorch.org/whl/cpu l153_pytorch.py
"""

import time

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import DataLoader
except ImportError:
    print("Nainstaluj: uv add torch torchvision --index-url https://download.pytorch.org/whl/cpu")
    raise

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ── Základy tensorů ───────────────────────────────────────────────────────────

def demo_tensory():
    print("\n=== Tensory ===")
    t1 = torch.tensor([[1.,2.],[3.,4.]])
    t2 = torch.randn(2, 2)
    print(f"  t1 shape: {t1.shape}, dtype: {t1.dtype}, device: {t1.device}")
    print(f"  t1 @ t2 =\n{t1 @ t2}")
    print(f"  t1 + t2 =\n{t1 + t2}")
    print(f"  t1.T =\n{t1.T}")
    print(f"  t1.sum(dim=0) = {t1.sum(dim=0)}")


def demo_autograd():
    print("\n=== Autograd ===")
    x = torch.tensor(2.0, requires_grad=True)
    y = x**3 + 2*x**2 - x + 1
    y.backward()
    print(f"  f(x)=x³+2x²-x+1 při x=2: f'(x)={x.grad:.1f} (analyticky: {3*4+8-1})")

    W = torch.randn(3, 2, requires_grad=True)
    b = torch.zeros(3, requires_grad=True)
    x = torch.tensor([[1.0, 2.0]])
    z = x @ W.T + b
    loss = z.pow(2).mean()
    loss.backward()
    print(f"  ∂L/∂b: {b.grad.detach().numpy().round(4)}")


# ── MLP ───────────────────────────────────────────────────────────────────────

class MLP(nn.Module):
    def __init__(self, vstup, skryte, vystup, dropout=0.0):
        super().__init__()
        vrstvy = []
        prev = vstup
        for n in skryte:
            vrstvy += [nn.Linear(prev, n), nn.BatchNorm1d(n), nn.ReLU()]
            if dropout > 0: vrstvy.append(nn.Dropout(dropout))
            prev = n
        vrstvy.append(nn.Linear(prev, vystup))
        self.sit = nn.Sequential(*vrstvy)

    def forward(self, x): return self.sit(x)


# ── CNN ───────────────────────────────────────────────────────────────────────

class CNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, 3), nn.BatchNorm2d(32), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3), nn.BatchNorm2d(64), nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(), nn.Linear(1600, 128), nn.ReLU(),
            nn.Dropout(0.5), nn.Linear(128, 10)
        )

    def forward(self, x): return self.classifier(self.features(x))


# ── MNIST trénink ─────────────────────────────────────────────────────────────

def nacti_mnist(bs=128):
    try:
        import torchvision
        import torchvision.transforms as T
        tf = T.Compose([T.ToTensor(), T.Normalize((0.1307,), (0.3081,))])
        train = torchvision.datasets.MNIST("./data", train=True, download=True, transform=tf)
        test  = torchvision.datasets.MNIST("./data", train=False, download=True, transform=tf)
        return DataLoader(train, bs, shuffle=True), DataLoader(test, bs)
    except Exception as e:
        print(f"  ⚠ MNIST nedostupné: {e}")
        return None, None


def trenuj_epochu(model, loader, opt, criterion):
    model.train()
    loss_total, ok, total = 0.0, 0, 0
    for X, y in loader:
        X, y = X.to(device), y.to(device)
        if isinstance(model, MLP): X = X.view(X.size(0), -1)
        opt.zero_grad()
        pred = model(X)
        loss = criterion(pred, y)
        loss.backward()
        opt.step()
        loss_total += loss.item() * y.size(0)
        ok += (pred.argmax(1) == y).sum().item()
        total += y.size(0)
    return loss_total/total, ok/total


@torch.no_grad()
def vyhodnot(model, loader, criterion):
    model.eval()
    loss_total, ok, total = 0.0, 0, 0
    for X, y in loader:
        X, y = X.to(device), y.to(device)
        if isinstance(model, MLP): X = X.view(X.size(0), -1)
        pred = model(X)
        loss_total += criterion(pred, y).item() * y.size(0)
        ok += (pred.argmax(1) == y).sum().item()
        total += y.size(0)
    return loss_total/total, ok/total


def demo_mnist():
    print("\n=== MNIST klasifikace ===")
    train_loader, test_loader = nacti_mnist()
    if train_loader is None:
        print("  Přeskakuji MNIST (stahování selhalo)")
        return

    for nazev, model, epochy in [
        ("MLP (784→256→128→10)", MLP(784, [256,128], 10, dropout=0.2).to(device), 5),
        ("CNN (Conv→Pool→Conv→Pool→FC)", CNN().to(device), 3),
    ]:
        params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        print(f"\n  {nazev} ({params:,} parametrů)")
        opt = torch.optim.Adam(model.parameters(), lr=1e-3)
        scheduler = torch.optim.lr_scheduler.StepLR(opt, step_size=3, gamma=0.5)
        crit = nn.CrossEntropyLoss()
        print(f"  {'Ep':>3} {'TrAcc':>7} {'TeAcc':>7} {'Čas':>6}")
        for ep in range(1, epochy+1):
            t = time.perf_counter()
            _, tr_acc = trenuj_epochu(model, train_loader, opt, crit)
            _, te_acc = vyhodnot(model, test_loader, crit)
            scheduler.step()
            print(f"  {ep:>3} {tr_acc:>6.1%} {te_acc:>6.1%} {time.perf_counter()-t:>5.1f}s")


def demo_jednoduchy_xor():
    print("\n=== XOR v PyTorch ===")
    X = torch.tensor([[0,0],[0,1],[1,0],[1,1]], dtype=torch.float32)
    y = torch.tensor([[0],[1],[1],[0]], dtype=torch.float32)

    model = nn.Sequential(
        nn.Linear(2, 8), nn.ReLU(),
        nn.Linear(8, 4), nn.ReLU(),
        nn.Linear(4, 1), nn.Sigmoid()
    )
    opt = torch.optim.Adam(model.parameters(), lr=0.01)
    crit = nn.BCELoss()

    for ep in range(2000):
        opt.zero_grad()
        pred = model(X)
        loss = crit(pred, y)
        loss.backward()
        opt.step()
        if ep % 400 == 0:
            print(f"  Epocha {ep:4d}: loss={loss.item():.6f}")

    print("\n  XOR predikce:")
    with torch.no_grad():
        pred = model(X)
    for inp, yhat, ytrue in zip(X.numpy(), pred.numpy().flatten(), y.numpy().flatten()):
        ok = "✅" if abs(yhat-ytrue) < 0.5 else "❌"
        print(f"  {ok} {inp} → {yhat:.4f}")


def main():
    print("=" * 50)
    print(f"  🔥 PyTorch Demo  (device: {device})")
    print("=" * 50)

    demo_tensory()
    demo_autograd()
    demo_jednoduchy_xor()
    demo_mnist()

    print("\n✅ Demo dokončeno!")
    print("\nDalší kroky:")
    print("  uv add torchvision  → MNIST/CIFAR datasety")
    print("  uv add lightning    → PyTorch Lightning (boilerplate-free)")
    print("  uv add transformers → Hugging Face (LLMs, BERT, ...)")


if __name__ == "__main__":
    main()

```
