# Lekce 153: PyTorch — tensory, autograd, nn.Module, MNIST

PyTorch je nejpopulárnější ML framework pro výzkum i produkci. Vychází přesně z principů z lekcí 151–152, jen s GPU akcelerací, CUDA a tisíci předdefinovanými vrstvami.

---

## 🚀 Instalace

```bash
# CPU only
uv add torch torchvision --index-url https://download.pytorch.org/whl/cpu

# GPU (CUDA 12.1)
uv add torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

---

## 🔢 Tensory

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

# Vytváření tensorů
t1 = torch.tensor([1.0, 2.0, 3.0])
t2 = torch.zeros(3, 4)
t3 = torch.randn(2, 3)          # náhodný N(0,1)
t4 = torch.arange(0, 10, 2)    # [0,2,4,6,8]
t5 = torch.linspace(0, 1, 5)   # [0, 0.25, 0.5, 0.75, 1.0]

print(f"dtype: {t3.dtype}, shape: {t3.shape}, device: {t3.device}")

# Operace
a = torch.tensor([[1., 2.], [3., 4.]])
b = torch.tensor([[5., 6.], [7., 8.]])

print(a + b)         # element-wise
print(a @ b)         # maticové násobení
print(a.T)           # transpozice
print(a.sum(dim=0))  # součet po sloupcích
print(a.mean())      # průměr

# Přetvarování
t = torch.randn(2, 3, 4)
print(t.view(6, 4).shape)       # (6, 4)
print(t.reshape(-1, 4).shape)   # (6, 4)
print(t.permute(2, 0, 1).shape) # (4, 2, 3)

# GPU (pokud dostupné)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
t_gpu = t3.to(device)
print(f"Zařízení: {device}")
```

---

## ⚡ Autograd

```python
# requires_grad=True → PyTorch sleduje operace
x = torch.tensor(2.0, requires_grad=True)
y = x**3 + 2*x**2 - x + 1

y.backward()
print(f"dy/dx = {x.grad}")  # 3x²+4x-1 = 3·4+8-1 = 19

# Praktický příklad
W = torch.randn(3, 2, requires_grad=True)
b = torch.zeros(3, requires_grad=True)
x = torch.tensor([[1.0, 2.0]])

z = x @ W.T + b
loss = z.pow(2).mean()
loss.backward()
print(f"∂L/∂W:\n{W.grad}")
print(f"∂L/∂b: {b.grad}")

# Zastavení sledování gradientů (inference)
with torch.no_grad():
    y_pred = x @ W.T + b  # žádné gradienty

# Context manager pro tréninkový vs inference mode
# model.train() vs model.eval()
```

---

## 🏗️ nn.Module — základní stavební blok

```python
class MLP(nn.Module):
    """Multi-Layer Perceptron."""

    def __init__(self, vstupni: int, skryte: list[int], vystupni: int,
                 aktivace=nn.ReLU, dropout: float = 0.0):
        super().__init__()
        vrstvy = []
        prev = vstupni
        for n in skryte:
            vrstvy.extend([
                nn.Linear(prev, n),
                nn.BatchNorm1d(n),
                aktivace(),
            ])
            if dropout > 0:
                vrstvy.append(nn.Dropout(dropout))
            prev = n
        vrstvy.append(nn.Linear(prev, vystupni))
        self.sit = nn.Sequential(*vrstvy)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.sit(x)


# Počet parametrů
model = MLP(784, [256, 128], 10)
params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"\nMLP parametrů: {params:,}")
print(model)
```

---

## 🏋️ Trénink — MNIST od nuly

```python
import torchvision
import torchvision.transforms as transforms


def nacti_mnist(batch_size: int = 64):
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    train = torchvision.datasets.MNIST("./data", train=True, download=True, transform=transform)
    test  = torchvision.datasets.MNIST("./data", train=False, download=True, transform=transform)
    return (
        DataLoader(train, batch_size=batch_size, shuffle=True),
        DataLoader(test, batch_size=batch_size, shuffle=False),
    )


def trenuj_epochu(model, loader, optimizer, criterion, device) -> tuple[float, float]:
    model.train()
    celkova_loss, spravne, celkem = 0.0, 0, 0
    for X, y in loader:
        X, y = X.to(device), y.to(device)
        X = X.view(X.size(0), -1)      # flatten: (B, 1, 28, 28) → (B, 784)
        optimizer.zero_grad()
        pred = model(X)
        loss = criterion(pred, y)
        loss.backward()
        optimizer.step()
        celkova_loss += loss.item() * y.size(0)
        spravne += (pred.argmax(1) == y).sum().item()
        celkem += y.size(0)
    return celkova_loss / celkem, spravne / celkem


@torch.no_grad()
def vyhodnoť(model, loader, criterion, device) -> tuple[float, float]:
    model.eval()
    celkova_loss, spravne, celkem = 0.0, 0, 0
    for X, y in loader:
        X, y = X.to(device), y.to(device)
        X = X.view(X.size(0), -1)
        pred = model(X)
        celkova_loss += criterion(pred, y).item() * y.size(0)
        spravne += (pred.argmax(1) == y).sum().item()
        celkem += y.size(0)
    return celkova_loss / celkem, spravne / celkem


def trenuj_mnist():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Zařízení: {device}")

    train_loader, test_loader = nacti_mnist(batch_size=128)

    model = MLP(784, [256, 128], 10, dropout=0.2).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)
    criterion = nn.CrossEntropyLoss()

    print(f"\nParametrů: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
    print(f"{'Epocha':>6} {'Train Loss':>11} {'Train Acc':>10} {'Test Loss':>10} {'Test Acc':>9}")
    print("-" * 55)

    for epocha in range(1, 11):
        train_loss, train_acc = trenuj_epochu(model, train_loader, optimizer, criterion, device)
        test_loss, test_acc = vyhodnoť(model, test_loader, criterion, device)
        scheduler.step()
        print(f"{epocha:>6} {train_loss:>11.4f} {train_acc:>9.1%} {test_loss:>10.4f} {test_acc:>8.1%}")

    return model
```

---

## 🖼️ CNN — konvoluční sítě

```python
class CNN(nn.Module):
    """Jednoduchá CNN pro MNIST."""

    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            # 1×28×28 → 32×26×26
            nn.Conv2d(1, 32, kernel_size=3),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            # 32×26×26 → 32×13×13
            nn.MaxPool2d(2),
            # 32×13×13 → 64×11×11
            nn.Conv2d(32, 64, kernel_size=3),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            # 64×11×11 → 64×5×5
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),             # 64×5×5 = 1600
            nn.Linear(1600, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, 10),
        )

    def forward(self, x):
        return self.classifier(self.features(x))


def trenuj_cnn():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_loader, test_loader = nacti_mnist(batch_size=128)

    model = CNN().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()

    print(f"\nCNN parametrů: {sum(p.numel() for p in model.parameters()):,}")
    print(f"{'Epocha':>6} {'Train Acc':>10} {'Test Acc':>9}")

    for epocha in range(1, 6):
        model.train()
        spravne_t, celkem_t = 0, 0
        for X, y in train_loader:
            X, y = X.to(device), y.to(device)
            optimizer.zero_grad()
            pred = model(X)
            nn.CrossEntropyLoss()(pred, y).backward()
            optimizer.step()
            spravne_t += (pred.argmax(1) == y).sum().item()
            celkem_t += y.size(0)

        _, test_acc = vyhodnoť(model, test_loader, criterion, device)
        print(f"{epocha:>6} {spravne_t/celkem_t:>9.1%} {test_acc:>8.1%}")
```

---

## 💾 Ukládání a načítání modelů

```python
# Uložení
torch.save(model.state_dict(), "model.pt")

# Načtení
model2 = MLP(784, [256, 128], 10)
model2.load_state_dict(torch.load("model.pt", map_location="cpu"))
model2.eval()

# Kompletní checkpoint (včetně optimizer stavu)
torch.save({
    "epocha": 10,
    "model_state": model.state_dict(),
    "optimizer_state": optimizer.state_dict(),
    "loss": 0.05,
}, "checkpoint.pt")

# Načtení checkpointu
checkpoint = torch.load("checkpoint.pt")
model.load_state_dict(checkpoint["model_state"])
optimizer.load_state_dict(checkpoint["optimizer_state"])
```

---

## 🔄 Transfer learning

```python
import torchvision.models as models

# Načti předdefinovaný model (ResNet18)
resnet = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

# Zmraz všechny vrstvy
for param in resnet.parameters():
    param.requires_grad = False

# Nahraď poslední vrstvu pro 10 tříd (MNIST)
resnet.fc = nn.Linear(resnet.fc.in_features, 10)

# Trénuj jen poslední vrstvu
optimizer = torch.optim.Adam(resnet.fc.parameters(), lr=1e-3)
```

---

## 📊 Srovnání: NumPy vs PyTorch vs TensorFlow

| | NumPy (od nuly) | PyTorch | TensorFlow/Keras |
|---|---|---|---|
| Autograd | ručně | ✅ dynamický | ✅ statický/dynamický |
| GPU | ❌ | ✅ CUDA/MPS | ✅ CUDA/TPU |
| Předdefinované vrstvy | ❌ | ✅ `nn.*` | ✅ `keras.layers.*` |
| Deployment | ❌ | TorchScript/ONNX | TFLite/SavedModel |
| Výzkum | experimentální | ✅ standard | ✅ |
| Produkce | ❌ | ✅ | ✅ |
| Křivka učení | strmá (ale poučná) | střední | mírná |

---

## ✏️ Cvičení

1. Natrénuj CNN na CIFAR-10 — 10 tříd barevných obrázků 32×32.
2. Implementuj **data augmentation** (`transforms.RandomHorizontalFlip`, `RandomCrop`).
3. Použij **transfer learning** — dotrénuj ResNet18 na vlastním datasetu.
4. Implementuj **early stopping** — zastav trénink pokud se test loss nezlepšuje 5 epoch.
5. Napiš **custom loss funkci** pro focal loss (pro nevyvážené datasety).
