# Program — Lekce 173: Lekce 173: Apache Airflow — orchestrace pipelines

Patří k lekci [Lekce 173: Apache Airflow — orchestrace pipelines](../173_airflow.md).

## Jak spustit

```bash
python3 programy/l173_airflow.py
```

## Zdrojový kód

### `l173_airflow.py`

```py
"""Lekce 173 — Apache Airflow: orchestrace pipelines.
Spuštění: uv run l173_airflow.py
Pro skutečný Airflow: uv add apache-airflow && airflow standalone
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Callable, Any


@dataclass
class TaskResult:
    task_id: str
    result: Any = None
    error: str = None
    duration: float = 0.0
    ok: bool = True


class SimpleDAG:
    """Jednoduchá simulace Airflow DAG bez skutečného Airflow."""

    def __init__(self, dag_id: str):
        self.dag_id = dag_id
        self.tasks: dict[str, Callable] = {}
        self.deps: dict[str, list[str]] = {}

    def task(self, task_id: str, depends_on: list[str] = None):
        def decorator(func):
            self.tasks[task_id] = func
            self.deps[task_id] = depends_on or []
            return func
        return decorator

    async def run(self) -> dict[str, TaskResult]:
        results: dict[str, TaskResult] = {}
        completed: set[str] = set()

        async def run_task(task_id: str):
            # Čekej na závislosti
            while not all(d in completed for d in self.deps[task_id]):
                await asyncio.sleep(0.01)
            start = time.perf_counter()
            try:
                context = {"ds": "2026-05-02", "task_id": task_id, "results": results}
                result = self.tasks[task_id](context)
                dur = time.perf_counter() - start
                results[task_id] = TaskResult(task_id, result, duration=dur)
                completed.add(task_id)
                print(f"  ✅ {task_id} ({dur*1000:.0f}ms): {str(result)[:60]}")
            except Exception as e:
                results[task_id] = TaskResult(task_id, error=str(e), ok=False)
                completed.add(task_id)
                print(f"  ❌ {task_id}: {e}")

        await asyncio.gather(*[run_task(t) for t in self.tasks])
        return results


def demo_etl_dag():
    print("\n=== ETL Pipeline DAG ===")
    dag = SimpleDAG("etl_pipeline")

    @dag.task("extrakce")
    def extrakce(ctx):
        time.sleep(0.1)
        return {"radku": 42000, "soubor": f"data_{ctx['ds']}.parquet"}

    @dag.task("transformace", depends_on=["extrakce"])
    def transformace(ctx):
        data = ctx["results"]["extrakce"].result
        time.sleep(0.15)
        return f"transformed_{data['soubor']}"

    @dag.task("validace", depends_on=["extrakce"])
    def validace(ctx):
        data = ctx["results"]["extrakce"].result
        assert data["radku"] > 0
        return f"validated: {data['radku']} řádků OK"

    @dag.task("nahrani", depends_on=["transformace", "validace"])
    def nahrani(ctx):
        soubor = ctx["results"]["transformace"].result
        time.sleep(0.05)
        return f"Nahráno do DWH: {soubor}"

    results = asyncio.run(dag.run())
    uspesne = sum(1 for r in results.values() if r.ok)
    print(f"\n  Celkem: {uspesne}/{len(results)} tasků úspěšných")


def demo_sensor():
    print("\n=== Sensor simulace ===")
    import os, tempfile

    # Vytvoř soubor po 2 sekundách
    cesta = tempfile.mktemp(suffix=".csv")

    def file_sensor(target_path, max_checks=5):
        for i in range(max_checks):
            if os.path.exists(target_path):
                print(f"    ✅ Soubor nalezen po {i+1} pokusech")
                return True
            print(f"    ⏳ Pokus {i+1}: soubor nenalezen, čekám...")
            time.sleep(0.2)
            if i == 2:  # vytvoř soubor při 3. pokusu
                open(target_path, "w").close()
        return False

    file_sensor(cesta)
    if os.path.exists(cesta):
        os.unlink(cesta)


def main():
    print("=" * 50)
    print("  🌊 Apache Airflow Demo")
    print("=" * 50)
    demo_etl_dag()
    demo_sensor()
    print("\n✅ Demo dokončeno!")
    print("Instalace: uv add apache-airflow")
    print("Start:     airflow standalone → http://localhost:8080")


if __name__ == "__main__":
    main()

```
