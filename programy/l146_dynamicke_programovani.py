"""Lekce 146 — Dynamické programování: knapsack, LCS, edit distance.

Spuštění:
    uv run l146_dynamicke_programovani.py
"""

import asyncio
import time
from functools import lru_cache


# ── Fibonacci ─────────────────────────────────────────────────────────────────

def fib_naivni(n):
    if n <= 1: return n
    return fib_naivni(n-1) + fib_naivni(n-2)

@lru_cache(maxsize=None)
def fib_memo(n):
    if n <= 1: return n
    return fib_memo(n-1) + fib_memo(n-2)

def fib_dp(n):
    if n <= 1: return n
    a, b = 0, 1
    for _ in range(2, n+1): a, b = b, a+b
    return b


# ── Knapsack ──────────────────────────────────────────────────────────────────

def knapsack(vahy, hodnoty, kapacita):
    n = len(vahy)
    dp = [[0]*(kapacita+1) for _ in range(n+1)]
    for i in range(1, n+1):
        for w in range(kapacita+1):
            dp[i][w] = dp[i-1][w]
            if vahy[i-1] <= w:
                dp[i][w] = max(dp[i][w], dp[i-1][w-vahy[i-1]] + hodnoty[i-1])
    # Rekonstrukce
    vybrane, w = [], kapacita
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            vybrane.append(i-1); w -= vahy[i-1]
    return dp[n][kapacita], list(reversed(vybrane))


# ── LCS ───────────────────────────────────────────────────────────────────────

def lcs(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            dp[i][j] = dp[i-1][j-1]+1 if s1[i-1]==s2[j-1] else max(dp[i-1][j], dp[i][j-1])
    # Rekonstrukce
    i, j, seq = m, n, []
    while i > 0 and j > 0:
        if s1[i-1] == s2[j-1]: seq.append(s1[i-1]); i -= 1; j -= 1
        elif dp[i-1][j] > dp[i][j-1]: i -= 1
        else: j -= 1
    return dp[m][n], "".join(reversed(seq))


# ── Edit Distance ──────────────────────────────────────────────────────────────

def edit_distance(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1): dp[i][0] = i
    for j in range(n+1): dp[0][j] = j
    for i in range(1, m+1):
        for j in range(1, n+1):
            if s1[i-1] == s2[j-1]: dp[i][j] = dp[i-1][j-1]
            else: dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    return dp[m][n]


# ── Coin Change ───────────────────────────────────────────────────────────────

def coin_change(mince, castka):
    dp = [float("inf")] * (castka+1)
    dp[0] = 0
    for c in range(1, castka+1):
        for m in mince:
            if m <= c: dp[c] = min(dp[c], dp[c-m]+1)
    return dp[castka] if dp[castka] != float("inf") else -1


# ── Async paralelní DP ────────────────────────────────────────────────────────

async def async_fib_worker(n: int) -> int:
    await asyncio.sleep(0)  # yield kontroly
    return fib_dp(n)


async def parallel_fib_sequence(hodnoty: list[int]) -> list[int]:
    """Paralelní výpočet Fibonacci čísel."""
    tasky = [asyncio.create_task(async_fib_worker(n)) for n in hodnoty]
    return await asyncio.gather(*tasky)


async def demo_async_dp():
    print("\n=== Async paralelní Fibonacci ===")
    hodnoty = list(range(30, 40))

    start = time.perf_counter()
    seq = [fib_dp(n) for n in hodnoty]
    t_seq = time.perf_counter() - start

    start = time.perf_counter()
    par = await parallel_fib_sequence(hodnoty)
    t_par = time.perf_counter() - start

    print(f"  Sekvenční: {t_seq*1000:.2f}ms → {seq[:3]}...")
    print(f"  Async:     {t_par*1000:.2f}ms → {par[:3]}...")
    assert seq == par


def main():
    print("=" * 50)
    print("  🧠 Dynamické programování Demo")
    print("=" * 50)

    # Fibonacci
    print("\n=== Fibonacci ===")
    n = 35
    for nazev, fn in [("Naivní", fib_naivni), ("Memo (@lru_cache)", fib_memo), ("DP O(1)", fib_dp)]:
        start = time.perf_counter()
        r = fn(n)
        t = (time.perf_counter()-start)*1000
        print(f"  {nazev:<22}: fib({n})={r}, {t:.2f}ms")

    # Knapsack
    print("\n=== Knapsack ===")
    vahy   = [2, 3, 4, 5, 1, 6, 3, 2]
    hodnoty = [3, 4, 5, 8, 2, 9, 6, 4]
    kapacita = 10
    max_h, vybrane = knapsack(vahy, hodnoty, kapacita)
    print(f"  Kapacita: {kapacita}, Max hodnota: {max_h}")
    print(f"  Věci: {vybrane}, Celková váha: {sum(vahy[i] for i in vybrane)}")

    # LCS
    print("\n=== LCS ===")
    for s1, s2 in [("ABCBDAB","BDCAB"), ("python","pyhton"), ("algoritmus","logaritmus")]:
        d, seq = lcs(s1, s2)
        print(f"  LCS('{s1}', '{s2}'): délka={d}, sekvence='{seq}'")

    # Edit distance
    print("\n=== Edit Distance ===")
    for s1, s2 in [("kitten","sitting"), ("python","pithon"), ("abc","abc"), ("","hello")]:
        print(f"  '{s1}' → '{s2}': {edit_distance(s1, s2)}")

    # Coin change
    print("\n=== Coin Change ===")
    for mince, castka in [([1,5,10,25], 41), ([2], 3), ([1,3,4], 6)]:
        print(f"  Mince {mince}, částka {castka}: {coin_change(mince, castka)} mincí")

    # Async
    asyncio.run(demo_async_dp())

    print("\n✅ Demo dokončeno!")


if __name__ == "__main__":
    main()
