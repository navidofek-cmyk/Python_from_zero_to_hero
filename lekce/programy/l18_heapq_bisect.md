# Program — Lekce 18: Lekce 18: `array`, `heapq`, `bisect`

Patří k lekci [Lekce 18: `array`, `heapq`, `bisect`](../18_array_heapq_bisect.md).

## Jak spustit

```bash
python3 programy/l18_heapq_bisect.py
```

## Zdrojový kód

### `l18_heapq_bisect.py`

```py
"""Lekce 18 — heapq a bisect."""

import bisect
import heapq
import random


def znamka(skore: int) -> str:
    hranice = [40, 60, 75, 90]
    znamky = ["F", "D", "C", "B", "A"]
    return znamky[bisect.bisect_left(hranice, skore)]


def main() -> None:
    # Heapq — top 3
    cisla = [random.randint(1, 100) for _ in range(20)]
    print(f"Čísla:    {cisla}")
    print(f"Top 3 max: {heapq.nlargest(3, cisla)}")
    print(f"Top 3 min: {heapq.nsmallest(3, cisla)}")

    # Prioritní fronta
    fronta = []
    heapq.heappush(fronta, (3, "počká"))
    heapq.heappush(fronta, (1, "URGENT"))
    heapq.heappush(fronta, (2, "středně"))

    print("\nPriority fronta:")
    while fronta:
        priorita, ukol = heapq.heappop(fronta)
        print(f"  [{priorita}] {ukol}")

    # Bisect — známkování
    print()
    for skore in [25, 45, 65, 80, 95, 100]:
        print(f"{skore} bodů → {znamka(skore)}")


if __name__ == "__main__":
    main()

```
