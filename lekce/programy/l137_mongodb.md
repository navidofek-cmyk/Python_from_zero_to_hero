# Program — Lekce 137: Lekce 137: MongoDB — dokumentová databáze

Patří k lekci [Lekce 137: MongoDB — dokumentová databáze](../137_mongodb.md).

## Jak spustit

```bash
python3 programy/l137_mongodb.py
```

## Zdrojový kód

### `l137_mongodb.py`

```py
"""Lekce 137 — MongoDB: dokumentová databáze.

Spuštění:
    docker run -d --name mongodb -p 27017:27017 mongo:7
    uv run --with pymongo l137_mongodb.py
"""

from datetime import datetime

try:
    from pymongo import MongoClient, ASCENDING, DESCENDING
    from pymongo.errors import DuplicateKeyError
except ImportError:
    print("Nainstaluj: uv add pymongo")
    raise


def pripoj() -> MongoClient:
    client = MongoClient("mongodb://localhost:27017/")
    client.admin.command("ping")
    return client


def demo_crud(db):
    print("\n=== CRUD operace ===")
    kol = db["uzivatele"]
    kol.drop()

    # Insert
    kol.insert_many([
        {"jmeno": "Anna", "vek": 30, "email": "anna@example.com",
         "tagy": ["python", "fastapi"], "adresa": {"mesto": "Praha"}},
        {"jmeno": "Bob", "vek": 25, "email": "bob@example.com",
         "tagy": ["docker", "kubernetes"], "adresa": {"mesto": "Brno"}},
        {"jmeno": "Carol", "vek": 35, "email": "carol@example.com",
         "tagy": ["python", "data"], "adresa": {"mesto": "Praha"}},
        {"jmeno": "Dan", "vek": 28, "email": "dan@example.com",
         "tagy": ["java", "spring"], "adresa": {"mesto": "Ostrava"}},
    ])
    print(f"Vloženo: {kol.count_documents({})} dokumentů")

    # Find
    print("\nUživ. starší 27:")
    for u in kol.find({"vek": {"$gt": 27}}, {"jmeno": 1, "vek": 1, "_id": 0}):
        print(f"  {u}")

    # Vnořený dotaz
    print("\nPražané:")
    for u in kol.find({"adresa.mesto": "Praha"}, {"jmeno": 1, "_id": 0}):
        print(f"  {u['jmeno']}")

    # Pole obsahuje hodnotu
    print("\nPython programátoři:")
    for u in kol.find({"tagy": "python"}, {"jmeno": 1, "_id": 0}):
        print(f"  {u['jmeno']}")

    # Update
    kol.update_one({"jmeno": "Anna"}, {"$set": {"vek": 31}, "$push": {"tagy": "ml"}})
    anna = kol.find_one({"jmeno": "Anna"})
    print(f"\nAnna po update: vek={anna['vek']}, tagy={anna['tagy']}")

    # Delete
    kol.delete_one({"jmeno": "Dan"})
    print(f"Po smazání Dana: {kol.count_documents({})} dokumentů")


def demo_agregace(db):
    print("\n=== Agregační pipeline ===")
    kol = db["uzivatele"]

    pipeline = [
        {"$match": {"vek": {"$gte": 25}}},
        {"$addFields": {
            "kategorie": {
                "$cond": {
                    "if": {"$lt": ["$vek", 30]},
                    "then": "junior",
                    "else": "senior"
                }
            }
        }},
        {"$group": {
            "_id": "$kategorie",
            "pocet": {"$sum": 1},
            "prumer_vek": {"$avg": "$vek"},
            "jmena": {"$push": "$jmeno"}
        }},
        {"$sort": {"pocet": -1}}
    ]

    for vysledek in kol.aggregate(pipeline):
        print(f"  {vysledek['_id']}: {vysledek['pocet']} lidí, "
              f"prům. vek {vysledek['prumer_vek']:.1f}, "
              f"jména: {vysledek['jmena']}")


def demo_indexy(db):
    print("\n=== Indexy ===")
    kol = db["produkty"]
    kol.drop()

    kol.insert_many([
        {"nazev": f"Produkt {i}", "cena": i * 100, "kategorie": "A" if i % 2 == 0 else "B"}
        for i in range(100)
    ])

    # Index na email (unique)
    kol_uz = db["uzivatele"]
    kol_uz.create_index("email", unique=True)

    try:
        kol_uz.insert_one({"jmeno": "Duplicitní", "email": "anna@example.com"})
    except DuplicateKeyError:
        print("  ✅ Unique index funguje — duplikát odmítnut")

    # Složený index
    kol.create_index([("kategorie", ASCENDING), ("cena", DESCENDING)])

    # Dotaz využívající index
    import time
    start = time.perf_counter()
    list(kol.find({"kategorie": "A"}).sort("cena", -1).limit(10))
    print(f"  Dotaz s indexem: {(time.perf_counter()-start)*1000:.2f}ms")

    print(f"  Indexy: {[idx['name'] for idx in kol.list_indexes()]}")


def demo_async():
    print("\n=== Async Motor (ukázka kódu) ===")
    kod = '''
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["asyncdb"]
    kol = db["data"]

    await kol.insert_one({"klic": "hodnota", "cas": datetime.utcnow()})

    async for dok in kol.find({}):
        print(dok)

    client.close()

asyncio.run(main())
'''
    print(kod)


def main():
    print("=" * 50)
    print("  🍃 MongoDB Demo")
    print("=" * 50)

    try:
        client = pripoj()
        print("✅ MongoDB připojeno")
    except Exception as e:
        print(f"❌ MongoDB nedostupné: {e}")
        print("   Spusť: docker run -d --name mongodb -p 27017:27017 mongo:7")
        return

    db = client["kurz_demo"]

    demo_crud(db)
    demo_agregace(db)
    demo_indexy(db)
    demo_async()

    client.close()
    print("\n✅ Demo dokončeno!")


if __name__ == "__main__":
    main()

```
