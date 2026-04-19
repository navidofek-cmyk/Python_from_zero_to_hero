# Lekce 93: Profilování — `cProfile`, `timeit`, `tracemalloc`

## ⏱️ `timeit` — měření malých kousků

```python
import timeit

# Jeden výraz
timeit.timeit("sum(range(100))", number=10_000)
# čas v sekundách

# Setup + statement
t = timeit.timeit(
    stmt="sum(x*x for x in data)",
    setup="data = list(range(1000))",
    number=1000,
)
print(f"{t:.3f}s")
```

Z příkazové řádky:
```bash
python -m timeit -n 10000 "sum(range(100))"
```

V notebooku/IPython:
```python
%timeit sum(range(100))
%%timeit                # pro celý cell
```

---

## 🔬 `cProfile` — profilování celého programu

```python
import cProfile

cProfile.run("hlavni_funkce()", sort="cumulative")
```

Nebo z CLI:
```bash
python -m cProfile -o profile.out muj_program.py
python -m pstats profile.out
```

Hledej **horké funkce** (cumtime, ncalls).

---

## 🔥 Flame graphy — `py-spy`, `austin`

```bash
pip install py-spy
py-spy record -o profile.svg -- python muj_program.py
```

Vyrobí **flame graph** (SVG) — vidíš, kde program tráví čas. Krásné a srozumitelné.

`py-spy` je **sampling profiler** — neslowuje program. Můžeš ho pustit i na **běžící proces**:

```bash
py-spy top --pid 12345
```

`austin` je alternativa.

---

## 💾 `tracemalloc` — sledování paměti

```python
import tracemalloc

tracemalloc.start()
# ... tvůj kód ...
snapshot = tracemalloc.take_snapshot()
top = snapshot.statistics("lineno")[:10]
for stat in top:
    print(stat)
```

Vidíš **kde alokuješ nejvíc paměti**.

---

## 🐉 `memray` — moderní memory profiler (Bloomberg)

```bash
pip install memray
memray run muj_program.py
memray flamegraph memray-XXX.bin
```

Vyrobí flame graph **paměti**. Krása.

---

## 🎯 Strategie optimalizace

1. **MĚŘ první** — neoptimuj na slepo.
2. **Najdi bottleneck** přes profiler.
3. **Optimalizuj jen ten** — zbytek nech být.
4. **Změř znovu** — opravdu to pomohlo?

> „Premature optimization is the root of all evil.“ — Knuth

---

## 📊 Co je rychlé / pomalé v Pythonu

✅ Rychlé:
- Lokální proměnné
- C-level funkce (`sum`, `len`)
- NumPy/Pandas vektorizace
- Built-in datové struktury

❌ Pomalé:
- Globální proměnné (nepatrně)
- Volání atributů v hot loopu (`obj.metoda` v cyklu — `m = obj.metoda; m()`)
- Vyrábění zbytečných objektů
- Kruhové reference (GC)

---

## ✏️ Cvičení

1. **Timeit:** Změř `[x*x for x in range(1000)]` vs `list(map(lambda x: x*x, range(1000)))`.
2. **cProfile:** Zprofiluj nějaký svůj program.
3. **py-spy:** Nainstaluj a vyrob flame graph.
4. **tracemalloc:** Najdi kde tvůj program alokuje nejvíc paměti.
