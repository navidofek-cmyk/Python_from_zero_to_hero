# Lekce 106: API Design — REST, versioning, BFF, Pydantic

## REST a Richardson Maturity Model

REST má 4 úrovně zralosti (Richardson Maturity Model):

| Úroveň | Název | Příklad |
|--------|-------|---------|
| 0 | The Swamp of POX | `POST /api?action=getUser` |
| 1 | Resources | `GET /users/42` |
| 2 | HTTP Verbs | `GET`, `POST`, `PUT`, `DELETE`, `PATCH` |
| 3 | Hypermedia (HATEOAS) | Odpověď obsahuje odkazy na další akce |

Většina API v praxi dosahuje úrovně 2.

---

## HTTP metody a jejich sémantika

| Metoda | Sémantika | Idempotentní | Bezpečná |
|--------|-----------|:---:|:---:|
| GET | Čtení zdroje | ano | ano |
| POST | Vytvoření, nestandardní operace | ne | ne |
| PUT | Nahrazení celého zdroje | ano | ne |
| PATCH | Částečná aktualizace | ne* | ne |
| DELETE | Smazání | ano | ne |

---

## HTTP stavové kódy

```
2xx  Úspěch
  200 OK                 — GET, PUT, PATCH
  201 Created            — POST (Location: /users/42)
  204 No Content         — DELETE, akce bez těla odpovědi

4xx  Chyba klienta
  400 Bad Request        — neplatná data, validační chyba
  401 Unauthorized       — chybí autentizace
  403 Forbidden          — autentizován, ale nemá právo
  404 Not Found          — zdroj neexistuje
  409 Conflict           — e-mail již existuje apod.
  422 Unprocessable      — data jsou validní JSON, ale sémanticky špatná

5xx  Chyba serveru
  500 Internal Error     — neočekávaná chyba
  503 Service Unavailable — přetížení, shutdown
```

---

## Pydantic v2 — modely pro request/response

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# Request model — vstup od klienta
class VytvorUzivateleRequest(BaseModel):
    jmeno: str = Field(min_length=2, max_length=100)
    email: EmailStr
    vek: int | None = Field(default=None, ge=0, le=150)

# Response model — co pošleme klientovi
class UzivatelResponse(BaseModel):
    id: int
    jmeno: str
    email: str
    vytvoreno: datetime

    model_config = {"from_attributes": True}  # ORM mode
```

Výhody Pydantic modelů:
- Automatická validace a chybová hlášení
- JSON Schema generování (pro dokumentaci, OpenAPI)
- Bezpečný: nikdy nevracíme interní fieldy (heslo, hash...)

---

## Versioning API

Tři běžné strategie:

```
# 1. URL versioning (nejčastější, nejviditelnejší)
GET /api/v1/users/42
GET /api/v2/users/42

# 2. Query parameter
GET /api/users/42?version=2

# 3. Accept header (nejčistší z REST hlediska)
GET /api/users/42
Accept: application/vnd.myapi.v2+json
```

Doporučení:
- Verzuj od začátku — zpětná kompatibilita je těžká
- `v1` nikdy nesmaž dokud ho klienti používají
- Breaking changes = nová verze (nové povinné pole, jiný typ...)
- Non-breaking changes = přidání nepovinného pole (OK v té samé verzi)

---

## Schema Evolution

```python
# v1 — původní model
class UzivatelV1(BaseModel):
    id: int
    jmeno: str
    email: str

# v2 — přidán phone (nepovinný = zpětně kompatibilní)
class UzivatelV2(BaseModel):
    id: int
    jmeno: str
    email: str
    phone: str | None = None   # non-breaking change

# v3 — jmeno rozděleno na jmeno + prijmeni (breaking change → nová verze!)
class UzivatelV3(BaseModel):
    id: int
    jmeno: str
    prijmeni: str       # nové povinné pole = breaking!
    email: str
    phone: str | None = None
```

---

## BFF — Backend for Frontend

BFF pattern: pro každého klienta (web, mobil, IoT) vznikne dedikovaný backend který agreguje volání a přizpůsobuje odpovědi.

```
Mobil ──> BFF Mobile ──┐
Web   ──> BFF Web   ──┼──> Mikroslužby (Users, Orders, Products)
IoT   ──> BFF IoT   ──┘
```

```python
# BFF agregace — sloučí data z více zdrojů
def nacti_profil_uzivatele(user_id: int) -> dict:
    # v reálu: paralelní HTTP volání
    uzivatel = users_service.get(user_id)
    objednavky = orders_service.possledni(user_id, limit=5)
    notifikace = notif_service.neprectene(user_id)

    return {
        "uzivatel": uzivatel,
        "posledni_objednavky": objednavky,
        "neprectene_notifikace": len(notifikace),
    }
```

---

## Chybové odpovědi — konzistentní formát

```python
from pydantic import BaseModel

class ApiChyba(BaseModel):
    kod: str            # strojově čitelný kód: "UZIVATEL_NENALEZEN"
    zprava: str         # lidsky čitelná zpráva
    detail: dict | None = None   # volitelné podrobnosti

# Příklad odpovědi:
# {
#   "kod": "VALIDACNI_CHYBA",
#   "zprava": "Vstup obsahuje neplatná data",
#   "detail": {"email": "Neplatný formát e-mailu"}
# }
```

---

## Shrnutí

- REST úroveň 2 (resources + HTTP verbs) je zlatý standard
- Pydantic oddělí validaci od business logiky
- Vždy mít Request a Response modely — nikdy neexponovat interní datové struktury
- Verzuj URL od začátku (`/api/v1/...`)
- BFF pro různé klienty — šít odpověď na míru klientovi

---

## Cvičení

1. Navrhni Pydantic modely pro CRUD objednávek: `VytvorObjednavkuRequest`, `ObjednavkaResponse`, `AktualizujObjednavkuRequest`.
2. Přidej `model_validator` který ověří, že `datum_doruceni` je po `datum_objednani`.
3. Vygeneruj JSON Schema pro jeden z modelů pomocí `model.model_json_schema()`.
4. Navrhni URL strukturu pro API e-shopu (products, orders, users) s verzováním.
