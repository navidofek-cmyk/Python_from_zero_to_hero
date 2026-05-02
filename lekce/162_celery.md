# Lekce 162: Celery — distribuované task queues

Celery zpracovává úlohy asynchronně mimo HTTP request-response cyklus. Posílej email, generuj report, processuj video — bez blokování serveru.

---

## 🚀 Instalace

```bash
uv add celery redis "celery[redis]"

# Redis jako broker (Docker)
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

---

## ⚙️ Konfigurace

`celery_app.py`:

```python
from celery import Celery
from celery.utils.log import get_task_logger
import time

logger = get_task_logger(__name__)

app = Celery(
    "moje_app",
    broker="redis://localhost:6379/0",    # kam posílat tasky
    backend="redis://localhost:6379/1",   # kam ukládat výsledky
    include=["tasky"],                    # moduly s tasky
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Prague",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,             # ACK až po dokončení (retry při selhání)
    worker_prefetch_multiplier=1,    # jeden task najednou (fair queue)
    task_routes={
        "tasky.posli_email": {"queue": "emaily"},
        "tasky.generuj_report": {"queue": "heavy"},
    },
)
```

---

## 📋 Definice tasků

`tasky.py`:

```python
from celery_app import app
from celery import Task
import time
import random


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def posli_email(self, adresa: str, predmet: str, obsah: str) -> dict:
    """Odešle email — retry při selhání."""
    logger.info(f"Posílám email na {adresa}")
    try:
        # Simulace posílání
        if random.random() < 0.1:   # 10% selhání
            raise ConnectionError("SMTP server nedostupný")
        time.sleep(0.5)
        return {"status": "odesláno", "adresa": adresa}
    except ConnectionError as exc:
        logger.warning(f"Retry {self.request.retries}/{self.max_retries}")
        raise self.retry(exc=exc, countdown=2**self.request.retries)


@app.task
def secti_cislice(a: int, b: int) -> int:
    """Jednoduchý task."""
    return a + b


@app.task(time_limit=300, soft_time_limit=240)
def generuj_report(uzivatel_id: int) -> str:
    """Náročný task s časovým limitem."""
    logger.info(f"Generuji report pro uzivatele {uzivatel_id}")
    time.sleep(2)   # simulace náročného výpočtu
    return f"report_{uzivatel_id}.pdf"


@app.task(bind=True)
def sledovany_task(self, kroky: int) -> str:
    """Task s průběžným stavem."""
    for i in range(kroky):
        time.sleep(0.1)
        self.update_state(
            state="PROGRESS",
            meta={"aktualni": i+1, "celkem": kroky, "procento": (i+1)/kroky*100}
        )
    return f"Hotovo {kroky} kroků"
```

---

## 🚀 Spuštění workeru

```bash
# Základní worker
celery -A celery_app worker --loglevel=info

# Více workerů s různými frontami
celery -A celery_app worker -Q emaily --concurrency=10 --loglevel=info &
celery -A celery_app worker -Q heavy --concurrency=2 --loglevel=info &

# Monitoring (Flower)
uv add flower
celery -A celery_app flower --port=5555
```

---

## 📬 Volání tasků

```python
# Asynchronní volání — vrátí AsyncResult
result = posli_email.delay("anna@example.com", "Test", "Ahoj!")
result = posli_email.apply_async(
    args=["anna@example.com", "Test", "Ahoj!"],
    countdown=60,         # spusť za 60 sekund
    eta=datetime(2026, 1, 1, 12, 0),  # nebo v určitý čas
    expires=3600,         # vypršení po 1 hodině
    queue="emaily",       # specifická fronta
    priority=9,           # 0-9, vyšší = důležitější
)

# Čekání na výsledek
try:
    vysledek = result.get(timeout=30)
    print(f"Výsledek: {vysledek}")
except Exception as e:
    print(f"Task selhal: {e}")

# Stav tasku
print(result.state)    # PENDING, STARTED, SUCCESS, FAILURE, RETRY
print(result.info)     # metadata (pro sledovany_task: {"aktualni": 5, ...})
```

---

## 🔗 Chains, Groups, Chords

```python
from celery import chain, group, chord


# Chain — sekvenční pipeline
pipeline = chain(
    secti_cislice.s(1, 2),        # → 3
    secti_cislice.s(10),           # → 13 (3 + 10)
    secti_cislice.s(100),          # → 113
)
result = pipeline.delay()
print(result.get())   # 113


# Group — paralelní tasky
paralelne = group(
    posli_email.s("a@test.com", "Test", "Ahoj"),
    posli_email.s("b@test.com", "Test", "Ahoj"),
    posli_email.s("c@test.com", "Test", "Ahoj"),
)
results = paralelne.delay()
print(results.get())   # [výsledek1, výsledek2, výsledek3]


# Chord — group + callback po dokončení všech
from celery import chord

def agreguj(vysledky: list) -> str:
    return f"Odesláno {len(vysledky)} emailů"

workflow = chord(
    group(
        posli_email.s(f"user{i}@test.com", "Novinka", "Text")
        for i in range(10)
    ),
    agreguj.s()   # zavolá se s [výsledek1, ..., výsledek10]
)
result = workflow.delay()
```

---

## ⏰ Celery Beat — periodické úlohy

`beat_schedule.py`:

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    "denni-report": {
        "task": "tasky.generuj_report",
        "schedule": crontab(hour=8, minute=0),   # každý den v 8:00
        "args": (1,),
    },
    "cada-minutu": {
        "task": "tasky.secti_cislice",
        "schedule": 60.0,   # každých 60 sekund
        "args": (1, 1),
    },
    "kazdy-pondeli": {
        "task": "tasky.posli_email",
        "schedule": crontab(day_of_week="monday"),
        "kwargs": {"adresa": "boss@company.com", "predmet": "Týdenní report"},
    },
}
```

Spuštění:
```bash
celery -A celery_app beat --loglevel=info
```

---

## 🎯 Celery architektura

```
FastAPI → Redis Broker → Celery Worker (1..N)
                       → Celery Beat (scheduler)
                       ↓
                 Redis Backend → FastAPI (polling výsledků)
```

---

## ✏️ Cvičení

1. Postav Celery pipeline pro zpracování obrázků: upload → resize → thumbnail → notifikace.
2. Implementuj **circuit breaker** pro tasky — po N selháních zastav volání externího API.
3. Nastav **priority queues** — kritické tasky před normálními.
4. Monitoruj Celery přes Flower — vizualizuj throughput a chybovost.
5. Napiš **idempotentní task** — opakované spuštění stejného tasku neduplikuje data.
