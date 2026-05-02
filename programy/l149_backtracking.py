"""Lekce 149 — Backtracking: N-Queens, Sudoku, permutace, bludiště.

Spuštění:
    uv run l149_backtracking.py
"""

import asyncio
import copy
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Iterator


# ── N-Queens ──────────────────────────────────────────────────────────────────

def n_queens(n: int) -> list[list[int]]:
    reseni = []
    def bt(radek, sl, d1, d2, r):
        if radek == n: reseni.append(r[:]); return
        for s in range(n):
            if s in sl or (radek-s) in d1 or (radek+s) in d2: continue
            sl.add(s); d1.add(radek-s); d2.add(radek+s); r.append(s)
            bt(radek+1, sl, d1, d2, r)
            sl.remove(s); d1.remove(radek-s); d2.remove(radek+s); r.pop()
    bt(0, set(), set(), set(), [])
    return reseni


def zobraz_queens(r: list[int]) -> str:
    n = len(r)
    return "\n".join(" ".join("♛" if r[i]==s else "·" for s in range(n)) for i in range(n))


# ── Sudoku ────────────────────────────────────────────────────────────────────

def sudoku_solver(grid: list[list[int]]) -> bool:
    def validni(r, s, c):
        if c in grid[r]: return False
        if c in (grid[i][s] for i in range(9)): return False
        br, bs = 3*(r//3), 3*(s//3)
        return not any(grid[i][j]==c for i in range(br,br+3) for j in range(bs,bs+3))
    def prazdne():
        for r in range(9):
            for s in range(9):
                if grid[r][s]==0: return r,s
        return None
    p = prazdne()
    if p is None: return True
    r, s = p
    for c in range(1,10):
        if validni(r, s, c):
            grid[r][s] = c
            if sudoku_solver(grid): return True
            grid[r][s] = 0
    return False


# ── Permutace a kombinace ─────────────────────────────────────────────────────

def permutace_gen(prvky: list) -> Iterator[list]:
    if len(prvky) <= 1: yield prvky[:]; return
    for i in range(len(prvky)):
        prvky[0], prvky[i] = prvky[i], prvky[0]
        for p in permutace_gen(prvky[1:]): yield [prvky[0]] + p
        prvky[0], prvky[i] = prvky[i], prvky[0]


def kombinace(prvky: list, k: int) -> list[list]:
    vysledky = []
    def bt(start, akt):
        if len(akt) == k: vysledky.append(akt[:]); return
        for i in range(start, len(prvky)):
            akt.append(prvky[i]); bt(i+1, akt); akt.pop()
    bt(0, [])
    return vysledky


def podmnoziny(prvky: list) -> list[list]:
    vysledky = []
    def bt(start, akt):
        vysledky.append(akt[:])
        for i in range(start, len(prvky)):
            akt.append(prvky[i]); bt(i+1, akt); akt.pop()
    bt(0, [])
    return vysledky


# ── Bludiště ──────────────────────────────────────────────────────────────────

def vyres_bludiste(bludiste, start, cil):
    radky, sloupce = len(bludiste), len(bludiste[0])
    navs = {start}
    def bt(pos, cesta):
        if pos == cil: return True
        r, s = pos
        for dr, ds in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, ns = r+dr, s+ds
            nova = (nr, ns)
            if 0<=nr<radky and 0<=ns<sloupce and bludiste[nr][ns]==0 and nova not in navs:
                navs.add(nova); cesta.append(nova)
                if bt(nova, cesta): return True
                cesta.pop(); navs.remove(nova)
        return False
    navs.add(start); cesta = [start]
    return cesta if bt(start, cesta) else None


# ── Async paralelní N-Queens ──────────────────────────────────────────────────

def _queens_worker(args):
    n, prvni = args
    reseni = []
    def bt(radek, sl, d1, d2, r):
        if radek == n: reseni.append(r[:]); return
        for s in range(n):
            if s in sl or (radek-s) in d1 or (radek+s) in d2: continue
            sl.add(s); d1.add(radek-s); d2.add(radek+s); r.append(s)
            bt(radek+1, sl, d1, d2, r)
            sl.remove(s); d1.remove(radek-s); d2.remove(radek+s); r.pop()
    bt(1, {prvni}, {0-prvni}, {0+prvni}, [prvni])
    return reseni


async def queens_parallel(n: int) -> list[list[int]]:
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as ex:
        vysledky = await asyncio.gather(*[
            loop.run_in_executor(ex, _queens_worker, (n, s)) for s in range(n)
        ])
    return [r for cast in vysledky for r in cast]


async def main():
    print("=" * 50)
    print("  🔙 Backtracking Demo")
    print("=" * 50)

    # N-Queens
    print("\n=== N-Queens ===")
    for n in range(1, 10):
        r = n_queens(n)
        print(f"  {n}-Queens: {len(r)} řešení")

    print(f"\nJedno řešení 8-Queens:")
    reseni = n_queens(8)
    for radek in zobraz_queens(reseni[0]).split("\n"):
        print("  ", radek)

    # Paralelní N-Queens
    print("\n=== Paralelní N-Queens (12) ===")
    t = time.perf_counter()
    seq = n_queens(12)
    t_seq = time.perf_counter() - t

    t = time.perf_counter()
    par = await queens_parallel(12)
    t_par = time.perf_counter() - t

    print(f"  Sekvenční: {len(seq)} řešení za {t_seq*1000:.0f}ms")
    print(f"  Paralelní: {len(par)} řešení za {t_par*1000:.0f}ms")

    # Sudoku
    print("\n=== Sudoku Solver ===")
    sudoku = [
        [5,3,0,0,7,0,0,0,0],[6,0,0,1,9,5,0,0,0],[0,9,8,0,0,0,0,6,0],
        [8,0,0,0,6,0,0,0,3],[4,0,0,8,0,3,0,0,1],[7,0,0,0,2,0,0,0,6],
        [0,6,0,0,0,0,2,8,0],[0,0,0,4,1,9,0,0,5],[0,0,0,0,8,0,0,7,9],
    ]
    grid = copy.deepcopy(sudoku)
    t = time.perf_counter()
    ok = sudoku_solver(grid)
    print(f"  Vyřešeno: {ok} za {(time.perf_counter()-t)*1000:.1f}ms")
    print("  " + str(grid[0]))

    # Permutace
    print("\n=== Permutace a kombinace ===")
    prvky = [1, 2, 3, 4]
    pocet_perm = sum(1 for _ in permutace_gen(prvky[:]))
    print(f"  Permutace {prvky}: {pocet_perm}")
    print(f"  Kombinace {prvky} k=2: {kombinace(prvky, 2)}")
    print(f"  Podmnožiny {{1,2,3}}: {podmnoziny([1,2,3])}")

    # Bludiště
    print("\n=== Bludiště ===")
    bludiste = [
        [0,1,0,0,0],[0,1,0,1,0],[0,0,0,1,0],[1,1,0,0,0],[0,0,0,1,0]
    ]
    cesta = vyres_bludiste(bludiste, (0,0), (4,4))
    print(f"  Cesta: {cesta}")
    if cesta:
        cesta_set = set(cesta)
        for r in range(5):
            print("  " + "".join(
                "●" if (r,s) in cesta_set else "█" if bludiste[r][s]==1 else "·"
                for s in range(5)
            ))

    print("\n✅ Demo dokončeno!")


if __name__ == "__main__":
    asyncio.run(main())
