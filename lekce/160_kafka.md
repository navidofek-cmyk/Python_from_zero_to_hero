# Lekce 160: Apache Kafka — event streaming

Kafka je distribuovaná event streaming platforma. Miliony zpráv za sekundu, perzistentní logy, consumer groups. Základ moderních data pipelines.

---

## 🚀 Instalace

```bash
uv add confluent-kafka aiokafka

# Kafka + Zookeeper (Docker)
docker run -d --name kafka \
  -p 9092:9092 \
  -e KAFKA_CFG_NODE_ID=0 \
  -e KAFKA_CFG_PROCESS_ROLES=controller,broker \
  -e KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
  -e KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  -e KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@localhost:9093 \
  -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER \
  bitnami/kafka:latest
```

---

## 📤 Producer

```python
from confluent_kafka import Producer
import json
import time


def delivery_report(err, msg):
    if err:
        print(f"❌ Doručení selhalo: {err}")
    else:
        print(f"✅ Zpráva doručena: topic={msg.topic()}, "
              f"partition={msg.partition()}, offset={msg.offset()}")


def vytvor_producenta(bootstrap_servers: str = "localhost:9092") -> Producer:
    return Producer({
        "bootstrap.servers": bootstrap_servers,
        "client.id": "python-producer",
        "acks": "all",                    # čekej na potvrzení od všech replik
        "retries": 3,
        "batch.size": 16384,              # 16 KB batch
        "linger.ms": 5,                   # čekej 5ms na batching
        "compression.type": "snappy",     # komprese
    })


producer = vytvor_producenta()

# Posílání zpráv
for i in range(10):
    zprava = {
        "id": i,
        "udalost": "nakup",
        "produkt": f"Produkt_{i}",
        "cena": round(100 + i * 15.5, 2),
        "cas": time.time(),
    }
    producer.produce(
        topic="nakupy",
        key=str(i).encode(),
        value=json.dumps(zprava).encode(),
        callback=delivery_report,
    )
    producer.poll(0)   # neblokující flush

producer.flush()   # počkej na doručení všech zpráv
print("Všechny zprávy odeslány")
```

---

## 📥 Consumer

```python
from confluent_kafka import Consumer, KafkaError


def vytvor_konzumenta(
    group_id: str,
    topics: list[str],
    bootstrap_servers: str = "localhost:9092",
) -> Consumer:
    consumer = Consumer({
        "bootstrap.servers": bootstrap_servers,
        "group.id": group_id,
        "auto.offset.reset": "earliest",    # od začátku nebo
        # "auto.offset.reset": "latest",    # jen nové zprávy
        "enable.auto.commit": True,
        "auto.commit.interval.ms": 5000,
    })
    consumer.subscribe(topics)
    return consumer


def konzumuj(group_id: str = "moje-app", max_zprav: int = 10):
    consumer = vytvor_konzumenta(group_id, ["nakupy"])

    try:
        zpracovano = 0
        while zpracovano < max_zprav:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"Konec partitionu {msg.partition()}")
                else:
                    print(f"Chyba: {msg.error()}")
                continue

            zprava = json.loads(msg.value().decode())
            print(f"  [P{msg.partition()}:O{msg.offset()}] {zprava}")
            zpracovano += 1

    finally:
        consumer.close()
```

---

## ⚡ Async Kafka (aiokafka)

```python
import asyncio
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer


async def async_producent(topic: str, zpravy: list[dict]):
    producer = AIOKafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode(),
        compression_type="gzip",
    )
    await producer.start()
    try:
        for zprava in zpravy:
            await producer.send_and_wait(topic, zprava)
            print(f"  Odesláno: {zprava}")
    finally:
        await producer.stop()


async def async_konzument(topic: str, group_id: str, max_zprav: int = 5):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers="localhost:9092",
        group_id=group_id,
        auto_offset_reset="earliest",
        value_deserializer=lambda v: json.loads(v.decode()),
    )
    await consumer.start()
    try:
        async for zprava in consumer:
            print(f"  Přijato: {zprava.value}")
            max_zprav -= 1
            if max_zprav <= 0:
                break
    finally:
        await consumer.stop()


async def demo_async_kafka():
    zpravy = [{"id": i, "data": f"event_{i}"} for i in range(5)]
    await async_producent("test-topic", zpravy)
    await async_konzument("test-topic", "async-group")
```

---

## 🔄 Consumer Groups — paralelní zpracování

```python
# Consumer group = N konzumentů sdílí partitions
# Partition může mít max 1 konzument ve skupině najednou
# → horizontální škálování

async def spust_konzumenty(n: int = 3):
    """Spustí N konzumentů ve stejné skupině."""
    tasky = [
        async_konzument("nakupy", "zpracovani-group", max_zprav=3)
        for _ in range(n)
    ]
    await asyncio.gather(*tasky)
```

---

## 📊 Schema Registry + Avro

```python
# Pro produkci — schéma validace zpráv
# uv add confluent-kafka[avro]

SCHEMA = """{
  "type": "record",
  "name": "Nakup",
  "fields": [
    {"name": "id", "type": "int"},
    {"name": "produkt", "type": "string"},
    {"name": "cena", "type": "float"}
  ]
}"""

# from confluent_kafka.schema_registry import SchemaRegistryClient
# from confluent_kafka.schema_registry.avro import AvroSerializer
# sr_client = SchemaRegistryClient({"url": "http://localhost:8081"})
print("Schema Registry + Avro připraven k použití")
```

---

## 🎯 Kafka architektura

```
Producer → [Topic: objednavky] → Consumer Group A (zpracování)
                               → Consumer Group B (analytics)
                               → Consumer Group C (notifikace)

Topic → Partitions (paralelismus)
Partition → Replicas (spolehlivost)
Offset → pozice konzumenta (lze replay)
```

---

## ✏️ Cvičení

1. Postav producer/consumer pipeline pro logování HTTP requestů do Kafky.
2. Implementuj **exactly-once** semantiku pomocí transakcí (`producer.init_transactions()`).
3. Napiš **stream processing** — konzumuj, transformuj a pošli zpět do jiného topicu.
4. Benchmark: porovnej throughput sync vs async producenta.
5. Implementuj **dead letter queue** — zprávy které selhaly při zpracování.
