# Lekce 127 — MLOps a LLMOps

MLOps (Machine Learning Operations) a LLMOps (Large Language Model Operations) jsou disciplíny,
které propojují vývoj ML modelů s jejich spolehlivým nasazením a provozem.
V této lekci si ukážeme klíčové patterns — bez ML knihoven.

---

## 1. Co jsou MLOps a LLMOps?

**MLOps** = DevOps aplikovaný na ML:
- Reprodukovatelné experimenty
- Verzování modelů a dat
- Automatizované trénování a nasazování
- Monitoring v produkci

**LLMOps** = MLOps specificky pro velké jazykové modely:
- Prompt verzování a A/B testování
- Evaluace výstupů (neexistuje "ground truth")
- Cost a latency budgety (tokeny jsou drahé)
- Guardrails a safety

---

## 2. Experiment Tracking

Sledování experimentů je základ reprodukovatelnosti. Ukládáme hyperparametry, metriky, artefakty.

```python
import json, time, uuid
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Any

@dataclass
class Run:
    """Jeden ML experiment run."""
    run_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, list[float]] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)
    status: str = "running"  # running | completed | failed
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None

    def log_param(self, key: str, value: Any) -> None:
        self.params[key] = value

    def log_metric(self, key: str, value: float, step: int | None = None) -> None:
        if key not in self.metrics:
            self.metrics[key] = []
        self.metrics[key].append(value)

    def finish(self, status: str = "completed") -> None:
        self.status = status
        self.end_time = time.time()

    @property
    def duration(self) -> float | None:
        if self.end_time:
            return round(self.end_time - self.start_time, 3)
        return None

    def best_metric(self, key: str, mode: str = "min") -> float | None:
        values = self.metrics.get(key)
        if not values:
            return None
        return min(values) if mode == "min" else max(values)


class ExperimentTracker:
    """Jednoduchý tracker ukládající runy do JSON."""

    def __init__(self, store_path: Path = Path("/tmp/mlops_runs.json")) -> None:
        self.store_path = store_path
        self._runs: dict[str, Run] = {}

    def start_run(self, name: str, tags: dict[str, str] | None = None) -> Run:
        run = Run(name=name, tags=tags or {})
        self._runs[run.run_id] = run
        return run

    def save(self) -> None:
        data = {rid: asdict(r) for rid, r in self._runs.items()}
        self.store_path.write_text(json.dumps(data, indent=2))

    def best_run(self, metric: str, mode: str = "min") -> Run | None:
        candidates = [
            r for r in self._runs.values()
            if r.status == "completed" and r.metrics.get(metric)
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda r: r.best_metric(metric, mode) or float("inf"))
            if mode == "min" else max(candidates, key=lambda r: r.best_metric(metric, mode) or 0)

    def compare(self, metric: str) -> list[dict]:
        rows = []
        for run in self._runs.values():
            best = run.best_metric(metric)
            if best is not None:
                rows.append({"run_id": run.run_id, "name": run.name, metric: best})
        return sorted(rows, key=lambda x: x[metric])
```

---

## 3. Model Registry pattern

Model registry je centrální úložiště verzovaných modelů se stavovými přechody.

```python
from enum import Enum

class ModelStage(str, Enum):
    CANDIDATE = "candidate"
    STAGING    = "staging"
    PRODUCTION = "production"
    ARCHIVED   = "archived"

@dataclass
class ModelVersion:
    name: str
    version: str                    # semver: "1.2.3"
    run_id: str
    stage: ModelStage = ModelStage.CANDIDATE
    metrics: dict[str, float] = field(default_factory=dict)
    registered_at: str = field(
        default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S")
    )
    description: str = ""

class ModelRegistry:
    def __init__(self) -> None:
        self._models: dict[str, list[ModelVersion]] = {}

    def register(self, model: ModelVersion) -> None:
        self._models.setdefault(model.name, []).append(model)

    def promote(self, name: str, version: str, stage: ModelStage) -> None:
        """Povýší model do dalšího stage."""
        for mv in self._models.get(name, []):
            if mv.version == version:
                mv.stage = stage
                return
        raise KeyError(f"Model {name} v{version} nenalezen")

    def get_production(self, name: str) -> ModelVersion | None:
        for mv in reversed(self._models.get(name, [])):
            if mv.stage == ModelStage.PRODUCTION:
                return mv
        return None

    def list_versions(self, name: str) -> list[ModelVersion]:
        return self._models.get(name, [])
```

---

## 4. A/B Test Infrastructure

A/B testování v ML = porovnání dvou verzí modelu na živém provozu.

```python
import hashlib
from typing import Callable

class ABTestRouter:
    """
    Deterministicky přiděluje uživatele do skupiny A nebo B.
    Stejný user_id → vždy stejná skupina (konzistentní zážitek).
    """

    def __init__(self, experiment_name: str, traffic_b: float = 0.1) -> None:
        self.experiment_name = experiment_name
        self.traffic_b = traffic_b  # podíl provozu pro variantu B (0.0–1.0)

    def assign(self, user_id: str) -> str:
        key = f"{self.experiment_name}:{user_id}".encode()
        h = int(hashlib.md5(key).hexdigest(), 16)
        bucket = (h % 1000) / 1000.0  # 0.0 – 0.999
        return "B" if bucket < self.traffic_b else "A"

    def route(
        self,
        user_id: str,
        model_a: Callable,
        model_b: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> tuple[str, Any]:
        group = self.assign(user_id)
        model = model_b if group == "B" else model_a
        return group, model(*args, **kwargs)
```

---

## 5. LLM Evaluace a metriky

Pro LLM neexistuje jednoduchá numerická loss — používáme specifické metriky.

```python
@dataclass
class LLMEvalResult:
    prompt: str
    response: str
    latency_ms: float
    input_tokens: int
    output_tokens: int
    cost_usd: float
    scores: dict[str, float] = field(default_factory=dict)

class LLMEvaluator:
    """Vyhodnocuje odpovědi LLM bez externích knihoven."""

    # Přibližné ceny (USD/1M tokenů, ilustrativní)
    PRICING: dict[str, dict[str, float]] = {
        "gpt-4o":   {"input": 2.50, "output": 10.0},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "claude-3-5-sonnet": {"input": 3.0, "output": 15.0},
    }

    def estimate_cost(self, model: str, input_t: int, output_t: int) -> float:
        p = self.PRICING.get(model, {"input": 1.0, "output": 3.0})
        return (input_t * p["input"] + output_t * p["output"]) / 1_000_000

    def score_length(self, text: str, min_words: int = 10, max_words: int = 200) -> float:
        """Penalizuje příliš krátké nebo příliš dlouhé odpovědi."""
        words = len(text.split())
        if words < min_words:
            return words / min_words
        if words > max_words:
            return max_words / words
        return 1.0

    def score_keyword_coverage(self, response: str, required: list[str]) -> float:
        """Podíl požadovaných klíčových slov přítomných v odpovědi."""
        if not required:
            return 1.0
        lower = response.lower()
        found = sum(1 for kw in required if kw.lower() in lower)
        return found / len(required)

    def score_no_refusal(self, response: str) -> float:
        """Penalizuje odmítnutí odpovědět."""
        refusals = ["i cannot", "i'm unable", "i apologize", "as an ai"]
        lower = response.lower()
        return 0.0 if any(r in lower for r in refusals) else 1.0
```

---

## 6. Cost & Latency Budgety

```python
@dataclass
class Budget:
    max_cost_usd: float
    max_latency_ms: float
    max_tokens: int

    def check(self, cost: float, latency: float, tokens: int) -> dict[str, bool]:
        return {
            "cost_ok":    cost <= self.max_cost_usd,
            "latency_ok": latency <= self.max_latency_ms,
            "tokens_ok":  tokens <= self.max_tokens,
        }

    def within_budget(self, cost: float, latency: float, tokens: int) -> bool:
        return all(self.check(cost, latency, tokens).values())
```

---

## 7. Přehled MLOps nástrojů

| Kategorie | Open-source | Cloud/SaaS |
|---|---|---|
| Experiment tracking | MLflow, DVC | W&B, Comet |
| Model registry | MLflow Registry | Vertex AI, SageMaker |
| Orchestrace | Airflow, Prefect | Kubeflow, SageMaker Pipelines |
| Monitoring | Evidently, Alibi | WhyLabs, Fiddler |
| LLM eval | RAGAS, PromptBench | Braintrust, LangSmith |
| LLM gateway | LiteLLM | Portkey, Helicone |

---

## Shrnutí

- **Experiment tracking**: zaznamenáváme hyperparams, metriky, tagy → reprodukovatelnost.
- **Model registry**: centrální verze modelů se stage přechody (candidate → staging → production).
- **A/B testování**: deterministické přiřazení uživatelů → konzistentní srovnání.
- **LLM evaluace**: bez ground truth → heuristiky (délka, klíčová slova, odmítnutí).
- **Cost & latency budgety**: tokeny stojí peníze — vždy měř, vždy omezuj.

## Cvičení

1. Rozšiř `ExperimentTracker` o perzistenci — načítání uložených runů ze souboru.
2. Implementuj `ShadowMode` — model B dostává stejné požadavky jako A, ale výsledky nejsou uživatelům vráceny (jen logování).
3. Přidej do `LLMEvaluator` scoring pomocí `difflib.SequenceMatcher` pro srovnání s referenční odpovědí.
4. Implementuj `PromptVersionRegistry` — verzování promptů s A/B testováním variant.
5. Vytvoř `CostTracker` agregující náklady per model, per uživatel, per den s alertingem při překročení limitu.
