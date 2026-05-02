# Lekce 147: Genetické algoritmy

Genetické algoritmy (GA) jsou **metaheuristiky inspirované přírodní evolucí** — selekce, křížení, mutace. Vynikají pro optimalizační problémy s velkým prohledávacím prostorem kde neexistuje exaktní řešení.

---

## 🧬 Základní pojmy

```
Populace     = sada kandidátních řešení (jedinců)
Jedinec      = jedno kandidátní řešení (chromozom)
Gen          = jedna hodnota v řešení
Fitness      = kvalita jedince (jak dobré je řešení)
Selekce      = výběr lepších jedinců pro reprodukci
Křížení      = kombinace genů dvou rodičů
Mutace       = náhodná změna genů (diverzita)
Generace     = jedna iterace celého procesu
```

---

## 🔧 Obecný GA framework

```python
import random
import asyncio
from typing import TypeVar, Callable
from dataclasses import dataclass, field
from concurrent.futures import ProcessPoolExecutor

T = TypeVar("T")

@dataclass
class GAConfig:
    velikost_populace: int = 100
    pocet_generaci: int = 200
    pravd_krizeni: float = 0.8
    pravd_mutace: float = 0.02
    velikost_turnaje: int = 5
    elitismus: int = 2          # počet nejlepších jedinců přenesených přímo


@dataclass
class Jedinec:
    chromozom: list
    fitness: float = 0.0

    def __lt__(self, other):
        return self.fitness < other.fitness


class GenetickyAlgoritmus:
    def __init__(
        self,
        config: GAConfig,
        vytvor_jedince: Callable[[], list],
        vypocti_fitness: Callable[[list], float],
        krizeni: Callable[[list, list], tuple[list, list]] = None,
        mutace: Callable[[list, float], list] = None,
    ):
        self.cfg = config
        self._vytvor = vytvor_jedince
        self._fitness = vypocti_fitness
        self._krizeni = krizeni or self._jednobodove_krizeni
        self._mutace = mutace or self._nahodna_mutace

    def _jednobodove_krizeni(self, rodic1: list, rodic2: list) -> tuple[list, list]:
        if len(rodic1) < 2:
            return rodic1[:], rodic2[:]
        bod = random.randint(1, len(rodic1) - 1)
        return (rodic1[:bod] + rodic2[bod:], rodic2[:bod] + rodic1[bod:])

    def _nahodna_mutace(self, chromozom: list, pravd: float) -> list:
        return [
            random.random() if random.random() < pravd else gen
            for gen in chromozom
        ]

    def _turnajova_selekce(self, populace: list[Jedinec]) -> Jedinec:
        turnaj = random.sample(populace, self.cfg.velikost_turnaje)
        return max(turnaj, key=lambda j: j.fitness)

    def _ohodnot(self, jedinec: Jedinec) -> None:
        jedinec.fitness = self._fitness(jedinec.chromozom)

    def evoluj(self, verbose: bool = True) -> tuple[Jedinec, list[float]]:
        # Inicializace
        populace = [Jedinec(self._vytvor()) for _ in range(self.cfg.velikost_populace)]
        for j in populace:
            self._ohodnot(j)

        historie = []
        nejlepsi = max(populace, key=lambda j: j.fitness)

        for generace in range(self.cfg.pocet_generaci):
            # Seřaď — nejlepší první
            populace.sort(key=lambda j: j.fitness, reverse=True)
            aktualni_nejlepsi = populace[0]

            if aktualni_nejlepsi.fitness > nejlepsi.fitness:
                nejlepsi = Jedinec(aktualni_nejlepsi.chromozom[:], aktualni_nejlepsi.fitness)

            historie.append(aktualni_nejlepsi.fitness)

            if verbose and generace % 20 == 0:
                print(f"  Gen {generace:4d}: fitness={aktualni_nejlepsi.fitness:.4f}")

            # Nová generace
            nova_populace = []

            # Elitismus — přenes nejlepší jedince
            nova_populace.extend(populace[:self.cfg.elitismus])

            # Reprodukce
            while len(nova_populace) < self.cfg.velikost_populace:
                rodic1 = self._turnajova_selekce(populace)
                rodic2 = self._turnajova_selekce(populace)

                if random.random() < self.cfg.pravd_krizeni:
                    dite1_chr, dite2_chr = self._krizeni(rodic1.chromozom, rodic2.chromozom)
                else:
                    dite1_chr, dite2_chr = rodic1.chromozom[:], rodic2.chromozom[:]

                dite1_chr = self._mutace(dite1_chr, self.cfg.pravd_mutace)
                dite2_chr = self._mutace(dite2_chr, self.cfg.pravd_mutace)

                dite1 = Jedinec(dite1_chr)
                dite2 = Jedinec(dite2_chr)
                self._ohodnot(dite1)
                self._ohodnot(dite2)
                nova_populace.extend([dite1, dite2])

            populace = nova_populace[:self.cfg.velikost_populace]

        return nejlepsi, historie
```

---

## 🎒 Příklad 1: Knapsack problém

```python
def reseni_knapsack():
    print("\n=== GA: Knapsack problém ===")

    # Věci: (váha, hodnota)
    veci = [(2,3),(3,4),(4,5),(5,8),(1,2),(6,9),(3,6),(2,4),(7,10),(4,7)]
    kapacita = 15
    n = len(veci)

    def vytvor_jedince() -> list:
        return [random.randint(0, 1) for _ in range(n)]

    def fitness(chromozom: list) -> float:
        celkova_vaha = sum(veci[i][0] * chromozom[i] for i in range(n))
        celkova_hodnota = sum(veci[i][1] * chromozom[i] for i in range(n))
        if celkova_vaha > kapacita:
            return 0.0   # penalizace za překročení kapacity
        return float(celkova_hodnota)

    def krizeni(r1: list, r2: list) -> tuple[list, list]:
        bod = random.randint(1, n-1)
        return r1[:bod]+r2[bod:], r2[:bod]+r1[bod:]

    def mutace(chr: list, pravd: float) -> list:
        return [1-g if random.random() < pravd else g for g in chr]

    cfg = GAConfig(velikost_populace=50, pocet_generaci=100, pravd_mutace=0.05)
    ga = GenetickyAlgoritmus(cfg, vytvor_jedince, fitness, krizeni, mutace)
    nejlepsi, _ = ga.evoluj(verbose=False)

    vybrane = [i for i, g in enumerate(nejlepsi.chromozom) if g == 1]
    print(f"  Nejlepší hodnota: {nejlepsi.fitness}")
    print(f"  Celková váha: {sum(veci[i][0] for i in vybrane)}/{kapacita}")
    print(f"  Vybrané věci: {vybrane}")
```

---

## 🗺️ Příklad 2: Traveling Salesman Problem (TSP)

```python
import math

def reseni_tsp():
    print("\n=== GA: Traveling Salesman Problem ===")

    # Náhodná města
    random.seed(42)
    mesta = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(15)]
    n = len(mesta)

    def vzdalenost(a: tuple, b: tuple) -> float:
        return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

    def celkova_vzdalenost(permutace: list) -> float:
        total = sum(
            vzdalenost(mesta[permutace[i]], mesta[permutace[(i+1) % n]])
            for i in range(n)
        )
        return total

    def fitness(chromozom: list) -> float:
        return 1.0 / celkova_vzdalenost(chromozom)  # minimalizujeme vzdálenost

    def vytvor_jedince() -> list:
        perm = list(range(n))
        random.shuffle(perm)
        return perm

    # Order crossover (OX) — zachová pořadí
    def ox_krizeni(r1: list, r2: list) -> tuple[list, list]:
        a, b = sorted(random.sample(range(n), 2))
        def ox(p1, p2):
            dite = [-1] * n
            dite[a:b+1] = p1[a:b+1]
            fill = [x for x in p2 if x not in dite]
            idx = 0
            for i in range(n):
                if dite[i] == -1:
                    dite[i] = fill[idx]
                    idx += 1
            return dite
        return ox(r1, r2), ox(r2, r1)

    # Swap mutace
    def swap_mutace(chr: list, pravd: float) -> list:
        chr = chr[:]
        for i in range(n):
            if random.random() < pravd:
                j = random.randint(0, n-1)
                chr[i], chr[j] = chr[j], chr[i]
        return chr

    cfg = GAConfig(
        velikost_populace=100, pocet_generaci=300,
        pravd_krizeni=0.9, pravd_mutace=0.02
    )
    ga = GenetickyAlgoritmus(cfg, vytvor_jedince, fitness, ox_krizeni, swap_mutace)
    nejlepsi, _ = ga.evoluj(verbose=False)

    print(f"  Nejkratší nalezená trasa: {1/nejlepsi.fitness:.2f} jednotek")
    print(f"  Pořadí měst: {nejlepsi.chromozom}")
```

---

## ⚡ Paralelní vyhodnocování fitness

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

def fitness_worker(chromozom: list) -> float:
    """CPU-intensive fitness funkce v separátním procesu."""
    import time, math
    # Simulace náročného výpočtu
    return sum(math.sin(x * math.pi) for x in chromozom)


async def async_ohodnot_populaci(populace: list[Jedinec]) -> None:
    """Async paralelní ohodnocení celé populace."""
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as executor:
        futures = [
            loop.run_in_executor(executor, fitness_worker, j.chromozom)
            for j in populace
        ]
        vysledky = await asyncio.gather(*futures)
    for j, fitness in zip(populace, vysledky):
        j.fitness = fitness


async def demo_parallel_ga():
    print("\n=== Paralelní GA (async + ProcessPool) ===")
    random.seed(42)

    populace = [Jedinec([random.random() for _ in range(20)]) for _ in range(50)]

    import time
    # Sekvenční
    start = time.perf_counter()
    for j in populace:
        j.fitness = fitness_worker(j.chromozom)
    cas_seq = time.perf_counter() - start

    # Paralelní
    start = time.perf_counter()
    await async_ohodnot_populaci(populace)
    cas_par = time.perf_counter() - start

    print(f"  Sekvenční: {cas_seq*1000:.1f}ms")
    print(f"  Paralelní: {cas_par*1000:.1f}ms")


# asyncio.run(demo_parallel_ga())
```

---

## 📈 Vizualizace konvergence

```python
def vizualizuj_konvergenci(historie: list[float], nazev: str = "") -> None:
    """ASCII graf konvergence."""
    if not historie:
        return
    max_f = max(historie)
    min_f = min(historie)
    sirka = 60
    vyska = 15

    print(f"\n  Konvergence{' — ' + nazev if nazev else ''}:")
    for radek in range(vyska, -1, -1):
        prah = min_f + (max_f - min_f) * radek / vyska
        radek_str = f"  {prah:8.3f} |"
        for i, f in enumerate(historie):
            if i % max(1, len(historie) // sirka) == 0:
                radek_str += "█" if f >= prah else " "
        print(radek_str)
    print("           " + "-" * (sirka + 1))
    print(f"           Gen 0{' ' * (sirka - 10)}Gen {len(historie)}")
```

---

## 🎯 Kdy použít GA

| Vhodné | Nevhodné |
|--------|---------|
| Velký diskrétní prohledávací prostor | Konvexní problémy (gradient descent) |
| Kombinatorická optimalizace | Problémy s exaktním řešením |
| Neznámá funkce fitness | Malý prohledávací prostor |
| Multi-kriteriální optimalizace | Real-time systémy |
| TSP, rozvrhování, plánování | Lineární programování |

---

## ✏️ Cvičení

1. Implementuj **ruletovou selekci** — pravděpodobnost výběru úměrná fitness.
2. Přidej **adaptivní mutaci** — snižuj pravděpodobnost mutace jak konverguje fitness.
3. Vyřeš **N-Queens** (N dam na šachovnici bez útoku) pomocí GA.
4. Implementuj **NSGA-II** — multi-objektivní GA pro optimalizaci dvou cílů najednou.
5. Paralelizuj GA plně — každá generace se vyhodnocuje v ProcessPoolExecutor.
