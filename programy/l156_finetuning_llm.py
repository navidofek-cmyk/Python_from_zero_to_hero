"""Lekce 156 — Fine-tuning LLM: LoRA od nuly.

Spuštění:
    uv run --with torch l156_finetuning_llm.py
"""

import math
import time

try:
    import torch
    import torch.nn as nn
except ImportError:
    print("Nainstaluj: uv add torch")
    raise


class LoRAVrstva(nn.Module):
    def __init__(self, original: nn.Linear, rank=4, alpha=16.0):
        super().__init__()
        self.original = original
        self.scaling = alpha / rank
        for p in original.parameters(): p.requires_grad = False
        d_in, d_out = original.in_features, original.out_features
        self.A = nn.Parameter(torch.randn(d_in, rank) / math.sqrt(rank))
        self.B = nn.Parameter(torch.zeros(rank, d_out))

    def forward(self, x):
        return self.original(x) + (x @ self.A @ self.B) * self.scaling

    @property
    def trainable(self): return self.A.numel() + self.B.numel()


def params(m):
    tr = sum(p.numel() for p in m.parameters() if p.requires_grad)
    tot = sum(p.numel() for p in m.parameters())
    return tr, tot


def main():
    print("=" * 50)
    print("  🔧 LoRA Fine-tuning Demo")
    print("=" * 50)

    # Simulace malého transformer-like modelu
    d = 256
    model = nn.Sequential(
        nn.Linear(d, d), nn.ReLU(),
        nn.Linear(d, d), nn.ReLU(),
        nn.Linear(d, 10)
    )
    tr_pred, tot = params(model)
    print(f"\nOriginální model: {tr_pred:,}/{tot:,} parametrů")

    # Přidej LoRA na první dvě Linear vrstvy
    model[0] = LoRAVrstva(model[0], rank=8, alpha=32)
    model[2] = LoRAVrstva(model[2], rank=8, alpha=32)

    tr_po, tot_po = params(model)
    print(f"Po LoRA (r=8):    {tr_po:,}/{tot_po:,} parametrů")
    print(f"Redukce:          {100*(1-tr_po/tot_po):.1f}%")

    # Trénink na toy datasetu
    print("\n=== Trénink LoRA (toy dataset) ===")
    X = torch.randn(200, d)
    y = torch.randint(0, 10, (200,))

    opt = torch.optim.Adam(
        [p for p in model.parameters() if p.requires_grad], lr=1e-3
    )
    crit = nn.CrossEntropyLoss()

    t = time.perf_counter()
    for ep in range(50):
        opt.zero_grad()
        loss = crit(model(X), y)
        loss.backward()
        opt.step()
        if (ep+1) % 10 == 0:
            acc = (model(X).argmax(1) == y).float().mean()
            print(f"  Epocha {ep+1:3d}: loss={loss.item():.4f}, acc={acc:.1%}")

    print(f"\nTrénink za {(time.perf_counter()-t)*1000:.0f}ms")

    # Srovnání trénovatelných parametrů
    print("\n=== Efektivita LoRA ===")
    for rank in [1, 4, 8, 16, 32]:
        lora = LoRAVrstva(nn.Linear(d, d), rank=rank)
        orig = d * d
        lora_p = lora.trainable
        print(f"  rank={rank:3d}: {lora_p:6,} LoRA params vs {orig:,} originálních "
              f"({100*lora_p/orig:.2f}%)")

    print("\n✅ Demo dokončeno!")
    print("Pro real fine-tuning: uv add transformers peft datasets")


if __name__ == "__main__":
    main()
