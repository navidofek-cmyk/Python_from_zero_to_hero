# Lekce 83: Vlákna (`threading`) a GIL

## 🧵 Co je vlákno?

**Vlákno** = paralelní cesta vykonávání ve stejném programu. Sdílejí paměť (žádné posílání zpráv).

```python
import threading
import time

def vital(jmeno):
    for i in range(3):
        print(f"{jmeno}: {i}")
        time.sleep(0.5)


t1 = threading.Thread(target=vital, args=("A",))
t2 = threading.Thread(target=vital, args=("B",))

t1.start()
t2.start()

t1.join()    # počkej
t2.join()
```

---

## 🔒 GIL (Global Interpreter Lock)

CPython má **GIL** — zámek, který říká: „**V daném okamžiku běží Python bytecode jen v JEDNOM vlákně.**“

To znamená:
- **CPU-bound** úlohy s threading **NEZRYCHLÍŠ** (jeden core).
- **I/O-bound** úlohy ANO (vlákno spí na I/O → GIL se uvolní).

### Příklad — kdy threading pomůže

```python
# I/O-bound — paralelní stahování
threads = [Thread(target=stahni, args=(url,)) for url in urls]
for t in threads: t.start()
for t in threads: t.join()
# 10 stahování paralelně → ~čas jednoho
```

### Kdy threading NEpomůže

```python
# CPU-bound — výpočty
threads = [Thread(target=spocti) for _ in range(4)]
# Bude to STEJNĚ pomalé jako jedno vlákno!
```

Pro CPU-bound → `multiprocessing` (lekce 84) nebo Python 3.13+ free-threaded build (lekce 87).

---

## 🔓 Synchronizace — `Lock`

Když víc vláken **zapisuje do stejné věci**, potřebuješ zámek:

```python
import threading

pocet = 0
lock = threading.Lock()

def pridej():
    global pocet
    with lock:
        pocet += 1


threads = [threading.Thread(target=pridej) for _ in range(1000)]
for t in threads: t.start()
for t in threads: t.join()

print(pocet)    # 1000
```

Bez locku by mohl být menší — race condition.

---

## 🚦 Další synchronizační primitiva

```python
threading.Lock()              # výhradní (jeden najednou)
threading.RLock()             # reentrant (stejné vlákno víckrát)
threading.Semaphore(N)        # max N najednou
threading.Event()             # flag (signál)
threading.Condition()         # wait/notify
threading.Barrier(N)          # počká na N vláken
queue.Queue()                 # bezpečná fronta mezi vlákny
```

---

## 🚧 Daemon vlákna

```python
t = threading.Thread(target=loop, daemon=True)
```

Daemon = ukončí se při ukončení programu. Pro background loops (logging, monitoring).

---

## 🎯 Kdy threading

✅ Síťové requesty (HTTP, DB čekání)
✅ Čtení/psaní souborů
✅ Subprocess čekání
✅ GUI aplikace (jedno vlákno = UI, jiné = work)

❌ CPU-intenzivní úlohy → `multiprocessing` nebo NumPy/Numba

---

## ✏️ Cvičení

1. **2 vlákna:** Spusť 2 vlákna co tisknou čísla 1–5 s sleep.
2. **Lock:** Implementuj počítadlo s `Lock`. Spusť bez locku — uvidíš race.
3. **Stahování:** Stáhni 5 URL pomocí 5 vláken. Změř čas.
4. **Queue:** Producent vyrobí 10 položek, 3 konzumenti je zpracují.
