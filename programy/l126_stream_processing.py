"""Lekce 126 — Stream Processing."""

from __future__ import annotations

import time
import random
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Generator, Iterator

# ── Zdroje dat ────────────────────────────────────────────────────────────────

def synthetic_events(
    count: int = 30,
    base_ts: float = 1_000_000.0,
) -> Generator[dict[str, Any], None, None]:
    """Generuje syntetické eventy s mírným out-of-order rozptylem."""
    rng = random.Random(42)
    for i in range(count):
        # Simulace opožděného eventu každých ~5 eventů
        jitter = rng.uniform(-2.0, 0.5)
        ts = base_ts + i + jitter
        yield {
            "id": i,
            "timestamp": round(ts, 3),
            "value": rng.randint(10, 100),
            "user_id": rng.choice(["alice", "bob", "charlie"]),
            "category": rng.choice(["A", "B"]),
        }


def ordered_events(count: int = 20, base_ts: float = 0.0) -> Generator[dict[str, Any], None, None]:
    """Striktně seřazené eventy (pro demo oken)."""
    for i in range(count):
        yield {
            "id": i,
            "timestamp": base_ts + float(i),
            "value": (i % 10) * 10 + 5,
            "user_id": ["alice", "bob"][(i % 4) < 2],
        }


# ── Stream operátory ──────────────────────────────────────────────────────────

def filter_stream(
    stream: Iterator[dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
) -> Generator[dict[str, Any], None, None]:
    """Filtruje eventy dle predikátu."""
    for event in stream:
        if predicate(event):
            yield event


def map_stream(
    stream: Iterator[dict[str, Any]],
    transform: Callable[[dict[str, Any]], dict[str, Any]],
) -> Generator[dict[str, Any], None, None]:
    """Transformuje každý event."""
    for event in stream:
        yield transform(event)


def dedup(
    stream: Iterator[dict[str, Any]],
    key: str,
) -> Generator[dict[str, Any], None, None]:
    """Odstraní duplikáty dle klíče."""
    seen: set[Any] = set()
    for event in stream:
        v = event[key]
        if v not in seen:
            seen.add(v)
            yield event


def running_sum(
    stream: Iterator[dict[str, Any]],
    group_key: str,
    val_key: str,
) -> Generator[dict[str, Any], None, None]:
    """Stateful operátor: průběžný součet per skupinu."""
    totals: dict[str, float] = {}
    for event in stream:
        k = event[group_key]
        totals[k] = totals.get(k, 0.0) + float(event[val_key])
        yield {**event, f"running_{val_key}": totals[k]}


# ── Tumbling Window ───────────────────────────────────────────────────────────

def tumbling_window(
    stream: Iterator[dict[str, Any]],
    size: int,
    val_key: str = "value",
) -> Generator[dict[str, Any], None, None]:
    """Pevná okna bez překryvu (každý event v právě jednom okně)."""
    window: list[dict[str, Any]] = []
    window_id = 0

    for event in stream:
        window.append(event)
        if len(window) >= size:
            values = [float(e[val_key]) for e in window]
            yield {
                "window_id": window_id,
                "size": len(window),
                "sum": round(sum(values), 2),
                "avg": round(sum(values) / len(values), 2),
                "min": min(values),
                "max": max(values),
                "first_id": window[0]["id"],
                "last_id": window[-1]["id"],
            }
            window = []
            window_id += 1


# ── Sliding Window ────────────────────────────────────────────────────────────

def sliding_window(
    stream: Iterator[dict[str, Any]],
    size: int,
    step: int,
    val_key: str = "value",
) -> Generator[dict[str, Any], None, None]:
    """Plovoucí okno s překryvem (step < size → sousední okna sdílejí eventy)."""
    buffer: deque[dict[str, Any]] = deque(maxlen=size)
    event_count = 0
    emits = 0

    for event in stream:
        buffer.append(event)
        event_count += 1

        # Emituj, jakmile buffer plný, pak každých `step` eventů
        if len(buffer) == size and (event_count - size) % step == 0:
            values = [float(e[val_key]) for e in buffer]
            emits += 1
            yield {
                "emit_n": emits,
                "event_count": event_count,
                "window_size": len(buffer),
                "avg": round(sum(values) / len(values), 2),
                "max": max(values),
                "min": min(values),
            }


# ── Time-based Window ─────────────────────────────────────────────────────────

def time_window(
    stream: Iterator[dict[str, Any]],
    window_seconds: float,
    ts_key: str = "timestamp",
    val_key: str = "value",
) -> Generator[dict[str, Any], None, None]:
    """Okna definovaná časovým rozsahem."""
    buffer: list[dict[str, Any]] = []

    for event in stream:
        buffer.append(event)
        now = float(event[ts_key])
        cutoff = now - window_seconds
        buffer = [e for e in buffer if float(e[ts_key]) >= cutoff]

        values = [float(e[val_key]) for e in buffer]
        yield {
            "ts": round(now, 3),
            "window_events": len(buffer),
            "window_avg": round(sum(values) / len(values), 2),
            "window_sum": round(sum(values), 2),
        }


# ── Watermark a Late Events ───────────────────────────────────────────────────

@dataclass
class WatermarkTracker:
    """Sleduje watermark = max(event_ts) - max_out_of_orderness."""

    max_out_of_orderness: float = 3.0
    _max_ts: float = field(default=0.0, init=False, repr=False)

    def update(self, event_ts: float) -> float:
        self._max_ts = max(self._max_ts, event_ts)
        return self.watermark

    @property
    def watermark(self) -> float:
        return self._max_ts - self.max_out_of_orderness

    def is_window_complete(self, window_end_ts: float) -> bool:
        return window_end_ts <= self.watermark


@dataclass
class LateEventHandler:
    """Kategorizuje eventy jako on_time / late_accepted / dropped."""

    allowed_lateness: float = 2.0
    _watermark: float = field(default=0.0, init=False, repr=False)
    _counts: dict[str, int] = field(
        default_factory=lambda: {"on_time": 0, "late_accepted": 0, "dropped": 0},
        init=False,
    )

    def process(
        self, event: dict[str, Any], ts_key: str = "timestamp"
    ) -> tuple[dict[str, Any], str]:
        event_ts = float(event[ts_key])
        self._watermark = max(self._watermark, event_ts)
        deadline = self._watermark - self.allowed_lateness

        if event_ts >= self._watermark:
            status = "on_time"
        elif event_ts >= deadline:
            status = "late_accepted"
        else:
            status = "dropped"

        self._counts[status] += 1
        return {**event, "_status": status, "_watermark": round(self._watermark, 3)}, status

    @property
    def stats(self) -> dict[str, Any]:
        total = sum(self._counts.values())
        return {
            **self._counts,
            "total": total,
            "drop_rate": round(self._counts["dropped"] / total, 3) if total else 0.0,
        }


# ── Demo funkce ───────────────────────────────────────────────────────────────

def demo_basic_pipeline() -> None:
    print("=== DEMO 1: Základní stream pipeline ===")
    pipeline = map_stream(
        filter_stream(
            ordered_events(15),
            predicate=lambda e: e["value"] >= 50,
        ),
        transform=lambda e: {**e, "value_norm": round(e["value"] / 100.0, 2)},
    )
    results = list(pipeline)
    print(f"  Eventů prošlo filtrem: {len(results)}/15")
    for e in results[:3]:
        print(f"    id={e['id']}, value={e['value']}, norm={e['value_norm']}")
    print()


def demo_tumbling_window() -> None:
    print("=== DEMO 2: Tumbling Window (size=5) ===")
    for win in tumbling_window(ordered_events(20), size=5):
        print(
            f"  Okno {win['window_id']}: "
            f"id {win['first_id']}–{win['last_id']}, "
            f"avg={win['avg']}, sum={win['sum']}"
        )
    print()


def demo_sliding_window() -> None:
    print("=== DEMO 3: Sliding Window (size=5, step=2) ===")
    for win in sliding_window(ordered_events(16), size=5, step=2):
        print(
            f"  Emit #{win['emit_n']} (po eventu {win['event_count']}): "
            f"avg={win['avg']}, max={win['max']}, min={win['min']}"
        )
    print()


def demo_time_window() -> None:
    print("=== DEMO 4: Time-based Window (3 sekundy) ===")
    results = list(time_window(ordered_events(10, base_ts=100.0), window_seconds=3.0))
    for r in results[::3]:  # každý 3. výsledek
        print(
            f"  ts={r['ts']}: {r['window_events']} eventů v okně, "
            f"avg={r['window_avg']}, sum={r['window_sum']}"
        )
    print()


def demo_late_events() -> None:
    print("=== DEMO 5: Late Events & Watermark ===")
    handler = LateEventHandler(allowed_lateness=2.0)

    # Simulace out-of-order streamu
    raw_events = [
        {"id": 0, "timestamp": 10.0, "value": 1},
        {"id": 1, "timestamp": 11.0, "value": 2},
        {"id": 2, "timestamp": 15.0, "value": 3},   # skok vpřed
        {"id": 3, "timestamp": 12.5, "value": 4},   # pozdní, ale přijatelný
        {"id": 4, "timestamp": 8.0, "value": 5},    # příliš pozdní → drop
        {"id": 5, "timestamp": 16.0, "value": 6},
        {"id": 6, "timestamp": 13.0, "value": 7},   # pozdní, přijatelný
        {"id": 7, "timestamp": 11.0, "value": 8},   # příliš pozdní → drop
    ]

    for raw in raw_events:
        enriched, status = handler.process(raw)
        mark = {"on_time": "✓", "late_accepted": "~", "dropped": "✗"}[status]
        print(
            f"  {mark} id={raw['id']:2d}, ts={raw['timestamp']:5.1f}, "
            f"watermark={enriched['_watermark']:5.1f} → {status}"
        )

    print(f"\n  Statistiky: {handler.stats}\n")


def demo_watermark() -> None:
    print("=== DEMO 6: Watermark Tracker ===")
    tracker = WatermarkTracker(max_out_of_orderness=3.0)
    windows = [(0.0, 5.0), (5.0, 10.0), (10.0, 15.0), (15.0, 20.0)]

    timestamps = [1.0, 4.0, 9.0, 7.0, 12.0, 11.0, 18.0]
    for ts in timestamps:
        wm = tracker.update(ts)
        completed = [w for w in windows if tracker.is_window_complete(w[1])]
        print(
            f"  event_ts={ts:5.1f} → watermark={wm:5.1f}, "
            f"uzavřená okna: {[f'{a:.0f}-{b:.0f}' for a, b in completed]}"
        )
    print()


def demo_running_sum() -> None:
    print("=== DEMO 7: Stateful operátor — Running Sum per uživatel ===")
    stream = running_sum(ordered_events(8), group_key="user_id", val_key="value")
    for e in stream:
        print(
            f"  id={e['id']:2d}, user={e['user_id']:7s}, "
            f"value={e['value']:3d}, running_value={e['running_value']:.0f}"
        )
    print()


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    demo_basic_pipeline()
    demo_tumbling_window()
    demo_sliding_window()
    demo_time_window()
    demo_late_events()
    demo_watermark()
    demo_running_sum()
    print("Hotovo! Všechny demo sekce lekce 126 proběhly úspěšně.")


if __name__ == "__main__":
    main()
