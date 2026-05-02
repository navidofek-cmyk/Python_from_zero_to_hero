# Lekce 164: GraphQL — Strawberry

GraphQL = klient si vybere přesně jaká data chce. Žádný over-fetching ani under-fetching.

---

## 🚀 Instalace

```bash
uv add strawberry-graphql "strawberry-graphql[fastapi]"
```

---

## 📋 Schema a typy

```python
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
from typing import Optional
import datetime


@strawberry.type
class Uzivatel:
    id: int
    jmeno: str
    email: str
    vek: int
    aktivni: bool = True


@strawberry.type
class Produkt:
    id: int
    nazev: str
    cena: float
    kategorie: str
    skladem: int


@strawberry.input
class UzivatelInput:
    jmeno: str
    email: str
    vek: int


@strawberry.input
class ProduktFilter:
    kategorie: Optional[str] = None
    min_cena: Optional[float] = None
    max_cena: Optional[float] = None
    jen_skladem: bool = False
```

---

## 🔍 Query — čtení dat

```python
# Simulace DB
UZIVATELE = [
    Uzivatel(id=1, jmeno="Anna", email="anna@example.com", vek=30),
    Uzivatel(id=2, jmeno="Bob", email="bob@example.com", vek=25),
    Uzivatel(id=3, jmeno="Carol", email="carol@example.com", vek=35),
]
PRODUKTY = [
    Produkt(id=1, nazev="Laptop", cena=25000, kategorie="Elektronika", skladem=5),
    Produkt(id=2, nazev="Myš", cena=500, kategorie="Elektronika", skladem=0),
    Produkt(id=3, nazev="Stůl", cena=8000, kategorie="Nábytek", skladem=10),
]


@strawberry.type
class Query:
    @strawberry.field
    def uzivatel(self, id: int) -> Optional[Uzivatel]:
        return next((u for u in UZIVATELE if u.id == id), None)

    @strawberry.field
    def uzivatele(self, aktivni: bool = True) -> list[Uzivatel]:
        return [u for u in UZIVATELE if u.aktivni == aktivni]

    @strawberry.field
    def produkty(self, filtr: Optional[ProduktFilter] = None) -> list[Produkt]:
        vysledky = PRODUKTY.copy()
        if filtr:
            if filtr.kategorie:
                vysledky = [p for p in vysledky if p.kategorie == filtr.kategorie]
            if filtr.min_cena:
                vysledky = [p for p in vysledky if p.cena >= filtr.min_cena]
            if filtr.max_cena:
                vysledky = [p for p in vysledky if p.cena <= filtr.max_cena]
            if filtr.jen_skladem:
                vysledky = [p for p in vysledky if p.skladem > 0]
        return vysledky
```

---

## ✏️ Mutation — zápis dat

```python
@strawberry.type
class Mutation:
    @strawberry.mutation
    def vytvor_uzivatele(self, vstup: UzivatelInput) -> Uzivatel:
        novy = Uzivatel(
            id=max(u.id for u in UZIVATELE) + 1,
            jmeno=vstup.jmeno,
            email=vstup.email,
            vek=vstup.vek,
        )
        UZIVATELE.append(novy)
        return novy

    @strawberry.mutation
    def smaz_uzivatele(self, id: int) -> bool:
        global UZIVATELE
        puvodni = len(UZIVATELE)
        UZIVATELE = [u for u in UZIVATELE if u.id != id]
        return len(UZIVATELE) < puvodni

    @strawberry.mutation
    def uprav_produkt(self, id: int, cena: Optional[float] = None,
                       skladem: Optional[int] = None) -> Optional[Produkt]:
        for p in PRODUKTY:
            if p.id == id:
                if cena is not None: p.cena = cena
                if skladem is not None: p.skladem = skladem
                return p
        return None
```

---

## 📡 Subscription — real-time

```python
import asyncio
from typing import AsyncGenerator


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def nova_objednavka(self) -> AsyncGenerator[Produkt, None]:
        """Real-time stream nových objednávek."""
        for i in range(5):
            await asyncio.sleep(1)
            yield PRODUKTY[i % len(PRODUKTY)]

    @strawberry.subscription
    async def cena_produktu(self, produkt_id: int) -> AsyncGenerator[float, None]:
        """Stream změn ceny produktu."""
        import random
        while True:
            await asyncio.sleep(2)
            yield round(random.uniform(100, 50000), 2)
```

---

## 🔐 Autentizace + context

```python
from strawberry.types import Info
from strawberry.fastapi import BaseContext


class MujContext(BaseContext):
    def __init__(self, request):
        self.request = request
        self.user_id: Optional[int] = None


async def get_context() -> MujContext:
    return MujContext(request=None)  # FastAPI request přijde automaticky


@strawberry.type
class AuthQuery:
    @strawberry.field
    def muj_profil(self, info: Info[MujContext, None]) -> Optional[Uzivatel]:
        if not info.context.user_id:
            raise Exception("Nepřihlášen")
        return next((u for u in UZIVATELE if u.id == info.context.user_id), None)
```

---

## 🏗️ FastAPI integrace

```python
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
)

app = FastAPI()
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def index():
    return {"zprava": "GraphQL API na /graphql"}

# Spuštění: fastapi dev app.py
# GraphQL Playground: http://localhost:8000/graphql
```

GraphQL dotaz:
```graphql
query {
  uzivatele {
    id
    jmeno
    email
  }
  produkty(filtr: {kategorie: "Elektronika", jenSkladem: true}) {
    nazev
    cena
    skladem
  }
}

mutation {
  vytvorUzivatele(vstup: {
    jmeno: "Dan"
    email: "dan@example.com"
    vek: 28
  }) {
    id
    jmeno
  }
}
```

---

## 🎯 GraphQL vs REST

| | GraphQL | REST |
|---|---------|------|
| Over-fetching | ❌ nikdy | ✅ časté |
| Under-fetching | ❌ nikdy | ✅ N+1 problém |
| Schéma | ✅ silně typované | OpenAPI (volitelné) |
| Verzování | ❌ nepotřebuje | /v1, /v2 |
| Caching | složitější (query hash) | přirozené (URL) |
| Subscription | ✅ | SSE/WebSocket |
| Learning curve | strmější | mírná |
| Ideální | komplexní data, mobilní app | jednoduché CRUD API |

---

## ✏️ Cvičení

1. Postav GraphQL API pro blog — Post, Comment, User s vnořenými dotazy.
2. Implementuj **DataLoader** (n+1 problem) — batch loading relací.
3. Přidej **pagination** — cursor-based nebo offset-based.
4. Napíš **directive** `@deprecated` a vlastní `@rateLimit`.
5. Benchmark: 1000 GraphQL dotazů vs ekvivalentní REST — porovnej latency.
