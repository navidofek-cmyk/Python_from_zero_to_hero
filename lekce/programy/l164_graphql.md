# Program — Lekce 164: Lekce 164: GraphQL — Strawberry

Patří k lekci [Lekce 164: GraphQL — Strawberry](../164_graphql.md).

## Jak spustit

```bash
python3 programy/l164_graphql.py
```

## Zdrojový kód

### `l164_graphql.py`

```py
"""Lekce 164 — GraphQL: Strawberry.

Spuštění:
    uv run --with "strawberry-graphql[fastapi]" --with "fastapi[standard]" l164_graphql.py
"""

import json


def demo_graphql_koncepty():
    print("=" * 50)
    print("  🍓 GraphQL — Strawberry Demo")
    print("=" * 50)

    print("""
GraphQL vs REST:

REST (over-fetching):
  GET /users/1
  → {"id":1,"jmeno":"Anna","email":"...","telefon":"...","adresa":{...}}
  (Potřebuješ jen jmeno a email, ale dostaneš vše)

GraphQL (přesně co chceš):
  query { uzivatel(id:1) { jmeno email } }
  → {"data":{"uzivatel":{"jmeno":"Anna","email":"..."}}}

Typy operací:
  query     → čtení (GET)
  mutation  → zápis (POST/PUT/DELETE)
  subscription → real-time (WebSocket)
""")


try:
    import strawberry
    from strawberry import Schema
    from typing import Optional

    @strawberry.type
    class Uzivatel:
        id: int
        jmeno: str
        email: str

    @strawberry.type
    class Produkt:
        id: int
        nazev: str
        cena: float

    UZIVATELE = [
        Uzivatel(id=1, jmeno="Anna", email="anna@example.com"),
        Uzivatel(id=2, jmeno="Bob", email="bob@example.com"),
    ]
    PRODUKTY = [
        Produkt(id=1, nazev="Laptop", cena=25000),
        Produkt(id=2, nazev="Myš", cena=500),
    ]

    @strawberry.type
    class Query:
        @strawberry.field
        def uzivatel(self, id: int) -> Optional[Uzivatel]:
            return next((u for u in UZIVATELE if u.id == id), None)

        @strawberry.field
        def uzivatele(self) -> list[Uzivatel]:
            return UZIVATELE

        @strawberry.field
        def produkty(self, max_cena: Optional[float] = None) -> list[Produkt]:
            if max_cena:
                return [p for p in PRODUKTY if p.cena <= max_cena]
            return PRODUKTY

    @strawberry.input
    class UzivatelInput:
        jmeno: str
        email: str

    @strawberry.type
    class Mutation:
        @strawberry.mutation
        def vytvor_uzivatele(self, vstup: UzivatelInput) -> Uzivatel:
            novy = Uzivatel(id=len(UZIVATELE)+1, jmeno=vstup.jmeno, email=vstup.email)
            UZIVATELE.append(novy)
            return novy

    schema = Schema(query=Query, mutation=Mutation)

    print("=== Strawberry GraphQL ===")

    # Spusť dotazy
    queries = [
        ('query { uzivatele { id jmeno } }', "Všichni uživatelé"),
        ('query { uzivatel(id: 1) { jmeno email } }', "Uživatel 1"),
        ('query { produkty(maxCena: 1000) { nazev cena } }', "Levné produkty"),
        ('mutation { vytvorUzivatele(vstup: {jmeno: "Carol", email: "carol@test.com"}) { id jmeno } }',
         "Vytvoř uživatele"),
    ]

    for query, popis in queries:
        result = schema.execute_sync(query)
        if result.errors:
            print(f"  ❌ {popis}: {result.errors[0]}")
        else:
            print(f"  ✅ {popis}:")
            print(f"     {json.dumps(result.data, ensure_ascii=False)}")

    print(f"\n  Schema SDL (zkráceně):")
    print(f"  {schema.as_str()[:300]}...")

except ImportError:
    print("\nStrawberry není dostupný — viz ukázkový kód v lekci")
    print("Instalace: uv add 'strawberry-graphql[fastapi]'")

    print("""
Ukázka kódu:
    import strawberry
    from strawberry.fastapi import GraphQLRouter
    from fastapi import FastAPI

    @strawberry.type
    class Query:
        @strawberry.field
        def hello(self) -> str:
            return "Ahoj z GraphQL!"

    schema = strawberry.Schema(query=Query)
    app = FastAPI()
    app.include_router(GraphQLRouter(schema), prefix="/graphql")
    # Playground: http://localhost:8000/graphql
""")


def main():
    demo_graphql_koncepty()
    print("\n✅ Demo dokončeno!")
    print("Pro FastAPI: uv add 'strawberry-graphql[fastapi]' 'fastapi[standard]'")


if __name__ == "__main__":
    main()

```
