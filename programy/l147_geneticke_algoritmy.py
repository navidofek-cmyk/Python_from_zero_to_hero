"""Lekce 147 — Genetické algoritmy: knapsack, TSP, async fitness.

Spuštění:
    uv run l147_geneticke_algoritmy.py
"""

import asyncio
import math
import random
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field


@dataclass
class Jedinec:
    chromozom: list
    fitness: float = 0.0
    def __lt__(self, o): return self.fitness < o.fitness


def turnaj(populace, k=5):
    return max(random.sample(populace, k), key=lambda j: j.fitness)


def evoluj(
    vytvor, fitness_fn, krizeni_fn, mutace_fn,
    pop_size=80, generaci=150, p_kriz=0.8, p_mut=0.03, elita=2
):
    pop = [Jedinec(vytvor()) for _ in range(pop_size)]
    for j in pop: j.fitness = fitness_fn(j.chromozom)
    nejlepsi = max(pop, key=lambda j: j.fitness)
    historie = []

    for _ in range(generaci):
        pop.sort(key=lambda j: j.fitness, reverse=True)
        nejlepsi = max(nejlepsi, pop[0], key=lambda j: j.fitness)
        historie.append(pop[0].fitness)

        nova = list(pop[:elita])
        while len(nova) < pop_size:
            r1, r2 = turnaj(pop), turnaj(pop)
            c1, c2 = (krizeni_fn(r1.chromozom, r2.chromozom)
                      if random.random() < p_kriz
                      else (r1.chromozom[:], r2.chromozom[:]))
            for c in [c1, c2]:
                j = Jedinec(mutace_fn(c, p_mut))
                j.fitness = fitness_fn(j.chromozom)
                nova.append(j)
        pop = nova[:pop_size]

    return nejlepsi, historie


# ── Knapsack ──────────────────────────────────────────────────────────────────

def demo_knapsack():
    print("\n=== GA: Knapsack ===")
    veci = [(2,3),(3,4),(4,5),(5,8),(1,2),(6,9),(3,6),(2,4),(7,10),(4,7)]
    kapacita, n = 15, len(veci)

    def vytvor(): return [random.randint(0,1) for _ in range(n)]
    def fitness(c):
        vaha = sum(veci[i][0]*c[i] for i in range(n))
        return float(sum(veci[i][1]*c[i] for i in range(n))) if vaha <= kapacita else 0.0
    def krizeni(r1, r2):
        b = random.randint(1, n-1)
        return r1[:b]+r2[b:], r2[:b]+r1[b:]
    def mutace(c, p): return [1-g if random.random()<p else g for g in c]

    random.seed(42)
    nejlepsi, _ = evoluj(vytvor, fitness, krizeni, mutace, pop_size=60, generaci=120)
    vybrane = [i for i,g in enumerate(nejlepsi.chromozom) if g]
    print(f"  Hodnota: {nejlepsi.fitness:.0f}, Váha: {sum(veci[i][0] for i in vybrane)}/{kapacita}")
    print(f"  Věci: {vybrane}")


# ── TSP ───────────────────────────────────────────────────────────────────────

def demo_tsp():
    print("\n=== GA: TSP (Traveling Salesman) ===")
    random.seed(7)
    n = 12
    mesta = [(random.uniform(0,100), random.uniform(0,100)) for _ in range(n)]
    def vzdal(a, b): return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)
    def celkem(perm): return sum(vzdal(mesta[perm[i]], mesta[perm[(i+1)%n]]) for i in range(n))
    def fitness(c): return 1.0 / celkem(c)
    def vytvor():
        p = list(range(n)); random.shuffle(p); return p
    def ox(r1, r2):
        a, b = sorted(random.sample(range(n), 2))
        def make(p1, p2):
            d = [-1]*n; d[a:b+1] = p1[a:b+1]
            fill = [x for x in p2 if x not in d]; idx = 0
            for i in range(n):
                if d[i]==-1: d[i]=fill[idx]; idx+=1
            return d
        return make(r1,r2), make(r2,r1)
    def mutace(c, p):
        c = c[:]
        for i in range(n):
            if random.random()<p: j=random.randint(0,n-1); c[i],c[j]=c[j],c[i]
        return c

    nejlepsi, _ = evoluj(vytvor, fitness, ox, mutace, pop_size=100, generaci=300, p_mut=0.02)
    print(f"  Nejkratší trasa: {1/nejlepsi.fitness:.2f} jednotek")
    print(f"  Pořadí: {nejlepsi.chromozom}")


# ── Async paralelní fitness ────────────────────────────────────────────────────

def _fitness_heavy(chromozom):
    """CPU-heavy fitness (v separátním procesu)."""
    return -sum(math.sin(x*math.pi)*math.cos(x*2) for x in chromozom)

async def async_gen(pop):
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor(max_workers=4) as ex:
        return await asyncio.gather(*[
            loop.run_in_executor(ex, _fitness_heavy, j.chromozom) for j in pop
        ])

async def demo_async_ga():
    print("\n=== Async GA (paralelní fitness přes ProcessPool) ===")
    random.seed(42)
    pop = [Jedinec([random.uniform(-1,1) for _ in range(10)]) for _ in range(40)]

    t = time.perf_counter()
    for j in pop: j.fitness = _fitness_heavy(j.chromozom)
    t_seq = time.perf_counter()-t

    t = time.perf_counter()
    fitnesses = await async_gen(pop)
    for j, f in zip(pop, fitnesses): j.fitness = f
    t_par = time.perf_counter()-t

    print(f"  Sekvenční fitness: {t_seq*1000:.1f}ms")
    print(f"  Async/parallel:   {t_par*1000:.1f}ms")


def main():
    print("=" * 50)
    print("  🧬 Genetické algoritmy Demo")
    print("=" * 50)

    demo_knapsack()
    demo_tsp()
    asyncio.run(demo_async_ga())

    print("\n✅ Demo dokončeno!")


if __name__ == "__main__":
    main()
