# Program — Lekce 162: Lekce 162: Celery — distribuované task queues

Patří k lekci [Lekce 162: Celery — distribuované task queues](../162_celery.md).

## Jak spustit

```bash
python3 programy/l162_celery.py
```

## Zdrojový kód

### `l162_celery.py`

```py
"""Lekce 162 — Celery: distribuované task queues.

Spuštění (demo bez Celery):
    uv run l162_celery.py

Pro skutečné Celery:
    docker run -d --name redis -p 6379:6379 redis:7-alpine
    uv run --with celery,redis l162_celery.py
"""

import asyncio
import time
import random
from dataclasses import dataclass, field
from typing import Callable, Any
from enum import Enum


class TaskStatus(Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"


@dataclass
class TaskResult:
    task_id: str
    status: TaskStatus
    result: Any = None
    error: str = None
    retries: int = 0


class SimpleTaskQueue:
    """Jednoduchá task queue simulace bez Celery/Redis."""

    def __init__(self, workers: int = 2):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.results: dict[str, TaskResult] = {}
        self.workers_count = workers
        self._id_counter = 0

    def _next_id(self) -> str:
        self._id_counter += 1
        return f"task-{self._id_counter:04d}"

    async def submit(self, func: Callable, *args, delay: float = 0, **kwargs) -> str:
        task_id = self._next_id()
        self.results[task_id] = TaskResult(task_id, TaskStatus.PENDING)
        await self.queue.put((task_id, func, args, kwargs, delay))
        return task_id

    async def worker(self, worker_id: int):
        while True:
            task_id, func, args, kwargs, delay = await self.queue.get()
            if delay > 0:
                await asyncio.sleep(delay)
            result = self.results[task_id]
            result.status = TaskStatus.STARTED
            print(f"  [W{worker_id}] START {task_id}: {func.__name__}")
            try:
                if asyncio.iscoroutinefunction(func):
                    val = await func(*args, **kwargs)
                else:
                    val = func(*args, **kwargs)
                result.status = TaskStatus.SUCCESS
                result.result = val
                print(f"  [W{worker_id}] DONE  {task_id}: {val}")
            except Exception as e:
                result.status = TaskStatus.FAILURE
                result.error = str(e)
                print(f"  [W{worker_id}] FAIL  {task_id}: {e}")
            finally:
                self.queue.task_done()

    async def run_until_empty(self):
        workers = [asyncio.create_task(self.worker(i)) for i in range(self.workers_count)]
        await self.queue.join()
        for w in workers: w.cancel()

    def get_result(self, task_id: str) -> TaskResult:
        return self.results.get(task_id)


# Ukázkové tasky
async def posli_email(adresa: str, predmet: str) -> str:
    await asyncio.sleep(0.2)  # simulace SMTP
    return f"Email odeslan: {adresa}"

async def generuj_report(user_id: int) -> str:
    await asyncio.sleep(0.5)  # simulace těžkého výpočtu
    return f"report_{user_id}.pdf"

def secti(a: int, b: int) -> int:
    return a + b

async def nestabilni_task(task_num: int) -> str:
    if random.random() < 0.3:  # 30% selhání
        raise RuntimeError(f"Simulované selhání tasku {task_num}")
    await asyncio.sleep(0.1)
    return f"OK: task {task_num}"


async def main():
    print("=" * 50)
    print("  ⚙️  Celery Task Queue Demo")
    print("=" * 50)

    random.seed(42)
    queue = SimpleTaskQueue(workers=3)

    print("\n=== Odesílám tasky ===")
    task_ids = []

    # Různé tasky
    t1 = await queue.submit(posli_email, "anna@test.com", "Vítejte!")
    t2 = await queue.submit(posli_email, "bob@test.com", "Novinka")
    t3 = await queue.submit(generuj_report, 42)
    t4 = await queue.submit(secti, 10, 20)
    task_ids.extend([t1, t2, t3, t4])

    # Tasky se zpožděním (countdown)
    t5 = await queue.submit(posli_email, "carol@test.com", "Zpožděný", delay=0.3)
    task_ids.append(t5)

    # Nestabilní tasky
    for i in range(5):
        tid = await queue.submit(nestabilni_task, i)
        task_ids.append(tid)

    print(f"\nOdesláno {len(task_ids)} tasků na {queue.workers_count} workery")

    print("\n=== Zpracování ===")
    start = time.perf_counter()
    await queue.run_until_empty()
    t = time.perf_counter()-start

    print(f"\n=== Výsledky ({t*1000:.0f}ms) ===")
    uspech = sum(1 for tid in task_ids if queue.get_result(tid).status == TaskStatus.SUCCESS)
    selhani = sum(1 for tid in task_ids if queue.get_result(tid).status == TaskStatus.FAILURE)
    print(f"  ✅ Úspěch: {uspech}")
    print(f"  ❌ Selhání: {selhani}")

    print("\n=== Celery konfigurace (pro produkci) ===")
    print("""
# celery_app.py
from celery import Celery

app = Celery(
    "moje_app",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

@app.task(bind=True, max_retries=3)
def muj_task(self, data):
    try:
        return zpracuj(data)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2**self.request.retries)

# Spuštění workeru:
# celery -A celery_app worker --loglevel=info

# Volání:
# result = muj_task.delay(data)
# print(result.get(timeout=30))
""")

    print("✅ Demo dokončeno!")
    print("Instalace: uv add celery redis 'celery[redis]'")


if __name__ == "__main__":
    asyncio.run(main())

```
