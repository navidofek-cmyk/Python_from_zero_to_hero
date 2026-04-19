# Lekce 97: Web — FastAPI

## 🌐 Co je FastAPI?

**FastAPI** je moderní web framework — rychlý, type-driven, s automatickou dokumentací.

```bash
pip install "fastapi[standard]"
```

```python
# main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Pes(BaseModel):
    jmeno: str
    vek: int


@app.get("/")
def root():
    return {"zprava": "Ahoj!"}


@app.get("/psi/{id}")
def get_pes(id: int):
    return {"id": id, "jmeno": "Rex"}


@app.post("/psi")
def vytvor_pes(pes: Pes):
    return {"vytvoreno": pes}
```

Spuštění:
```bash
fastapi dev main.py
# → http://127.0.0.1:8000
# → http://127.0.0.1:8000/docs   (Swagger UI automaticky!)
```

---

## ✨ Klíčové features

✅ **Type-driven** — používá typové anotace pro validaci
✅ **Pydantic** pro modely
✅ **Auto docs** — Swagger UI + ReDoc
✅ **Async ready** — `async def` z krabice
✅ **Rychlý** — postavený na Starlette + Pydantic v Rustu

---

## 🎯 Path & query parametry

```python
@app.get("/items/{item_id}")
def get_item(item_id: int, limit: int = 10, sort: str = "asc"):
    return {"id": item_id, "limit": limit, "sort": sort}
```

`item_id` je z cesty, ostatní z query string.

---

## 📦 Pydantic modely

```python
from pydantic import BaseModel, Field, EmailStr

class Uzivatel(BaseModel):
    jmeno: str = Field(min_length=1, max_length=50)
    vek: int = Field(ge=0, le=150)
    email: EmailStr
```

**Pydantic** validuje vstup automaticky. Při špatném vstupu vrátí 422.

---

## 🛠️ Dependency injection

```python
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users")
def list_users(db = Depends(get_db)):
    return db.query(...)
```

---

## 🔒 Auth

```python
from fastapi.security import OAuth2PasswordBearer

oauth = OAuth2PasswordBearer(tokenUrl="login")

@app.get("/me")
def me(token: str = Depends(oauth)):
    return decode(token)
```

---

## 📤 Async

```python
import httpx

@app.get("/proxy/{url}")
async def proxy(url: str):
    async with httpx.AsyncClient() as c:
        r = await c.get(url)
        return r.json()
```

---

## 🎯 Alternativy

- **Flask** — klasika, jednodušší, sync. Pro malé věci.
- **Django** — full-stack (DB, admin, ORM). Pro webové aplikace.
- **Starlette** — pod kapotou FastAPI, low-level.
- **Litestar** — alternativa k FastAPI.

V 2026 je **FastAPI standard** pro REST API.

---

## ✏️ Cvičení

1. **Hello world:** Vyrob `app.py` s `/` endpointem.
2. **CRUD:** GET, POST, PUT, DELETE `/items`.
3. **Pydantic:** Model `Item(nazev, cena)` s validací (cena > 0).
4. **Docs:** Otevři `/docs`, vyzkoušej API přes Swagger.
