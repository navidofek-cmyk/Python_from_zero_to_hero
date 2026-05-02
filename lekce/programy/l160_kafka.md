# Program — Lekce 160: Lekce 160: Apache Kafka — event streaming

Patří k lekci [Lekce 160: Apache Kafka — event streaming](../160_kafka.md).

## Jak spustit

```bash
python3 programy/l160_kafka.py
```

## Zdrojový kód

### `l160_kafka.py`

```py
"""Lekce 160 — Apache Kafka: event streaming.

Spuštění (s Kafka):
    docker run -d --name kafka -p 9092:9092 \
      -e KAFKA_CFG_PROCESS_ROLES=controller,broker \
      -e KAFKA_CFG_NODE_ID=0 \
      -e KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
      -e KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
      -e KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@localhost:9093 \
      -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER \
      bitnami/kafka:latest

    uv run --with confluent-kafka l160_kafka.py
"""

import json
import time
import asyncio


def demo_bez_kafky():
    """Demo architektury Kafka bez skutečného serveru."""
    print("=" * 50)
    print("  📨 Kafka Architektura Demo")
    print("=" * 50)

    print("""
Kafka architektura:
  Producer → [Topic: nakupy] → Consumer Group A
                              → Consumer Group B

Topic = kategorie zpráv
Partition = paralelismus (N partitions = N konzumentů)
Offset = pozice v logu (lze replay od libovolného bodu)
Consumer Group = skupina konzumentů sdílí partitions
""")

    # Simulace producer/consumer bez skutečné Kafky
    fronta: list[dict] = []

    def producer(zpravy: list[dict]):
        print("Producer posílá zprávy:")
        for i, zprava in enumerate(zpravy):
            zprava["offset"] = i
            zprava["cas"] = time.time()
            fronta.append(zprava)
            print(f"  → [{i}] {zprava['typ']}: {zprava.get('data', '')}")

    def consumer(group_id: str, max_zprav: int = None):
        print(f"\nConsumer '{group_id}' zpracovává:")
        pocet = 0
        while fronta and (max_zprav is None or pocet < max_zprav):
            zprava = fronta.pop(0)
            print(f"  ← [{zprava['offset']}] {zprava['typ']}")
            pocet += 1

    zpravy = [
        {"typ": "nakup", "data": "Produkt A", "cena": 150},
        {"typ": "nakup", "data": "Produkt B", "cena": 250},
        {"typ": "vraceni", "data": "Produkt A"},
        {"typ": "nakup", "data": "Produkt C", "cena": 99},
        {"typ": "platba", "data": "karta", "castka": 400},
    ]

    producer(zpravy)
    consumer("zpracovani-objednavek")

    print("\n=== Kafka konfigurace (pro produkci) ===")
    config = {
        "bootstrap.servers": "kafka-1:9092,kafka-2:9092,kafka-3:9092",
        "acks": "all",
        "retries": 3,
        "batch.size": 16384,
        "linger.ms": 5,
        "compression.type": "snappy",
        "enable.idempotence": True,
    }
    for k, v in config.items():
        print(f"  {k}: {v}")


async def demo_async_simulace():
    print("\n=== Async Producer/Consumer simulace ===")

    fronta: asyncio.Queue = asyncio.Queue(maxsize=100)

    async def async_producer(n: int):
        for i in range(n):
            zprava = {"id": i, "data": f"event_{i}"}
            await fronta.put(zprava)
            print(f"  [Producer] → {zprava}")
            await asyncio.sleep(0.05)

    async def async_consumer(worker_id: int, max_zprav: int):
        zpracovano = 0
        while zpracovano < max_zprav:
            zprava = await fronta.get()
            print(f"  [Worker {worker_id}] ← {zprava}")
            fronta.task_done()
            zpracovano += 1

    # Producer + 2 konzumenti paralelně
    await asyncio.gather(
        async_producer(6),
        async_consumer(1, 3),
        async_consumer(2, 3),
    )


def main():
    demo_bez_kafky()
    asyncio.run(demo_async_simulace())
    print("\n✅ Demo dokončeno!")
    print("Pro skutečnou Kafku: uv add confluent-kafka aiokafka")


if __name__ == "__main__":
    main()

```
