"""Lekce 145 — Grafové algoritmy: BFS, DFS, Dijkstra, A*, async.

Spuštění:
    uv run l145_grafove_algoritmy.py
"""

import asyncio
import heapq
import time
from collections import deque, defaultdict


GRAF = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["D", "F"],
    "D": ["G"],
    "E": ["G"],
    "F": ["G"],
    "G": []
}

GRAF_OHODNOCENY = {
    "A": [("B", 4), ("C", 2)],
    "B": [("D", 3), ("E", 1)],
    "C": [("B", 1), ("D", 5)],
    "D": [("F", 2)],
    "E": [("D", 1), ("F", 6)],
    "F": []
}


def bfs(graf, start):
    navs = {start}; q = deque([start]); r = []
    while q:
        u = q.popleft(); r.append(u)
        for s in graf.get(u, []):
            if s not in navs: navs.add(s); q.append(s)
    return r


def bfs_cesta(graf, start, cil):
    if start == cil: return [start]
    navs = {start}; q = deque([[start]])
    while q:
        cesta = q.popleft(); u = cesta[-1]
        for s in graf.get(u, []):
            if s == cil: return cesta + [s]
            if s not in navs: navs.add(s); q.append(cesta + [s])
    return None


def dfs(graf, start, navs=None):
    if navs is None: navs = set()
    navs.add(start); r = [start]
    for s in graf.get(start, []):
        if s not in navs: r.extend(dfs(graf, s, navs))
    return r


def ma_cyklus(graf):
    bile, sede = set(graf.keys()), set()
    def visit(u):
        bile.discard(u); sede.add(u)
        for s in graf.get(u, []):
            if s in sede: return True
            if s in bile and visit(s): return True
        sede.discard(u)
        return False
    return any(visit(u) for u in list(bile) if u in bile)


def topologicke_razeni(graf):
    in_deg = defaultdict(int)
    for u in graf:
        for s in graf[u]: in_deg[s] += 1
    q = deque(u for u in graf if in_deg[u] == 0)
    r = []
    while q:
        u = q.popleft(); r.append(u)
        for s in graf[u]:
            in_deg[s] -= 1
            if in_deg[s] == 0: q.append(s)
    return r if len(r) == len(graf) else None


def dijkstra(graf, start):
    dist = {u: float("inf") for u in graf}
    dist[start] = 0
    pred = {u: None for u in graf}
    pq = [(0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]: continue
        for s, w in graf.get(u, []):
            nd = dist[u] + w
            if nd < dist[s]:
                dist[s] = nd; pred[s] = u
                heapq.heappush(pq, (nd, s))
    return dist, pred


def rekonstruuj(pred, start, cil):
    cesta, u = [], cil
    while u: cesta.append(u); u = pred[u]
    cesta.reverse()
    return cesta if cesta and cesta[0] == start else []


# ── Async BFS ─────────────────────────────────────────────────────────────────

async def async_fetch_sousede(uzel: str, graf: dict) -> list[str]:
    """Simulace async operace (HTTP request, DB dotaz)."""
    await asyncio.sleep(0.005)
    return graf.get(uzel, [])


async def async_bfs(graf, start):
    navs = {start}; q = deque([start]); r = []
    while q:
        uroven = list(q); q.clear()
        # Paralelní fetch sousedů celé úrovně
        tasky = [asyncio.create_task(async_fetch_sousede(u, graf)) for u in uroven]
        vysledky = await asyncio.gather(*tasky)
        for u, sousede in zip(uroven, vysledky):
            r.append(u)
            for s in sousede:
                if s not in navs: navs.add(s); q.append(s)
    return r


async def srovnej_bfs(graf):
    # Sekvenční
    start = time.perf_counter()
    seq = bfs(graf, "A")
    cas_seq = time.perf_counter() - start

    # Async (paralelní zpracování úrovně)
    start = time.perf_counter()
    par = await async_bfs(graf, "A")
    cas_par = time.perf_counter() - start

    return seq, cas_seq, par, cas_par


def main():
    print("=" * 50)
    print("  🗺️  Grafové algoritmy Demo")
    print("=" * 50)

    print(f"\nGraf: {dict(list(GRAF.items())[:4])}...")

    print("\n=== BFS / DFS ===")
    print(f"  BFS od A: {bfs(GRAF, 'A')}")
    print(f"  DFS od A: {dfs(GRAF, 'A')}")
    print(f"  Cesta A→G: {bfs_cesta(GRAF, 'A', 'G')}")
    print(f"  Má cyklus: {ma_cyklus(GRAF)}")

    print("\n=== Topologické řazení ===")
    zavislosti = {
        "numpy": [], "scipy": ["numpy"], "pandas": ["numpy"],
        "matplotlib": ["numpy"], "seaborn": ["matplotlib", "pandas"],
        "sklearn": ["numpy", "scipy"],
    }
    print(f"  Pořadí instalace: {topologicke_razeni(zavislosti)}")

    print("\n=== Dijkstra ===")
    dist, pred = dijkstra(GRAF_OHODNOCENY, "A")
    for cil in ["B", "C", "D", "E", "F"]:
        cesta = rekonstruuj(pred, "A", cil)
        print(f"  A→{cil}: vzdálenost={dist[cil]}, cesta={cesta}")

    print("\n=== Async paralelní BFS ===")
    seq, t_seq, par, t_par = asyncio.run(srovnej_bfs(GRAF))
    print(f"  Sekvenční BFS: {seq} ({t_seq*1000:.1f}ms)")
    print(f"  Async BFS:     {par} ({t_par*1000:.1f}ms)")
    assert seq == par, "Výsledky se liší!"
    print(f"  ✅ Výsledky jsou stejné")

    print("\n✅ Demo dokončeno!")


if __name__ == "__main__":
    main()
