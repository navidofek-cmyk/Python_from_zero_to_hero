# Program — Lekce 127: Lekce 127 — MLOps a LLMOps

Patří k lekci [Lekce 127 — MLOps a LLMOps](../127_mlops_llmops.md).

## Jak spustit

```bash
python3 programy/l127_mlops_llmops.py
```

## Zdrojový kód

### `l127_mlops_llmops.py`

```py
"""Lekce 127 — MLOps a LLMOps."""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Callable

# ── Experiment Tracking ───────────────────────────────────────────────────────

@dataclass
class Run:
    """Jeden experimentální run s parametry a metrikami."""

    run_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, list[float]] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)
    status: str = "running"
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None

    def log_param(self, key: str, value: Any) -> None:
        self.params[key] = value

    def log_metric(self, key: str, value: float) -> None:
        self.metrics.setdefault(key, []).append(round(value, 6))

    def finish(self, status: str = "completed") -> None:
        self.status = status
        self.end_time = time.time()

    @property
    def duration(self) -> float | None:
        if self.end_time:
            return round(self.end_time - self.start_time, 4)
        return None

    def best_metric(self, key: str, mode: str = "min") -> float | None:
        values = self.metrics.get(key)
        if not values:
            return None
        return min(values) if mode == "min" else max(values)


class ExperimentTracker:
    """Tracker ukládající runy do JSON souboru."""

    def __init__(self, store_path: Path = Path("/tmp/mlops_runs.json")) -> None:
        self.store_path = store_path
        self._runs: dict[str, Run] = {}

    def start_run(self, name: str, tags: dict[str, str] | None = None) -> Run:
        run = Run(name=name, tags=tags or {})
        self._runs[run.run_id] = run
        return run

    def save(self) -> None:
        data = {rid: asdict(r) for rid, r in self._runs.items()}
        self.store_path.write_text(json.dumps(data, indent=2, default=str))

    def compare(self, metric: str, mode: str = "min") -> list[dict[str, Any]]:
        rows = [
            {
                "run_id": r.run_id,
                "name": r.name,
                "status": r.status,
                metric: r.best_metric(metric, mode),
                "duration_s": r.duration,
                "params": r.params,
            }
            for r in self._runs.values()
            if r.best_metric(metric, mode) is not None
        ]
        reverse = mode == "max"
        return sorted(rows, key=lambda x: x[metric] or 0, reverse=reverse)

    def best_run(self, metric: str, mode: str = "min") -> Run | None:
        completed = [
            r for r in self._runs.values()
            if r.status == "completed" and r.metrics.get(metric)
        ]
        if not completed:
            return None
        if mode == "min":
            return min(completed, key=lambda r: r.best_metric(metric, mode) or float("inf"))
        return max(completed, key=lambda r: r.best_metric(metric, mode) or 0.0)


# ── Model Registry ────────────────────────────────────────────────────────────

class ModelStage(str, Enum):
    CANDIDATE  = "candidate"
    STAGING    = "staging"
    PRODUCTION = "production"
    ARCHIVED   = "archived"


@dataclass
class ModelVersion:
    """Verze ML modelu v registru."""

    name: str
    version: str
    run_id: str
    stage: ModelStage = ModelStage.CANDIDATE
    metrics: dict[str, float] = field(default_factory=dict)
    description: str = ""
    registered_at: str = field(
        default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S")
    )


class ModelRegistry:
    """Centrální úložiště verzí modelů."""

    def __init__(self) -> None:
        self._models: dict[str, list[ModelVersion]] = {}

    def register(self, model: ModelVersion) -> None:
        self._models.setdefault(model.name, []).append(model)
        print(f"  Zaregistrován: {model.name} v{model.version} [{model.stage.value}]")

    def promote(self, name: str, version: str, stage: ModelStage) -> None:
        for mv in self._models.get(name, []):
            if mv.version == version:
                old = mv.stage.value
                mv.stage = stage
                print(f"  Povýšen: {name} v{version} {old} → {stage.value}")
                return
        raise KeyError(f"Model {name} v{version} nenalezen")

    def get_production(self, name: str) -> ModelVersion | None:
        for mv in reversed(self._models.get(name, [])):
            if mv.stage == ModelStage.PRODUCTION:
                return mv
        return None

    def list_versions(self, name: str) -> list[ModelVersion]:
        return self._models.get(name, [])


# ── A/B Test Router ───────────────────────────────────────────────────────────

class ABTestRouter:
    """Deterministické přiřazení uživatelů do skupin A/B."""

    def __init__(self, experiment_name: str, traffic_b: float = 0.1) -> None:
        self.experiment_name = experiment_name
        self.traffic_b = traffic_b

    def assign(self, user_id: str) -> str:
        key = f"{self.experiment_name}:{user_id}".encode()
        bucket = (int(hashlib.md5(key).hexdigest(), 16) % 1000) / 1000.0
        return "B" if bucket < self.traffic_b else "A"

    def route(
        self,
        user_id: str,
        model_a: Callable[..., Any],
        model_b: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> tuple[str, Any]:
        group = self.assign(user_id)
        model = model_b if group == "B" else model_a
        return group, model(*args, **kwargs)

    def distribution(self, user_ids: list[str]) -> dict[str, int]:
        dist: dict[str, int] = {"A": 0, "B": 0}
        for uid in user_ids:
            dist[self.assign(uid)] += 1
        return dist


# ── LLM Evaluátor ─────────────────────────────────────────────────────────────

@dataclass
class LLMResponse:
    """Odpověď od LLM s metadaty."""

    prompt: str
    response: str
    model: str
    latency_ms: float
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class LLMEvaluator:
    """Vyhodnocuje odpovědi LLM pomocí heuristik."""

    PRICING: dict[str, dict[str, float]] = {
        "gpt-4o":            {"input": 2.50,  "output": 10.00},
        "gpt-4o-mini":       {"input": 0.15,  "output": 0.60},
        "claude-3-5-sonnet": {"input": 3.00,  "output": 15.00},
        "claude-3-haiku":    {"input": 0.25,  "output": 1.25},
    }

    def estimate_cost(self, model: str, input_t: int, output_t: int) -> float:
        p = self.PRICING.get(model, {"input": 1.0, "output": 3.0})
        return round((input_t * p["input"] + output_t * p["output"]) / 1_000_000, 8)

    def score_length(
        self, text: str, min_words: int = 10, max_words: int = 200
    ) -> float:
        words = len(text.split())
        if words < min_words:
            return round(words / min_words, 3)
        if words > max_words:
            return round(max_words / words, 3)
        return 1.0

    def score_keyword_coverage(
        self, response: str, required: list[str]
    ) -> float:
        if not required:
            return 1.0
        lower = response.lower()
        found = sum(1 for kw in required if kw.lower() in lower)
        return round(found / len(required), 3)

    def score_no_refusal(self, response: str) -> float:
        refusals = ["i cannot", "i'm unable", "i apologize", "as an ai", "nemohu", "nedokáži"]
        lower = response.lower()
        return 0.0 if any(r in lower for r in refusals) else 1.0

    def evaluate(
        self,
        resp: LLMResponse,
        required_keywords: list[str] | None = None,
    ) -> dict[str, Any]:
        cost = self.estimate_cost(resp.model, resp.input_tokens, resp.output_tokens)
        length_score = self.score_length(resp.response)
        keyword_score = self.score_keyword_coverage(resp.response, required_keywords or [])
        refusal_score = self.score_no_refusal(resp.response)
        overall = round((length_score + keyword_score + refusal_score) / 3, 3)

        return {
            "model": resp.model,
            "latency_ms": resp.latency_ms,
            "total_tokens": resp.total_tokens,
            "cost_usd": cost,
            "scores": {
                "length": length_score,
                "keyword_coverage": keyword_score,
                "no_refusal": refusal_score,
                "overall": overall,
            },
        }


# ── Cost & Latency Budget ─────────────────────────────────────────────────────

@dataclass
class Budget:
    """Definice limitů pro LLM volání."""

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

    def report(self, cost: float, latency: float, tokens: int) -> str:
        checks = self.check(cost, latency, tokens)
        lines = [
            f"  cost:    ${cost:.6f} / ${self.max_cost_usd:.6f}  {'✓' if checks['cost_ok'] else '✗'}",
            f"  latency: {latency:.0f}ms / {self.max_latency_ms:.0f}ms  {'✓' if checks['latency_ok'] else '✗'}",
            f"  tokens:  {tokens} / {self.max_tokens}  {'✓' if checks['tokens_ok'] else '✗'}",
        ]
        return "\n".join(lines)


# ── Demo funkce ───────────────────────────────────────────────────────────────

def demo_experiment_tracking() -> None:
    print("=== DEMO 1: Experiment Tracking ===")
    tracker = ExperimentTracker()

    configs = [
        {"lr": 0.01, "depth": 3, "loss_vals": [0.8, 0.6, 0.45, 0.38]},
        {"lr": 0.001, "depth": 5, "loss_vals": [0.9, 0.7, 0.5, 0.35]},
        {"lr": 0.1, "depth": 2, "loss_vals": [0.7, 0.55, 0.5, 0.48]},
    ]

    for cfg in configs:
        run = tracker.start_run(
            name=f"lr={cfg['lr']}_depth={cfg['depth']}",
            tags={"framework": "numpy", "dataset": "cifar10"},
        )
        run.log_param("learning_rate", cfg["lr"])
        run.log_param("max_depth", cfg["depth"])
        for v in cfg["loss_vals"]:
            run.log_metric("val_loss", v)
        run.finish()

    print("  Srovnání runů (val_loss, ascendentně):")
    for row in tracker.compare("val_loss"):
        print(
            f"    {row['name']:30s}  val_loss={row['val_loss']:.4f}  "
            f"({row['duration_s']:.4f}s)"
        )

    best = tracker.best_run("val_loss", mode="min")
    if best:
        print(f"  Nejlepší run: {best.name} (val_loss={best.best_metric('val_loss'):.4f})\n")


def demo_model_registry() -> None:
    print("=== DEMO 2: Model Registry ===")
    registry = ModelRegistry()

    v1 = ModelVersion(
        name="churn_predictor",
        version="1.0.0",
        run_id="abc123",
        metrics={"auc": 0.82, "f1": 0.75},
        description="Baseline logistická regrese",
    )
    v2 = ModelVersion(
        name="churn_predictor",
        version="1.1.0",
        run_id="def456",
        metrics={"auc": 0.87, "f1": 0.80},
        description="Gradient boosting — lepší features",
    )

    registry.register(v1)
    registry.register(v2)
    registry.promote("churn_predictor", "1.0.0", ModelStage.ARCHIVED)
    registry.promote("churn_predictor", "1.1.0", ModelStage.STAGING)
    registry.promote("churn_predictor", "1.1.0", ModelStage.PRODUCTION)

    prod = registry.get_production("churn_predictor")
    if prod:
        print(f"  Produkční model: {prod.name} v{prod.version}, AUC={prod.metrics.get('auc')}\n")


def demo_ab_test() -> None:
    print("=== DEMO 3: A/B Test Router ===")
    router = ABTestRouter("price_sensitivity_v2", traffic_b=0.2)

    def model_a(user_id: str) -> dict:
        return {"price": 299, "discount": 0}

    def model_b(user_id: str) -> dict:
        return {"price": 249, "discount": 50}

    users = [f"user_{i:04d}" for i in range(50)]
    results: dict[str, list[dict]] = {"A": [], "B": []}

    for uid in users[:5]:
        group, result = router.route(uid, model_a, model_b, uid)
        print(f"  {uid} → skupina {group}: {result}")

    dist = router.distribution(users)
    total = sum(dist.values())
    print(f"\n  Distribuce (n={total}): A={dist['A']} ({dist['A']/total:.0%}), B={dist['B']} ({dist['B']/total:.0%})")
    print(f"  Cílená B alokace: {router.traffic_b:.0%}\n")


def demo_llm_evaluator() -> None:
    print("=== DEMO 4: LLM Evaluace ===")
    evaluator = LLMEvaluator()

    responses = [
        LLMResponse(
            prompt="Vysvětli mi Python dataclasses.",
            response=(
                "Python dataclasses jsou dekorátory, které automaticky generují "
                "__init__, __repr__ a __eq__ metody. Používáte je pro jednoduché "
                "datové kontejnery. Příklad: @dataclass class Point: x: float; y: float"
            ),
            model="gpt-4o-mini",
            latency_ms=320,
            input_tokens=25,
            output_tokens=58,
        ),
        LLMResponse(
            prompt="Vysvětli mi Python dataclasses.",
            response="Nemohu na tuto otázku odpovědět.",
            model="gpt-4o-mini",
            latency_ms=150,
            input_tokens=25,
            output_tokens=8,
        ),
        LLMResponse(
            prompt="Vysvětli mi Python dataclasses.",
            response=(
                "Dataclasses jsou skvělé. Python dataclasses dekorátor. "
                "Automatické metody jako __init__. Moderní Python. Typing podpora."
            ),
            model="claude-3-haiku",
            latency_ms=210,
            input_tokens=25,
            output_tokens=22,
        ),
    ]

    for i, resp in enumerate(responses, 1):
        result = evaluator.evaluate(resp, required_keywords=["dataclass", "__init__"])
        scores = result["scores"]
        print(
            f"  Odpověď #{i} [{resp.model}]: "
            f"overall={scores['overall']:.3f}, "
            f"délka={scores['length']:.2f}, "
            f"klíčová slova={scores['keyword_coverage']:.2f}, "
            f"bez odmítnutí={scores['no_refusal']:.1f}, "
            f"cost=${result['cost_usd']:.6f}"
        )
    print()


def demo_budget() -> None:
    print("=== DEMO 5: Cost & Latency Budgety ===")
    budget = Budget(max_cost_usd=0.001, max_latency_ms=500.0, max_tokens=500)

    calls = [
        {"cost": 0.0005, "latency": 320, "tokens": 200},
        {"cost": 0.0015, "latency": 480, "tokens": 450},
        {"cost": 0.0008, "latency": 620, "tokens": 300},
    ]

    for i, call in enumerate(calls, 1):
        within = budget.within_budget(call["cost"], call["latency"], call["tokens"])
        status = "V ROZPOČTU" if within else "PŘEKROČEN"
        print(f"  Volání #{i} — {status}:")
        print(budget.report(call["cost"], call["latency"], call["tokens"]))
        print()


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    demo_experiment_tracking()
    demo_model_registry()
    demo_ab_test()
    demo_llm_evaluator()
    demo_budget()
    print("Hotovo! Všechny demo sekce lekce 127 proběhly úspěšně.")


if __name__ == "__main__":
    main()

```
