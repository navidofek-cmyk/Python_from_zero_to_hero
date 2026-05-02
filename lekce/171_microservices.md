# Lekce 171: Microservices — architektura a vzory

Microservices = aplikace rozdělená na malé, nezávislé služby. Každá má vlastní databázi, API a deployment.

---

## 🏗️ Monolith vs Microservices

```
Monolith:
  [Uživatel] → [Jedna velká aplikace] → [Jedna DB]
  + jednoduchý vývoj, testování
  - škálování celku, technologický lock-in

Microservices:
  [Uživatel] → [API Gateway]
                    ├── [User Service]    → [Users DB]
                    ├── [Order Service]   → [Orders DB]
                    ├── [Payment Service] → [Payments DB]
                    └── [Email Service]   → [Queue]
  + nezávislé nasazení, škálování, technologie
  - distribuovaná složitost, síťová latency
```

---

## 🚀 User Service

```python
# user_service/main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
import httpx
import os

app = FastAPI(title="User Service", version="1.0.0")

# Simulace DB
USERS_DB: dict[int, dict] = {
    1: {"id": 1, "jmeno": "Anna", "email": "anna@example.com", "aktivni": True},
    2: {"id": 2, "jmeno": "Bob", "email": "bob@example.com", "aktivni": True},
}


class UserCreate(BaseModel):
    jmeno: str
    email: str


class UserResponse(BaseModel):
    id: int
    jmeno: str
    email: str
    aktivni: bool


@app.get("/health")
def health():
    return {"status": "ok", "service": "user-service"}


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    if user_id not in USERS_DB:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")
    return USERS_DB[user_id]


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    new_id = max(USERS_DB.keys()) + 1
    new_user = {"id": new_id, **user.dict(), "aktivni": True}
    USERS_DB[new_id] = new_user
    return new_user


@app.get("/users")
def list_users():
    return list(USERS_DB.values())
```

---

## 📦 Order Service

```python
# order_service/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="Order Service", version="1.0.0")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001")
ORDERS_DB: dict[int, dict] = {}


class OrderCreate(BaseModel):
    user_id: int
    produkty: list[str]
    celkova_cena: float


@app.get("/health")
def health():
    return {"status": "ok", "service": "order-service"}


@app.post("/orders", status_code=201)
async def create_order(order: OrderCreate):
    # Ověř, že uživatel existuje (service-to-service call)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{USER_SERVICE_URL}/users/{order.user_id}",
                timeout=5.0,
            )
            if response.status_code == 404:
                raise HTTPException(status_code=400, detail="Uživatel neexistuje")
            response.raise_for_status()
        except httpx.TimeoutException:
            raise HTTPException(status_code=503, detail="User Service nedostupný")

    new_id = len(ORDERS_DB) + 1
    new_order = {"id": new_id, "status": "pending", **order.dict()}
    ORDERS_DB[new_id] = new_order
    return new_order


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    if order_id not in ORDERS_DB:
        raise HTTPException(status_code=404, detail="Objednávka nenalezena")
    return ORDERS_DB[order_id]
```

---

## 🔀 API Gateway

```python
# gateway/main.py
from fastapi import FastAPI, Request, HTTPException
import httpx
import os

app = FastAPI(title="API Gateway")

SERVICES = {
    "users":  os.getenv("USER_SERVICE_URL",  "http://localhost:8001"),
    "orders": os.getenv("ORDER_SERVICE_URL", "http://localhost:8002"),
}


@app.api_route("/{service}/{path:path}", methods=["GET","POST","PUT","DELETE"])
async def proxy(service: str, path: str, request: Request):
    """Proxy všechny requesty na správné microservices."""
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service}' nenalezena")

    url = f"{SERVICES[service]}/{path}"
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=url,
                content=body,
                headers=headers,
                params=request.query_params,
                timeout=30.0,
            )
            return response.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail=f"Service {service} nedostupná")
```

---

## 🐳 Docker Compose

```yaml
# docker-compose.yml
version: "3.9"
services:
  user-service:
    build: ./user_service
    ports: ["8001:8001"]
    environment:
      - DATABASE_URL=postgresql://postgres:heslo@users-db/users
    depends_on: [users-db]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      retries: 3

  order-service:
    build: ./order_service
    ports: ["8002:8002"]
    environment:
      - USER_SERVICE_URL=http://user-service:8001
    depends_on: [user-service]

  gateway:
    build: ./gateway
    ports: ["8000:8000"]
    environment:
      - USER_SERVICE_URL=http://user-service:8001
      - ORDER_SERVICE_URL=http://order-service:8002

  users-db:
    image: postgres:16
    environment:
      POSTGRES_DB: users
      POSTGRES_PASSWORD: heslo
```

---

## 🔄 Service Discovery + Load Balancing

```python
import random
from dataclasses import dataclass, field


@dataclass
class ServiceInstance:
    url: str
    healthy: bool = True
    weight: int = 1


class ServiceRegistry:
    """Jednoduchý service registry s round-robin load balancing."""

    def __init__(self):
        self._services: dict[str, list[ServiceInstance]] = {}
        self._idx: dict[str, int] = {}

    def registruj(self, nazev: str, url: str):
        if nazev not in self._services:
            self._services[nazev] = []
            self._idx[nazev] = 0
        self._services[nazev].append(ServiceInstance(url=url))
        print(f"  Registrováno: {nazev} @ {url}")

    def ziskej(self, nazev: str) -> str:
        """Round-robin výběr zdravé instance."""
        instance = [i for i in self._services.get(nazev, []) if i.healthy]
        if not instance:
            raise RuntimeError(f"Žádná dostupná instance pro {nazev}")
        idx = self._idx[nazev] % len(instance)
        self._idx[nazev] = idx + 1
        return instance[idx].url

    def oznac_nezdrave(self, nazev: str, url: str):
        for inst in self._services.get(nazev, []):
            if inst.url == url:
                inst.healthy = False


registry = ServiceRegistry()
registry.registruj("user-service", "http://user-1:8001")
registry.registruj("user-service", "http://user-2:8001")
registry.registruj("user-service", "http://user-3:8001")

print("\nLoad balancing:")
for _ in range(6):
    url = registry.ziskej("user-service")
    print(f"  → {url}")
```

---

## 🔒 Circuit Breaker

```python
from enum import Enum
import time


class CBStav(Enum):
    ZAVRENY = "closed"      # normální provoz
    OTEVRENY = "open"       # blokuje requesty
    POLOTEVRENY = "half"    # zkouší obnovit


class CircuitBreaker:
    def __init__(self, prah_selhani: int = 5, timeout: float = 60.0):
        self.prah = prah_selhani
        self.timeout = timeout
        self.stav = CBStav.ZAVRENY
        self.pocet_selhani = 0
        self.posledni_selhani = 0.0

    def __call__(self, func):
        import functools

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if self.stav == CBStav.OTEVRENY:
                if time.time() - self.posledni_selhani > self.timeout:
                    self.stav = CBStav.POLOTEVRENY
                else:
                    raise RuntimeError("Circuit breaker OTEVŘEN — service nedostupná")

            try:
                result = await func(*args, **kwargs)
                if self.stav == CBStav.POLOTEVRENY:
                    self.stav = CBStav.ZAVRENY
                    self.pocet_selhani = 0
                return result
            except Exception as e:
                self.pocet_selhani += 1
                self.posledni_selhani = time.time()
                if self.pocet_selhani >= self.prah:
                    self.stav = CBStav.OTEVRENY
                    print(f"  🔴 Circuit breaker OTEVŘEN po {self.pocet_selhani} selháních")
                raise

        return wrapper
```

---

## ✏️ Cvičení

1. Postav 3 microservices (User, Product, Order) s Docker Compose — ověř service-to-service komunikaci.
2. Implementuj **Saga pattern** — distribuovaná transakce přes Kafka (kompenzační transakce).
3. Přidej **distributed tracing** pomocí OpenTelemetry — sleduj request přes všechny services.
4. Implementuj **API versioning** v gateway — `/v1/users` → user-service-v1, `/v2/users` → v2.
5. Nastav **Istio service mesh** — automatický mTLS, circuit breaking, traffic management.
