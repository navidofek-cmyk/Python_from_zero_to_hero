"""Lekce 109 — Validace a kontrakty: Pydantic v2 (simulace bez externí lib)."""

from __future__ import annotations

# Poznámka: Tento soubor implementuje zjednodušenou validaci bez pydantic
# pro demonstraci konceptů. V produkci použijte:
#   pip install pydantic
#   from pydantic import BaseModel, Field, field_validator, model_validator

import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


# ── Mini-validátor (simulace Pydantic API) ────────────────────────────────────

class ValidationError(Exception):
    def __init__(self, chyby: list[dict[str, str]]) -> None:
        self.chyby = chyby
        zpravy = "; ".join(f"{c['loc']}: {c['msg']}" for c in chyby)
        super().__init__(f"Validační chyba [{zpravy}]")

    def __str__(self) -> str:
        lines = [f"  ValidationError ({len(self.chyby)} chyb):"]
        for c in self.chyby:
            lines.append(f"    [{c['loc']}] {c['msg']}")
        return "\n".join(lines)


def _chyba(loc: str, msg: str) -> dict[str, str]:
    return {"loc": loc, "msg": msg}


class BaseModel:
    """Zjednodušená náhrada Pydantic BaseModel — demonstrace konceptů."""

    def model_dump(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue
            if isinstance(v, BaseModel):
                result[k] = v.model_dump()
            elif isinstance(v, list):
                result[k] = [i.model_dump() if isinstance(i, BaseModel) else i for i in v]
            elif isinstance(v, (date, datetime)):
                result[k] = v.isoformat()
            else:
                result[k] = v
        return result

    def model_dump_json(self) -> str:
        return json.dumps(self.model_dump(), ensure_ascii=False, indent=2)

    @classmethod
    def model_json_schema(cls) -> dict[str, Any]:
        """Zjednodušené JSON Schema — reálný Pydantic generuje plné schéma."""
        props: dict[str, Any] = {}
        annotations = {}
        for klass in reversed(cls.__mro__):
            if hasattr(klass, "__annotations__"):
                annotations.update(klass.__annotations__)

        for attr, typ in annotations.items():
            if attr.startswith("_"):
                continue
            props[attr] = {"type": str(typ)}

        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": cls.__name__,
            "type": "object",
            "properties": props,
        }

    def __repr__(self) -> str:
        fields_str = ", ".join(f"{k}={v!r}" for k, v in self.model_dump().items())
        return f"{self.__class__.__name__}({fields_str})"


# ── Modely: Adresa ────────────────────────────────────────────────────────────

class Adresa(BaseModel):
    ulice: str
    mesto: str
    psc: str

    def __init__(self, ulice: str, mesto: str, psc: str) -> None:
        chyby = []
        if not ulice.strip():
            chyby.append(_chyba("ulice", "Ulice nesmí být prázdná"))
        if not mesto.strip():
            chyby.append(_chyba("mesto", "Město nesmí být prázdné"))
        # Pydantic field_validator pro PSC: NNN NN nebo NNNNN
        psc_clean = psc.replace(" ", "")
        if not re.match(r"^\d{5}$", psc_clean):
            chyby.append(_chyba("psc", "PSČ musí mít formát '12345' nebo '123 45'"))
        if chyby:
            raise ValidationError(chyby)
        self.ulice = ulice
        self.mesto = mesto
        self.psc = psc_clean  # normalizace: uložíme bez mezery

    def __str__(self) -> str:
        return f"{self.ulice}, {self.psc[:3]} {self.psc[3:]} {self.mesto}"


# ── Modely: Uzivatel (schema evolution V1 → V2 → V3) ────────────────────────

class UzivatelV1(BaseModel):
    id: int
    email: str

    def __init__(self, id: int, email: str) -> None:
        chyby = []
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            chyby.append(_chyba("email", "Neplatný formát e-mailu"))
        if chyby:
            raise ValidationError(chyby)
        self.id = id
        self.email = email.lower()  # normalizace


class UzivatelV2(BaseModel):
    """V2: přidán nepovinný telefon — non-breaking change."""
    id: int
    email: str
    telefon: str | None = None   # nepovinné → zpětně kompatibilní

    def __init__(self, id: int, email: str, telefon: str | None = None) -> None:
        chyby = []
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            chyby.append(_chyba("email", "Neplatný formát e-mailu"))
        if telefon is not None and not re.match(r"^\+?\d{9,15}$", telefon.replace(" ", "")):
            chyby.append(_chyba("telefon", "Neplatný formát telefonu"))
        if chyby:
            raise ValidationError(chyby)
        self.id = id
        self.email = email.lower()
        self.telefon = telefon


# ── Model: Produkt s Field omezeními ─────────────────────────────────────────

class Produkt(BaseModel):
    """
    Pydantic v2 verze by vypadala:

    from pydantic import BaseModel, Field

    class Produkt(BaseModel):
        id: int
        nazev: str = Field(min_length=2, max_length=200)
        cena: float = Field(gt=0, description="Cena v Kč bez DPH")
        sleva: float = Field(default=0.0, ge=0.0, le=100.0)
        ean: str = Field(pattern=r"^\\d{13}$")
    """

    id: int
    nazev: str
    cena: float
    sleva: float
    ean: str

    def __init__(self, id: int, nazev: str, cena: float, sleva: float = 0.0, ean: str = "") -> None:
        chyby = []
        if len(nazev) < 2:
            chyby.append(_chyba("nazev", "Název musí mít alespoň 2 znaky"))
        if len(nazev) > 200:
            chyby.append(_chyba("nazev", "Název může mít nejvýše 200 znaků"))
        if cena <= 0:
            chyby.append(_chyba("cena", "Cena musí být větší než 0"))
        if not (0.0 <= sleva <= 100.0):
            chyby.append(_chyba("sleva", "Sleva musí být v rozsahu 0–100 %"))
        if ean and not re.match(r"^\d{13}$", ean):
            chyby.append(_chyba("ean", "EAN musí mít přesně 13 číslic"))
        if chyby:
            raise ValidationError(chyby)
        self.id = id
        self.nazev = nazev
        self.cena = cena
        self.sleva = sleva
        self.ean = ean

    def cena_s_dph(self, sazba_dph: float = 21.0) -> float:
        cena_po_sleve = self.cena * (1 - self.sleva / 100)
        return round(cena_po_sleve * (1 + sazba_dph / 100), 2)


# ── Model: Rezervace s křížovou validací (model_validator) ───────────────────

class Rezervace(BaseModel):
    """
    Pydantic v2 verze:
    from pydantic import model_validator

    @model_validator(mode="after")
    def zkontroluj_datumy(self) -> "Rezervace":
        if self.do <= self.od:
            raise ValueError("Datum odjezdu musí být po datu příjezdu")
        return self
    """

    od: date
    do: date
    pocet_hostu: int
    dite: bool
    zakaznik: UzivatelV2

    def __init__(
        self,
        od: date,
        do: date,
        pocet_hostu: int,
        dite: bool,
        zakaznik: UzivatelV2,
    ) -> None:
        chyby = []
        # field_validator ekvivalenty
        if pocet_hostu < 1 or pocet_hostu > 10:
            chyby.append(_chyba("pocet_hostu", "Počet hostů musí být 1–10"))
        # model_validator ekvivalenty (křížová validace)
        if do <= od:
            chyby.append(_chyba("do", "Datum odjezdu musí být po datu příjezdu"))
        if dite and pocet_hostu < 2:
            chyby.append(_chyba("dite", "Dítě musí mít doprovod — počet hostů ≥ 2"))
        if chyby:
            raise ValidationError(chyby)
        self.od = od
        self.do = do
        self.pocet_hostu = pocet_hostu
        self.dite = dite
        self.zakaznik = zakaznik

    @property
    def pocet_noci(self) -> int:
        return (self.do - self.od).days


# ── Demo ──────────────────────────────────────────────────────────────────────

def ukazka_validacni_chyby(label: str, fn: Any) -> None:
    try:
        result = fn()
        print(f"  ✓ {label}: {result}")
    except ValidationError as exc:
        print(f"  ✗ {label}:")
        print(exc)


def main() -> None:
    print("=== Validace a kontrakty — Pydantic v2 demo ===\n")

    # --- Adresa: field_validator pro PSC ---
    print("--- Adresa: validace PSČ ---")
    ukazka_validacni_chyby(
        "Platné PSČ '12000'",
        lambda: Adresa("Náměstí 1", "Praha", "12000"),
    )
    ukazka_validacni_chyby(
        "Platné PSČ '120 00'",
        lambda: Adresa("Ulice 5", "Brno", "602 00"),
    )
    ukazka_validacni_chyby(
        "Neplatné PSČ '1234'",
        lambda: Adresa("Ulice 5", "Brno", "1234"),
    )

    # --- Produkt: omezení hodnot ---
    print("\n--- Produkt: Field omezení ---")
    ukazka_validacni_chyby(
        "Platný produkt",
        lambda: Produkt(1, "Notebook Pro 15", 29999.0, sleva=10.0, ean="1234567890123"),
    )

    p = Produkt(1, "Notebook", 29999.0)
    print(f"  Cena bez DPH: {p.cena:.2f} Kč")
    print(f"  Cena s DPH:   {p.cena_s_dph():.2f} Kč")

    ukazka_validacni_chyby(
        "Záporná cena",
        lambda: Produkt(2, "Špatný", -100.0),
    )
    ukazka_validacni_chyby(
        "Krátký název + špatný EAN",
        lambda: Produkt(3, "X", 100.0, ean="abc"),
    )

    # --- Schema evolution ---
    print("\n--- Schema Evolution: V1 → V2 ---")
    u_v1 = UzivatelV1(1, "anna@example.com")
    u_v2 = UzivatelV2(1, "anna@example.com", telefon="+420777123456")
    u_v2_compat = UzivatelV2(1, "anna@example.com")  # bez telefonu = zpětně kompatibilní
    print(f"  V1 fields: {list(u_v1.model_dump().keys())}")
    print(f"  V2 fields: {list(u_v2.model_dump().keys())}")
    print(f"  V2 bez nového pole: {u_v2_compat.model_dump()}")

    # --- Rezervace: model_validator (křížová validace) ---
    print("\n--- Rezervace: křížová validace ---")
    zakaznik = UzivatelV2(1, "anna@example.com")

    ukazka_validacni_chyby(
        "Platná rezervace",
        lambda: Rezervace(
            od=date(2026, 7, 10),
            do=date(2026, 7, 15),
            pocet_hostu=2,
            dite=True,
            zakaznik=zakaznik,
        ),
    )
    ukazka_validacni_chyby(
        "Odjezd před příjezdem",
        lambda: Rezervace(
            od=date(2026, 7, 15),
            do=date(2026, 7, 10),   # špatně
            pocet_hostu=2,
            dite=False,
            zakaznik=zakaznik,
        ),
    )
    ukazka_validacni_chyby(
        "Dítě bez doprovodu",
        lambda: Rezervace(
            od=date(2026, 8, 1),
            do=date(2026, 8, 5),
            pocet_hostu=1,    # špatně — dítě potřebuje ≥ 2 hosty
            dite=True,
            zakaznik=zakaznik,
        ),
    )

    rez = Rezervace(
        od=date(2026, 7, 10),
        do=date(2026, 7, 15),
        pocet_hostu=3,
        dite=False,
        zakaznik=zakaznik,
    )
    print(f"\n  Platná rezervace: {rez.od} – {rez.do} ({rez.pocet_noci} nocí)")

    # --- JSON Schema ---
    print("\n--- JSON Schema ---")
    schema = Produkt.model_json_schema()
    print(f"  Schema title: {schema['title']}")
    print(f"  Properties:   {list(schema['properties'].keys())}")
    print("  (Pydantic v2 generuje plné JSON Schema včetně omezení, description atd.)")

    # --- model_dump a model_dump_json ---
    print("\n--- Serializace ---")
    rezervace_dict = rez.model_dump()
    print(f"  model_dump keys: {list(rezervace_dict.keys())}")
    print(f"  zakaznik.email: {rezervace_dict['zakaznik']['email']}")

    print("\n--- Pydantic v2 oproti v1 ---")
    rozdily = [
        ("BaseModel.__init__",     "Stejné API, ale 5–50× rychlejší (Rust core)"),
        ("@validator",             "Přejmenován na @field_validator"),
        ("@root_validator",        "Přejmenován na @model_validator"),
        ("Config class",           "Nahrazen model_config = ConfigDict(...)"),
        ("orm_mode = True",        "Nahrazen from_attributes=True v ConfigDict"),
    ]
    for stare, nove in rozdily:
        print(f"  {stare:30s} → {nove}")


if __name__ == "__main__":
    main()
