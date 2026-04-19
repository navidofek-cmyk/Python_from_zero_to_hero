# Lekce 125 — Data Engineering Pipelines

Data engineering pipelines jsou páteří každého analytického systému. V této lekci si ukážeme,
jak navrhnout DAG-based pipeline v čistém Pythonu, zajistit idempotenci tasků,
implementovat backfill pattern a sledovat lineage (původ dat).

---

## 1. Co je pipeline a DAG?

**Pipeline** je řetězec transformačních kroků, kde výstup jednoho kroku je vstupem dalšího.
**DAG** (Directed Acyclic Graph) rozšiřuje tuto myšlenku o větvení a závislosti — každý task
má nula nebo více předchůdců, cyklus není povolen.

```
extract_sales ──► normalize ──► aggregate ──► load_warehouse
                     │
                     └──► validate ──► send_report
```

Populární nástroje: Apache Airflow, Prefect, Dagster, Mage. My si celý mechanismus
implementujeme sami v čistém Pythonu.

---

## 2. Základní stavební kameny

### Task

Každý task je callable s metadaty: jméno, závislosti, funkce.

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Any

@dataclass
class Task:
    name: str
    fn: Callable[..., Any]
    depends_on: list[str] = field(default_factory=list)

    def run(self, context: dict[str, Any]) -> Any:
        deps = {dep: context[dep] for dep in self.depends_on}
        return self.fn(**deps)
```

### DAG

```python
class DAG:
    def __init__(self, name: str) -> None:
        self.name = name
        self._tasks: dict[str, Task] = {}

    def register(self, task: Task) -> None:
        self._tasks[task.name] = task

    def topological_order(self) -> list[str]:
        """Kahn's algoritmus — vrátí tasky v topologickém pořadí."""
        in_degree: dict[str, int] = {t: 0 for t in self._tasks}
        for task in self._tasks.values():
            for dep in task.depends_on:
                in_degree[task.name] += 1

        queue = [name for name, deg in in_degree.items() if deg == 0]
        order: list[str] = []
        adj: dict[str, list[str]] = {t: [] for t in self._tasks}
        for task in self._tasks.values():
            for dep in task.depends_on:
                adj[dep].append(task.name)

        while queue:
            node = queue.pop(0)
            order.append(node)
            for child in adj[node]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        if len(order) != len(self._tasks):
            raise ValueError("DAG obsahuje cyklus!")
        return order

    def run(self) -> dict[str, Any]:
        context: dict[str, Any] = {}
        for name in self.topological_order():
            task = self._tasks[name]
            result = task.run(context)
            context[name] = result
            print(f"  ✓ {name} → {repr(result)[:60]}")
        return context
```

---

## 3. Idempotentní tasky

Idempotence znamená: spustit task vícekrát se stejným výsledkem jako spustit ho jednou.
Klíčový koncept pro spolehlivé pipeline.

```python
import hashlib, json, os
from pathlib import Path

class IdempotentTask:
    """Task, který přeskočí práci, pokud výsledek již existuje."""

    def __init__(self, name: str, cache_dir: Path = Path("/tmp/pipeline_cache")) -> None:
        self.name = name
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, params: dict[str, Any]) -> str:
        payload = json.dumps(params, sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()[:16]

    def run_once(self, params: dict[str, Any], fn: Callable[[], Any]) -> Any:
        key = self._cache_key(params)
        cache_file = self.cache_dir / f"{self.name}_{key}.json"

        if cache_file.exists():
            print(f"  ↩ {self.name}: cache hit ({key})")
            return json.loads(cache_file.read_text())

        result = fn()
        cache_file.write_text(json.dumps(result))
        print(f"  ✓ {self.name}: vypočítáno a uloženo ({key})")
        return result
```

### Příklad použití

```python
task = IdempotentTask("aggregate_daily")
result = task.run_once(
    params={"date": "2024-01-15", "table": "orders"},
    fn=lambda: {"sum": 42000, "count": 123}
)
# Druhé spuštění se stejnými params vrátí cache hit
result2 = task.run_once(
    params={"date": "2024-01-15", "table": "orders"},
    fn=lambda: {"sum": 42000, "count": 123}
)
```

---

## 4. Backfill pattern

Backfill = retroaktivní spuštění pipeline pro historická data (např. při opravě chyby nebo
nasazení nové metriky).

```python
from datetime import date, timedelta

def date_range(start: date, end: date) -> list[date]:
    """Generuje seznam datumů od start do end (včetně)."""
    current = start
    dates: list[date] = []
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)
    return dates

def backfill(
    pipeline_fn: Callable[[date], dict[str, Any]],
    start: date,
    end: date,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Spustí pipeline pro každý datum v rozsahu."""
    results: list[dict[str, Any]] = []
    for d in date_range(start, end):
        if dry_run:
            print(f"  [DRY RUN] by spustil: {d.isoformat()}")
        else:
            print(f"  → Spouštím pipeline pro {d.isoformat()}")
            result = pipeline_fn(d)
            results.append(result)
    return results
```

### Příklad backfillu

```python
def my_daily_pipeline(run_date: date) -> dict[str, Any]:
    # Simulace: zpracování dat pro daný datum
    return {
        "date": run_date.isoformat(),
        "rows_processed": 1000,
        "status": "ok",
    }

results = backfill(
    my_daily_pipeline,
    start=date(2024, 1, 1),
    end=date(2024, 1, 5),
)
```

---

## 5. Data Lineage — sledování původu dat

Lineage říká: "odkud tento výsledek pochází?" Umožňuje audit, debugging a impact analysis.

```python
from dataclasses import dataclass, field
import datetime

@dataclass
class LineageNode:
    name: str
    source_tables: list[str] = field(default_factory=list)
    transformation: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat(timespec="seconds")
    )
    row_count: int = 0

class LineageTracker:
    def __init__(self) -> None:
        self._graph: dict[str, LineageNode] = {}

    def record(self, node: LineageNode) -> None:
        self._graph[node.name] = node

    def trace(self, name: str, depth: int = 0) -> None:
        """Rekurzivně vypíše lineage stromu."""
        node = self._graph.get(name)
        if not node:
            print("  " * depth + f"[neznámý zdroj: {name}]")
            return
        prefix = "  " * depth
        print(f"{prefix}→ {node.name} ({node.row_count} řádků, {node.created_at})")
        if node.transformation:
            print(f"{prefix}  transformace: {node.transformation}")
        for src in node.source_tables:
            self.trace(src, depth + 1)

    def impact_analysis(self, source: str) -> list[str]:
        """Které tabulky by byly ovlivněny změnou source?"""
        affected: list[str] = []
        for name, node in self._graph.items():
            if source in node.source_tables:
                affected.append(name)
        return affected
```

### Příklad

```python
tracker = LineageTracker()
tracker.record(LineageNode("raw_orders", source_tables=[], row_count=50_000))
tracker.record(LineageNode(
    "cleaned_orders",
    source_tables=["raw_orders"],
    transformation="dedup + null removal",
    row_count=48_000,
))
tracker.record(LineageNode(
    "daily_revenue",
    source_tables=["cleaned_orders"],
    transformation="GROUP BY date, SUM(amount)",
    row_count=365,
))

tracker.trace("daily_revenue")
# → daily_revenue (365 řádků, ...)
#   transformace: GROUP BY date, SUM(amount)
#   → cleaned_orders (48000 řádků, ...)
#     transformace: dedup + null removal
#     → raw_orders (50000 řádků, ...)

print(tracker.impact_analysis("raw_orders"))
# ['cleaned_orders']
```

---

## 6. Kompletní mini-pipeline

```python
# Definice tasků
def extract() -> list[dict]:
    return [{"id": i, "amount": i * 10} for i in range(1, 6)]

def validate(extract: list[dict]) -> list[dict]:
    return [r for r in extract if r["amount"] > 0]

def transform(validate: list[dict]) -> list[dict]:
    return [{"id": r["id"], "amount_eur": r["amount"] * 0.92} for r in validate]

def load(transform: list[dict]) -> str:
    return f"Načteno {len(transform)} záznamů do warehouse"

dag = DAG("sales_pipeline")
dag.register(Task("extract", extract))
dag.register(Task("validate", validate, depends_on=["extract"]))
dag.register(Task("transform", transform, depends_on=["validate"]))
dag.register(Task("load", load, depends_on=["transform"]))

context = dag.run()
print(context["load"])
```

---

## 7. Srovnání přístupů

| Přístup | Výhody | Nevýhody |
|---|---|---|
| Čistý Python DAG | Žádné závislosti, plná kontrola | Bez UI, scheduleru |
| Apache Airflow | Webové UI, scheduler, retry | Těžká instalace, Pythonic API |
| Prefect | Moderní API, cloud | Závislost na cloudu |
| Dagster | Assets-first, type safety | Strmá křivka učení |
| Mage | Notebook-friendly | Méně vyspělý ekosystém |

---

## Shrnutí

- **DAG** popisuje závislosti mezi tasky; topologické řazení zajistí správné pořadí.
- **Idempotence** = spustit task vícekrát je stejné jako jednou — klíčové pro recovery.
- **Backfill** umožňuje retroaktivní zpracování historických dat.
- **Lineage** sleduje původ dat a pomáhá s auditováním a debuggingem.
- Všechny tyto koncepty lze implementovat v čistém Pythonu bez externích závislostí.

## Cvičení

1. Rozšiř `DAG` o podporu paralelního spouštění nezávislých tasků (`ThreadPoolExecutor`).
2. Přidej do `LineageTracker` metodu `export_dot()`, která vygeneruje Graphviz DOT formát.
3. Implementuj `BackfillManager` s persistencí stavu (které dny již byly zpracovány) do JSON souboru.
4. Přidej do tasků měření doby běhu a výpis statistik po dokončení pipeline.
5. Implementuj `retry` dekorátor pro tasky, který při chybě zopakuje task N-krát s exponenciálním backoffem.
