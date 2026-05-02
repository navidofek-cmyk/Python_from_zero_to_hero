# Program — Lekce 134: Lekce 134: Structured Outputs — Strukturovaný výstup z LLM

Patří k lekci [Lekce 134: Structured Outputs — Strukturovaný výstup z LLM](../134_structured_outputs.md).

## Jak spustit

```bash
python3 programy/l134_structured_outputs.py
```

## Zdrojový kód

### `l134_structured_outputs.py`

```py
"""Lekce 134 — Structured Outputs (strukturovaný výstup z LLM)."""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Optional

# ── Pydantic (volitelné) ──────────────────────────────────────────────────────

try:
    from pydantic import BaseModel, Field, field_validator, model_validator
    PYDANTIC_OK = True
except ImportError:
    PYDANTIC_OK = False
    BaseModel = object  # type: ignore[assignment,misc]

# ── Datové modely (stdlib dataclass verze — vždy dostupné) ───────────────────


@dataclass
class Produkt:
    nazev: str
    cena_czk: int
    hodnoceni: float
    dostupny: bool

    def __post_init__(self) -> None:
        if not self.nazev.strip():
            raise ValueError("Název nesmí být prázdný.")
        if self.cena_czk <= 0:
            raise ValueError(f"Cena musí být kladná, dostali jsme: {self.cena_czk}")
        if not (0.0 <= self.hodnoceni <= 5.0):
            raise ValueError(f"Hodnocení musí být 0–5, dostali jsme: {self.hodnoceni}")

    @classmethod
    def z_dict(cls, d: dict[str, Any]) -> "Produkt":
        return cls(
            nazev=str(d["nazev"]),
            cena_czk=int(d["cena_czk"]),
            hodnoceni=float(d["hodnoceni"]),
            dostupny=bool(d["dostupny"]),
        )

    def jako_dict(self) -> dict[str, Any]:
        return {
            "nazev": self.nazev,
            "cena_czk": self.cena_czk,
            "hodnoceni": self.hodnoceni,
            "dostupny": self.dostupny,
        }


@dataclass
class Osoba:
    jmeno: str
    vek: Optional[int] = None
    profese: Optional[str] = None

    @classmethod
    def z_dict(cls, d: dict[str, Any]) -> "Osoba":
        return cls(
            jmeno=str(d["jmeno"]),
            vek=int(d["vek"]) if d.get("vek") is not None else None,
            profese=str(d["profese"]) if d.get("profese") else None,
        )


# ── Pydantic modely (pokud nainstalováno) ─────────────────────────────────────

if PYDANTIC_OK:
    class ProduktPydantic(BaseModel):  # type: ignore[no-redef]
        nazev: str
        cena_czk: int = Field(gt=0)
        hodnoceni: float = Field(ge=0.0, le=5.0)
        dostupny: bool

        @field_validator("nazev")
        @classmethod
        def nazev_neprazdny(cls, v: str) -> str:
            v = v.strip()
            if not v:
                raise ValueError("Název nesmí být prázdný.")
            return v

    class OsobaPydantic(BaseModel):  # type: ignore[no-redef]
        jmeno: str
        vek: Optional[int] = None
        profese: Optional[str] = None

    class SeznamOsobPydantic(BaseModel):
        osoby: list[OsobaPydantic]


# ── JSON schémata pro tool use ────────────────────────────────────────────────

SCHEMA_PRODUKT: dict[str, Any] = {
    "name": "uloz_produkt",
    "description": "Uloží strukturovaná data o produktu extrahovaná z textu.",
    "input_schema": {
        "type": "object",
        "properties": {
            "nazev":     {"type": "string",  "description": "Název produktu"},
            "cena_czk":  {"type": "integer", "description": "Cena v Kč (celé číslo)"},
            "hodnoceni": {"type": "number",  "description": "Hodnocení 0.0–5.0"},
            "dostupny":  {"type": "boolean", "description": "Je produkt skladem?"},
        },
        "required": ["nazev", "cena_czk", "hodnoceni", "dostupny"],
    },
}

SCHEMA_OSOBY: dict[str, Any] = {
    "name": "uloz_osoby",
    "description": "Extrahuje seznam osob z textu.",
    "input_schema": {
        "type": "object",
        "properties": {
            "osoby": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "jmeno":   {"type": "string"},
                        "vek":     {"type": "integer"},
                        "profese": {"type": "string"},
                    },
                    "required": ["jmeno"],
                },
            }
        },
        "required": ["osoby"],
    },
}


# ── Pomocná funkce: čištění JSONu z markdownu ─────────────────────────────────

def vycisti_json(raw: str) -> str:
    """Odstraní ```json ... ``` obaly a bílé znaky."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()


# ── Simulace LLM odpovědí (bez API) ──────────────────────────────────────────

@dataclass
class SimulovanaOdpoved:
    text: str
    typ: str = "text"   # "text" nebo "tool_use"
    tool_input: dict[str, Any] = field(default_factory=dict)


def simuluj_llm_produkt(popis: str) -> SimulovanaOdpoved:
    """Simuluje LLM odpověď — extrakce produktu z popisu."""
    # Jednoduché keyword-matching pro demo bez API
    cena_match = re.search(r"(\d[\d\s]*)\s*[Kk]č", popis)
    hodnoceni_match = re.search(r"(\d[,.]?\d?)\s*(?:hvězd|z 5|/5)", popis)
    dostupny = any(s in popis.lower() for s in ["skladem", "dostupný", "k dispozici"])

    nazev_candidates = re.findall(r'"([^"]+)"|([A-Z][a-zA-Z]+ (?:Pro|Plus|Max|Ultra|Basic))', popis)
    nazev = nazev_candidates[0][0] or nazev_candidates[0][1] if nazev_candidates else "Neznámý produkt"

    data: dict[str, Any] = {
        "nazev": nazev or "Demo produkt",
        "cena_czk": int(cena_match.group(1).replace(" ", "")) if cena_match else 999,
        "hodnoceni": float(hodnoceni_match.group(1).replace(",", ".")) if hodnoceni_match else 4.0,
        "dostupny": dostupny,
    }
    return SimulovanaOdpoved(
        text=json.dumps(data, ensure_ascii=False),
        typ="tool_use",
        tool_input=data,
    )


def simuluj_llm_osoby(text: str) -> SimulovanaOdpoved:
    """Simuluje LLM odpověď — extrakce osob z textu."""
    osoby = []
    # Hledáme vzor "Jméno Příjmení (věk) - profese"
    vzory = re.finditer(
        r"([A-ZÁÉÍÓÚŮŽ][a-záéíóúůž]+ [A-ZÁÉÍÓÚŮŽ][a-záéíóúůž]+)"
        r"(?:\s*\((\d+)\))?"
        r"(?:\s*[-–]\s*([^,.]+))?",
        text,
    )
    for m in vzory:
        osoby.append({
            "jmeno": m.group(1),
            "vek": int(m.group(2)) if m.group(2) else None,
            "profese": m.group(3).strip() if m.group(3) else None,
        })
    return SimulovanaOdpoved(
        text=json.dumps({"osoby": osoby}, ensure_ascii=False),
        typ="tool_use",
        tool_input={"osoby": osoby},
    )


# ── Strategie 1: Přímé instrukce ─────────────────────────────────────────────

def extrahuj_primy_prompt(popis: str, pouzit_api: bool = False) -> dict[str, Any] | None:
    """Strategie 1: systémový prompt instruuje formát."""
    if pouzit_api and os.environ.get("ANTHROPIC_API_KEY"):
        try:
            import anthropic
            klient = anthropic.Anthropic()
            r = klient.messages.create(
                model="claude-opus-4-5",
                max_tokens=512,
                system=(
                    'Vrať POUZE validní JSON objekt, žádný jiný text. '
                    'Schema: {"nazev": str, "cena_czk": int, "hodnoceni": float, "dostupny": bool}'
                ),
                messages=[{"role": "user", "content": popis}],
            )
            raw = vycisti_json(r.content[0].text)
            return json.loads(raw)
        except Exception as exc:
            print(f"  API chyba: {exc}")
            return None
    else:
        sim = simuluj_llm_produkt(popis)
        return json.loads(vycisti_json(sim.text))


# ── Strategie 2: Tool use ─────────────────────────────────────────────────────

def extrahuj_tool_use(popis: str, pouzit_api: bool = False) -> dict[str, Any] | None:
    """Strategie 2: vynucené tool use (nejspolehlivější)."""
    if pouzit_api and os.environ.get("ANTHROPIC_API_KEY"):
        try:
            import anthropic
            klient = anthropic.Anthropic()
            r = klient.messages.create(
                model="claude-opus-4-5",
                max_tokens=512,
                tools=[SCHEMA_PRODUKT],
                tool_choice={"type": "tool", "name": "uloz_produkt"},
                messages=[{"role": "user", "content": popis}],
            )
            blok = next(b for b in r.content if b.type == "tool_use")
            return blok.input
        except Exception as exc:
            print(f"  API chyba: {exc}")
            return None
    else:
        sim = simuluj_llm_produkt(popis)
        return sim.tool_input


# ── Strategie 3: Retry smyčka ─────────────────────────────────────────────────

def extrahuj_s_retry(
    popis: str,
    max_pokusu: int = 3,
    pouzit_api: bool = False,
) -> Produkt | None:
    """Strategie 3: retry s chybovou zpětnou vazbou."""
    posledni_chyba = ""
    dotaz = popis

    for pokus in range(1, max_pokusu + 1):
        if pokus > 1:
            dotaz = (
                f"{popis}\n\n"
                f"Předchozí odpověď nebyla validní: {posledni_chyba}\n"
                f"Vrať POUZE čistý JSON bez markdownu."
            )

        raw_data = extrahuj_primy_prompt(dotaz, pouzit_api)

        if raw_data is None:
            posledni_chyba = "Žádná odpověď"
            continue

        try:
            produkt = Produkt.z_dict(raw_data)
            print(f"    Pokus {pokus}/{max_pokusu}: OK")
            return produkt
        except (KeyError, ValueError, TypeError) as exc:
            posledni_chyba = str(exc)
            print(f"    Pokus {pokus}/{max_pokusu}: CHYBA — {exc}")
            if pokus < max_pokusu:
                time.sleep(0.5)

    return None


# ── Extrakce osob z textu ─────────────────────────────────────────────────────

def extrahuj_osoby(text: str, pouzit_api: bool = False) -> list[Osoba]:
    """Extrahuje osoby z textu pomocí tool use (nebo simulace)."""
    if pouzit_api and os.environ.get("ANTHROPIC_API_KEY"):
        try:
            import anthropic
            klient = anthropic.Anthropic()
            r = klient.messages.create(
                model="claude-opus-4-5",
                max_tokens=1024,
                tools=[SCHEMA_OSOBY],
                tool_choice={"type": "tool", "name": "uloz_osoby"},
                messages=[{"role": "user", "content": f"Extrahuj osoby:\n{text}"}],
            )
            data = next(b for b in r.content if b.type == "tool_use").input
            return [Osoba.z_dict(o) for o in data["osoby"]]
        except Exception as exc:
            print(f"  API chyba: {exc}")
            return []
    else:
        sim = simuluj_llm_osoby(text)
        return [Osoba.z_dict(o) for o in sim.tool_input.get("osoby", [])]


# ── Pydantic demo ─────────────────────────────────────────────────────────────

def demo_pydantic() -> None:
    print("\n=== Pydantic modely ===\n")

    if not PYDANTIC_OK:
        print("  pydantic není nainstalován. Spusť: pip install pydantic")
        print("  (Demo přeskočeno — použij dataclass verzi výše.)")
        return

    # Validní data
    raw = '{"nazev": "Widget Pro", "cena_czk": 299, "hodnoceni": 4.5, "dostupny": true}'
    p = ProduktPydantic.model_validate_json(raw)
    print(f"  Validní produkt: {p.nazev}, {p.cena_czk} Kč, ★{p.hodnoceni}")

    # Nevalidní data
    nevalidni_pripady = [
        '{"nazev": "", "cena_czk": 100, "hodnoceni": 3.0, "dostupny": true}',
        '{"nazev": "Test", "cena_czk": -50, "hodnoceni": 3.0, "dostupny": false}',
        '{"nazev": "Test", "cena_czk": 100, "hodnoceni": 9.9, "dostupny": false}',
    ]
    print("\n  Nevalidní vstupy:")
    for raw_bad in nevalidni_pripady:
        try:
            ProduktPydantic.model_validate_json(raw_bad)
        except Exception as exc:
            print(f"    {raw_bad[:50]}...")
            print(f"      → Chyba: {exc}")

    # Dump
    print(f"\n  model_dump():      {p.model_dump()}")
    print(f"  model_dump_json(): {p.model_dump_json()}")


# ── Demo: extrakce produktů ───────────────────────────────────────────────────

def demo_extrakce_produktu() -> None:
    pouzit_api = bool(os.environ.get("ANTHROPIC_API_KEY"))
    rezim = "reálné API" if pouzit_api else "simulace"
    print(f"\n=== Extrakce produktů ({rezim}) ===\n")

    popisy = [
        '"Widget Pro" je dostupný skladem za 1 299 Kč, hodnocení 4.7 z 5.',
        "Smartphone Galaxy Ultra (2 499 Kč) není momentálně k dispozici. Hodnocení 3.9/5.",
        "Sluchátka SoundMax Plus stojí 599 Kč, skladem, hvězdičky: 4.2 z 5.",
    ]

    print("  Strategie 1 (přímý prompt):")
    for popis in popisy[:2]:
        data = extrahuj_primy_prompt(popis, pouzit_api)
        print(f"    vstup: {popis[:50]}...")
        print(f"    výstup: {data}")

    print("\n  Strategie 2 (tool use):")
    for popis in popisy:
        data = extrahuj_tool_use(popis, pouzit_api)
        if data:
            try:
                p = Produkt.z_dict(data)
                print(f"    {p.nazev:25s} | {p.cena_czk:6d} Kč | ★{p.hodnoceni} | {'ano' if p.dostupny else 'ne'}")
            except ValueError as exc:
                print(f"    Validace selhala: {exc}")

    print("\n  Strategie 3 (retry smyčka):")
    produkt = extrahuj_s_retry(popisy[0], max_pokusu=3, pouzit_api=pouzit_api)
    if produkt:
        print(f"    Výsledek: {produkt}")
    else:
        print("    Extrakce selhala po všech pokusech.")


# ── Demo: extrakce osob ───────────────────────────────────────────────────────

def demo_extrakce_osob() -> None:
    pouzit_api = bool(os.environ.get("ANTHROPIC_API_KEY"))
    rezim = "reálné API" if pouzit_api else "simulace"
    print(f"\n=== Extrakce osob z textu ({rezim}) ===\n")

    texty = [
        "Na konferenci vystoupili Jan Novák (35) - programátor a Marie Svobodová (28) - designérka.",
        "Tým vedl Petr Dvořák (42) - projektový manažer. Pomáhala mu Jana Procházková - analytička.",
    ]

    for text in texty:
        print(f"  Text: {text}")
        osoby = extrahuj_osoby(text, pouzit_api)
        for o in osoby:
            vek_str = f", {o.vek} let" if o.vek else ""
            prof_str = f", {o.profese}" if o.profese else ""
            print(f"    → {o.jmeno}{vek_str}{prof_str}")
        print()


# ── Demo: čištění JSONu ───────────────────────────────────────────────────────

def demo_cisteni_json() -> None:
    print("\n=== Čištění JSON z markdownu ===\n")

    vzorky = [
        '```json\n{"nazev": "Test", "cena_czk": 100}\n```',
        '```\n{"nazev": "Test2", "cena_czk": 200}\n```',
        '{"nazev": "Test3", "cena_czk": 300}',
        '  \n{"nazev": "Test4", "cena_czk": 400}  \n',
    ]

    for vzor in vzorky:
        ocisteny = vycisti_json(vzor)
        data = json.loads(ocisteny)
        print(f"  vstup:  {repr(vzor[:50])}")
        print(f"  výstup: {data}\n")


# ── Demo: srovnání strategií ──────────────────────────────────────────────────

def demo_srovnani() -> None:
    print("\n=== Srovnání strategií ===\n")

    radky = [
        ("Přímý prompt",          "Střední",      "Nízká",   "Prototypy"),
        ("Tool use (schema)",     "Vysoká",       "Střední", "Produkce"),
        ("Tool use + Pydantic",   "Velmi vysoká", "Střední", "Typová bezpečnost"),
        ("Retry smyčka",          "Velmi vysoká", "Vyšší",   "Kritické pipelines"),
    ]
    hlavicka = f"  {'Strategie':<25} {'Spolehlivost':<16} {'Složitost':<12} Kdy použít"
    print(hlavicka)
    print("  " + "-" * 80)
    for radek in radky:
        print(f"  {radek[0]:<25} {radek[1]:<16} {radek[2]:<12} {radek[3]}")


# ── Hlavní funkce ─────────────────────────────────────────────────────────────

def main() -> None:
    demo_cisteni_json()
    demo_extrakce_produktu()
    demo_extrakce_osob()
    demo_pydantic()
    demo_srovnani()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "\nTip: Pro reálnou extrakci nastav ANTHROPIC_API_KEY "
            "a znovu spusť skript."
        )


if __name__ == "__main__":
    main()

```
