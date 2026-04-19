# Lekce 122: Async architektura ve velkém

Základy `asyncio` nestačí pro produkční systémy. Potřebujeme backpressure, bounded concurrency, správné rušení úkolů a strukturovanou souběžnost.

---

## Backpressure s `asyncio.Queue`

Backpressure = mechanismus, který zabraňuje producenti přetížit konzumenta. Bez něj narůstá fronta donekonečna.

```python
import asyncio

async def producent(fronta: asyncio.Queue[int], n: int) -> None:
    for i in range(n):
        await fronta.put(i)   # Blokuje, pokud fronta plná
        print(f"Produkováno: {i}")
    await fronta.put(None)    # Sentinel — konec

async def konzument(fronta: asyncio.Queue[int]) -> None:
    while True:
        polozka = await fronta.get()
        if polozka is None:
            break
        await asyncio.sleep(0.1)   # Simulace zpracování
        print(f"  Zpracováno: {polozka}")
        fronta.task_done()

async def main() -> None:
    # maxsize=3 — fronta unese max 3 položky
    fronta: asyncio.Queue[int] = asyncio.Queue(maxsize=3)
    await asyncio.gather(
        producent(fronta, 10),
        konzument(fronta),
    )
```

### Proč `maxsize`?

| `maxsize` | Chování |
|---|---|
| `0` (výchozí) | Neomezená fronta — risk OOM |
| `> 0` | Producent čeká, až konzument uvolní místo |

---

## Bounded Concurrency s `asyncio.Semaphore`

Semafor omezuje počet souběžně běžících korutin. Klíčové pro omezení zátěže na downstream služby.

```python
import asyncio

async def volej_api(id_: int, semafor: asyncio.Semaphore) -> str:
    async with semafor:            # Max N souběžně
        print(f"Volám API {id_}")
        await asyncio.sleep(0.2)   # Simulace HTTP požadavku
        return f"Výsledek {id_}"

async def main() -> None:
    semafor = asyncio.Semaphore(3)   # Max 3 souběžná volání
    ukoly = [volej_api(i, semafor) for i in range(10)]
    vysledky = await asyncio.gather(*ukoly)
    print(vysledky)
```

Bez semaforu by všech 10 požadavků šlo najednou. Se semaforem maximálně 3 současně.

---

## `asyncio.TaskGroup` (Python 3.11+)

`TaskGroup` je moderní náhrada za `gather` — přináší strukturovanou souběžnost:
- Pokud jeden úkol selže, ostatní jsou automaticky zrušeny
- Výjimky jsou správně propagovány

```python
import asyncio

async def ukol(id_: int) -> int:
    await asyncio.sleep(0.1 * id_)
    if id_ == 3:
        raise ValueError(f"Úkol {id_} selhal!")
    return id_ * 10

async def main() -> None:
    try:
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(ukol(1))
            t2 = tg.create_task(ukol(2))
            t3 = tg.create_task(ukol(3))   # Selže
            t4 = tg.create_task(ukol(4))
        # Sem se nedostaneme — t3 selhal
    except* ValueError as eg:
        print(f"Chyby: {eg.exceptions}")
        # t4 byl zrušen automaticky
```

`except*` je nová syntaxe Pythonu 3.11 pro `ExceptionGroup`.

---

## Správné rušení úkolů (Cancellation)

Zrušení korutiny vyvolá `asyncio.CancelledError`. Je kriticky důležité:
1. Nechat `CancelledError` propagovat (nepohltit ho)
2. Úklid provést v `finally`

```python
import asyncio

async def dlouha_operace() -> None:
    try:
        print("Začínám dlouhou operaci")
        await asyncio.sleep(10)
        print("Hotovo")
    except asyncio.CancelledError:
        print("Byl jsem zrušen — úklid")
        # Úklid zdrojů (close connections, flush buffers)
        raise   # VŽDY znovu vyhodit!

async def main() -> None:
    ukol = asyncio.create_task(dlouha_operace())
    await asyncio.sleep(0.5)
    ukol.cancel()
    try:
        await ukol
    except asyncio.CancelledError:
        print("Úkol zrušen")
```

### Špatný vzor — pohltit CancelledError

```python
async def spatne() -> None:
    try:
        await asyncio.sleep(10)
    except Exception:         # CHYBA: pohltí i CancelledError!
        pass
```

---

## Timeout s `asyncio.timeout` (Python 3.11+)

```python
import asyncio

async def pomala_operace() -> str:
    await asyncio.sleep(5)
    return "hotovo"

async def main() -> None:
    try:
        async with asyncio.timeout(1.0):
            vysledek = await pomala_operace()
    except TimeoutError:
        print("Operace překročila timeout")
```

Starší varianta (Python 3.9+):

```python
try:
    vysledek = await asyncio.wait_for(pomala_operace(), timeout=1.0)
except asyncio.TimeoutError:
    print("Timeout")
```

---

## Vzor: Worker Pool s omezenou souběžností

```python
import asyncio
from collections.abc import Callable, Awaitable

async def worker(
    id_: int,
    fronta: asyncio.Queue[int | None],
    callback: Callable[[int, int], Awaitable[None]],
) -> None:
    while True:
        polozka = await fronta.get()
        if polozka is None:
            fronta.put_nowait(None)  # Předej sentinel dalšímu workeru
            break
        await callback(id_, polozka)
        fronta.task_done()

async def zpracuj(worker_id: int, polozka: int) -> None:
    await asyncio.sleep(0.05)
    print(f"Worker {worker_id}: zpracováno {polozka}")

async def main() -> None:
    fronta: asyncio.Queue[int | None] = asyncio.Queue(maxsize=10)
    pocet_workeru = 3

    workeri = [asyncio.create_task(worker(i, fronta, zpracuj))
               for i in range(pocet_workeru)]

    for i in range(20):
        await fronta.put(i)
    await fronta.put(None)

    await asyncio.gather(*workeri)
```

---

## Shrnutí

| Nástroj | Použití |
|---|---|
| `Queue(maxsize=N)` | Backpressure — producent/konzument |
| `Semaphore(N)` | Omezení souběžnosti na N |
| `TaskGroup` | Strukturovaná souběžnost (Python 3.11+) |
| `timeout()` | Časový limit pro operace (Python 3.11+) |
| `CancelledError` re-raise | Správné šíření zrušení |

---

## Cvičení

1. Napiš producent/konzument s `Queue(maxsize=5)` — producent je 3× rychlejší než konzument.
2. Implementuj `rate_limiter` jako `Semaphore`: max 10 požadavků za sekundu.
3. Pomocí `TaskGroup` spusť 5 úkolů — jeden záměrně selže po 0.3s, ověř, že ostatní jsou zrušeny.
4. Napiš funkci `retry_with_timeout`, která opakuje async operaci max 3× s timeoutem 1s.
