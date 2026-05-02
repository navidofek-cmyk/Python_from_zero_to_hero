# Program — Lekce 171: Lekce 171: Microservices — architektura a vzory

Patří k lekci [Lekce 171: Microservices — architektura a vzory](../171_microservices.md).

## Jak spustit

```bash
python3 programy/l171_microservices.py
```

## Zdrojový kód

### `l171_microservices.py`

```py
"""Lekce 171 — Microservices: architektura a vzory.

Spuštění:
    uv run --with "fastapi[standard]" --with httpx l171_microservices.py
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ── Circuit Breaker ───────────────────────────────────────────────────────────

class CBStav(Enum):
    ZAVRENY = "closed"
    OTEVRENY = "open"
    POLOTEVRENY = "half"


class CircuitBreaker:
    def __init__(self, prah=3, timeout=5.0):
        self.prah = prah
        self.timeout = timeout
        self.stav = CBStav.ZAVRENY
        self.selhani = 0
        self.posledni_selhani = 0.0

    async def volej(self, func, *args, **kwargs):
        if self.stav == CBStav.OTEVRENY:
            if time.time() - self.posledni_selhani > self.timeout:
                self.stav = CBStav.POLOTEVRENY
            else:
                raise RuntimeError(f"Circuit breaker OTEVŘEN")
        try:
            result = await func(*args, **kwargs)
            if self.stav == CBStav.POLOTEVRENY:
                self.stav = CBStav.ZAVRENY
                self.selhani = 0
                print(f"    CB obnoveno → ZAVRENY")
            return result
        except Exception as e:
            self.selhani += 1
            self.posledni_selhani = time.time()
            if self.selhani >= self.prah:
                self.stav = CBStav.OTEVRENY
                print(f"    CB → OTEVŘEN po {self.selhani} selháních")
            raise


# ── Service Registry ──────────────────────────────────────────────────────────

class ServiceRegistry:
    def __init__(self):
        self._services: dict[str, list[str]] = {}
        self._idx: dict[str, int] = {}

    def registruj(self, nazev: str, url: str):
        self._services.setdefault(nazev, [])
        self._idx.setdefault(nazev, 0)
        self._services[nazev].append(url)

    def ziskej(self, nazev: str) -> str:
        instance = self._services.get(nazev, [])
        if not instance: raise RuntimeError(f"Žádná instance pro {nazev}")
        idx = self._idx[nazev] % len(instance)
        self._idx[nazev] = idx + 1
        return instance[idx]


# ── Simulace microservices ────────────────────────────────────────────────────

registry = ServiceRegistry()
registry.registruj("user-service", "http://user-1:8001")
registry.registruj("user-service", "http://user-2:8001")
registry.registruj("order-service", "http://order-1:8002")

USERS_DB = {1: {"id": 1, "jmeno": "Anna"}, 2: {"id": 2, "jmeno": "Bob"}}
ORDERS_DB = {}
_order_id = 0

call_count = {"success": 0, "fail": 0}


async def user_service_get(user_id: int) -> dict:
    await asyncio.sleep(0.01)  # síťová latency
    if user_id not in USERS_DB:
        raise ValueError(f"User {user_id} not found")
    call_count["success"] += 1
    return USERS_DB[user_id]


async def nestabilni_platba(castka: float) -> dict:
    """Simulace nestabilní platební brány."""
    import random
    await asyncio.sleep(0.05)
    if random.random() < 0.4:  # 40% selhání
        call_count["fail"] += 1
        raise ConnectionError("Platební brána nedostupná")
    call_count["success"] += 1
    return {"status": "ok", "castka": castka}


async def order_service_create(user_id: int, produkty: list, cena: float) -> dict:
    global _order_id
    # Ověř uživatele (service-to-service)
    uzivatel = await user_service_get(user_id)
    _order_id += 1
    objednavka = {"id": _order_id, "user": uzivatel["jmeno"], "produkty": produkty, "cena": cena}
    ORDERS_DB[_order_id] = objednavka
    return objednavka


async def demo_microservices():
    print("\n=== Service Registry + Load Balancing ===")
    for _ in range(6):
        url = registry.ziskej("user-service")
        print(f"  → {url}")

    print("\n=== Service-to-Service komunikace ===")
    for uid in [1, 2, 99]:
        try:
            u = await user_service_get(uid)
            print(f"  User {uid}: {u}")
        except ValueError as e:
            print(f"  User {uid}: ❌ {e}")

    print("\n=== Circuit Breaker ===")
    cb = CircuitBreaker(prah=3, timeout=2.0)
    import random; random.seed(7)

    for i in range(8):
        try:
            result = await cb.volej(nestabilni_platba, 100.0 + i*10)
            print(f"  Volání {i+1}: ✅ {result['status']} (stav CB: {cb.stav.value})")
        except RuntimeError as e:
            print(f"  Volání {i+1}: 🔴 {e}")
        except Exception as e:
            print(f"  Volání {i+1}: ❌ {e} (stav CB: {cb.stav.value})")
        await asyncio.sleep(0.1)

    print("\n=== Objednávkový workflow ===")
    objednavka = await order_service_create(1, ["Laptop", "Myš"], 25500)
    print(f"  Objednávka vytvořena: {objednavka}")


def demo_docker_compose():
    print("\n=== Docker Compose (pro produkci) ===")
    print("""
version: "3.9"
services:
  gateway:
    image: nginx:alpine    # nebo FastAPI gateway
    ports: ["8000:8000"]

  user-service:
    build: ./user_service
    deploy:
      replicas: 2          # 2 instance = load balancing
    environment:
      DATABASE_URL: postgresql://...

  order-service:
    build: ./order_service
    environment:
      USER_SERVICE_URL: http://user-service:8001
      KAFKA_URL: kafka:9092

  kafka:
    image: bitnami/kafka:latest
    ports: ["9092:9092"]

Spuštění:
  docker-compose up --scale user-service=3
""")


async def main():
    print("=" * 55)
    print("  🏗️  Microservices Demo")
    print("=" * 55)

    await demo_microservices()
    demo_docker_compose()

    print(f"\n=== Statistiky ===")
    print(f"  Úspěšných volání: {call_count['success']}")
    print(f"  Selhání:          {call_count['fail']}")

    print("\n✅ Demo dokončeno!")
    print("Pro plné microservices: uv add 'fastapi[standard]' httpx")


if __name__ == "__main__":
    asyncio.run(main())

```
