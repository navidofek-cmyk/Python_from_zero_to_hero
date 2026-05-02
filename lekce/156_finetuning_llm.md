# Lekce 156: Fine-tuning LLM — LoRA a PEFT

Fine-tuning přizpůsobí předtrénovaný LLM specifické úloze. **LoRA** (Low-Rank Adaptation) trénuje jen zlomek parametrů — 10–100× méně paměti.

---

## 🧠 Proč ne full fine-tuning?

```
GPT-2 small:   117M parametrů  ~  450 MB
LLaMA-7B:     7B parametrů    ~  14 GB (fp16)
LLaMA-70B:   70B parametrů    ~ 140 GB (fp16)

Full fine-tuning 7B = potřebuješ ~80 GB VRAM (A100×2)
LoRA fine-tuning 7B = potřebuješ ~12 GB VRAM (RTX 3090)
QLoRA (4-bit) 7B    = potřebuješ ~ 6 GB VRAM (RTX 3060)
```

---

## 🔧 LoRA — Low-Rank Adaptation

```python
import torch
import torch.nn as nn
import math


class LoRAVrstva(nn.Module):
    """
    LoRA vrstva — přidá nízkorangovou adaptaci k existující lineární vrstvě.

    Originální váhy W jsou zmrazeny.
    Trénují se jen matice A (d×r) a B (r×k) kde r << d,k.

    Výstup: (W + BA) · x = Wx + BAx
    """

    def __init__(self, original: nn.Linear, rank: int = 4, alpha: float = 16.0):
        super().__init__()
        self.original = original
        self.rank = rank
        self.alpha = alpha
        self.scaling = alpha / rank

        # Zmraz originální váhy
        for p in original.parameters():
            p.requires_grad = False

        d_in = original.in_features
        d_out = original.out_features

        # LoRA matice
        self.lora_A = nn.Parameter(torch.randn(d_in, rank) / math.sqrt(rank))
        self.lora_B = nn.Parameter(torch.zeros(rank, d_out))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Originální + LoRA příspěvek
        return self.original(x) + (x @ self.lora_A @ self.lora_B) * self.scaling

    @property
    def trainable_params(self) -> int:
        return self.lora_A.numel() + self.lora_B.numel()


def lora_parametry(model: nn.Module) -> tuple[int, int]:
    """Vrátí (trénovatelné, celkové) parametry."""
    trenovateln = sum(p.numel() for p in model.parameters() if p.requires_grad)
    celkem = sum(p.numel() for p in model.parameters())
    return trenovateln, celkem


# Demo — nahraď Linear vrstvu LoRA
original_layer = nn.Linear(768, 768)
lora_layer = LoRAVrstva(original_layer, rank=8, alpha=32)

tr, total = lora_parametry(lora_layer)
print(f"Originální vrstva: {original_layer.weight.numel():,} parametrů")
print(f"LoRA parametrů:    {lora_layer.trainable_params:,}")
print(f"Úspora:            {100*(1-tr/total):.1f}%")

x = torch.randn(2, 10, 768)
out = lora_layer(x)
print(f"Výstup: {out.shape}")
```

---

## 🏗️ Přidání LoRA do existujícího modelu

```python
def pridej_lora(model: nn.Module, cil_moduly: list[str],
                rank: int = 8, alpha: float = 16.0) -> nn.Module:
    """Nahradí vybrané Linear vrstvy LoRA vrstvami."""
    for nazev, modul in list(model.named_modules()):
        if any(cil in nazev for cil in cil_moduly):
            if isinstance(modul, nn.Linear):
                # Najdi rodiče a nahraď
                casti = nazev.split(".")
                rodic = model
                for cast in casti[:-1]:
                    rodic = getattr(rodic, cast)
                setattr(rodic, casti[-1], LoRAVrstva(modul, rank=rank, alpha=alpha))
    return model


# Příklad na malém transformeru
class MiniTransformer(nn.Module):
    def __init__(self, d=128, n_heads=4, n_layers=2):
        super().__init__()
        self.layers = nn.ModuleList([
            nn.ModuleDict({
                "q_proj": nn.Linear(d, d),
                "k_proj": nn.Linear(d, d),
                "v_proj": nn.Linear(d, d),
                "out_proj": nn.Linear(d, d),
                "ff1": nn.Linear(d, 4*d),
                "ff2": nn.Linear(4*d, d),
            })
            for _ in range(n_layers)
        ])

    def forward(self, x): return x  # zjednodušeno


model = MiniTransformer()
tr_pred, total_pred = lora_parametry(model)
model = pridej_lora(model, ["q_proj", "v_proj"], rank=4)
tr_po, total_po = lora_parametry(model)

print(f"\nPřed LoRA: {tr_pred:,}/{total_pred:,} trénovatelných")
print(f"Po LoRA:   {tr_po:,}/{total_po:,} trénovatelných")
print(f"Redukce:   {100*(1-tr_po/total_po):.1f}%")
```

---

## 📦 Hugging Face PEFT

```python
# pip install transformers peft datasets accelerate bitsandbytes

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, TaskType

# Konfigurace LoRA
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,                      # rank
    lora_alpha=32,            # alpha = škálování
    target_modules=["q_proj", "v_proj"],  # které vrstvy
    lora_dropout=0.1,
    bias="none",
)

# Načti model a aplikuj LoRA
# model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
# model = get_peft_model(model, lora_config)
# model.print_trainable_parameters()
# → trainable params: 4,194,304 || all params: 6,742,609,920 || trainable%: 0.0622%

print("\nPEFT konfigurace:")
print(f"  rank={lora_config.r}, alpha={lora_config.lora_alpha}")
print(f"  cílové moduly: {lora_config.target_modules}")
```

---

## 🏋️ Trénink s LoRA

```python
from dataclasses import dataclass

@dataclass
class TreninkovyConfig:
    model_nazev: str = "gpt2"
    dataset: str = "tatsu-lab/alpaca"
    vystupni_slozka: str = "./lora-output"
    rank: int = 8
    alpha: float = 16.0
    dropout: float = 0.1
    lr: float = 2e-4
    batch_size: int = 4
    gradient_accumulation: int = 4   # efektivní batch = 16
    epochy: int = 3
    max_delka: int = 512
    fp16: bool = True
    load_in_4bit: bool = True        # QLoRA

# Typický trénovací skript:
TRENINK_SKRIPT = '''
from transformers import TrainingArguments, Trainer
from trl import SFTTrainer

training_args = TrainingArguments(
    output_dir=cfg.vystupni_slozka,
    num_train_epochs=cfg.epochy,
    per_device_train_batch_size=cfg.batch_size,
    gradient_accumulation_steps=cfg.gradient_accumulation,
    learning_rate=cfg.lr,
    fp16=cfg.fp16,
    logging_steps=10,
    save_strategy="epoch",
)

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    dataset_text_field="text",
    max_seq_length=cfg.max_delka,
    peft_config=lora_config,
)
trainer.train()
trainer.model.save_pretrained(cfg.vystupni_slozka)
'''
print("Trénovací skript připraven — viz komentáře v kódu.")
```

---

## 💾 Merge LoRA vah

Po tréninku lze LoRA váhy sloučit s originálními — nulová inference latency.

```python
# from peft import PeftModel
# base_model = AutoModelForCausalLM.from_pretrained("base_model_name")
# model = PeftModel.from_pretrained(base_model, "lora_checkpoint/")
# merged = model.merge_and_unload()  # sloučí váhy
# merged.save_pretrained("merged_model/")
print("LoRA merge: peft.merge_and_unload()")
```

---

## 🎯 LoRA vs ostatní PEFT metody

| Metoda | Parametrů | Paměť | Inference overhead |
|--------|-----------|-------|-------------------|
| Full FT | 100% | vysoká | žádný |
| LoRA | 0.01–1% | nízká | žádný (po merge) |
| QLoRA (4-bit) | 0.01–1% | velmi nízká | malý |
| Prefix Tuning | < 0.1% | nízká | malý |
| Adapter | 0.1–3% | nízká | malý |
| IA3 | < 0.01% | velmi nízká | malý |

---

## ✏️ Cvičení

1. Natrénuj GPT-2 na vlastní dataset pomocí LoRA (např. básně, recepty).
2. Porovnej výsledky rank=4 vs rank=16 vs rank=64 — jak moc záleží na ranku?
3. Implementuj **QLoRA** pipeline — 4-bit kvantizace + LoRA.
4. Fine-tune BERT klasifikátor sentimentu na českých datech.
5. Měř inference rychlost: merged model vs LoRA model (overhead adaptérů).
