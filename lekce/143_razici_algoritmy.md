# Lekce 143: Řadící algoritmy

Řazení je jeden ze základních algoritmických problémů. Porozumění různým přístupům naučí přemýšlet o **časové a prostorové složitosti**.

---

## 📊 Přehled složitostí

| Algoritmus | Nejlepší | Průměrný | Nejhorší | Paměť | Stabilní |
|------------|---------|---------|---------|-------|---------|
| Bubble sort | O(n) | O(n²) | O(n²) | O(1) | ✅ |
| Selection sort | O(n²) | O(n²) | O(n²) | O(1) | ❌ |
| Insertion sort | O(n) | O(n²) | O(n²) | O(1) | ✅ |
| Merge sort | O(n log n) | O(n log n) | O(n log n) | O(n) | ✅ |
| Quick sort | O(n log n) | O(n log n) | O(n²) | O(log n) | ❌ |
| Heap sort | O(n log n) | O(n log n) | O(n log n) | O(1) | ❌ |
| Counting sort | O(n+k) | O(n+k) | O(n+k) | O(k) | ✅ |
| Radix sort | O(nk) | O(nk) | O(nk) | O(n+k) | ✅ |
| Tim sort | O(n) | O(n log n) | O(n log n) | O(n) | ✅ |

> **Tim sort** = Python's built-in `sorted()` — kombinace merge + insertion sort.

---

## 🫧 Bubble Sort

Jednoduchý, pomalý. Vhodný jen pro výuku.

```python
def bubble_sort(arr: list) -> list:
    arr = arr.copy()
    n = len(arr)
    for i in range(n):
        prohozeno = False
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                prohozeno = True
        if not prohozeno:   # pole je seřazené — early exit
            break
    return arr

print(bubble_sort([64, 34, 25, 12, 22, 11, 90]))
# [11, 12, 22, 25, 34, 64, 90]
```

---

## 🃏 Insertion Sort

Ideální pro **malá pole** nebo **téměř seřazená data**.

```python
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
```

---

## 🔀 Merge Sort

**Rozděl a panuj.** Garantuje O(n log n), stabilní, ale potřebuje O(n) paměti.

```python
def merge_sort(arr: list) -> list:
    if len(arr) <= 1:
        return arr

    stred = len(arr) // 2
    leva = merge_sort(arr[:stred])
    prava = merge_sort(arr[stred:])
    return merge(leva, prava)


def merge(leva: list, prava: list) -> list:
    vysledek = []
    i = j = 0
    while i < len(leva) and j < len(prava):
        if leva[i] <= prava[j]:
            vysledek.append(leva[i])
            i += 1
        else:
            vysledek.append(prava[j])
            j += 1
    vysledek.extend(leva[i:])
    vysledek.extend(prava[j:])
    return vysledek

print(merge_sort([38, 27, 43, 3, 9, 82, 10]))
# [3, 9, 10, 27, 38, 43, 82]
```

---

## ⚡ Quick Sort

**Průměrně nejrychlejší v praxi.** Klíč je volba pivotu.

```python
def quick_sort(arr: list) -> list:
    if len(arr) <= 1:
        return arr

    # Pivot = medián z prvního, středního a posledního prvku
    pivot = median_of_three(arr[0], arr[len(arr) // 2], arr[-1])
    mensi = [x for x in arr if x < pivot]
    rovne = [x for x in arr if x == pivot]
    vetsi = [x for x in arr if x > pivot]
    return quick_sort(mensi) + rovne + quick_sort(vetsi)


def median_of_three(a, b, c):
    return sorted([a, b, c])[1]


# In-place verze (efektivnější)
def quick_sort_inplace(arr: list, lo: int = 0, hi: int = None) -> None:
    if hi is None:
        hi = len(arr) - 1
    if lo < hi:
        pivot_idx = partition(arr, lo, hi)
        quick_sort_inplace(arr, lo, pivot_idx - 1)
        quick_sort_inplace(arr, pivot_idx + 1, hi)


def partition(arr: list, lo: int, hi: int) -> int:
    pivot = arr[hi]
    i = lo - 1
    for j in range(lo, hi):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
    return i + 1
```

---

## 🏔️ Heap Sort

Využívá **haldu (heap)** — vždy O(n log n), O(1) paměť.

```python
def heap_sort(arr: list) -> list:
    arr = arr.copy()
    n = len(arr)

    # Postav max-heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)

    # Vyjmi po jednom největší prvek
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(arr, i, 0)

    return arr


def heapify(arr: list, n: int, i: int) -> None:
    nejvetsi = i
    leve = 2 * i + 1
    prave = 2 * i + 2

    if leve < n and arr[leve] > arr[nejvetsi]:
        nejvetsi = leve
    if prave < n and arr[prave] > arr[nejvetsi]:
        nejvetsi = prave

    if nejvetsi != i:
        arr[i], arr[nejvetsi] = arr[nejvetsi], arr[i]
        heapify(arr, n, nejvetsi)
```

---

## 🔢 Counting Sort & Radix Sort

Pro čísla v omezeném rozsahu — lineární čas!

```python
def counting_sort(arr: list) -> list:
    """O(n + k) kde k je rozsah hodnot. Funguje jen pro nezáporná celá čísla."""
    if not arr:
        return arr
    max_val = max(arr)
    pocty = [0] * (max_val + 1)
    for x in arr:
        pocty[x] += 1
    vysledek = []
    for val, pocet in enumerate(pocty):
        vysledek.extend([val] * pocet)
    return vysledek


def radix_sort(arr: list) -> list:
    """O(nk) kde k je počet číslic. Řadí po cifrách od nejméně významné."""
    if not arr:
        return arr
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        arr = counting_sort_by_digit(arr, exp)
        exp *= 10
    return arr


def counting_sort_by_digit(arr: list, exp: int) -> list:
    n = len(arr)
    vystup = [0] * n
    pocty = [0] * 10
    for i in arr:
        index = (i // exp) % 10
        pocty[index] += 1
    for i in range(1, 10):
        pocty[i] += pocty[i - 1]
    for i in range(n - 1, -1, -1):
        index = (arr[i] // exp) % 10
        vystup[pocty[index] - 1] = arr[i]
        pocty[index] -= 1
    return vystup

print(radix_sort([170, 45, 75, 90, 802, 24, 2, 66]))
# [2, 24, 45, 66, 75, 90, 170, 802]
```

---

## 📏 Benchmarking

```python
import time
import random

def bench(func, data: list, nazev: str) -> None:
    kopia = data.copy()
    start = time.perf_counter()
    func(kopia)
    cas = (time.perf_counter() - start) * 1000
    print(f"  {nazev:<20}: {cas:.2f} ms")


n = 5000
nahodna = [random.randint(0, 10000) for _ in range(n)]
temer_serazena = sorted(nahodna)
temer_serazena[::50] = [random.randint(0, 10000)] * len(temer_serazena[::50])

print(f"\nNáhodná data ({n} prvků):")
for nazev, fn in [
    ("Bubble sort", lambda a: bubble_sort(a)),
    ("Insertion sort", lambda a: insertion_sort(a)),
    ("Merge sort", lambda a: merge_sort(a)),
    ("Quick sort", lambda a: quick_sort(a)),
    ("Heap sort", lambda a: heap_sort(a)),
    ("Python sorted()", lambda a: sorted(a)),
]:
    bench(fn, nahodna, nazev)

print(f"\nTéměř seřazená data ({n} prvků):")
for nazev, fn in [
    ("Insertion sort", lambda a: insertion_sort(a)),
    ("Merge sort", lambda a: merge_sort(a)),
    ("Python sorted()", lambda a: sorted(a)),
]:
    bench(fn, temer_serazena, nazev)
```

---

## 🎯 Kdy použít který algoritmus

| Situace | Doporučení |
|---------|-----------|
| Obecné použití | `sorted()` nebo `list.sort()` — Tim sort |
| Malé pole (< 20 prvků) | Insertion sort |
| Téměř seřazená data | Insertion sort nebo Tim sort |
| Garantovaný O(n log n) | Merge sort nebo Heap sort |
| Průměrně nejrychlejší | Quick sort |
| Celá čísla v malém rozsahu | Counting sort |
| Velká čísla s mnoha ciframi | Radix sort |
| Stabilní řazení nutné | Merge sort nebo Tim sort |

---

## ✏️ Cvičení

1. Implementuj **Shell sort** — zobecnění insertion sortu se zmenšujícím se krokem.
2. Porovnej výkon quick sortu s různými strategiemi pivotu: první prvek, náhodný, medián tří.
3. Implementuj **external merge sort** pro soubory větší než paměť.
4. Napiš `k_nejvetsi(arr, k)` bez plného řazení — použij min-heap nebo quick select O(n).
5. Seřaď seznam slovníků `[{"jmeno": "Anna", "vek": 30}, ...]` podle více klíčů stabilně.
