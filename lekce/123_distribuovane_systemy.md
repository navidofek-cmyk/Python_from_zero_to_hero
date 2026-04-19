# Lekce 123: Distribuované systémy

Distribuované systémy jsou složité — sítě selhávají, zprávy se duplikují, hodiny nejsou synchronizovány. Tato lekce pokrývá základní vzory a jak je simulovat v Pythonu.

---

## Message Broker Pattern

Message broker odděluje producenty od konzumentů. Producent nezná konzumenty — jen pošle zprávu do fronty/topiku.

```
Producent → [Message Broker / Queue] → Konzument A
                                     → Konzument B
```

Simulace v Pythonu s `queue.Queue`:

```python
import queue
import threading
import time
from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class Zprava:
    id_: str = field(default_factory=lambda: str(uuid4())[:8])
    payload: str = ""
    retry_count: int = 0

def producent(broker: queue.Queue[Zprava], pocet: int) -> None:
    for i in range(pocet):
        z = Zprava(payload=f"data_{i}")
        broker.put(z)
        print(f"[Producent] Odesláno: {z.id_} — {z.payload}")
        time.sleep(0.05)

def konzument(broker: queue.Queue[Zprava], id_: int) -> None:
    while True:
        try:
            z = broker.get(timeout=1.0)
            print(f"  [Konzument {id_}] Přijato: {z.id_}")
            broker.task_done()
        except queue.Empty:
            break

broker: queue.Queue[Zprava] = queue.Queue()
p = threading.Thread(target=producent, args=(broker, 10))
k1 = threading.Thread(target=konzument, args=(broker, 1))
k2 = threading.Thread(target=konzument, args=(broker, 2))
for t in [p, k1, k2]:
    t.start()
for t in [p, k1, k2]:
    t.join()
```

---

## Celery-like Worker Pattern

Celery je populární task queue. Simulujeme základní vzor: task producer + worker pool + result storage.

```python
import queue
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable
from uuid import uuid4

@dataclass
class Task:
    id_: str = field(default_factory=lambda: str(uuid4())[:8])
    fn_name: str = ""
    args: tuple[Any, ...] = ()

@dataclass
class TaskResult:
    task_id: str
    vysledek: Any = None
    chyba: str | None = None

class TaskQueue:
    def __init__(self) -> None:
        self._fronta: queue.Queue[Task] = queue.Queue()
        self._vysledky: dict[str, TaskResult] = {}
        self._zamek = threading.Lock()
        self._funkce: dict[str, Callable[..., Any]] = {}

    def registruj(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Dekorátor: zaregistruje funkci jako task."""
        self._funkce[fn.__name__] = fn
        return fn

    def odeslat(self, fn_name: str, *args: Any) -> str:
        task = Task(fn_name=fn_name, args=args)
        self._fronta.put(task)
        return task.id_

    def worker(self) -> None:
        while True:
            try:
                task = self._fronta.get(timeout=2.0)
                fn = self._funkce.get(task.fn_name)
                if fn is None:
                    vysl = TaskResult(task.id_, chyba="Neznámá funkce")
                else:
                    try:
                        vysledek = fn(*task.args)
                        vysl = TaskResult(task.id_, vysledek=vysledek)
                    except Exception as e:
                        vysl = TaskResult(task.id_, chyba=str(e))
                with self._zamek:
                    self._vysledky[task.id_] = vysl
                self._fronta.task_done()
            except queue.Empty:
                break

    def get_result(self, task_id: str) -> TaskResult | None:
        with self._zamek:
            return self._vysledky.get(task_id)
```

---

## Idempotency Keys

V distribuovaných systémech zpráva může dorazit **vícekrát** (síť selže, retry). Idempotency key zaručuje, že zpracování je bezpečné i při duplikátu.

```python
import threading

class IdempotentProcessor:
    def __init__(self) -> None:
        self._zpracovane: set[str] = set()
        self._zamek = threading.Lock()

    def zpracuj(self, idempotency_key: str, payload: str) -> str:
        with self._zamek:
            if idempotency_key in self._zpracovane:
                return f"DUPLICATE — klíč {idempotency_key} již zpracován"
            self._zpracovane.add(idempotency_key)
        # Skutečné zpracování (pouze jednou)
        vysledek = payload.upper()
        return f"ZPRACOVÁNO: {vysledek}"

proc = IdempotentProcessor()
klic = "objednavka-12345"
print(proc.zpracuj(klic, "data"))   # ZPRACOVÁNO: DATA
print(proc.zpracuj(klic, "data"))   # DUPLICATE
print(proc.zpracuj(klic, "data"))   # DUPLICATE
```

---

## Exactly-Once — iluze vs realita

| Sémantika | Popis | V praxi |
|---|---|---|
| **At-most-once** | Zpráva dorazí 0× nebo 1× | Ztrátová, jednoduchá |
| **At-least-once** | Zpráva dorazí ≥ 1× | Retry → duplikáty |
| **Exactly-once** | Zpráva dorazí přesně 1× | Vyžaduje idempotentní konzumenty + transakce |

Pravé "exactly-once" v distribuovaných systémech je velmi obtížné. Většinou implementujeme **at-least-once + idempotentní zpracování**.

```python
import time

class AtLeastOnceQueue:
    """Fronta s automatickým retry při selhání."""

    def __init__(self, max_retries: int = 3) -> None:
        import queue
        self._fronta: queue.Queue[tuple[str, str, int]] = queue.Queue()
        self._max_retries = max_retries

    def put(self, key: str, payload: str) -> None:
        self._fronta.put((key, payload, 0))

    def process_one(self) -> bool:
        import queue
        try:
            key, payload, retries = self._fronta.get_nowait()
        except queue.Empty:
            return False

        try:
            self._zpracuj(key, payload)
        except Exception as e:
            if retries < self._max_retries:
                print(f"  Retry {retries+1}/{self._max_retries} pro {key}")
                self._fronta.put((key, payload, retries + 1))
            else:
                print(f"  DLQ: {key} selhalo po {self._max_retries} pokusech")
        return True

    def _zpracuj(self, key: str, payload: str) -> None:
        import random
        if random.random() < 0.5:   # 50% selhání — simulace sítě
            raise ConnectionError("Simulovaná chyba sítě")
        print(f"  OK: {key} = {payload}")
```

---

## Dead Letter Queue (DLQ)

Zprávy, které nelze zpracovat ani po opakování, jdou do DLQ — k analýze a manuálnímu zpracování.

```python
import queue

class BrokerSDLQ:
    def __init__(self) -> None:
        self.hlavni: queue.Queue[str] = queue.Queue()
        self.dlq: queue.Queue[str] = queue.Queue()

    def zpracuj_vse(self, max_retries: int = 2) -> None:
        pending: list[tuple[str, int]] = []

        while not self.hlavni.empty():
            pending.append((self.hlavni.get_nowait(), 0))

        while pending:
            zprava, pokusy = pending.pop(0)
            try:
                self._handler(zprava)
            except Exception:
                if pokusy + 1 < max_retries:
                    pending.append((zprava, pokusy + 1))
                else:
                    self.dlq.put(zprava)
                    print(f"DLQ: {zprava!r}")

    def _handler(self, zprava: str) -> None:
        if zprava.startswith("bad"):
            raise ValueError(f"Nelze zpracovat: {zprava!r}")
        print(f"OK: {zprava!r}")
```

---

## Shrnutí

- **Message broker** odděluje producenty a konzumenty — decoupling
- **Worker pattern** = task queue + pool workerů + result store
- **Idempotency key** zabrání dvojímu zpracování při retry
- **At-least-once** je reálné; exactly-once vyžaduje idempotentní zpracování
- **DLQ** (Dead Letter Queue) zachytí neúspěšné zprávy pro analýzu

---

## Cvičení

1. Rozšiř `TaskQueue` o prioritní frontu (`queue.PriorityQueue`).
2. Implementuj `ExpiringMessage` — zpráva s TTL, která se zahodí, pokud není zpracována včas.
3. Napiš `CircuitBreaker` — po 3 selháních za sebou přestane posílat požadavky po dobu 5s.
4. Simuluj fan-out: jedna zpráva dorazí do 3 různých konzumentů současně.
