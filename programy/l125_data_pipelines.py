"""Lekce 125 — Data Engineering Pipelines."""

from __future__ import annotations

import hashlib
import json
import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

# ── Task a DAG ───────────────────────────────────────────────────────────────

@dataclass
class Task:
    """Jeden krok v pipeline s deklarovanými závislostmi."""

    name: str
    fn: Callable[..., Any]
    depends_on: list[str] = field(default_factory=list)

    def run(self, context: dict[str, Any]) -> Any:
        deps = {dep: context[dep] for dep in self.depends_on}
        return self.fn(**deps)


class DAG:
    """Directed Acyclic Graph — orchestrátor pipeline tasků."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._tasks: dict[str, Task] = {}

    def register(self, task: Task) -> None:
        self._tasks[task.name] = task

    def topological_order(self) -> list[str]:
        """Kahn's algoritmus topologického řazení."""
        in_degree: dict[str, int] = {t: 0 for t in self._tasks}
        adj: dict[str, list[str]] = {t: [] for t in self._tasks}

        for task in self._tasks.values():
            for dep in task.depends_on:
                in_degree[task.name] += 1
                adj[dep].append(task.name)

        queue: list[str] = [n for n, d in in_degree.items() if d == 0]
        order: list[str] = []

        while queue:
            node = queue.pop(0)
            order.append(node)
            for child in adj[node]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        if len(order) != len(self._tasks):
            raise ValueError(f"DAG '{self.name}' obsahuje cyklus!")
        return order

    def run(self) -> dict[str, Any]:
        context: dict[str, Any] = {}
        print(f"\n=== Spouštím DAG: {self.name} ===")
        for name in self.topological_order():
            task = self._tasks[name]
            result = task.run(context)
            context[name] = result
            preview = repr(result)[:60]
            print(f"  ✓ {name} → {preview}")
        print(f"=== DAG '{self.name}' dokončen ===\n")
        return context


# ── Idempotentní tasky ────────────────────────────────────────────────────────

class IdempotentTask:
    """Task s cache — stejné vstupy = přeskočení výpočtu."""

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
            print(f"  ↩ {self.name}: cache hit (klíč={key})")
            return json.loads(cache_file.read_text())

        result = fn()
        cache_file.write_text(json.dumps(result, default=str))
        print(f"  ✓ {self.name}: vypočítáno a uloženo (klíč={key})")
        return result


# ── Backfill pattern ──────────────────────────────────────────────────────────

def date_range(
    start: datetime.date,
    end: datetime.date,
) -> list[datetime.date]:
    """Vrátí seznam datumů od start do end (včetně)."""
    dates: list[datetime.date] = []
    current = start
    while current <= end:
        dates.append(current)
        current += datetime.timedelta(days=1)
    return dates


def backfill(
    pipeline_fn: Callable[[datetime.date], dict[str, Any]],
    start: datetime.date,
    end: datetime.date,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Retroaktivně spustí pipeline pro každý den v rozsahu."""
    print(f"\n=== Backfill: {start} → {end} {'[DRY RUN]' if dry_run else ''} ===")
    results: list[dict[str, Any]] = []
    for d in date_range(start, end):
        if dry_run:
            print(f"  [DRY RUN] {d.isoformat()} — přeskočeno")
        else:
            print(f"  → {d.isoformat()}", end="")
            result = pipeline_fn(d)
            results.append(result)
            print(f" ✓ ({result.get('rows_processed', '?')} řádků)")
    print(f"=== Backfill dokončen: {len(results)} dní zpracováno ===\n")
    return results


# ── Data Lineage ───────────────────────────────────────────────────────────────

@dataclass
class LineageNode:
    """Uzel grafu lineage — jedna datová entita."""

    name: str
    source_tables: list[str] = field(default_factory=list)
    transformation: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat(timespec="seconds")
    )
    row_count: int = 0


class LineageTracker:
    """Sleduje původ dat a umožňuje impact analysis."""

    def __init__(self) -> None:
        self._graph: dict[str, LineageNode] = {}

    def record(self, node: LineageNode) -> None:
        self._graph[node.name] = node

    def trace(self, name: str, depth: int = 0) -> None:
        """Rekurzivně zobrazí lineage strom."""
        node = self._graph.get(name)
        indent = "  " * depth
        if not node:
            print(f"{indent}[neznámý zdroj: {name}]")
            return
        print(f"{indent}→ {node.name} ({node.row_count:,} řádků, {node.created_at})")
        if node.transformation:
            print(f"{indent}  transformace: {node.transformation}")
        for src in node.source_tables:
            self.trace(src, depth + 1)

    def impact_analysis(self, source: str) -> list[str]:
        """Které tabulky závisí na daném zdroji?"""
        return [
            name
            for name, node in self._graph.items()
            if source in node.source_tables
        ]

    def export_json(self) -> str:
        """Exportuje celý lineage graf jako JSON."""
        data = {
            name: {
                "sources": node.source_tables,
                "transformation": node.transformation,
                "row_count": node.row_count,
                "created_at": node.created_at,
            }
            for name, node in self._graph.items()
        }
        return json.dumps(data, indent=2, ensure_ascii=False)


# ── Ukázková pipeline ─────────────────────────────────────────────────────────

def demo_dag() -> None:
    print("=== DEMO 1: Základní DAG pipeline ===")

    def extract() -> list[dict[str, Any]]:
        return [{"id": i, "amount": i * 10, "currency": "CZK"} for i in range(1, 8)]

    def validate(extract: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [r for r in extract if r["amount"] > 0]

    def transform(validate: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {"id": r["id"], "amount_eur": round(r["amount"] * 0.04, 2)}
            for r in validate
        ]

    def aggregate(transform: list[dict[str, Any]]) -> dict[str, Any]:
        total = sum(r["amount_eur"] for r in transform)
        return {"count": len(transform), "total_eur": round(total, 2)}

    def load(aggregate: dict[str, Any]) -> str:
        return (
            f"Načteno do warehouse: {aggregate['count']} záznamů, "
            f"celkem {aggregate['total_eur']} EUR"
        )

    dag = DAG("sales_pipeline")
    dag.register(Task("extract", extract))
    dag.register(Task("validate", validate, depends_on=["extract"]))
    dag.register(Task("transform", transform, depends_on=["validate"]))
    dag.register(Task("aggregate", aggregate, depends_on=["transform"]))
    dag.register(Task("load", load, depends_on=["aggregate"]))

    context = dag.run()
    print("Výsledek:", context["load"])


def demo_idempotent() -> None:
    print("=== DEMO 2: Idempotentní tasky ===")
    task = IdempotentTask("daily_aggregate")
    params = {"date": "2024-01-15", "table": "orders"}

    result1 = task.run_once(params, fn=lambda: {"sum_czk": 42_000, "count": 123})
    result2 = task.run_once(params, fn=lambda: {"sum_czk": 42_000, "count": 123})

    print(f"  Výsledek 1: {result1}")
    print(f"  Výsledek 2: {result2}")
    print(f"  Shodné: {result1 == result2}\n")


def demo_backfill() -> None:
    print("=== DEMO 3: Backfill pattern ===")

    def daily_pipeline(run_date: datetime.date) -> dict[str, Any]:
        base = (run_date - datetime.date(2024, 1, 1)).days + 1
        return {
            "date": run_date.isoformat(),
            "rows_processed": base * 100,
            "status": "ok",
        }

    # Nejprve dry run
    backfill(
        daily_pipeline,
        start=datetime.date(2024, 1, 1),
        end=datetime.date(2024, 1, 3),
        dry_run=True,
    )

    # Pak skutečný backfill
    results = backfill(
        daily_pipeline,
        start=datetime.date(2024, 1, 1),
        end=datetime.date(2024, 1, 3),
    )
    total_rows = sum(r["rows_processed"] for r in results)
    print(f"  Celkem zpracováno řádků: {total_rows:,}\n")


def demo_lineage() -> None:
    print("=== DEMO 4: Data Lineage ===")

    tracker = LineageTracker()
    tracker.record(LineageNode(
        "raw_orders",
        source_tables=[],
        transformation="LOAD FROM S3",
        row_count=50_000,
    ))
    tracker.record(LineageNode(
        "cleaned_orders",
        source_tables=["raw_orders"],
        transformation="dedup + null removal + type casting",
        row_count=48_200,
    ))
    tracker.record(LineageNode(
        "enriched_orders",
        source_tables=["cleaned_orders"],
        transformation="JOIN s customers",
        row_count=48_200,
    ))
    tracker.record(LineageNode(
        "daily_revenue",
        source_tables=["enriched_orders"],
        transformation="GROUP BY date, SUM(amount)",
        row_count=365,
    ))
    tracker.record(LineageNode(
        "monthly_report",
        source_tables=["daily_revenue"],
        transformation="RESAMPLE monthly",
        row_count=12,
    ))

    print("Lineage pro 'monthly_report':")
    tracker.trace("monthly_report")

    print("\nImpact analysis — co závisí na 'cleaned_orders'?")
    affected = tracker.impact_analysis("cleaned_orders")
    print(f"  Ovlivněné tabulky: {affected}")

    print("\nExport JSON (zkráceno):")
    export = json.loads(tracker.export_json())
    for name, info in list(export.items())[:2]:
        print(f"  {name}: {info['row_count']:,} řádků")
    print()


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    demo_dag()
    demo_idempotent()
    demo_backfill()
    demo_lineage()
    print("Hotovo! Všechny demo sekce lekce 125 proběhly úspěšně.")


if __name__ == "__main__":
    main()
