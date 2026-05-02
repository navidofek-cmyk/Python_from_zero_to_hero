"""Lekce 165 — OAuth2 a JWT autentizace.

Spuštění:
    uv run --with "python-jose[cryptography]" --with "passlib[bcrypt]" l165_oauth2_jwt.py
"""

import secrets
import time

try:
    from jose import jwt, JWTError
    from passlib.context import CryptContext
    LIBS_AVAILABLE = True
except ImportError:
    LIBS_AVAILABLE = False
    print("Nainstaluj: uv add 'python-jose[cryptography]' 'passlib[bcrypt]'")

from datetime import datetime, timedelta, timezone


if LIBS_AVAILABLE:
    TAJNY_KLIC = secrets.token_hex(32)
    ALGORITMUS = "HS256"
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def vytvor_token(data: dict, expiry_min: int = 30) -> str:
        payload = data.copy()
        payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expiry_min)
        payload["iat"] = datetime.now(timezone.utc)
        return jwt.encode(payload, TAJNY_KLIC, algorithm=ALGORITMUS)

    def over_token(token: str) -> dict:
        return jwt.decode(token, TAJNY_KLIC, algorithms=[ALGORITMUS])

    def zahashuj(heslo: str) -> str:
        return pwd_context.hash(heslo)

    def over_heslo(heslo: str, hash: str) -> bool:
        return pwd_context.verify(heslo, hash)


def demo_jwt():
    print("\n=== JWT Token ===")
    token = vytvor_token({"sub": "42", "role": "admin", "email": "anna@example.com"})
    print(f"  Token: {token[:60]}...")

    # Dekóduj (3 části odělené tečkou)
    header, payload_b64, sig = token.split(".")
    import base64
    padding = 4 - len(payload_b64) % 4
    payload_json = base64.b64decode(payload_b64 + "=" * padding)
    print(f"  Payload (decoded): {payload_json.decode()}")

    payload = over_token(token)
    print(f"  Verifikace: sub={payload['sub']}, role={payload['role']}")

    # Expirovaný token
    expired = vytvor_token({"sub": "test"}, expiry_min=-1)
    try:
        over_token(expired)
    except JWTError:
        print("  ✅ Expirovaný token správně odmítnut")


def demo_hesla():
    print("\n=== Hashování hesel ===")
    heslo = "tajne123"
    hash1 = zahashuj(heslo)
    hash2 = zahashuj(heslo)
    print(f"  Heslo: {heslo}")
    print(f"  Hash1: {hash1[:30]}...")
    print(f"  Hash2: {hash2[:30]}... (jiný! — salt)")
    print(f"  Ověření správného: {over_heslo(heslo, hash1)}")
    print(f"  Ověření špatného:  {over_heslo('spatne', hash1)}")

    # Benchmark
    start = time.perf_counter()
    zahashuj("heslo")
    t = time.perf_counter()-start
    print(f"  Čas hashování: {t*1000:.0f}ms (záměrně pomalé — bcrypt)")


def demo_fastapi_kod():
    print("\n=== FastAPI OAuth2 kód ===")
    print("""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
async def prihlaseni(form: OAuth2PasswordRequestForm = Depends()):
    uzivatel = autentizuj(form.username, form.password)
    if not uzivatel:
        raise HTTPException(status_code=401)
    return {
        "access_token": vytvor_token({"sub": uzivatel["id"]}),
        "token_type": "bearer"
    }

async def get_user(token: str = Depends(oauth2_scheme)):
    payload = over_token(token)
    return nacti_uzivatele(payload["sub"])

@app.get("/me")
async def profil(user = Depends(get_user)):
    return user

@app.get("/admin")
async def admin(user = Depends(get_user)):
    if user["role"] != "admin":
        raise HTTPException(403, "Přístup zamítnut")
    return {"msg": "Vítej, admine!"}
""")


def main():
    print("=" * 50)
    print("  🔐 OAuth2 + JWT Demo")
    print("=" * 50)

    if LIBS_AVAILABLE:
        demo_jwt()
        demo_hesla()
    demo_fastapi_kod()

    print("\n✅ Demo dokončeno!")
    print("Instalace: uv add 'python-jose[cryptography]' 'passlib[bcrypt]' 'fastapi[standard]'")


if __name__ == "__main__":
    main()
