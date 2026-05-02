# Lekce 150: Divide & Conquer + rekurzivní fraktály

**Rozděl a panuj** = rozděl problém na menší podproblémy stejného typu, rekurzivně je vyřeš, výsledky spoj.

```
T(n) = a·T(n/b) + f(n)
Master theorem:
  f(n) = O(n^log_b(a) - ε)  →  T(n) = Θ(n^log_b(a))
  f(n) = Θ(n^log_b(a))      →  T(n) = Θ(n^log_b(a) · log n)
  f(n) = Ω(n^log_b(a) + ε)  →  T(n) = Θ(f(n))
```

---

## 🔍 Binární vyhledávání

Klasický D&C: O(log n) místo O(n).

```python
def binary_search(arr: list, cil, lo: int = 0, hi: int = None) -> int:
    """Rekurzivní binární vyhledávání. Vrátí index nebo -1."""
    if hi is None:
        hi = len(arr) - 1
    if lo > hi:
        return -1
    mid = (lo + hi) // 2
    if arr[mid] == cil:
        return mid
    if arr[mid] < cil:
        return binary_search(arr, cil, mid + 1, hi)
    return binary_search(arr, cil, lo, mid - 1)


def binary_search_first(arr: list, cil) -> int:
    """Najde první výskyt v seřazeném poli s duplikáty."""
    lo, hi, vysledek = 0, len(arr) - 1, -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == cil:
            vysledek = mid
            hi = mid - 1   # hledej dál vlevo
        elif arr[mid] < cil:
            lo = mid + 1
        else:
            hi = mid - 1
    return vysledek


serazeny = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
print("Binární vyhledávání:")
for x in [7, 1, 19, 6]:
    idx = binary_search(serazeny, x)
    print(f"  Hledám {x}: index={idx}")
```

---

## 📏 Nejbližší pár bodů (Closest Pair)

Naivně O(n²), D&C O(n log n).

```python
import math
from typing import NamedTuple


class Bod(NamedTuple):
    x: float
    y: float


def vzdalenost(a: Bod, b: Bod) -> float:
    return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)


def nejblizsi_par(body: list[Bod]) -> tuple[float, Bod, Bod]:
    """D&C O(n log n)."""

    def strip_min(strip: list[Bod], d: float) -> tuple[float, Bod, Bod]:
        """Minimum v pruhu šířky d kolem středu."""
        strip.sort(key=lambda b: b.y)
        min_d, best = d, (strip[0], strip[1]) if len(strip) >= 2 else (None, None)
        for i in range(len(strip)):
            for j in range(i+1, len(strip)):
                if strip[j].y - strip[i].y >= min_d:
                    break
                v = vzdalenost(strip[i], strip[j])
                if v < min_d:
                    min_d, best = v, (strip[i], strip[j])
        return min_d, best[0], best[1]

    def dc(pts: list[Bod]) -> tuple[float, Bod, Bod]:
        n = len(pts)
        if n <= 3:
            min_d, ba, bb = float("inf"), pts[0], pts[1]
            for i in range(n):
                for j in range(i+1, n):
                    v = vzdalenost(pts[i], pts[j])
                    if v < min_d:
                        min_d, ba, bb = v, pts[i], pts[j]
            return min_d, ba, bb

        mid = n // 2
        stred_x = pts[mid].x
        dl, al, bl = dc(pts[:mid])
        dr, ar, br = dc(pts[mid:])
        d = min(dl, dr)
        best_a, best_b = (al, bl) if dl <= dr else (ar, br)

        strip = [p for p in pts if abs(p.x - stred_x) < d]
        if len(strip) >= 2:
            ds, sa, sb = strip_min(strip, d)
            if ds < d:
                d, best_a, best_b = ds, sa, sb

        return d, best_a, best_b

    body_sorted = sorted(body, key=lambda b: b.x)
    return dc(body_sorted)


import random
random.seed(42)
body = [Bod(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(20)]
d, a, b = nejblizsi_par(body)
print(f"\nNejbližší pár: {a} ↔ {b} = {d:.4f}")
```

---

## ✖️ Karatsubovo násobení

Násobení velkých čísel O(n^1.585) místo O(n²).

```python
def karatsuba(x: int, y: int) -> int:
    """Rekurzivní násobení velkých čísel."""
    if x < 10 or y < 10:
        return x * y

    n = max(len(str(x)), len(str(y)))
    m = n // 2

    a, b = x // 10**m, x % 10**m
    c, d = y // 10**m, y % 10**m

    ac = karatsuba(a, c)
    bd = karatsuba(b, d)
    ad_bc = karatsuba(a + b, c + d) - ac - bd

    return ac * 10**(2*m) + ad_bc * 10**m + bd


x = 123456789
y = 987654321
print(f"\nKaratsuba: {x} × {y}")
print(f"  Karatsuba: {karatsuba(x, y)}")
print(f"  Python:    {x * y}")
print(f"  Shoduje se: {karatsuba(x, y) == x * y}")
```

---

## 🔢 Strassenovo maticové násobení

Násobení matic O(n^2.807) místo O(n³).

```python
def matice_scitani(A, B):
    n = len(A)
    return [[A[i][j] + B[i][j] for j in range(n)] for i in range(n)]

def matice_odcitani(A, B):
    n = len(A)
    return [[A[i][j] - B[i][j] for j in range(n)] for i in range(n)]

def strassen(A: list[list], B: list[list]) -> list[list]:
    """Strassenovo násobení 2^k × 2^k matic."""
    n = len(A)
    if n == 1:
        return [[A[0][0] * B[0][0]]]

    mid = n // 2
    A11 = [row[:mid] for row in A[:mid]]
    A12 = [row[mid:] for row in A[:mid]]
    A21 = [row[:mid] for row in A[mid:]]
    A22 = [row[mid:] for row in A[mid:]]
    B11 = [row[:mid] for row in B[:mid]]
    B12 = [row[mid:] for row in B[:mid]]
    B21 = [row[:mid] for row in B[mid:]]
    B22 = [row[mid:] for row in B[mid:]]

    M1 = strassen(matice_scitani(A11, A22), matice_scitani(B11, B22))
    M2 = strassen(matice_scitani(A21, A22), B11)
    M3 = strassen(A11, matice_odcitani(B12, B22))
    M4 = strassen(A22, matice_odcitani(B21, B11))
    M5 = strassen(matice_scitani(A11, A12), B22)
    M6 = strassen(matice_odcitani(A21, A11), matice_scitani(B11, B12))
    M7 = strassen(matice_odcitani(A12, A22), matice_scitani(B21, B22))

    C11 = matice_scitani(matice_odcitani(matice_scitani(M1, M4), M5), M7)
    C12 = matice_scitani(M3, M5)
    C21 = matice_scitani(M2, M4)
    C22 = matice_scitani(matice_odcitani(matice_scitani(M1, M3), M2), M6)

    C = []
    for i in range(mid):
        C.append(C11[i] + C12[i])
    for i in range(mid):
        C.append(C21[i] + C22[i])
    return C


A = [[1,2],[3,4]]
B = [[5,6],[7,8]]
C = strassen(A, B)
print(f"\nStrassen 2×2: {C}")   # [[19,22],[43,50]]
```

---

## 🎨 Rekurzivní fraktály

### Koch snowflake (ASCII verze)

```python
def koch_uroven(uroven: int, delka: float) -> list[tuple]:
    """Vrátí seznam úseček Koch křivky."""
    if uroven == 0:
        return [(0, 0, delka, 0)]

    d = delka / 3
    segmenty = []

    def koch_segment(x1, y1, x2, y2, hloubka):
        if hloubka == 0:
            segmenty.append((x1, y1, x2, y2))
            return
        dx, dy = (x2-x1)/3, (y2-y1)/3
        # Čtyři nové body
        ax, ay = x1+dx, y1+dy
        bx, by = x1+2*dx, y1+2*dy
        # Špička trojúhelníku
        cx = ax + (dx - dy*math.sqrt(3)/3)  # aproximace
        cy = ay + (dy + dx*math.sqrt(3)/3)
        # Zjednodušení pro ASCII: jen rotace o 60°
        mx, my = (ax+bx)/2, (ay+by)/2
        peak_x = mx - (by-ay)*math.sqrt(3)/2
        peak_y = my + (bx-ax)*math.sqrt(3)/2

        koch_segment(x1, y1, ax, ay, hloubka-1)
        koch_segment(ax, ay, peak_x, peak_y, hloubka-1)
        koch_segment(peak_x, peak_y, bx, by, hloubka-1)
        koch_segment(bx, by, x2, y2, hloubka-1)

    koch_segment(0, 0, delka, 0, uroven)
    return segmenty


def sierpinski_ascii(n: int) -> list[str]:
    """Sierpiňského trojúhelník v ASCII."""
    if n == 0:
        return ["*"]

    mensi = sierpinski_ascii(n - 1)
    sirka = len(mensi[-1])
    mezera = " " * (sirka // 2 + 1)

    horni = [mezera + radek + mezera for radek in mensi]
    dolni = [radek + " " + radek for radek in mensi]
    return horni + dolni


print("\nSierpiňského trojúhelník (hloubka 3):")
for radek in sierpinski_ascii(3):
    print(" ", radek)
```

### Hilbertova křivka (ASCII)

```python
def hilbert_ascii(poradi: int, sirka: int = 32) -> list[str]:
    """Hilbertova křivka v ASCII mřížce."""
    grid = [[" "] * sirka for _ in range(sirka)]
    body = []

    def hilbert(x, y, xi, xj, yi, yj, n):
        if n <= 0:
            body.append((x + (xi + yi) // 2, y + (xj + yj) // 2))
        else:
            hilbert(x,            y,            yi//2, yj//2, xi//2, xj//2, n-1)
            hilbert(x+xi//2,      y+xj//2,      xi//2, xj//2, yi//2, yj//2, n-1)
            hilbert(x+xi//2+yi//2,y+xj//2+yj//2,xi//2, xj//2, yi//2, yj//2, n-1)
            hilbert(x+xi//2+yi,   y+xj//2+yj,  -yi//2,-yj//2,-xi//2,-xj//2, n-1)

    hilbert(0, 0, sirka, 0, 0, sirka, poradi)

    for px, py in body:
        if 0 <= px < sirka and 0 <= py < sirka:
            grid[py][px] = "█"

    return ["".join(radek) for radek in grid]


print("\nHilbertova křivka (řád 2):")
for radek in hilbert_ascii(2, 16):
    print(" ", radek)
```

### Dragon Curve

```python
def dragon_curve(iterace: int) -> str:
    """Sekvence zatáček Dragon Curve: R=doprava, L=doleva."""
    sekvence = "R"
    for _ in range(iterace - 1):
        nova = sekvence + "R"
        nova += "".join("L" if z == "R" else "R" for z in reversed(sekvence))
        sekvence = nova
    return sekvence


def dragon_do_ascii(sekvence: str, sirka: int = 40, vyska: int = 20) -> list[str]:
    """Vykreslí Dragon Curve do ASCII mřížky."""
    grid = [[" "] * sirka for _ in range(vyska)]
    x, y = sirka // 2, vyska // 2
    smer = 0   # 0=vpravo, 1=dolů, 2=vlevo, 3=nahoru
    dx = [1, 0, -1, 0]
    dy = [0, 1, 0, -1]

    if 0 <= x < sirka and 0 <= y < vyska:
        grid[y][x] = "▪"
    for zatacka in sekvence:
        smer = (smer + (1 if zatacka == "R" else -1)) % 4
        x += dx[smer]; y += dy[smer]
        if 0 <= x < sirka and 0 <= y < vyska:
            grid[y][x] = "▪"

    return ["".join(radek) for radek in grid]


print("\nDragon Curve (10 iterací):")
seq = dragon_curve(10)
for radek in dragon_do_ascii(seq):
    if radek.strip():
        print(" ", radek)
```

---

## ⚡ Paralelní D&C s asyncio

```python
import asyncio


async def parallel_merge_sort(arr: list, min_chunk: int = 100) -> list:
    """Merge sort s paralelním řazením nezávislých polovin."""
    if len(arr) <= min_chunk:
        return sorted(arr)

    mid = len(arr) // 2
    leva, prava = await asyncio.gather(
        parallel_merge_sort(arr[:mid], min_chunk),
        parallel_merge_sort(arr[mid:], min_chunk),
    )
    # Merge
    vysledek, i, j = [], 0, 0
    while i < len(leva) and j < len(prava):
        if leva[i] <= prava[j]:
            vysledek.append(leva[i]); i += 1
        else:
            vysledek.append(prava[j]); j += 1
    return vysledek + leva[i:] + prava[j:]
```

---

## 🎯 Přehled D&C algoritmů

| Algoritmus | Naivní | D&C | Podproblémy |
|-----------|--------|-----|-------------|
| Merge Sort | O(n²) | O(n log n) | 2 × n/2 |
| Quick Sort | O(n²) worst | O(n log n) avg | 2 × n/2 |
| Binary Search | O(n) | O(log n) | 1 × n/2 |
| Closest Pair | O(n²) | O(n log n) | 2 × n/2 |
| Karatsuba | O(n²) | O(n^1.585) | 3 × n/2 |
| Strassen | O(n³) | O(n^2.807) | 7 × n/2 |
| FFT | O(n²) | O(n log n) | 2 × n/2 |

---

## ✏️ Cvičení

1. Implementuj **QuickSelect** — O(n) průměrně nalezne k-tý nejmenší prvek bez plného řazení.
2. Napiš **rekurzivní výpočet FFT** (Fast Fourier Transform) — základ pro zpracování signálů.
3. Implementuj **rekurzivní flood fill** — bucket tool z grafických editorů (4-směrový i 8-směrový).
4. Vyresuj **Mandelbrotovu množinu** v ASCII — každý bod grid = rekurzivní iterace z² + c.
5. Paralelizuj Closest Pair pomocí `asyncio.gather` — levá a pravá polovina rekurzivně paralelně.
