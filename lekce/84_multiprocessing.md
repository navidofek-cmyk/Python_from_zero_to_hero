# Lekce 84: `multiprocessing` — paralelismus pro CPU

## ⚙️ Proč ne threading pro CPU?

Kvůli GIL (lekce 83). `multiprocessing` **spustí víc Python procesů** — každý má svůj GIL = pravdivý paralelismus.

```python
import multiprocessing as mp

def tezky_vypocet(n):
    return sum(i * i for i in range(n))


if __name__ == "__main__":
    with mp.Pool(processes=4) as pool:
        vysledky = pool.map(tezky_vypocet, [1_000_000] * 8)
    print(vysledky)
```

Na 4-jádrovém CPU → ~4× rychlejší.

---

## ⚠️ `if __name__ == "__main__":`

Na Windows/macOS multiprocessing **vyžaduje** tuhle ochranu — jinak nekonečná rekurze procesů.

---

## 🛠️ Pool metody

```python
pool.map(f, iterable)              # synchronní
pool.imap(f, iterable)             # iterator
pool.imap_unordered(f, iterable)   # bez pořadí (rychlejší)
pool.apply(f, args)                # jeden úkol
pool.apply_async(f, args)          # async (vrací Future)
pool.starmap(f, iter_of_tuples)    # f(*args)
```

---

## 📨 Komunikace mezi procesy

Procesy **NESDÍLEJÍ paměť** (na rozdíl od vláken). Musíš si posílat data:

```python
from multiprocessing import Process, Queue

def worker(q):
    q.put(42)

if __name__ == "__main__":
    q = Queue()
    p = Process(target=worker, args=(q,))
    p.start()
    p.join()
    print(q.get())     # 42
```

### Pipe (peer-to-peer)

```python
parent, child = mp.Pipe()
parent.send("ahoj")
print(child.recv())
```

---

## 🌐 Sdílená paměť

```python
from multiprocessing import shared_memory
import numpy as np

shm = shared_memory.SharedMemory(create=True, size=1024)
# Sdílení velkých dat bez kopírování
```

Pro velká pole **`shared_memory`** ušetří hodně. Jinak `Manager`:

```python
mng = mp.Manager()
sdileny_dict = mng.dict()
```

---

## 🆚 `concurrent.futures`

Jednodušší API — viz lekce 85.

---

## ⚠️ Pasti

1. **Picklovatelnost** — vše posílané musí jít serializovat (žádné lambdy, otevřené sockety).
2. **Spuštění je drahé** — pro každý task dělat nový proces je hloupé. Použij **pool**.
3. **`if __name__ == "__main__":`** povinné.
4. Sdílení dat = pomalé. Kvůli pickle.

---

## ✏️ Cvičení

1. **Pool:** Vyrob pool 4 procesů, počítej `n*n` pro `n` v `range(1_000_000, 1_000_010)`.
2. **Měření:** Porovnej `Pool.map` s obyčejným `map` na CPU těžké úloze.
3. **Queue:** Producent → fronta → konzument (vše v procesech).
4. **Manager dict:** Sdílený dict, 4 procesy přidávají klíče.
