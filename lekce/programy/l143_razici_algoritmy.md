# Program — Lekce 143: Lekce 143: Řadící algoritmy

Patří k lekci [Lekce 143: Řadící algoritmy](../143_razici_algoritmy.md).

## Jak spustit

```bash
python3 programy/l143_razici_algoritmy.py
```

## Zdrojový kód

### `l143_razici_algoritmy.py`

```py
"""Lekce 143 — Řadící algoritmy.

Spuštění:
    uv run l143_razici_algoritmy.py
"""

import random
import time
from typing import Callable


def bubble_sort(arr: list) -> list:
    arr = arr.copy()
    n = len(arr)
    for i in range(n):
        prohozeno = False
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                prohozeno = True
        if not prohozeno:
            break
    return arr


def insertion_sort(arr: list) -> list:
    arr = arr.copy()
    for i in range(1, len(arr)):
        klic = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > klic:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = klic
    return arr


def merge_sort(arr: list) -> list:
    if len(arr) <= 1:
        return arr
    stred = len(arr) // 2
    leva = merge_sort(arr[:stred])
    prava = merge_sort(arr[stred:])
    return _merge(leva, prava)


def _merge(leva: list, prava: list) -> list:
    vysledek, i, j = [], 0, 0
    while i < len(leva) and j < len(prava):
        if leva[i] <= prava[j]:
            vysledek.append(leva[i]); i += 1
        else:
            vysledek.append(prava[j]); j += 1
    vysledek.extend(leva[i:])
    vysledek.extend(prava[j:])
    return vysledek


def quick_sort(arr: list) -> list:
    if len(arr) <= 1:
        return arr
    pivot = sorted([arr[0], arr[len(arr)//2], arr[-1]])[1]
    mensi = [x for x in arr if x < pivot]
    rovne = [x for x in arr if x == pivot]
    vetsi = [x for x in arr if x > pivot]
    return quick_sort(mensi) + rovne + quick_sort(vetsi)


def heap_sort(arr: list) -> list:
    arr = arr.copy()
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        _heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        _heapify(arr, i, 0)
    return arr


def _heapify(arr, n, i):
    nejvetsi = i
    l, r = 2*i+1, 2*i+2
    if l < n and arr[l] > arr[nejvetsi]: nejvetsi = l
    if r < n and arr[r] > arr[nejvetsi]: nejvetsi = r
    if nejvetsi != i:
        arr[i], arr[nejvetsi] = arr[nejvetsi], arr[i]
        _heapify(arr, n, nejvetsi)


def radix_sort(arr: list) -> list:
    if not arr: return arr
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        arr = _counting_digit(arr, exp)
        exp *= 10
    return arr


def _counting_digit(arr, exp):
    n, vystup, pocty = len(arr), [0]*len(arr), [0]*10
    for i in arr: pocty[(i // exp) % 10] += 1
    for i in range(1, 10): pocty[i] += pocty[i-1]
    for i in range(n-1, -1, -1):
        idx = (arr[i] // exp) % 10
        vystup[pocty[idx]-1] = arr[i]
        pocty[idx] -= 1
    return vystup


def bench(fn: Callable, data: list, nazev: str) -> None:
    kopia = data.copy()
    start = time.perf_counter()
    vysledek = fn(kopia)
    cas = (time.perf_counter() - start) * 1000
    ok = "✅" if vysledek == sorted(data) else "❌"
    print(f"  {ok} {nazev:<20}: {cas:7.2f} ms")


def main():
    print("=" * 50)
    print("  📊 Řadící algoritmy — benchmark")
    print("=" * 50)

    seed = 42
    random.seed(seed)

    algoritmy = [
        ("Bubble sort", bubble_sort),
        ("Insertion sort", insertion_sort),
        ("Merge sort", merge_sort),
        ("Quick sort", quick_sort),
        ("Heap sort", heap_sort),
        ("Radix sort", radix_sort),
        ("Python sorted()", lambda a: sorted(a)),
    ]

    for n, popis in [(100, "Malé"), (1000, "Střední"), (5000, "Větší")]:
        data = [random.randint(0, 10000) for _ in range(n)]
        print(f"\n{popis} pole ({n} prvků) — náhodná data:")
        for nazev, fn in algoritmy:
            if n > 1000 and nazev in ("Bubble sort", "Insertion sort"):
                print(f"  ⏭  {nazev:<20}: přeskočeno (O(n²))")
                continue
            bench(fn, data, nazev)

    print("\nTéměř seřazená data (1000 prvků):")
    data_sorted = sorted([random.randint(0, 10000) for _ in range(1000)])
    data_sorted[::20] = [random.randint(0, 10000)] * len(data_sorted[::20])
    for nazev, fn in [("Insertion sort", insertion_sort),
                       ("Merge sort", merge_sort),
                       ("Python sorted()", lambda a: sorted(a))]:
        bench(fn, data_sorted, nazev)

    print("\nOverě správnost na malém poli:")
    test = [64, 34, 25, 12, 22, 11, 90]
    ocekavany = sorted(test)
    for nazev, fn in algoritmy:
        vysledek = fn(test)
        ok = "✅" if vysledek == ocekavany else "❌"
        print(f"  {ok} {nazev}: {vysledek}")


if __name__ == "__main__":
    main()

```
