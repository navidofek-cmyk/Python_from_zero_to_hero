# Lekce 173: Apache Airflow — orchestrace pipelines

Airflow plánuje a spouští komplexní workflows (DAGy). Každý úkol závisí na předchozích, Airflow hlídá pořadí, retry a monitorování.

---

## 🚀 Instalace

```bash
uv add "apache-airflow[celery,postgres,redis]"

# Docker (nejjednodušší start)
docker compose -f https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml up
# UI: http://localhost:8080 (admin/admin)
```

---

## 📋 Základní DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": ["admin@company.com"],
}

with DAG(
    dag_id="etl_pipeline",
    default_args=default_args,
    description="Denní ETL pipeline",
    schedule="0 6 * * *",       # každý den v 6:00
    start_date=datetime(2026, 1, 1),
    catchup=False,               # nespouštěj minulé runs
    tags=["etl", "produkce"],
) as dag:

    def extrahuj(**context):
        """Stáhni data ze zdroje."""
        ds = context["ds"]   # datum spuštění (YYYY-MM-DD)
        print(f"Extrahuji data pro {ds}")
        # Pushni výsledek do XCom
        context["ti"].xcom_push(key="pocet_radku", value=42000)
        return "data_2026-01-01.parquet"

    def transformuj(**context):
        """Transformuj a vyčisti data."""
        soubor = context["ti"].xcom_pull(task_ids="extrakce")
        pocet = context["ti"].xcom_pull(task_ids="extrakce", key="pocet_radku")
        print(f"Transformuji {soubor} ({pocet} řádků)")
        return "transformed.parquet"

    def nahraj(**context):
        """Nahraj do datového skladu."""
        soubor = context["ti"].xcom_pull(task_ids="transformace")
        print(f"Nahrávám {soubor} do DWH")

    extrakce = PythonOperator(
        task_id="extrakce",
        python_callable=extrahuj,
    )

    transformace = PythonOperator(
        task_id="transformace",
        python_callable=transformuj,
    )

    nahravani = PythonOperator(
        task_id="nahravani",
        python_callable=nahraj,
    )

    validace = BashOperator(
        task_id="validace",
        bash_command="echo 'Data validována: {{ ds }}'",
    )

    # Definice závislostí
    extrakce >> transformace >> nahravani >> validace
```

---

## 🔀 Větvení a podmínky

```python
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator


def rozhodnout(**context):
    """Rozhodne jestli jít cestou A nebo B."""
    hodina = datetime.now().hour
    if hodina < 12:
        return "ranní_zpracování"
    return "odpolední_zpracování"


rozvětvi = BranchPythonOperator(
    task_id="rozvětvi",
    python_callable=rozhodnout,
)

ranní = PythonOperator(
    task_id="ranní_zpracování",
    python_callable=lambda: print("Ranní batch"),
)

odpolední = PythonOperator(
    task_id="odpolední_zpracování",
    python_callable=lambda: print("Odpolední batch"),
)

spoj = EmptyOperator(
    task_id="spoj",
    trigger_rule="none_failed_min_one_success",
)

rozvětvi >> [ranní, odpolední] >> spoj
```

---

## 📡 Sensors — čekej na podmínku

```python
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.python import PythonSensor
from airflow.providers.http.sensors.http import HttpSensor


# Čekej na soubor
cekej_na_soubor = FileSensor(
    task_id="cekej_na_soubor",
    filepath="/data/input/dnesni_data.csv",
    poke_interval=60,   # kontroluj každých 60s
    timeout=3600,       # timeout 1h
    mode="reschedule",  # uvolni worker slot mezi kontrolami
)

# Čekej na HTTP endpoint
cekej_na_api = HttpSensor(
    task_id="cekej_na_api",
    http_conn_id="moje_api",
    endpoint="/api/status",
    response_check=lambda r: r.json()["ready"] == True,
    poke_interval=30,
)

# Vlastní podmínka
def je_data_pripravena():
    import os
    return os.path.exists("/data/ready.flag")

vlastní_sensor = PythonSensor(
    task_id="vlastní_sensor",
    python_callable=je_data_pripravena,
    poke_interval=120,
)
```

---

## ⚡ TaskFlow API (moderní styl)

```python
from airflow.decorators import dag, task
from pendulum import datetime as pdt


@dag(
    schedule="@daily",
    start_date=pdt(2026, 1, 1),
    catchup=False,
    tags=["taskflow"],
)
def moderní_dag():
    """DAG s TaskFlow API — čistší než Operators."""

    @task()
    def stáhni_data(ds: str = None) -> dict:
        return {"radky": 1000, "soubor": f"data_{ds}.parquet"}

    @task()
    def zpracuj(data: dict) -> list:
        print(f"Zpracovávám {data['radky']} řádků")
        return [1, 2, 3]   # výsledky

    @task()
    def uloz(vysledky: list) -> None:
        print(f"Ukládám {len(vysledky)} výsledků")

    @task.branch()
    def zkontroluj_kvalitu(data: dict) -> str:
        if data["radky"] > 500:
            return "uloz"
        return "pošli_alert"

    @task()
    def pošli_alert() -> None:
        print("Alert: málo dat!")

    # Automatické předávání dat mezi tasky
    data = stáhni_data()
    vetve = zkontroluj_kvalitu(data)
    vysledky = zpracuj(data)
    uloz(vysledky)


dag_instance = moderní_dag()
```

---

## 🔌 Connections a Variables

```python
# Connections — přihlašovací údaje (v Airflow UI nebo env)
# AIRFLOW_CONN_MY_DB=postgresql://user:pass@host/db

from airflow.hooks.base import BaseHook

conn = BaseHook.get_connection("my_postgres")
print(f"Host: {conn.host}, DB: {conn.schema}")

# Variables — konfigurace
from airflow.models import Variable

batch_size = Variable.get("batch_size", default_var="1000")
env = Variable.get("environment", default_var="prod")

# Secrets backend (produkce)
# Vault, AWS Secrets Manager, GCP Secret Manager
```

---

## 📊 Monitoring a SLA

```python
from airflow.models.dag import DAG

with DAG(
    dag_id="sla_dag",
    sla_miss_callback=lambda dag, task_list, blocking, slas, blocking_tis:
        print(f"SLA porušena: {task_list}"),
) as dag:
    task = PythonOperator(
        task_id="pomalý_task",
        python_callable=lambda: None,
        sla=timedelta(hours=2),   # musí dokončit do 2h
    )
```

---

## 🎯 Airflow vs alternativy

| | Airflow | Prefect | Dagster | Celery Beat |
|---|---------|---------|---------|-------------|
| Komplexnost | vysoká | střední | vysoká | nízká |
| UI | ✅ bohaté | ✅ moderní | ✅ moderní | ❌ Flower |
| Dynamické DAGy | omezené | ✅ | ✅ | ✅ |
| Testování | obtížné | snadné | ✅ assets | snadné |
| Produkce | ✅ standard | ✅ | roste | ✅ |

---

## ✏️ Cvičení

1. Postav ETL pipeline: stáhni CSV z URL → transformuj Polars → ulož do PostgreSQL.
2. Implementuj **dynamic DAG** — generuj tasky z databáze konfigurací.
3. Přidej **email notifikaci** při selhání tasku.
4. Napiš **custom sensor** — čeká na nový řádek v PostgreSQL tabulce.
5. Benchmark: Airflow vs Prefect na stejném pipeline — developer experience.
