# Lekce 148: Evoluční algoritmy

Evoluční algoritmy (EA) jsou rodina optimalizačních metod. Oproti GA jsou obecnější a zahrnují **diferenciální evoluci, CMA-ES, rojové inteligence (PSO)** a další.

---

## 🌊 Particle Swarm Optimization (PSO)

Inspirováno chováním hejn ptáků. Každá částice = kandidátní řešení. Pohybuje se prostorem vlivem vlastní nejlepší pozice a globálního nejlepšího.

```python
import asyncio
import random
import math
import time
from dataclasses import dataclass, field
from concurrent.futures import ProcessPoolExecutor
from typing import Callable


@dataclass
class Castice:
    pozice: list[float]
    rychlost: list[float]
    nejlepsi_pozice: list[float] = field(default_factory=list)
    nejlepsi_fitness: float = float("inf")
    fitness: float = float("inf")

    def __post_init__(self):
        if not self.nejlepsi_pozice:
            self.nejlepsi_pozice = self.pozice[:]


class PSO:
    def __init__(
        self,
        fitness_fn: Callable[[list[float]], float],
        dimenze: int,
        meze: tuple[float, float] = (-5.0, 5.0),
        n_castic: int = 50,
        max_iteraci: int = 200,
        w: float = 0.7,    # setrvačnost
        c1: float = 1.5,   # kognitivní koeficient (vlastní nejlepší)
        c2: float = 1.5,   # sociální koeficient (globální nejlepší)
    ):
        self.fn = fitness_fn
        self.dim = dimenze
        self.meze = meze
        self.n = n_castic
        self.max_iter = max_iteraci
        self.w = w
        self.c1 = c1
        self.c2 = c2

    def _nahodna_castice(self) -> Castice:
        lo, hi = self.meze
        pozice = [random.uniform(lo, hi) for _ in range(self.dim)]
        max_v = (hi - lo) * 0.1
        rychlost = [random.uniform(-max_v, max_v) for _ in range(self.dim)]
        return Castice(pozice, rychlost)

    def optimalizuj(self, verbose: bool = True) -> tuple[list[float], float, list[float]]:
        castice = [self._nahodna_castice() for _ in range(self.n)]

        # Inicializace fitness
        for c in castice:
            c.fitness = self.fn(c.pozice)
            c.nejlepsi_fitness = c.fitness
            c.nejlepsi_pozice = c.pozice[:]

        globalni_nejlepsi = min(castice, key=lambda c: c.nejlepsi_fitness)
        g_best_pos = globalni_nejlepsi.nejlepsi_pozice[:]
        g_best_fit = globalni_nejlepsi.nejlepsi_fitness

        historie = [g_best_fit]

        for iterace in range(self.max_iter):
            for c in castice:
                for d in range(self.dim):
                    r1, r2 = random.random(), random.random()
                    # Aktualizace rychlosti
                    c.rychlost[d] = (
                        self.w * c.rychlost[d]
                        + self.c1 * r1 * (c.nejlepsi_pozice[d] - c.pozice[d])
                        + self.c2 * r2 * (g_best_pos[d] - c.pozice[d])
                    )
                    # Omezení rychlosti
                    max_v = (self.meze[1] - self.meze[0]) * 0.1
                    c.rychlost[d] = max(-max_v, min(max_v, c.rychlost[d]))
                    # Aktualizace pozice
                    c.pozice[d] += c.rychlost[d]
                    c.pozice[d] = max(self.meze[0], min(self.meze[1], c.pozice[d]))

                # Ohodnocení
                c.fitness = self.fn(c.pozice)
                if c.fitness < c.nejlepsi_fitness:
                    c.nejlepsi_fitness = c.fitness
                    c.nejlepsi_pozice = c.pozice[:]

                if c.nejlepsi_fitness < g_best_fit:
                    g_best_fit = c.nejlepsi_fitness
                    g_best_pos = c.nejlepsi_pozice[:]

            historie.append(g_best_fit)
            if verbose and iterace % 50 == 0:
                print(f"  Iter {iterace:4d}: fitness={g_best_fit:.6f}")

        return g_best_pos, g_best_fit, historie


# Test na Rastrigin funkci (mnoho lokálních minim)
def rastrigin(x: list[float]) -> float:
    n = len(x)
    return 10 * n + sum(xi**2 - 10 * math.cos(2 * math.pi * xi) for xi in x)


def sphere(x: list[float]) -> float:
    return sum(xi**2 for xi in x)


print("=== PSO: Rastrigin (minimum = 0 v [0,...,0]) ===")
pso = PSO(rastrigin, dimenze=5, meze=(-5.12, 5.12), n_castic=50, max_iteraci=300)
best_pos, best_fit, _ = pso.optimalizuj(verbose=False)
print(f"  Nalezené minimum: {best_fit:.6f}")
print(f"  Pozice: {[round(x, 4) for x in best_pos]}")
```

---

## 🔄 Diferenciální evoluce (DE)

Robustní EA pro spojitou optimalizaci. Mutace = kombinace tří náhodných jedinců.

```python
class DifferentialEvolution:
    def __init__(
        self,
        fitness_fn: Callable[[list[float]], float],
        dimenze: int,
        meze: tuple[float, float] = (-5.0, 5.0),
        velikost_pop: int = 50,
        max_generaci: int = 300,
        F: float = 0.8,     # faktor mutace (0.4–1.0)
        CR: float = 0.9,    # pravděpodobnost křížení
    ):
        self.fn = fitness_fn
        self.dim = dimenze
        self.meze = meze
        self.pop_size = velikost_pop
        self.max_gen = max_generaci
        self.F = F
        self.CR = CR

    def optimalizuj(self, verbose: bool = True) -> tuple[list[float], float, list[float]]:
        lo, hi = self.meze
        # Inicializace populace
        pop = [[random.uniform(lo, hi) for _ in range(self.dim)]
               for _ in range(self.pop_size)]
        fitness_pop = [self.fn(ind) for ind in pop]

        nejlepsi_idx = min(range(self.pop_size), key=lambda i: fitness_pop[i])
        historie = [fitness_pop[nejlepsi_idx]]

        for generace in range(self.max_gen):
            for i in range(self.pop_size):
                # Vyber 3 různé jedince (a ≠ b ≠ c ≠ i)
                kandidati = [j for j in range(self.pop_size) if j != i]
                a, b, c = random.sample(kandidati, 3)

                # Mutace: v = pop[a] + F * (pop[b] - pop[c])
                mutant = [
                    max(lo, min(hi, pop[a][d] + self.F * (pop[b][d] - pop[c][d])))
                    for d in range(self.dim)
                ]

                # Křížení: zkombinuj mutanta s pop[i]
                trial = [
                    mutant[d] if random.random() < self.CR or d == random.randint(0, self.dim-1)
                    else pop[i][d]
                    for d in range(self.dim)
                ]

                # Selekce: lepší z trial a pop[i]
                trial_fitness = self.fn(trial)
                if trial_fitness <= fitness_pop[i]:
                    pop[i] = trial
                    fitness_pop[i] = trial_fitness

            nejlepsi_idx = min(range(self.pop_size), key=lambda i: fitness_pop[i])
            historie.append(fitness_pop[nejlepsi_idx])

            if verbose and generace % 50 == 0:
                print(f"  Gen {generace:4d}: fitness={fitness_pop[nejlepsi_idx]:.6f}")

        nejlepsi_idx = min(range(self.pop_size), key=lambda i: fitness_pop[i])
        return pop[nejlepsi_idx], fitness_pop[nejlepsi_idx], historie


print("\n=== Diferenciální evoluce: Rastrigin ===")
de = DifferentialEvolution(rastrigin, dimenze=5, meze=(-5.12, 5.12))
best_pos, best_fit, _ = de.optimalizuj(verbose=False)
print(f"  Nalezené minimum: {best_fit:.6f}")
```

---

## 🧮 CMA-ES (Covariance Matrix Adaptation)

Nejrobustnější EA pro spojitou optimalizaci. Adaptuje kovariančí matici.

```python
def cma_es_simple(
    fitness_fn: Callable[[list[float]], float],
    x0: list[float],
    sigma0: float = 0.5,
    max_iter: int = 500,
    lambda_: int = None,  # velikost populace
) -> tuple[list[float], float]:
    """Zjednodušená verze CMA-ES (bez plné adaptace)."""
    n = len(x0)
    if lambda_ is None:
        lambda_ = 4 + int(3 * math.log(n))

    mu = lambda_ // 2
    pesos = [math.log(mu + 0.5) - math.log(i + 1) for i in range(mu)]
    suma_pesos = sum(pesos)
    pesos = [p / suma_pesos for p in pesos]

    mean = x0[:]
    sigma = sigma0
    pc = [0.0] * n  # evoluční cesta
    ps = [0.0] * n
    C = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]  # kovariační matice

    cs = (mu + 2) / (n + mu + 5)
    cc = (4 + mu/n) / (n + 4 + 2*mu/n)
    chiN = math.sqrt(n) * (1 - 1/(4*n) + 1/(21*n**2))

    nejlepsi_fitness = float("inf")
    nejlepsi_reseni = mean[:]

    for iterace in range(max_iter):
        # Vzorkování populace
        populace = []
        for _ in range(lambda_):
            z = [random.gauss(0, 1) for _ in range(n)]
            # Transformace pomocí kovariační matice (zjednodušená)
            y = [sum(math.sqrt(max(0, C[i][j])) * z[j] if i == j else 0
                     for j in range(n)) for i in range(n)]
            x = [mean[i] + sigma * y[i] for i in range(n)]
            f = fitness_fn(x)
            populace.append((f, x, z))

        populace.sort(key=lambda t: t[0])

        if populace[0][0] < nejlepsi_fitness:
            nejlepsi_fitness = populace[0][0]
            nejlepsi_reseni = populace[0][1][:]

        # Aktualizace mean
        novy_mean = []
        for i in range(n):
            novy_mean.append(sum(pesos[k] * populace[k][1][i] for k in range(mu)))

        if iterace % 100 == 0 and iterace > 0:
            print(f"  Iter {iterace:4d}: sigma={sigma:.4f}, fitness={nejlepsi_fitness:.6f}")

        mean = novy_mean

        # Zjednodušená sigma adaptace
        sigma *= math.exp(0.2 * (sum(populace[k][0] for k in range(mu)) /
                                  (mu * nejlepsi_fitness + 1e-10) - 1))
        sigma = max(1e-10, min(1.0, sigma))

    return nejlepsi_reseni, nejlepsi_fitness


print("\n=== CMA-ES: Sphere funkce ===")
reseni, fitness = cma_es_simple(sphere, x0=[3.0, 3.0, 3.0], sigma0=1.0, max_iter=300)
print(f"  Nalezené minimum: {fitness:.8f}")
print(f"  Pozice: {[round(x, 6) for x in reseni]}")
```

---

## ⚡ Async paralelní EA

```python
async def async_ohodnot(
    populace: list[list[float]],
    fitness_fn: Callable,
    n_workers: int = 4
) -> list[float]:
    """Paralelní ohodnocení populace přes ProcessPoolExecutor."""
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor(max_workers=n_workers) as ex:
        futures = [
            loop.run_in_executor(ex, fitness_fn, jedinec)
            for jedinec in populace
        ]
        return await asyncio.gather(*futures)


async def parallel_de(fitness_fn, dimenze: int, max_gen: int = 100):
    """DE s paralelním vyhodnocením fitness."""
    lo, hi = -5.12, 5.12
    pop_size = 50
    F, CR = 0.8, 0.9

    pop = [[random.uniform(lo, hi) for _ in range(dimenze)] for _ in range(pop_size)]
    fitness_pop = await async_ohodnot(pop, fitness_fn)

    for gen in range(max_gen):
        trial_pop = []
        for i in range(pop_size):
            kandidati = [j for j in range(pop_size) if j != i]
            a, b, c = random.sample(kandidati, 3)
            mutant = [max(lo, min(hi, pop[a][d] + F * (pop[b][d] - pop[c][d])))
                      for d in range(dimenze)]
            trial = [mutant[d] if random.random() < CR else pop[i][d]
                     for d in range(dimenze)]
            trial_pop.append(trial)

        # Paralelní ohodnocení trials
        trial_fitness = await async_ohodnot(trial_pop, fitness_fn)

        for i in range(pop_size):
            if trial_fitness[i] <= fitness_pop[i]:
                pop[i] = trial_pop[i]
                fitness_pop[i] = trial_fitness[i]

    nejlepsi_idx = min(range(pop_size), key=lambda i: fitness_pop[i])
    return pop[nejlepsi_idx], fitness_pop[nejlepsi_idx]


# asyncio.run(parallel_de(rastrigin, dimenze=10))
```

---

## 📊 Srovnání EA algoritmů

| Algoritmus | Typ problému | Silné stránky | Slabé stránky |
|------------|-------------|--------------|--------------|
| GA | diskrétní/kombinatorický | flexibilní, křížení | ladění parametrů |
| PSO | spojitý | jednoduchý, rychlý | uváznutí v lok. min |
| DE | spojitý | robustní, málo parametrů | pomalnější konvergence |
| CMA-ES | spojitý | self-adaptive, nejlepší pro unimodální | složitá implementace |
| Simulated Annealing | obecný | jednoduchý, uniká lok. min | pomalý |
| Ant Colony | kombinatorický | dobré pro grafy (TSP) | pomalý |

---

## 🎯 Benchmark funkcí

```python
def ackley(x: list[float]) -> float:
    """Mnoho lokálních minim, globální minimum v [0,...,0] = 0."""
    n = len(x)
    a, b, c = 20, 0.2, 2 * math.pi
    sum1 = sum(xi**2 for xi in x)
    sum2 = sum(math.cos(c * xi) for xi in x)
    return -a * math.exp(-b * math.sqrt(sum1/n)) - math.exp(sum2/n) + a + math.e

def rosenbrock(x: list[float]) -> float:
    """Banana funkce — globální minimum v [1,...,1] = 0."""
    return sum(100*(x[i+1]-x[i]**2)**2 + (1-x[i])**2 for i in range(len(x)-1))

def schwefel(x: list[float]) -> float:
    """Záludná — globální minimum daleko od lokálních."""
    return 418.9829 * len(x) - sum(xi * math.sin(math.sqrt(abs(xi))) for xi in x)
```

---

## ✏️ Cvičení

1. Implementuj **Simulated Annealing** — porovnej s PSO na Rastrigin funkci.
2. Napiš **NSGA-II** (multi-objektivní) — optimalizuj dvě protichůdné fitness funkce současně.
3. Parallelizuj PSO plně — každá částice jako async task, fitness přes ProcessPoolExecutor.
4. Implementuj **Ant Colony Optimization** pro TSP.
5. Porovnej GA, PSO, DE a CMA-ES na 5 benchmark funkcích — graf konvergence, čas, přesnost.
