# Lekce 137: MongoDB — dokumentová databáze

MongoDB ukládá data jako **JSON dokumenty** (interně BSON). Žádné schéma — každý dokument může mít jiné pole. Ideální pro nestrukturovaná nebo rychle se měnící data.

---

## 🚀 Instalace

```bash
uv add pymongo "motor[asyncio]"

# MongoDB server (Docker)
docker run -d --name mongodb -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=heslo \
  mongo:7
```

---

## 🔌 Připojení — pymongo (sync)

```python
from pymongo import MongoClient

# Lokální bez hesla
client = MongoClient("mongodb://localhost:27017/")

# S autentizací
client = MongoClient("mongodb://admin:heslo@localhost:27017/")

# Z URI
client = MongoClient("mongodb+srv://user:pass@cluster.mongodb.net/")

db = client["moje_databaze"]
kolekce = db["uzivatele"]

# Ověření připojení
client.admin.command("ping")
print("Připojeno!")
```

---

## 📝 CRUD operace

### Create — vkládání dokumentů

```python
# Jeden dokument
vysledek = kolekce.insert_one({
    "jmeno": "Anna",
    "vek": 30,
    "email": "anna@example.com",
    "tagy": ["python", "fastapi"],
    "adresa": {
        "mesto": "Praha",
        "psc": "11000"
    }
})
print(vysledek.inserted_id)  # ObjectId("...")

# Více dokumentů najednou
vysledek = kolekce.insert_many([
    {"jmeno": "Bob", "vek": 25, "email": "bob@example.com"},
    {"jmeno": "Carol", "vek": 35, "email": "carol@example.com"},
    {"jmeno": "Dan", "vek": 28, "email": "dan@example.com"},
])
print(vysledek.inserted_ids)
```

### Read — dotazy

```python
# Jeden dokument
uzivatel = kolekce.find_one({"jmeno": "Anna"})
print(uzivatel)  # celý dokument včetně _id

# Více dokumentů — vrací cursor
for u in kolekce.find({"vek": {"$gt": 25}}):
    print(u["jmeno"], u["vek"])

# Projekce — vyber jen určitá pole
for u in kolekce.find({}, {"jmeno": 1, "email": 1, "_id": 0}):
    print(u)

# Řazení, limit, skip
vysledky = list(
    kolekce.find()
    .sort("vek", -1)   # -1 = sestupně
    .skip(0)
    .limit(10)
)

# Počet
kolekce.count_documents({"vek": {"$gt": 25}})
```

### Operátory dotazů

```python
# Porovnávání
kolekce.find({"vek": {"$gt": 18, "$lt": 65}})   # 18 < vek < 65
kolekce.find({"vek": {"$in": [25, 30, 35]}})     # vek in [25, 30, 35]
kolekce.find({"vek": {"$nin": [25, 30]}})         # vek not in [25, 30]

# Logické
kolekce.find({"$or": [{"vek": {"$lt": 18}}, {"vek": {"$gt": 65}}]})
kolekce.find({"$and": [{"jmeno": "Anna"}, {"vek": 30}]})

# Existence pole
kolekce.find({"email": {"$exists": True}})
kolekce.find({"telefon": {"$exists": False}})

# Regex
import re
kolekce.find({"email": {"$regex": "@gmail\\.com$"}})

# Vnořené dokumenty
kolekce.find({"adresa.mesto": "Praha"})

# Pole obsahuje hodnotu
kolekce.find({"tagy": "python"})
kolekce.find({"tagy": {"$all": ["python", "fastapi"]}})
```

### Update — aktualizace

```python
from pymongo import ReturnDocument

# Aktualizuj jeden dokument
kolekce.update_one(
    {"jmeno": "Anna"},
    {"$set": {"vek": 31, "aktualizovano": True}}
)

# Aktualizuj více dokumentů
kolekce.update_many(
    {"vek": {"$lt": 18}},
    {"$set": {"kategorie": "junior"}}
)

# Upsert — vytvoř pokud neexistuje
kolekce.update_one(
    {"email": "novy@example.com"},
    {"$set": {"jmeno": "Nový", "vek": 20}},
    upsert=True
)

# Operátory aktualizace
kolekce.update_one({"jmeno": "Anna"}, {"$inc": {"vek": 1}})        # increment
kolekce.update_one({"jmeno": "Anna"}, {"$push": {"tagy": "ml"}})   # push do pole
kolekce.update_one({"jmeno": "Anna"}, {"$pull": {"tagy": "ml"}})   # odeber z pole
kolekce.update_one({"jmeno": "Anna"}, {"$unset": {"telefon": ""}}) # smaž pole

# Vrať aktualizovaný dokument
aktualizovany = kolekce.find_one_and_update(
    {"jmeno": "Anna"},
    {"$set": {"vek": 32}},
    return_document=ReturnDocument.AFTER
)
```

### Delete — mazání

```python
kolekce.delete_one({"jmeno": "Bob"})
kolekce.delete_many({"vek": {"$lt": 18}})
kolekce.drop()  # smaž celou kolekci
```

---

## 🔍 Agregační pipeline

Mocný nástroj pro transformaci a analýzu dat.

```python
pipeline = [
    # Stage 1: Filtruj
    {"$match": {"vek": {"$gte": 18}}},

    # Stage 2: Přidej počítané pole
    {"$addFields": {
        "vek_kategorie": {
            "$switch": {
                "branches": [
                    {"case": {"$lt": ["$vek", 30]}, "then": "junior"},
                    {"case": {"$lt": ["$vek", 50]}, "then": "mid"},
                ],
                "default": "senior"
            }
        }
    }},

    # Stage 3: Seskup a agreguj
    {"$group": {
        "_id": "$vek_kategorie",
        "pocet": {"$sum": 1},
        "prumer_vek": {"$avg": "$vek"},
        "vsichni": {"$push": "$jmeno"}
    }},

    # Stage 4: Seřaď
    {"$sort": {"pocet": -1}},

    # Stage 5: Omez výsledky
    {"$limit": 5}
]

for vysledek in kolekce.aggregate(pipeline):
    print(vysledek)
```

---

## 📊 Indexy

```python
from pymongo import ASCENDING, DESCENDING, TEXT, GEOSPHERE

# Jednoduchý index
kolekce.create_index("email", unique=True)

# Složený index
kolekce.create_index([("jmeno", ASCENDING), ("vek", DESCENDING)])

# Text index pro fulltext vyhledávání
kolekce.create_index([("popis", TEXT)])
kolekce.find({"$text": {"$search": "python programování"}})

# TTL index — automatické mazání starých dokumentů
kolekce.create_index("vytvoreno", expireAfterSeconds=3600)

# Všechny indexy
print(list(kolekce.list_indexes()))
```

---

## ⚡ Motor — async MongoDB

```python
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient


async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["asyncdb"]
    kolekce = db["produkty"]

    # Insert
    await kolekce.insert_one({"nazev": "Laptop", "cena": 25000})

    # Find
    async for produkt in kolekce.find({"cena": {"$gt": 1000}}):
        print(produkt["nazev"])

    # Agregace
    pipeline = [{"$group": {"_id": None, "celkem": {"$sum": "$cena"}}}]
    async for vysledek in kolekce.aggregate(pipeline):
        print(f"Celkem: {vysledek['celkem']} Kč")

    client.close()


asyncio.run(main())
```

---

## 🏗️ Pydantic + MongoDB

```python
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Neplatné ObjectId")
        return str(v)


class Uzivatel(BaseModel):
    id: PyObjectId | None = Field(default=None, alias="_id")
    jmeno: str
    email: str
    vek: int
    vytvoreno: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


def uloz_uzivatele(kolekce, uzivatel: Uzivatel) -> str:
    doc = uzivatel.model_dump(by_alias=True, exclude={"id"})
    vysledek = kolekce.insert_one(doc)
    return str(vysledek.inserted_id)


def nacti_uzivatele(kolekce, uzivatel_id: str) -> Uzivatel | None:
    doc = kolekce.find_one({"_id": ObjectId(uzivatel_id)})
    if doc:
        return Uzivatel(**doc)
    return None
```

---

## 🔐 Transakce (replica set)

```python
with client.start_session() as session:
    with session.start_transaction():
        db.ucty.update_one(
            {"_id": "ucet_1"},
            {"$inc": {"zustatek": -100}},
            session=session
        )
        db.ucty.update_one(
            {"_id": "ucet_2"},
            {"$inc": {"zustatek": 100}},
            session=session
        )
        # Automatický commit nebo rollback při výjimce
```

---

## 🎯 MongoDB vs SQL

| | MongoDB | PostgreSQL |
|---|---------|-----------|
| Schéma | flexibilní | pevné |
| Vztahy | embedding / $lookup | JOIN |
| Transakce | od v4.0 | plná podpora |
| Dotazy | JSON/BSON | SQL |
| Horizontální škálování | nativní sharding | složitější |
| ACID | v replica set | vždy |
| Ideální pro | dokumenty, katalogy, logy | relační data, banky |

---

## ✏️ Cvičení

1. Spusť MongoDB v Dockeru, vlož 10 dokumentů e-shopu (produkt, cena, kategorie).
2. Napiš agregaci: celková cena zboží podle kategorie, seřazená sestupně.
3. Vytvoř index na `email` (unique) a otestuj co se stane při duplikátu.
4. Implementuj async CRUD pro kolekci `blogove_prispevky` pomocí Motor.
5. Navrhni schéma pro blogovací platformu — autor, příspěvky, komentáře. Kdy embedding, kdy reference?
