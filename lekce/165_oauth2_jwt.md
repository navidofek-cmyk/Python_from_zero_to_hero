# Lekce 165: OAuth2 a JWT — autentizace API

JWT = JSON Web Token — bezstavová autentizace. OAuth2 = autorizační protokol. Základ každého produkčního API.

---

## 🚀 Instalace

```bash
uv add "python-jose[cryptography]" passlib "passlib[bcrypt]" "fastapi[standard]"
```

---

## 🔐 JWT — JSON Web Tokens

```python
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import secrets

# Konfigurace
TAJNY_KLIC = secrets.token_hex(32)   # v produkci: z env proměnné!
ALGORITMUS = "HS256"
ACCESS_TOKEN_EXPIRY = timedelta(minutes=30)
REFRESH_TOKEN_EXPIRY = timedelta(days=7)


def vytvor_access_token(data: dict, expiry: timedelta = None) -> str:
    """Vytvoří JWT access token."""
    payload = data.copy()
    if expiry is None:
        expiry = ACCESS_TOKEN_EXPIRY
    payload["exp"] = datetime.now(timezone.utc) + expiry
    payload["iat"] = datetime.now(timezone.utc)   # issued at
    payload["type"] = "access"
    return jwt.encode(payload, TAJNY_KLIC, algorithm=ALGORITMUS)


def vytvor_refresh_token(user_id: int) -> str:
    """Refresh token s delší platností."""
    return jwt.encode(
        {"sub": str(user_id), "type": "refresh",
         "exp": datetime.now(timezone.utc) + REFRESH_TOKEN_EXPIRY},
        TAJNY_KLIC, algorithm=ALGORITMUS
    )


def over_token(token: str) -> dict:
    """Ověří JWT a vrátí payload. Vyhodí výjimku při neplatném tokenu."""
    try:
        payload = jwt.decode(token, TAJNY_KLIC, algorithms=[ALGORITMUS])
        return payload
    except JWTError as e:
        raise ValueError(f"Neplatný token: {e}")


# Demo
token = vytvor_access_token({"sub": "42", "role": "admin", "email": "anna@example.com"})
print(f"Token: {token[:50]}...")

payload = over_token(token)
print(f"Payload: sub={payload['sub']}, role={payload['role']}")
```

---

## 🔒 Hashování hesel

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def zahashuj_heslo(heslo: str) -> str:
    return pwd_context.hash(heslo)


def over_heslo(heslo: str, hash: str) -> bool:
    return pwd_context.verify(heslo, hash)


# Nikdy neukládej hesla v plaintextu!
hash1 = zahashuj_heslo("tajne123")
print(f"Hash hesla: {hash1[:30]}...")
print(f"Ověření správného: {over_heslo('tajne123', hash1)}")
print(f"Ověření špatného: {over_heslo('spatne', hash1)}")
```

---

## 🏗️ FastAPI autentizace

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Simulace DB
UZIVATELE_DB = {
    "anna": {
        "id": 1,
        "username": "anna",
        "email": "anna@example.com",
        "hashed_password": zahashuj_heslo("tajne123"),
        "role": "admin",
        "aktivni": True,
    }
}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800


class AktualniUzivatel(BaseModel):
    id: int
    username: str
    email: str
    role: str


def nacti_uzivatele(username: str) -> Optional[dict]:
    return UZIVATELE_DB.get(username)


def autentizuj_uzivatele(username: str, heslo: str) -> Optional[dict]:
    uzivatel = nacti_uzivatele(username)
    if not uzivatel:
        return None
    if not over_heslo(heslo, uzivatel["hashed_password"]):
        return None
    return uzivatel


async def get_current_user(token: str = Depends(oauth2_scheme)) -> AktualniUzivatel:
    """Dependency — ověří token a vrátí aktuálního uživatele."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Neplatné přihlašovací údaje",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = over_token(token)
        if payload.get("type") != "access":
            raise credentials_exception
        username = payload.get("sub")
        if not username:
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    uzivatel = nacti_uzivatele(username)
    if not uzivatel or not uzivatel["aktivni"]:
        raise credentials_exception
    return AktualniUzivatel(**uzivatel)


def vyzaduj_roli(role: str):
    """Factory pro role-based přístup."""
    async def check(uzivatel: AktualniUzivatel = Depends(get_current_user)):
        if uzivatel.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Potřebná role: {role}"
            )
        return uzivatel
    return check


@app.post("/token", response_model=TokenResponse)
async def prihlaseni(form: OAuth2PasswordRequestForm = Depends()):
    """Přihlášení — vrátí access + refresh token."""
    uzivatel = autentizuj_uzivatele(form.username, form.password)
    if not uzivatel:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Špatné jméno nebo heslo",
        )
    return TokenResponse(
        access_token=vytvor_access_token({"sub": uzivatel["username"], "role": uzivatel["role"]}),
        refresh_token=vytvor_refresh_token(uzivatel["id"]),
    )


@app.post("/token/refresh")
async def obnov_token(refresh_token: str):
    """Obnov access token pomocí refresh tokenu."""
    try:
        payload = over_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Špatný typ tokenu")
        uzivatel = nacti_uzivatele(payload["sub"])
        if not uzivatel:
            raise ValueError("Uživatel neexistuje")
        return {
            "access_token": vytvor_access_token({"sub": uzivatel["username"]}),
            "token_type": "bearer",
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/me", response_model=AktualniUzivatel)
async def me(uzivatel: AktualniUzivatel = Depends(get_current_user)):
    return uzivatel


@app.get("/admin")
async def admin_only(uzivatel: AktualniUzivatel = Depends(vyzaduj_roli("admin"))):
    return {"zprava": f"Vítej, administrátore {uzivatel.username}!"}
```

---

## 🌐 OAuth2 s externím providerem

```python
# Google OAuth2 (example)
import httpx

GOOGLE_CLIENT_ID = "..."
GOOGLE_CLIENT_SECRET = "..."
REDIRECT_URI = "http://localhost:8000/auth/google/callback"


@app.get("/auth/google")
async def google_login():
    """Přesměruj na Google přihlášení."""
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
    }
    from urllib.parse import urlencode
    url = "https://accounts.google.com/o/oauth2/auth?" + urlencode(params)
    return {"redirect_url": url}


@app.get("/auth/google/callback")
async def google_callback(code: str):
    """Zpracuj callback od Googlu."""
    async with httpx.AsyncClient() as client:
        # Vyměň code za token
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code",
            }
        )
        tokens = token_response.json()

        # Načti info o uživateli
        user_info = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        uzivatel = user_info.json()

    # Vytvoř vlastní JWT pro uživatele
    nas_token = vytvor_access_token({"sub": uzivatel["email"], "role": "user"})
    return {"access_token": nas_token, "uzivatel": uzivatel}
```

---

## 🛡️ Bezpečnostní checklist

```python
# ✅ Správné praktiky:

# 1. Tajný klíč z prostředí
import os
TAJNY_KLIC = os.environ.get("JWT_SECRET_KEY")
assert TAJNY_KLIC, "JWT_SECRET_KEY musí být nastavena!"

# 2. HTTPS pouze (v produkci)
# app.add_middleware(HTTPSRedirectMiddleware)

# 3. Rate limiting přihlašovacího endpointu
from slowapi import Limiter
limiter = Limiter(key_func=lambda r: r.client.host)

# @app.post("/token")
# @limiter.limit("5/minute")
# async def prihlaseni(...): ...

# 4. Revokace tokenů (blacklist v Redis)
import redis as r_module
redis_client = r_module.Redis()

def revokuj_token(jti: str, expiry: int):
    redis_client.setex(f"revoked:{jti}", expiry, "1")

def je_revokovan(jti: str) -> bool:
    return bool(redis_client.exists(f"revoked:{jti}"))
```

---

## ✏️ Cvičení

1. Implementuj **two-factor authentication** (TOTP) pomocí `pyotp`.
2. Přidej **token blacklist** — po odhlášení je token neplatný (Redis).
3. Implementuj **API keys** — alternativa k JWT pro server-to-server komunikaci.
4. Napiš **OAuth2 provider** — jiné aplikace se mohou přihlásit přes tvůj server.
5. Audit bezpečnosti: najdi a oprav 5 bezpečnostních chyb v ukázkovém kódu výše.
