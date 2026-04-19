# Lekce 126 — Stream Processing

Stream processing zpracovává data průběžně, event po eventu, místo čekání na kompletní dataset.
V této lekci implementujeme celý streaming engine pomocí Python generátorů — bez externích knihoven.

---

## 1. Co je stream processing?

| Batch processing | Stream processing |
|---|---|
| Čeká na všechna data | Zpracovává data ihned po příchodu |
| Spouští se periodicky | Běží kontinuálně |
| Vysoká latence | Nízká latence |
| Jednoduché | Složitější (čas, pořadí, late events) |

Příklady: zpracování kliknutí uživatelů v reálném čase, monitoring metrik, fraud detection.

---

## 2. Generator-based streaming

Python generátory jsou přirozeným modelem pro streaming: lazy evaluation, bez bufferu.

```python
from typing import Generator, Iterator

# Zdroj dat — simuluje nekonečný proud eventů
def event_source(count: int = 20) -> Generator[dict, None, None]:
    import time, random
    for i in range(count):
        yield {
            "id": i,
            "timestamp": time.time() + i * 0.1,
            "value": random.randint(1, 100),
            "user_id": random.choice(["alice", "bob", "charlie"]),
        }

# Transformační krok — filtr
def filter_stream(
    stream: Iterator[dict],
    predicate: Callable[[dict], bool],
) -> Generator[dict, None, None]:
    for event in stream:
        if predicate(event):
            yield event

# Transformační krok — map
def map_stream(
    stream: Iterator[dict],
    transform: Callable[[dict], dict],
) -> Generator[dict, None, None]:
    for event in stream:
        yield transform(event)

# Složení pipeline
pipeline = map_stream(
    filter_stream(
        event_source(10),
        predicate=lambda e: e["value"] > 50,
    ),
    transform=lambda e: {**e, "value_doubled": e["value"] * 2},
)

for event in pipeline:
    print(event)
```

---

## 3. Windowing — okénkové agregace

Windowing rozděluje nekonečný proud dat do konečných "oken" pro agregaci.

### Tumbling Window (nekrývající se okna)

```python
def tumbling_window(
    stream: Iterator[dict],
    size: int,
    key: str = "value",
) -> Generator[dict, None, None]:
    """Pevná okna bez překryvu. Každý event patří do právě jednoho okna."""
    window: list[dict] = []
    window_id = 0

    for event in stream:
        window.append(event)
        if len(window) >= size:
            values = [e[key] for e in window]
            yield {
                "window_id": window_id,
                "count": len(window),
                "sum": sum(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "events": window.copy(),
            }
            window = []
            window_id += 1
```

### Sliding Window (překrývající se okna)

```python
from collections import deque

def sliding_window(
    stream: Iterator[dict],
    size: int,
    step: int,
    key: str = "value",
) -> Generator[dict, None, None]:
    """Okna s překryvem. step < size → sousední okna sdílí eventy."""
    buffer: deque[dict] = deque(maxlen=size)
    event_count = 0

    for event in stream:
        buffer.append(event)
        event_count += 1

        # Emituj okno každých `step` eventů (jakmile je okno plné)
        if len(buffer) == size and (event_count - size) % step == 0:
            values = [e[key] for e in buffer]
            yield {
                "window_end": event_count,
                "count": len(buffer),
                "avg": round(sum(values) / len(values), 2),
                "max": max(values),
            }
```

### Time-based Window (časová okna)

```python
import time as _time
from collections import deque

def time_window(
    stream: Iterator[dict],
    window_seconds: float,
    ts_key: str = "timestamp",
    val_key: str = "value",
) -> Generator[dict, None, None]:
    """Okna definovaná časem místo počtem eventů."""
    buffer: list[dict] = []

    for event in stream:
        buffer.append(event)

        # Odstraň staré eventy (mimo okno)
        now = event[ts_key]
        buffer = [e for e in buffer if e[ts_key] >= now - window_seconds]

        values = [e[val_key] for e in buffer]
        yield {
            "ts": round(now, 2),
            "window_count": len(buffer),
            "window_avg": round(sum(values) / len(values), 2),
        }
```

---

## 4. Late Events — zpracování opožděných dat

V reálných systémech přicházejí eventy mimo pořadí (síťové zpoždění, mobilní zařízení offline).

```python
@dataclass
class LateEventHandler:
    """
    Správa opožděných eventů.

    allowed_lateness: kolik sekund za watermarkem ještě akceptujeme.
    """
    allowed_lateness: float = 5.0
    _watermark: float = 0.0
    _late_count: int = 0
    _accepted_count: int = 0

    def process(self, event: dict, ts_key: str = "timestamp") -> str:
        """Vrátí 'on_time', 'late_accepted' nebo 'dropped'."""
        event_ts = event[ts_key]

        # Posun watermarku dopředu (nikdy zpět)
        self._watermark = max(self._watermark, event_ts)

        deadline = self._watermark - self.allowed_lateness

        if event_ts >= deadline:
            self._accepted_count += 1
            status = "on_time" if event_ts >= self._watermark else "late_accepted"
        else:
            self._late_count += 1
            status = "dropped"

        return status

    @property
    def stats(self) -> dict:
        total = self._accepted_count + self._late_count
        return {
            "accepted": self._accepted_count,
            "dropped": self._late_count,
            "drop_rate": round(self._late_count / total, 3) if total else 0.0,
            "watermark": round(self._watermark, 2),
        }
```

---

## 5. Watermark pattern

Watermark je odhad "jak daleko jsme v čase" — pomáhá rozhodovat, kdy uzavřít okno.

```python
class WatermarkTracker:
    """
    Sleduje watermark jako `max(event_timestamp) - max_out_of_orderness`.

    Okno s end_time ≤ watermark je považováno za kompletní.
    """

    def __init__(self, max_out_of_orderness: float = 3.0) -> None:
        self._max_ts: float = 0.0
        self.max_out_of_orderness = max_out_of_orderness

    def update(self, event_ts: float) -> float:
        self._max_ts = max(self._max_ts, event_ts)
        return self.watermark

    @property
    def watermark(self) -> float:
        return self._max_ts - self.max_out_of_orderness

    def is_window_complete(self, window_end_ts: float) -> bool:
        return window_end_ts <= self.watermark
```

---

## 6. Stream operátory

```python
# Stateful operátor: průběžný součet per klíč
def running_sum(
    stream: Iterator[dict],
    group_key: str,
    val_key: str,
) -> Generator[dict, None, None]:
    totals: dict[str, float] = {}
    for event in stream:
        k = event[group_key]
        totals[k] = totals.get(k, 0.0) + event[val_key]
        yield {**event, f"running_{val_key}": totals[k]}

# Dedup operátor: odstraní duplicity dle klíče
def dedup(
    stream: Iterator[dict],
    key: str,
) -> Generator[dict, None, None]:
    seen: set = set()
    for event in stream:
        v = event[key]
        if v not in seen:
            seen.add(v)
            yield event

# Rate limiter
def rate_limit(
    stream: Iterator[dict],
    max_per_second: float,
) -> Generator[dict, None, None]:
    import time
    interval = 1.0 / max_per_second
    for event in stream:
        yield event
        time.sleep(interval)
```

---

## 7. Srovnání windowing strategií

| Strategie | Překryv | Paměť | Použití |
|---|---|---|---|
| Tumbling | Ne | O(size) | Denní/hodinové statistiky |
| Sliding | Ano | O(size) | Klouzavý průměr, anomalie |
| Session | Dynamický | O(aktivní relace) | Uživatelské session |
| Time-based | Volitelný | O(eventy v okně) | Reálný čas |

---

## Shrnutí

- Python generátory jsou ideální pro stream processing — lazy, kompozitabilní, nulová paměť.
- **Tumbling window**: pevná okna bez překryvu.
- **Sliding window**: plovoucí okno s krokem — pro klouzavé metriky.
- **Late events**: eventy mohou přijít mimo pořadí — watermark pomáhá rozhodovat.
- **Watermark**: konzervativní odhad pokroku v čase; uzavírá okna.
- Stateful operátory (running sum, dedup) potřebují in-memory stav — pozor na paměť.

## Cvičení

1. Implementuj `session_window()` — okno se uzavře po N sekundách nečinnosti uživatele.
2. Přidej do `sliding_window()` podporu pro `group_by` klíč (statistiky per uživatel).
3. Implementuj operátor `join_streams()`, který spojí dva streamy dle společného klíče v časovém okně.
4. Vytvoř `StreamPipeline` třídu s fluent API: `source.filter(...).map(...).window(...).sink(...)`.
5. Přidej metriky throughput (eventů/sec) a latency (čas od event_timestamp do zpracování).
