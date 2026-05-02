"""Lekce 150 — Divide & Conquer + rekurzivní fraktály.

Spuštění:
    uv run l150_divide_and_conquer.py
"""

import asyncio
import math
import random
import time
from typing import NamedTuple


# ── Binární vyhledávání ───────────────────────────────────────────────────────

def binary_search(arr: list, cil, lo=0, hi=None) -> int:
    if hi is None: hi = len(arr) - 1
    if lo > hi: return -1
    mid = (lo + hi) // 2
    if arr[mid] == cil: return mid
    if arr[mid] < cil: return binary_search(arr, cil, mid+1, hi)
    return binary_search(arr, cil, lo, mid-1)


# ── Nejbližší pár bodů ────────────────────────────────────────────────────────

class Bod(NamedTuple):
    x: float
    y: float

def dist(a: Bod, b: Bod) -> float:
    return math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2)

def nejblizsi_par_naivni(body):
    best, ba, bb = float("inf"), body[0], body[1]
    for i in range(len(body)):
        for j in range(i+1, len(body)):
            d = dist(body[i], body[j])
            if d < best: best, ba, bb = d, body[i], body[j]
    return best, ba, bb

def nejblizsi_par_dc(body):
    def strip_min(strip, d):
        strip.sort(key=lambda b: b.y)
        best, ba, bb = d, strip[0], strip[1] if len(strip)>=2 else strip[0]
        for i in range(len(strip)):
            for j in range(i+1, len(strip)):
                if strip[j].y - strip[i].y >= best: break
                v = dist(strip[i], strip[j])
                if v < best: best, ba, bb = v, strip[i], strip[j]
        return best, ba, bb

    def dc(pts):
        n = len(pts)
        if n <= 3:
            best, ba, bb = float("inf"), pts[0], pts[1] if n>1 else pts[0]
            for i in range(n):
                for j in range(i+1, n):
                    v = dist(pts[i], pts[j])
                    if v < best: best, ba, bb = v, pts[i], pts[j]
            return best, ba, bb
        mid = n // 2
        mx = pts[mid].x
        dl, al, bl = dc(pts[:mid])
        dr, ar, br = dc(pts[mid:])
        if dl <= dr: d, ba, bb = dl, al, bl
        else: d, ba, bb = dr, ar, br
        strip = [p for p in pts if abs(p.x-mx) < d]
        if len(strip) >= 2:
            ds, sa, sb = strip_min(strip, d)
            if ds < d: d, ba, bb = ds, sa, sb
        return d, ba, bb

    return dc(sorted(body, key=lambda b: b.x))


# ── Karatsuba ─────────────────────────────────────────────────────────────────

def karatsuba(x: int, y: int) -> int:
    if x < 10 or y < 10: return x * y
    n = max(len(str(x)), len(str(y)))
    m = n // 2
    a, b = x // 10**m, x % 10**m
    c, d = y // 10**m, y % 10**m
    ac = karatsuba(a, c)
    bd = karatsuba(b, d)
    ad_bc = karatsuba(a+b, c+d) - ac - bd
    return ac * 10**(2*m) + ad_bc * 10**m + bd


# ── Fraktály ──────────────────────────────────────────────────────────────────

def sierpinski(n: int) -> list[str]:
    if n == 0: return ["*"]
    mensi = sierpinski(n-1)
    sirka = len(mensi[-1])
    mez = " " * (sirka//2 + 1)
    return [mez+r+mez for r in mensi] + [r+" "+r for r in mensi]


def dragon_curve(iterace: int) -> str:
    seq = "R"
    for _ in range(iterace-1):
        seq = seq + "R" + "".join("L" if z=="R" else "R" for z in reversed(seq))
    return seq


def dragon_ascii(seq: str, w=50, h=18) -> list[str]:
    grid = [[" "]*w for _ in range(h)]
    x, y = w//2, h//2
    smer = 0
    dx, dy = [1,0,-1,0], [0,1,0,-1]
    if 0<=x<w and 0<=y<h: grid[y][x]="▪"
    for z in seq:
        smer = (smer + (1 if z=="R" else -1)) % 4
        x += dx[smer]; y += dy[smer]
        if 0<=x<w and 0<=y<h: grid[y][x]="▪"
    return ["".join(r) for r in grid]


def mandelbrot_ascii(w=60, h=24, max_iter=30) -> list[str]:
    """Mandelbrotova množina v ASCII."""
    chars = " .·:+*#@"
    radky = []
    for py in range(h):
        radek = ""
        for px in range(w):
            c = complex(
                -2.5 + px * 3.5 / w,
                -1.25 + py * 2.5 / h
            )
            z, n = 0, 0
            while abs(z) <= 2 and n < max_iter:
                z = z*z + c
                n += 1
            radek += chars[n * (len(chars)-1) // max_iter]
        radky.append(radek)
    return radky


# ── Async paralelní merge sort ────────────────────────────────────────────────

async def async_merge_sort(arr: list, chunk: int = 200) -> list:
    if len(arr) <= chunk: return sorted(arr)
    mid = len(arr) // 2
    leva, prava = await asyncio.gather(
        async_merge_sort(arr[:mid], chunk),
        async_merge_sort(arr[mid:], chunk),
    )
    r, i, j = [], 0, 0
    while i < len(leva) and j < len(prava):
        if leva[i] <= prava[j]: r.append(leva[i]); i += 1
        else: r.append(prava[j]); j += 1
    return r + leva[i:] + prava[j:]


async def main():
    print("=" * 55)
    print("  ⚡ Divide & Conquer + Fraktály Demo")
    print("=" * 55)

    # Binary search
    print("\n=== Binární vyhledávání (rekurzivní) ===")
    arr = list(range(0, 200, 2))
    for x in [42, 99, 0, 198, 7]:
        idx = binary_search(arr, x)
        print(f"  Hledám {x:3d}: index={idx}")

    # Nejbližší pár
    print("\n=== Nejbližší pár bodů ===")
    random.seed(42)
    body = [Bod(random.uniform(0,100), random.uniform(0,100)) for _ in range(1000)]

    t = time.perf_counter()
    d_n, *_ = nejblizsi_par_naivni(body[:100])
    t_n = time.perf_counter()-t

    t = time.perf_counter()
    d_dc, a, b = nejblizsi_par_dc(body)
    t_dc = time.perf_counter()-t

    print(f"  Naivní  (100 bodů): vzdálenost={d_n:.4f}, {t_n*1000:.1f}ms")
    print(f"  D&C  (1000 bodů): vzdálenost={d_dc:.4f}, {t_dc*1000:.1f}ms")

    # Karatsuba
    print("\n=== Karatsuba násobení ===")
    for x, y in [(123456789, 987654321), (999999999999, 888888888888)]:
        k = karatsuba(x, y)
        ok = "✅" if k == x*y else "❌"
        print(f"  {ok} {x} × {y} = {k}")

    # Sierpiňský trojúhelník
    print("\n=== Sierpiňský trojúhelník (hloubka 3) ===")
    for radek in sierpinski(3):
        print(" ", radek)

    # Dragon Curve
    print("\n=== Dragon Curve (11 iterací) ===")
    seq = dragon_curve(11)
    for radek in dragon_ascii(seq):
        if radek.strip(): print(" ", radek)

    # Mandelbrot
    print("\n=== Mandelbrotova množina ===")
    for radek in mandelbrot_ascii(60, 20):
        print(" ", radek)

    # Async merge sort
    print("\n=== Async paralelní Merge Sort ===")
    random.seed(7)
    data = [random.randint(0, 10000) for _ in range(5000)]

    t = time.perf_counter()
    seq_r = sorted(data)
    t_seq = time.perf_counter()-t

    t = time.perf_counter()
    par_r = await async_merge_sort(data)
    t_par = time.perf_counter()-t

    ok = "✅" if seq_r == par_r else "❌"
    print(f"  {ok} sorted():       {t_seq*1000:.2f}ms")
    print(f"  {ok} async merge:    {t_par*1000:.2f}ms")

    print("\n✅ Demo dokončeno!")


if __name__ == "__main__":
    asyncio.run(main())
