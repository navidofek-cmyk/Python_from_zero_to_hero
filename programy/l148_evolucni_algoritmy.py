"""Lekce 148 — Evoluční algoritmy: PSO, Diferenciální evoluce, async.

Spuštění:
    uv run l148_evolucni_algoritmy.py
"""

import asyncio
import math
import random
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field


# ── Benchmark funkce ──────────────────────────────────────────────────────────

def rastrigin(x):
    n = len(x)
    return 10*n + sum(xi**2 - 10*math.cos(2*math.pi*xi) for xi in x)

def sphere(x):
    return sum(xi**2 for xi in x)

def ackley(x):
    n = len(x)
    a, b, c = 20, 0.2, 2*math.pi
    return (-a*math.exp(-b*math.sqrt(sum(xi**2 for xi in x)/n))
            - math.exp(sum(math.cos(c*xi) for xi in x)/n) + a + math.e)


# ── PSO ───────────────────────────────────────────────────────────────────────

def pso(fitness_fn, dim, bounds=(-5.12, 5.12), n=50, iters=300,
        w=0.7, c1=1.5, c2=1.5, seed=42):
    random.seed(seed)
    lo, hi = bounds
    pos  = [[random.uniform(lo,hi) for _ in range(dim)] for _ in range(n)]
    vel  = [[random.uniform(-(hi-lo)*0.1, (hi-lo)*0.1) for _ in range(dim)] for _ in range(n)]
    pb   = [p[:] for p in pos]
    pbf  = [fitness_fn(p) for p in pos]
    gi   = min(range(n), key=lambda i: pbf[i])
    gb, gbf = pb[gi][:], pbf[gi]
    hist = [gbf]

    for _ in range(iters):
        for i in range(n):
            for d in range(dim):
                r1, r2 = random.random(), random.random()
                vel[i][d] = (w*vel[i][d]
                             + c1*r1*(pb[i][d]-pos[i][d])
                             + c2*r2*(gb[d]-pos[i][d]))
                vel[i][d] = max(-0.5, min(0.5, vel[i][d]))
                pos[i][d] = max(lo, min(hi, pos[i][d]+vel[i][d]))
            f = fitness_fn(pos[i])
            if f < pbf[i]: pbf[i]=f; pb[i]=pos[i][:]
            if f < gbf: gbf=f; gb=pos[i][:]
        hist.append(gbf)

    return gb, gbf, hist


# ── Diferenciální evoluce ─────────────────────────────────────────────────────

def de(fitness_fn, dim, bounds=(-5.12, 5.12), pop_size=50,
       max_gen=300, F=0.8, CR=0.9, seed=42):
    random.seed(seed)
    lo, hi = bounds
    pop = [[random.uniform(lo,hi) for _ in range(dim)] for _ in range(pop_size)]
    fit = [fitness_fn(ind) for ind in pop]
    hist = [min(fit)]

    for _ in range(max_gen):
        for i in range(pop_size):
            a,b,c = random.sample([j for j in range(pop_size) if j!=i], 3)
            mutant = [max(lo,min(hi, pop[a][d]+F*(pop[b][d]-pop[c][d]))) for d in range(dim)]
            jrand = random.randint(0, dim-1)
            trial = [mutant[d] if random.random()<CR or d==jrand else pop[i][d] for d in range(dim)]
            tf = fitness_fn(trial)
            if tf <= fit[i]: pop[i]=trial; fit[i]=tf
        hist.append(min(fit))

    bi = min(range(pop_size), key=lambda i: fit[i])
    return pop[bi], fit[bi], hist


# ── Async paralelní DE ────────────────────────────────────────────────────────

def _eval(args):
    fn_name, x = args
    fns = {"rastrigin": rastrigin, "sphere": sphere, "ackley": ackley}
    return fns[fn_name](x)

async def async_de(fn_name, dim, max_gen=100, pop_size=40, seed=42):
    random.seed(seed)
    lo, hi = -5.12, 5.12
    F, CR = 0.8, 0.9
    pop = [[random.uniform(lo,hi) for _ in range(dim)] for _ in range(pop_size)]

    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor(max_workers=4) as ex:
        # Paralelní inicializace
        fits = list(await asyncio.gather(*[
            loop.run_in_executor(ex, _eval, (fn_name, p)) for p in pop
        ]))

        for _ in range(max_gen):
            trials = []
            for i in range(pop_size):
                a,b,c = random.sample([j for j in range(pop_size) if j!=i], 3)
                mutant = [max(lo,min(hi, pop[a][d]+F*(pop[b][d]-pop[c][d]))) for d in range(dim)]
                jrand = random.randint(0, dim-1)
                trials.append([mutant[d] if random.random()<CR or d==jrand else pop[i][d] for d in range(dim)])

            # Paralelní ohodnocení
            trial_fits = list(await asyncio.gather(*[
                loop.run_in_executor(ex, _eval, (fn_name, t)) for t in trials
            ]))

            for i in range(pop_size):
                if trial_fits[i] <= fits[i]:
                    pop[i] = trials[i]; fits[i] = trial_fits[i]

    bi = min(range(pop_size), key=lambda i: fits[i])
    return pop[bi], fits[bi]


def konvergence_ascii(hist, sirka=50, vyska=8, label=""):
    if not hist: return
    lo, hi = min(hist), max(hist)
    rng = hi - lo if hi != lo else 1
    print(f"\n  Konvergence {label}:")
    for r in range(vyska, -1, -1):
        prah = lo + rng * r / vyska
        radek = f"  {prah:8.3f} |"
        krok = max(1, len(hist)//sirka)
        for i in range(0, len(hist), krok):
            radek += "█" if hist[i] >= prah else " "
        print(radek)
    print("           " + "─"*(sirka+1))


async def main_async():
    print("=" * 50)
    print("  🌊 Evoluční algoritmy Demo")
    print("=" * 50)

    DIM = 5
    print(f"\nBenchmark: Rastrigin {DIM}D (minimum = 0.0 v nule)")

    # PSO
    t = time.perf_counter()
    _, gbf_pso, hist_pso = pso(rastrigin, DIM)
    t_pso = time.perf_counter()-t
    print(f"\n  PSO:  minimum={gbf_pso:.6f}  ({t_pso*1000:.0f}ms)")
    konvergence_ascii(hist_pso, label="PSO")

    # DE
    t = time.perf_counter()
    _, gbf_de, hist_de = de(rastrigin, DIM)
    t_de = time.perf_counter()-t
    print(f"\n  DE:   minimum={gbf_de:.6f}  ({t_de*1000:.0f}ms)")
    konvergence_ascii(hist_de, label="DE")

    # Async DE
    print(f"\n  Async DE (paralelní ProcessPool):")
    t = time.perf_counter()
    _, gbf_ade = await async_de("rastrigin", DIM, max_gen=80)
    t_ade = time.perf_counter()-t
    print(f"  Async DE: minimum={gbf_ade:.6f}  ({t_ade*1000:.0f}ms)")

    print(f"\n{'='*50}")
    print(f"  Srovnání na Sphere {DIM}D:")
    for label, fn in [("PSO", lambda: pso(sphere, DIM)),
                       ("DE",  lambda: de(sphere, DIM))]:
        _, f, _ = fn()
        print(f"  {label}: {f:.8f}")

    print("\n✅ Demo dokončeno!")


if __name__ == "__main__":
    asyncio.run(main_async())
