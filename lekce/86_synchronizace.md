# Lekce 86: Synchronizační primitiva

## 🔒 `Lock` — výhradní přístup

```python
import threading

lock = threading.Lock()

with lock:
    # jen JEDNO vlákno tady najednou
    kriticka_sekce()
```

`with lock:` je hezčí než `lock.acquire()` / `lock.release()` — uvolní se i při výjimce.

---

## 🔁 `RLock` — reentrant lock

`Lock` se zamkne sám pro sebe (deadlock):

```python
lock = threading.Lock()

def vnejsi():
    with lock:
        vnitrni()

def vnitrni():
    with lock:    # ❌ DEADLOCK!
        ...
```

`RLock` umí zamknout opakovaně **stejné vlákno** (drží počítadlo):

```python
lock = threading.RLock()

def vnejsi():
    with lock:
        vnitrni()       # ✅ projde

def vnitrni():
    with lock:
        ...
```

---

## 🚦 `Semaphore` — N najednou

```python
sem = threading.Semaphore(5)        # max 5 vláken

def stahni():
    with sem:
        # max 5 stahování paralelně
        ...
```

Užitečné na **rate limiting**.

---

## 📢 `Event` — jednoduché signály

```python
event = threading.Event()

def consumer():
    event.wait()        # čeká dokud .set()
    print("Spuštěno!")

def producer():
    time.sleep(2)
    event.set()         # uvolní wait
```

---

## ⏰ `Condition` — wait/notify

```python
cv = threading.Condition()
data = []

def producer():
    with cv:
        data.append(42)
        cv.notify()    # probud jednoho čekajícího

def consumer():
    with cv:
        while not data:
            cv.wait()
        print(data.pop())
```

Pro složitější koordinaci.

---

## 🚧 `Barrier` — počkej na N vláken

```python
barrier = threading.Barrier(3)

def vlakno():
    print("Připraven")
    barrier.wait()        # čekej až jsou 3
    print("Jdeme!")
```

---

## 📬 `queue.Queue` — fronta bezpečná pro vlákna

```python
import queue

q = queue.Queue(maxsize=100)

# Producent
q.put(item)

# Konzument
item = q.get()
q.task_done()
```

```python
queue.Queue()          # FIFO
queue.LifoQueue()      # LIFO
queue.PriorityQueue()
```

---

## ⚠️ Klasické problémy

### Race condition

Dvě vlákna čtou + zapisují stejnou věc bez locku → nedeterministický výsledek.

### Deadlock

Dvě vlákna čekají vzájemně:
- A drží X, čeká na Y
- B drží Y, čeká na X

**Pravidlo:** **Vždy zamykej locks ve stejném pořadí.**

### Livelock

Vlákna se snaží uhnout sobě a nikdo nepokračuje.

---

## ✏️ Cvičení

1. **Lock:** Implementuj počítadlo s lockem. Bez locku — uvidíš race.
2. **Semafor:** Spusť 100 úloh, ale jen 5 najednou.
3. **Event:** Vlákno čeká na signál „start“.
4. **Queue:** 1 producent + 3 konzumenti přes `queue.Queue`.
