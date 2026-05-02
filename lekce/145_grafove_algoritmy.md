# Lekce 145: Grafové algoritmy

Grafy modelují vztahy mezi objekty — sociální sítě, mapy, závislosti balíčků, routování. Paralelní a async varianty pro výkon.

---

## 📐 Reprezentace grafů

```python
from collections import defaultdict
from typing import Iterator

# Adjacency list — nejčastější
graf_orientovany = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D", "E"],
    "D": ["F"],
    "E": ["F"],
    "F": []
}

# Ohodnocený graf (weighted)
graf_ohodnoceny = {
    "A": [("B", 4), ("C", 2)],
    "B": [("D", 3), ("E", 1)],
    "C": [("B", 1), ("D", 5)],
    "D": [("F", 2)],
    "E": [("D", 1), ("F", 6)],
    "F": []
}

# Matice sousednosti — pro husté grafy
import numpy as np
matice = np.array([
    [0, 4, 2, 0, 0, 0],
    [0, 0, 0, 3, 1, 0],
    [0, 1, 0, 5, 0, 0],
    [0, 0, 0, 0, 0, 2],
    [0, 0, 0, 1, 0, 6],
    [0, 0, 0, 0, 0, 0],
])
```

---

## 🔍 BFS — Prohledávání do šířky

**Nejkratší cesta** (neohodnocený graf). O(V + E).

```python
from collections import deque

def bfs(graf: dict, start: str) -> list[str]:
    """Vrátí uzly v BFS pořadí."""
    navstivene = {start}
    fronta = deque([start])
    poradi = []
    while fronta:
        uzel = fronta.popleft()
        poradi.append(uzel)
        for soused in graf.get(uzel, []):
            if soused not in navstivene:
                navstivene.add(soused)
                fronta.append(soused)
    return poradi


def bfs_cesta(graf: dict, start: str, cil: str) -> list[str] | None:
    """Nejkratší cesta v neohodnoceném grafu."""
    if start == cil:
        return [start]
    navstivene = {start}
    fronta = deque([[start]])
    while fronta:
        cesta = fronta.popleft()
        uzel = cesta[-1]
        for soused in graf.get(uzel, []):
            if soused == cil:
                return cesta + [soused]
            if soused not in navstivene:
                navstivene.add(soused)
                fronta.append(cesta + [soused])
    return None


print("BFS:", bfs(graf_orientovany, "A"))
print("Cesta A→F:", bfs_cesta(graf_orientovany, "A", "F"))
```

---

## 🌀 DFS — Prohledávání do hloubky

**Průchod, detekce cyklů, topologické řazení.** O(V + E).

```python
def dfs(graf: dict, start: str, navstivene: set = None) -> list[str]:
    if navstivene is None:
        navstivene = set()
    navstivene.add(start)
    poradi = [start]
    for soused in graf.get(start, []):
        if soused not in navstivene:
            poradi.extend(dfs(graf, soused, navstivene))
    return poradi


def dfs_iterativni(graf: dict, start: str) -> list[str]:
    """Iterativní DFS — bez rizika stack overflow pro velké grafy."""
    navstivene = set()
    zasobnik = [start]
    poradi = []
    while zasobnik:
        uzel = zasobnik.pop()
        if uzel not in navstivene:
            navstivene.add(uzel)
            poradi.append(uzel)
            for soused in reversed(graf.get(uzel, [])):
                if soused not in navstivene:
                    zasobnik.append(soused)
    return poradi


def ma_cyklus(graf: dict) -> bool:
    """Detekce cyklu v orientovaném grafu pomocí DFS."""
    bile = set(graf.keys())   # nenavštívené
    sede = set()              # právě zpracovávané
    cerne = set()             # hotové

    def dfs_barvy(uzel: str) -> bool:
        bile.discard(uzel)
        sede.add(uzel)
        for soused in graf.get(uzel, []):
            if soused in sede:
                return True   # nalezen cyklus
            if soused in bile:
                if dfs_barvy(soused):
                    return True
        sede.discard(uzel)
        cerne.add(uzel)
        return False

    for uzel in list(bile):
        if uzel in bile:
            if dfs_barvy(uzel):
                return True
    return False


print("\nDFS:", dfs(graf_orientovany, "A"))
print("Má cyklus:", ma_cyklus(graf_orientovany))
```

---

## 📊 Topologické řazení

Řazení uzlů DAGu (Directed Acyclic Graph) — závislosti, build systémy.

```python
def topologicke_razeni(graf: dict) -> list[str]:
    """Kahnův algoritmus — BFS přístup."""
    vstupni_stupen = defaultdict(int)
    for uzel in graf:
        for soused in graf[uzel]:
            vstupni_stupen[soused] += 1

    fronta = deque([u for u in graf if vstupni_stupen[u] == 0])
    vysledek = []

    while fronta:
        uzel = fronta.popleft()
        vysledek.append(uzel)
        for soused in graf[uzel]:
            vstupni_stupen[soused] -= 1
            if vstupni_stupen[soused] == 0:
                fronta.append(soused)

    if len(vysledek) != len(graf):
        raise ValueError("Graf obsahuje cyklus — topologické řazení není možné")
    return vysledek


zavislosti = {
    "numpy": [],
    "pandas": ["numpy"],
    "matplotlib": ["numpy"],
    "seaborn": ["matplotlib", "pandas"],
    "sklearn": ["numpy", "scipy"],
    "scipy": ["numpy"],
}
print("\nPořadí instalace:", topologicke_razeni(zavislosti))
```

---

## 🗺️ Dijkstrův algoritmus

**Nejkratší cesta** v ohodnoceném grafu (kladné váhy). O((V + E) log V).

```python
import heapq

def dijkstra(graf: dict, start: str) -> tuple[dict, dict]:
    """
    Vrátí (vzdalenosti, predchudci).
    graf: {uzel: [(soused, vaha), ...]}
    """
    vzdalenosti = {uzel: float("inf") for uzel in graf}
    vzdalenosti[start] = 0
    predchudci = {uzel: None for uzel in graf}
    prioritni_fronta = [(0, start)]

    while prioritni_fronta:
        aktualni_vzd, uzel = heapq.heappop(prioritni_fronta)
        if aktualni_vzd > vzdalenosti[uzel]:
            continue   # zastaralý záznam
        for soused, vaha in graf.get(uzel, []):
            nova_vzd = vzdalenosti[uzel] + vaha
            if nova_vzd < vzdalenosti[soused]:
                vzdalenosti[soused] = nova_vzd
                predchudci[soused] = uzel
                heapq.heappush(prioritni_fronta, (nova_vzd, soused))

    return vzdalenosti, predchudci


def rekonstruuj_cestu(predchudci: dict, start: str, cil: str) -> list[str]:
    cesta = []
    uzel = cil
    while uzel is not None:
        cesta.append(uzel)
        uzel = predchudci[uzel]
    cesta.reverse()
    return cesta if cesta[0] == start else []


vzd, pred = dijkstra(graf_ohodnoceny, "A")
print("\nDijkstra od A:")
for uzel, d in vzd.items():
    cesta = rekonstruuj_cestu(pred, "A", uzel)
    print(f"  A → {uzel}: vzdálenost={d}, cesta={cesta}")
```

---

## ⭐ A* algoritmus

Dijkstra + **heuristika** (odhad vzdálenosti k cíli). Rychlejší pro mapy.

```python
def a_star(
    graf: dict,
    start: tuple,
    cil: tuple,
    heuristika=None
) -> list[tuple] | None:
    """A* pro 2D mřížku. Graf: {(r,c): [(soused, vaha), ...]}"""
    if heuristika is None:
        def heuristika(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance

    otevrene = [(0, start)]
    g_skore = {start: 0}
    predchudci = {start: None}

    while otevrene:
        _, aktualni = heapq.heappop(otevrene)
        if aktualni == cil:
            cesta = []
            while aktualni:
                cesta.append(aktualni)
                aktualni = predchudci[aktualni]
            return list(reversed(cesta))

        for soused, vaha in graf.get(aktualni, []):
            novy_g = g_skore[aktualni] + vaha
            if novy_g < g_skore.get(soused, float("inf")):
                g_skore[soused] = novy_g
                f_skore = novy_g + heuristika(soused, cil)
                heapq.heappush(otevrene, (f_skore, soused))
                predchudci[soused] = aktualni

    return None  # cesta nenalezena


# Příklad: A* na 2D mřížce
def vytvor_mrizku(radky: int, sloupce: int, prekazky: set) -> dict:
    graf = {}
    for r in range(radky):
        for c in range(sloupce):
            if (r, c) in prekazky:
                continue
            sousede = []
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < radky and 0 <= nc < sloupce and (nr,nc) not in prekazky:
                    sousede.append(((nr, nc), 1))
            graf[(r, c)] = sousede
    return graf

prekazky = {(1,1),(1,2),(2,1),(3,3)}
mrizka = vytvor_mrizku(5, 5, prekazky)
cesta = a_star(mrizka, (0,0), (4,4))
print("\nA* cesta (0,0)→(4,4):", cesta)
```

---

## ⚡ Paralelní BFS s asyncio

```python
import asyncio
from collections import deque

async def async_bfs_uzel(uzel: str, sousede: list[str]) -> list[str]:
    """Simulace async zpracování uzlu (např. HTTP request)."""
    await asyncio.sleep(0.01)   # simulace I/O
    return sousede


async def parallel_bfs(graf: dict, start: str) -> list[str]:
    """BFS kde zpracování každého uzlu je async operace."""
    navstivene = {start}
    fronta = deque([start])
    poradi = []

    while fronta:
        # Zpracuj celou úroveň paralelně
        uroven = list(fronta)
        fronta.clear()

        # Paralelní zpracování uzlů stejné úrovně
        tasky = [
            asyncio.create_task(async_bfs_uzel(uzel, graf.get(uzel, [])))
            for uzel in uroven
        ]
        vysledky = await asyncio.gather(*tasky)

        for uzel, sousede in zip(uroven, vysledky):
            poradi.append(uzel)
            for soused in sousede:
                if soused not in navstivene:
                    navstivene.add(soused)
                    fronta.append(soused)

    return poradi


asyncio.run(parallel_bfs(graf_orientovany, "A"))
```

---

## 🔗 Komponenty silné souvislosti (Tarjanův algoritmus)

```python
def tarjan_scc(graf: dict) -> list[list[str]]:
    """Najde všechny silně souvislé komponenty."""
    index_pocitadlo = [0]
    zasobnik = []
    na_zasobniku = set()
    index = {}
    lowlink = {}
    komponenty = []

    def strongconnect(uzel):
        index[uzel] = lowlink[uzel] = index_pocitadlo[0]
        index_pocitadlo[0] += 1
        zasobnik.append(uzel)
        na_zasobniku.add(uzel)

        for soused in graf.get(uzel, []):
            if soused not in index:
                strongconnect(soused)
                lowlink[uzel] = min(lowlink[uzel], lowlink[soused])
            elif soused in na_zasobniku:
                lowlink[uzel] = min(lowlink[uzel], index[soused])

        if lowlink[uzel] == index[uzel]:
            komponenta = []
            while True:
                w = zasobnik.pop()
                na_zasobniku.discard(w)
                komponenta.append(w)
                if w == uzel:
                    break
            komponenty.append(komponenta)

    for uzel in graf:
        if uzel not in index:
            strongconnect(uzel)
    return komponenty
```

---

## 🎯 Přehled algoritmů

| Algoritmus | Složitost | Použití |
|------------|-----------|---------|
| BFS | O(V+E) | nejkratší cesta (neohodnocená) |
| DFS | O(V+E) | průchod, cykly, topologické řazení |
| Dijkstra | O((V+E) log V) | nejkratší cesta (kladné váhy) |
| Bellman-Ford | O(VE) | nejkratší cesta (záporné váhy) |
| A* | O(E log V) | nejkratší cesta s heuristikou |
| Floyd-Warshall | O(V³) | nejkratší cesty mezi všemi páry |
| Kahn | O(V+E) | topologické řazení |
| Tarjan | O(V+E) | silně souvislé komponenty |

---

## ✏️ Cvičení

1. Implementuj **Bellman-Ford** — detekuj záporné cykly.
2. Napiš BFS pro nalezení **nejkratší cesty v bludišti** (2D mřížka, '#' = zeď).
3. Implementuj **Floyd-Warshall** pro nejkratší cesty mezi všemi páry uzlů.
4. Napiš paralelní Dijkstru pomocí `asyncio` — simuluj async fetch vzdálenosti hran.
5. Detekuj **mostové hrany** (bridge edges) v neorientovaném grafu — jejich odebrání rozdělí graf.
