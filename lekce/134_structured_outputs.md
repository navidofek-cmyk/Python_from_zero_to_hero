# Lekce 134: Structured Outputs — Strukturovaný výstup z LLM

## Proč strukturovaný výstup?

LLM generují volný text — ale aplikace potřebují data v pevné struktuře (JSON, Python objekty). Cílem je donutit model vrátit **validní, parsovatelný výstup** bez nutnosti složitého čištění textu.

```
Nestrukturovaný výstup:
  "Produkt se jmenuje Widget Pro, stojí 299 Kč a má hodnocení 4.5 hvězdičky."

Strukturovaný výstup:
  {"nazev": "Widget Pro", "cena_czk": 299, "hodnoceni": 4.5}
```

---

## Strategie 1: Přímé instrukce v promptu

Nejjednodušší přístup — popros model v systémovém promptu:

```python
import anthropic, json

klient = anthropic.Anthropic()

def extrahuj_produkt(popis: str) -> dict:
    odpoved = klient.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        system=(
            "Vrať POUZE validní JSON objekt, žádný jiný text. "
            "Schema: {\"nazev\": str, \"cena_czk\": int, \"hodnoceni\": float}"
        ),
        messages=[{"role": "user", "content": popis}],
    )
    return json.loads(odpoved.content[0].text)
```

Nevýhoda: model může přidat komentář nebo obalit JSON do Markdownu (` ```json ... ``` `).

---

## Strategie 2: Tool use jako JSON schema

Spolehlivější způsob — definuj nástroj s požadovaným schématem. Model **musí** zavolat nástroj, aby odpověděl.

```python
SCHEMA = {
    "name": "uloz_produkt",
    "description": "Uloží extrahovaná data o produktu.",
    "input_schema": {
        "type": "object",
        "properties": {
            "nazev":     {"type": "string",  "description": "Název produktu"},
            "cena_czk":  {"type": "integer", "description": "Cena v Kč"},
            "hodnoceni": {"type": "number",  "description": "Hodnocení 0–5"},
            "dostupny":  {"type": "boolean", "description": "Skladová dostupnost"},
        },
        "required": ["nazev", "cena_czk", "hodnoceni", "dostupny"],
    },
}

def extrahuj_tool_use(popis: str) -> dict:
    r = klient.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        tools=[SCHEMA],
        tool_choice={"type": "tool", "name": "uloz_produkt"},  # vynuť volání
        messages=[{"role": "user", "content": popis}],
    )
    tool_blok = next(b for b in r.content if b.type == "tool_use")
    return tool_blok.input  # vždy dict odpovídající schématu
```

`tool_choice={"type": "tool", "name": "..."}` — **nutí** model zavolat konkrétní nástroj.

---

## Strategie 3: Pydantic modely + validace

Pydantic zajistí **typovou bezpečnost a validaci** dat po parsování:

```python
from pydantic import BaseModel, Field, field_validator
import json

class Produkt(BaseModel):
    nazev: str
    cena_czk: int = Field(gt=0, description="Cena musí být kladná")
    hodnoceni: float = Field(ge=0.0, le=5.0)
    dostupny: bool

    @field_validator("nazev")
    @classmethod
    def nazev_neprazdny(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Název nesmí být prázdný.")
        return v.strip()

# Parsování z JSON stringu
raw = '{"nazev": "Widget Pro", "cena_czk": 299, "hodnoceni": 4.5, "dostupny": true}'
produkt = Produkt.model_validate_json(raw)
print(produkt.nazev)     # "Widget Pro"
print(produkt.cena_czk)  # 299

# Zpět na dict / JSON
print(produkt.model_dump())
print(produkt.model_dump_json())
```

---

## Retry při chybě parsování

LLM může občas vrátit neplatný JSON. Správný pattern:

```python
import json, time

def extrahuj_s_retry(text: str, model: Produkt, max_pokusu: int = 3) -> Produkt | None:
    posledni_chyba = ""

    for pokus in range(1, max_pokusu + 1):
        prompt = text if pokus == 1 else (
            f"{text}\n\n"
            f"Předchozí odpověď nebyla validní JSON: {posledni_chyba}\n"
            f"Oprav ji a vrať pouze čistý JSON objekt."
        )

        r = klient.messages.create(
            model="claude-opus-4-5", max_tokens=512,
            system="Vrať POUZE validní JSON, bez markdownu.",
            messages=[{"role": "user", "content": prompt}],
        )
        raw = r.content[0].text.strip()
        # Odstraní případné ```json ... ``` obaly
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        try:
            return Produkt.model_validate_json(raw)
        except Exception as e:
            posledni_chyba = str(e)
            print(f"  Pokus {pokus}/{max_pokusu} selhal: {e}")
            if pokus < max_pokusu:
                time.sleep(1)

    return None
```

---

## Extrakce strukturovaných dat z textu

Praktický příklad: extrakce více entit z volného textu.

```python
from pydantic import BaseModel
from typing import Optional

class Osoba(BaseModel):
    jmeno: str
    vek: Optional[int] = None
    profese: Optional[str] = None

class SeznamOsob(BaseModel):
    osoby: list[Osoba]

SCHEMA_OSOB = {
    "name": "uloz_osoby",
    "description": "Extrahuje osoby z textu.",
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

def extrahuj_osoby(text: str) -> SeznamOsob:
    r = klient.messages.create(
        model="claude-opus-4-5", max_tokens=1024,
        tools=[SCHEMA_OSOB],
        tool_choice={"type": "tool", "name": "uloz_osoby"},
        messages=[{"role": "user", "content": f"Extrahuj osoby z textu:\n{text}"}],
    )
    data = next(b for b in r.content if b.type == "tool_use").input
    return SeznamOsob.model_validate(data)
```

---

## Vnořené struktury a diskriminované unions

```python
from typing import Literal, Union
from pydantic import BaseModel

class KreditniKarta(BaseModel):
    typ: Literal["kreditni_karta"]
    cislo_posledni_4: str

class BankovniPrevod(BaseModel):
    typ: Literal["bankovni_prevod"]
    iban: str

class Hotovost(BaseModel):
    typ: Literal["hotovost"]

Platba = Union[KreditniKarta, BankovniPrevod, Hotovost]

class Objednavka(BaseModel):
    id: str
    castka_czk: float
    platba: Platba  # Pydantic automaticky vybere správný typ

# Parsování:
raw = '{"id": "OBJ-001", "castka_czk": 1299.0, "platba": {"typ": "kreditni_karta", "cislo_posledni_4": "4242"}}'
obj = Objednavka.model_validate_json(raw)
assert obj.platba.typ == "kreditni_karta"
```

---

## Srovnání strategií

| Strategie | Spolehlivost | Složitost | Kdy použít |
|-----------|-------------|-----------|-----------|
| Prompt instrukce | Střední | Nízká | Prototypy, jednoduchý JSON |
| Tool use (schema) | Vysoká | Střední | Produkce, komplexní schémata |
| Tool use + Pydantic | Velmi vysoká | Střední | Typová bezpečnost + validace |
| Retry smyčka | Velmi vysoká | Vyšší | Kritické pipelines, high accuracy |

---

## Shrnutí

- **Přímé instrukce** v promptu jsou nejjednodušší, ale nespolehlivé
- **Tool use** s `tool_choice` nutí model vrátit přesně definovanou strukturu
- **Pydantic** zajišťuje typovou bezpečnost a validaci po parsování
- **Retry smyčka** s chybovou zpětnou vazbou dramaticky zvyšuje spolehlivost
- Vždy odstraňuj markdown obaly (` ```json `) před parsováním

---

## Cvičení

1. Vytvoř Pydantic model `Faktura` s položkami (`polozky: list[Polozka]`) a validuj celkovou cenu (součet položek).
2. Implementuj extrakci strukturovaných dat z recenzí e-shopu: `{"produkt": str, "hodnoceni": 1-5, "klady": list[str], "zapory": list[str]}`.
3. Přidej do retry smyčky exponenciální back-off (`time.sleep(2 ** pokus)`).
4. Napiš funkci `extrahuj_nebo_vychozi(text, model, vychozi)`, která vrátí výchozí hodnotu, pokud parsování selže po všech pokusech.
5. Vytvoř pipeline: načti CSV s popisky produktů, extrahuj strukturovaná data pro každý řádek, ulož výsledky do SQLite.
