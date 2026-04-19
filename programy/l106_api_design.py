"""Lekce 106 — API design: REST, versioning, BFF, Pydantic modely."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ── Pydantic simulace (bez external lib — vlastní mini-validátor) ─────────────
# V reálném projektu by toto byl: from pydantic import BaseModel, Field

class ValidacniChyba(Exception):
    def __init__(self, chyby: dict[str, str]) -> None:
        self.chyby = chyby
        super().__init__(str(chyby))


class ModelBase:
    """Zjednodušená náhrada za Pydantic BaseModel — pro demo bez externích závislostí."""

    def model_dump(self) -> dict[str, Any]:
        return {
            k: v for k, v in self.__dict__.items()
            if not k.startswith("_")
        }

    def model_dump_json(self) -> str:
        def serialize(obj: Any) -> Any:
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, ModelBase):
                return obj.model_dump()
            return obj

        data = {k: serialize(v) for k, v in self.model_dump().items()}
        return json.dumps(data, ensure_ascii=False, indent=2)

    @classmethod
    def model_json_schema(cls) -> dict[str, Any]:
        """Velmi zjednodušená ukázka — reálně Pydantic generuje plné JSON Schema."""
        hints = {}
        for k, v in cls.__annotations__.items():
            hints[k] = str(v)
        return {
            "title": cls.__name__,
            "type": "object",
            "properties": {k: {"type": t} for k, t in hints.items()},
        }

    def __repr__(self) -> str:
        fields = ", ".join(f"{k}={v!r}" for k, v in self.model_dump().items())
        return f"{self.__class__.__name__}({fields})"


# ── V1 API modely ─────────────────────────────────────────────────────────────

@dataclass
class VytvorUzivateleV1Request(ModelBase):
    """Request model pro vytvoření uživatele — vstup od klienta."""
    jmeno: str
    email: str
    vek: int | None = None

    def __post_init__(self) -> None:
        chyby: dict[str, str] = {}
        if len(self.jmeno) < 2:
            chyby["jmeno"] = "Jméno musí mít alespoň 2 znaky"
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            chyby["email"] = "Neplatný formát e-mailu"
        if self.vek is not None and not (0 <= self.vek <= 150):
            chyby["vek"] = "Věk musí být v rozsahu 0–150"
        if chyby:
            raise ValidacniChyba(chyby)


@dataclass
class UzivatelV1Response(ModelBase):
    """Response model V1 — nikdy neexponujeme interní pole (heslo, hash...)."""
    id: int
    jmeno: str
    email: str
    vytvoreno: datetime


# ── V2 API modely (schema evolution) ─────────────────────────────────────────

@dataclass
class VytvorUzivateleV2Request(ModelBase):
    """V2: přidán nepovinný telefon (non-breaking change)."""
    jmeno: str
    email: str
    vek: int | None = None
    telefon: str | None = None   # přidáno ve V2

    def __post_init__(self) -> None:
        chyby: dict[str, str] = {}
        if len(self.jmeno) < 2:
            chyby["jmeno"] = "Jméno musí mít alespoň 2 znaky"
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            chyby["email"] = "Neplatný formát e-mailu"
        if self.telefon is not None and not re.match(r"^\+?\d{9,15}$", self.telefon):
            chyby["telefon"] = "Neplatný formát telefonu"
        if chyby:
            raise ValidacniChyba(chyby)


@dataclass
class UzivatelV2Response(ModelBase):
    """Response model V2 — zpětně kompatibilní s V1."""
    id: int
    jmeno: str
    email: str
    vytvoreno: datetime
    telefon: str | None = None   # nové pole, nepovinné → zpětně kompatibilní


# ── Chybový model — konzistentní formát ──────────────────────────────────────

@dataclass
class ApiChyba(ModelBase):
    kod: str
    zprava: str
    detail: dict[str, Any] | None = None

    def __str__(self) -> str:
        return f"[{self.kod}] {self.zprava}"


# ── Simulace API endpointů ────────────────────────────────────────────────────

class SimulovanyUzivatelStore:
    """In-memory úložiště pro demo."""
    def __init__(self) -> None:
        self._users: dict[int, dict[str, Any]] = {}
        self._seq = 1

    def vloz(self, data: dict[str, Any]) -> dict[str, Any]:
        id = self._seq
        self._seq += 1
        zaznam = {**data, "id": id, "vytvoreno": datetime.now()}
        self._users[id] = zaznam
        return zaznam

    def najdi(self, id: int) -> dict[str, Any] | None:
        return self._users.get(id)

    def seznam(self) -> list[dict[str, Any]]:
        return list(self._users.values())


class UzivatelApiV1:
    """Simulace REST API endpointů — /api/v1/users."""

    def __init__(self, store: SimulovanyUzivatelStore) -> None:
        self._store = store

    def post_users(self, body: dict[str, Any]) -> tuple[int, Any]:
        """POST /api/v1/users → 201 Created nebo 400 Bad Request."""
        try:
            req = VytvorUzivateleV1Request(
                jmeno=body.get("jmeno", ""),
                email=body.get("email", ""),
                vek=body.get("vek"),
            )
        except ValidacniChyba as exc:
            return 400, ApiChyba(
                kod="VALIDACNI_CHYBA",
                zprava="Vstup obsahuje neplatná data",
                detail=exc.chyby,
            )

        if any(u["email"] == req.email for u in self._store.seznam()):
            return 409, ApiChyba(
                kod="EMAIL_JIZ_EXISTUJE",
                zprava=f"E-mail {req.email!r} je již registrován",
            )

        zaznam = self._store.vloz({"jmeno": req.jmeno, "email": req.email, "vek": req.vek})
        response = UzivatelV1Response(
            id=zaznam["id"],
            jmeno=zaznam["jmeno"],
            email=zaznam["email"],
            vytvoreno=zaznam["vytvoreno"],
        )
        return 201, response

    def get_users_id(self, id: int) -> tuple[int, Any]:
        """GET /api/v1/users/{id} → 200 OK nebo 404 Not Found."""
        zaznam = self._store.najdi(id)
        if zaznam is None:
            return 404, ApiChyba(
                kod="UZIVATEL_NENALEZEN",
                zprava=f"Uživatel s id={id} nebyl nalezen",
            )
        return 200, UzivatelV1Response(
            id=zaznam["id"],
            jmeno=zaznam["jmeno"],
            email=zaznam["email"],
            vytvoreno=zaznam["vytvoreno"],
        )

    def get_users(self) -> tuple[int, list[UzivatelV1Response]]:
        """GET /api/v1/users → 200 OK."""
        return 200, [
            UzivatelV1Response(
                id=u["id"], jmeno=u["jmeno"],
                email=u["email"], vytvoreno=u["vytvoreno"],
            )
            for u in self._store.seznam()
        ]


# ── BFF — Backend for Frontend ────────────────────────────────────────────────

@dataclass
class MobilniProfilResponse(ModelBase):
    """BFF response pro mobilní aplikaci — agreguje více zdrojů."""
    uzivatel_id: int
    zobrazovane_jmeno: str
    email: str
    pocet_objednavek: int
    neprectene_zpravy: int
    posledni_aktivita: str


class MobilniBFF:
    """BFF vrstva — přizpůsobí odpověď mobilnímu klientovi."""

    def __init__(self, user_api: UzivatelApiV1) -> None:
        self._user_api = user_api

    def nacti_profil(self, user_id: int) -> tuple[int, Any]:
        status, data = self._user_api.get_users_id(user_id)
        if status != 200:
            return status, data

        # Simulace volání dalších mikroslužeb
        pocet_obj = 3           # orders_service.count(user_id)
        neprectene = 7          # notifications_service.unread_count(user_id)

        return 200, MobilniProfilResponse(
            uzivatel_id=data.id,
            zobrazovane_jmeno=data.jmeno.split()[0],  # jen křestní jméno pro mobil
            email=data.email,
            pocet_objednavek=pocet_obj,
            neprectene_zpravy=neprectene,
            posledni_aktivita=data.vytvoreno.strftime("%d. %m. %Y"),
        )


# ── Demo ──────────────────────────────────────────────────────────────────────

def tiskni_odpoved(metoda: str, cesta: str, status: int, data: Any) -> None:
    icon = "✓" if status < 400 else "✗"
    print(f"  {icon} {metoda} {cesta} → {status}")
    if hasattr(data, "model_dump"):
        for k, v in data.model_dump().items():
            val = v.isoformat() if isinstance(v, datetime) else v
            print(f"      {k}: {val}")
    elif isinstance(data, list):
        print(f"      [{len(data)} položek]")
    print()


def main() -> None:
    print("=== API Design demo ===\n")

    store = SimulovanyUzivatelStore()
    api_v1 = UzivatelApiV1(store)

    print("--- POST /api/v1/users — vytvoření uživatelů ---")
    uzivatele = [
        {"jmeno": "Anna Nováková", "email": "anna@example.com", "vek": 28},
        {"jmeno": "Bob Svoboda", "email": "bob@example.com", "vek": 35},
        {"jmeno": "Cyril Dvořák", "email": "cyril@example.com"},
    ]
    for body in uzivatele:
        status, data = api_v1.post_users(body)
        tiskni_odpoved("POST", "/api/v1/users", status, data)

    print("--- Validační chyba (400) ---")
    status, data = api_v1.post_users({"jmeno": "X", "email": "neplatny-email"})
    tiskni_odpoved("POST", "/api/v1/users", status, data)

    print("--- Konflikt — duplicitní e-mail (409) ---")
    status, data = api_v1.post_users({"jmeno": "Anna2", "email": "anna@example.com"})
    tiskni_odpoved("POST", "/api/v1/users", status, data)

    print("--- GET /api/v1/users/1 — čtení uživatele ---")
    status, data = api_v1.get_users_id(1)
    tiskni_odpoved("GET", "/api/v1/users/1", status, data)

    print("--- GET /api/v1/users/999 — neexistující (404) ---")
    status, data = api_v1.get_users_id(999)
    tiskni_odpoved("GET", "/api/v1/users/999", status, data)

    print("--- BFF: mobilní profil ---")
    bff = MobilniBFF(api_v1)
    status, data = bff.nacti_profil(1)
    tiskni_odpoved("GET", "/bff/mobile/profil/1", status, data)

    print("--- Schema Evolution: V1 vs V2 ---")
    print("  V1 Request fields:", list(VytvorUzivateleV1Request.__annotations__))
    print("  V2 Request fields:", list(VytvorUzivateleV2Request.__annotations__))
    print("  Nové pole 'telefon' je nepovinné → zpětně kompatibilní (non-breaking)")

    print("\n--- JSON Schema (zjednodušené) ---")
    schema = UzivatelV1Response.model_json_schema()
    print(f"  {schema['title']}: {list(schema['properties'].keys())}")

    print("\n--- Richardson Maturity Model ---")
    urovne = [
        (0, "The Swamp of POX",  "POST /api?action=getUser"),
        (1, "Resources",          "GET /users/42"),
        (2, "HTTP Verbs",         "GET/POST/PUT/DELETE /users"),
        (3, "HATEOAS",            "Odpověď obsahuje _links"),
    ]
    for uroven, nazev, priklad in urovne:
        hvezdicky = "★" * (uroven + 1)
        print(f"  Level {uroven} {hvezdicky:4s} {nazev:20s} → {priklad}")


if __name__ == "__main__":
    main()
