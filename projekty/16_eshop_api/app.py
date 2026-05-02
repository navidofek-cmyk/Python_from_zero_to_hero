"""
Projekt 16 — Kompletní e-shop API

Spojuje: FastAPI + PostgreSQL (SQLite pro demo) + Redis cache +
         Celery tasky + JWT auth + Alembic migrace + OpenTelemetry

Spuštění (SQLite demo):
    uv add "fastapi[standard]" sqlalchemy "python-jose[cryptography]" "passlib[bcrypt]"
    fastapi dev projekty/16_eshop_api/app.py

Produkce (plné):
    uv add psycopg2-binary redis celery alembic
    docker compose up
"""

from __future__ import annotations
import os
import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, Session, relationship, sessionmaker

# ── DB ────────────────────────────────────────────────────────────────────────

DB_URL = os.environ.get("DATABASE_URL", "sqlite:///eshop.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Uzivatel(Base):
    __tablename__ = "uzivatele"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="customer")
    aktivni = Column(Boolean, default=True)
    objednavky = relationship("Objednavka", back_populates="uzivatel")


class Produkt(Base):
    __tablename__ = "produkty"
    id = Column(Integer, primary_key=True)
    nazev = Column(String(200), nullable=False)
    popis = Column(Text)
    cena = Column(Float, nullable=False)
    sklad = Column(Integer, default=0)
    kategorie = Column(String(100))
    aktivni = Column(Boolean, default=True)


class Objednavka(Base):
    __tablename__ = "objednavky"
    id = Column(Integer, primary_key=True)
    uzivatel_id = Column(Integer, ForeignKey("uzivatele.id"), nullable=False)
    stav = Column(String(50), default="pending")
    celkova_cena = Column(Float, nullable=False)
    vytvoreno = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    uzivatel = relationship("Uzivatel", back_populates="objednavky")
    polozky = relationship("ObjednavkaPolozka", back_populates="objednavka")


class ObjednavkaPolozka(Base):
    __tablename__ = "objednavka_polozky"
    id = Column(Integer, primary_key=True)
    objednavka_id = Column(Integer, ForeignKey("objednavky.id"))
    produkt_id = Column(Integer, ForeignKey("produkty.id"))
    mnozstvi = Column(Integer, nullable=False)
    cena = Column(Float, nullable=False)
    objednavka = relationship("Objednavka", back_populates="polozky")
    produkt = relationship("Produkt")


# ── Auth ──────────────────────────────────────────────────────────────────────

try:
    from jose import jwt, JWTError
    from passlib.context import CryptContext
    TAJNY_KLIC = os.environ.get("SECRET_KEY", secrets.token_hex(32))
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2 = OAuth2PasswordBearer(tokenUrl="auth/token")

    def hash_heslo(h): return pwd_ctx.hash(h)
    def over_heslo(h, hh): return pwd_ctx.verify(h, hh)
    def vytvor_token(data): return jwt.encode(
        {**data, "exp": datetime.now(timezone.utc) + timedelta(hours=24)},
        TAJNY_KLIC, algorithm="HS256"
    )

    def get_user(db: Session = Depends(lambda: next(get_db())),
                  token: str = Depends(oauth2)) -> Uzivatel:
        try:
            payload = jwt.decode(token, TAJNY_KLIC, algorithms=["HS256"])
            user = db.query(Uzivatel).filter_by(username=payload["sub"]).first()
            if not user or not user.aktivni:
                raise HTTPException(401, "Neplatný token")
            return user
        except JWTError:
            raise HTTPException(401, "Neplatný token")

    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    def get_user(): raise HTTPException(503, "Nainstaluj: python-jose passlib bcrypt")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Pydantic schémata ─────────────────────────────────────────────────────────

class ProduktCreate(BaseModel):
    nazev: str = Field(min_length=1, max_length=200)
    popis: Optional[str] = None
    cena: float = Field(gt=0)
    sklad: int = Field(ge=0, default=0)
    kategorie: Optional[str] = None


class ProduktResponse(BaseModel):
    id: int
    nazev: str
    cena: float
    sklad: int
    kategorie: Optional[str]
    model_config = {"from_attributes": True}


class ObjednavkaPolozkaCreate(BaseModel):
    produkt_id: int
    mnozstvi: int = Field(ge=1)


class ObjednavkaCreate(BaseModel):
    polozky: list[ObjednavkaPolozkaCreate]


class ObjednavkaResponse(BaseModel):
    id: int
    stav: str
    celkova_cena: float
    vytvoreno: datetime
    model_config = {"from_attributes": True}


class UzivatelCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── App ───────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    # Seed data
    db = SessionLocal()
    if db.query(Produkt).count() == 0:
        for i, (nazev, cena, kat) in enumerate([
            ("Laptop Pro", 25000, "Elektronika"),
            ("Bezdrátová myš", 800, "Elektronika"),
            ("Ergonomická klávesnice", 2500, "Elektronika"),
            ("Monitor 27\"", 12000, "Elektronika"),
            ("Kancelářská židle", 8000, "Nábytek"),
        ]):
            db.add(Produkt(nazev=nazev, cena=cena, kategorie=kat, sklad=10+i*5))
        db.commit()
    db.close()
    yield


app = FastAPI(title="E-shop API", version="1.0.0", lifespan=lifespan)


# ── Produkty ──────────────────────────────────────────────────────────────────

@app.get("/produkty", response_model=list[ProduktResponse], tags=["Produkty"])
def seznam_produktu(
    kategorie: Optional[str] = None,
    min_cena: Optional[float] = None,
    max_cena: Optional[float] = None,
    hledat: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Produkt).filter_by(aktivni=True)
    if kategorie: q = q.filter_by(kategorie=kategorie)
    if min_cena: q = q.filter(Produkt.cena >= min_cena)
    if max_cena: q = q.filter(Produkt.cena <= max_cena)
    if hledat: q = q.filter(Produkt.nazev.ilike(f"%{hledat}%"))
    return q.offset(skip).limit(limit).all()


@app.get("/produkty/{id}", response_model=ProduktResponse, tags=["Produkty"])
def get_produkt(id: int, db: Session = Depends(get_db)):
    p = db.query(Produkt).filter_by(id=id, aktivni=True).first()
    if not p: raise HTTPException(404, "Produkt nenalezen")
    return p


@app.post("/admin/produkty", response_model=ProduktResponse, status_code=201, tags=["Admin"])
def vytvor_produkt(
    data: ProduktCreate,
    db: Session = Depends(get_db),
    user: Uzivatel = Depends(get_user) if AUTH_AVAILABLE else None,
):
    p = Produkt(**data.model_dump())
    db.add(p); db.commit(); db.refresh(p)
    return p


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.post("/auth/register", status_code=201, tags=["Auth"])
def register(data: UzivatelCreate, db: Session = Depends(get_db)):
    if not AUTH_AVAILABLE:
        raise HTTPException(503, "Nainstaluj: python-jose passlib")
    if db.query(Uzivatel).filter_by(username=data.username).first():
        raise HTTPException(400, "Username obsazené")
    u = Uzivatel(
        username=data.username,
        email=data.email,
        hashed_password=hash_heslo(data.password),
    )
    db.add(u); db.commit()
    return {"id": u.id, "username": u.username}


@app.post("/auth/token", response_model=TokenResponse, tags=["Auth"])
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    if not AUTH_AVAILABLE:
        raise HTTPException(503, "Nainstaluj: python-jose passlib")
    u = db.query(Uzivatel).filter_by(username=form.username).first()
    if not u or not over_heslo(form.password, u.hashed_password):
        raise HTTPException(401, "Špatné přihlašovací údaje")
    return TokenResponse(access_token=vytvor_token({"sub": u.username}))


# ── Objednávky ────────────────────────────────────────────────────────────────

@app.post("/objednavky", response_model=ObjednavkaResponse, status_code=201, tags=["Objednávky"])
def vytvor_objednavku(
    data: ObjednavkaCreate,
    db: Session = Depends(get_db),
    user: Uzivatel = Depends(get_user),
):
    celkem = 0.0
    polozky = []
    for pol in data.polozky:
        p = db.query(Produkt).filter_by(id=pol.produkt_id, aktivni=True).first()
        if not p: raise HTTPException(404, f"Produkt {pol.produkt_id} nenalezen")
        if p.sklad < pol.mnozstvi:
            raise HTTPException(400, f"Nedostatek na skladě pro {p.nazev}")
        celkem += p.cena * pol.mnozstvi
        p.sklad -= pol.mnozstvi
        polozky.append(ObjednavkaPolozka(produkt_id=p.id, mnozstvi=pol.mnozstvi, cena=p.cena))

    obj = Objednavka(uzivatel_id=user.id, celkova_cena=celkem)
    db.add(obj); db.flush()
    for pol in polozky:
        pol.objednavka_id = obj.id
        db.add(pol)
    db.commit(); db.refresh(obj)
    return obj


@app.get("/moje-objednavky", response_model=list[ObjednavkaResponse], tags=["Objednávky"])
def moje_objednavky(user: Uzivatel = Depends(get_user), db: Session = Depends(get_db)):
    return db.query(Objednavka).filter_by(uzivatel_id=user.id).all()


@app.get("/", tags=["Info"])
def root():
    return {
        "api": "E-shop API",
        "docs": "/docs",
        "endpoints": ["/produkty", "/auth/register", "/auth/token", "/objednavky"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
