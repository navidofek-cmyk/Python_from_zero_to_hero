# Program — Lekce 132: Lekce 132: AI Agenti — LLM + nástroje + smyčka

Patří k lekci [Lekce 132: AI Agenti — LLM + nástroje + smyčka](../132_ai_agents.md).

## Jak spustit

```bash
python3 programy/l132_ai_agents.py
```

## Zdrojový kód

### `l132_ai_agents.py`

```py
"""Lekce 132 — AI Agenti (LLM + nástroje + smyčka)."""

from __future__ import annotations

import json
import math
import os
import random
from dataclasses import dataclass, field
from typing import Any

# ── Definice nástrojů (JSON schema pro Anthropic API) ────────────────────────

SCHEMA_NASTROJU: list[dict[str, Any]] = [
    {
        "name": "kalkulator",
        "description": (
            "Vypočítá matematický výraz zadaný jako string. "
            "Podporuje: +, -, *, /, **, sqrt(), abs(), round()."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "vyraz": {
                    "type": "string",
                    "description": "Matematický výraz, např. '2 ** 10' nebo 'sqrt(144)'.",
                }
            },
            "required": ["vyraz"],
        },
    },
    {
        "name": "pocasi",
        "description": "Vrátí aktuální (simulované) počasí pro zadané město.",
        "input_schema": {
            "type": "object",
            "properties": {
                "mesto": {
                    "type": "string",
                    "description": "Název města, např. 'Praha'.",
                }
            },
            "required": ["mesto"],
        },
    },
    {
        "name": "preved_meny",
        "description": "Převede částku z jedné měny do druhé (pevný simulovaný kurz).",
        "input_schema": {
            "type": "object",
            "properties": {
                "castka": {"type": "number", "description": "Částka k převodu."},
                "z_meny": {"type": "string", "description": "Zdrojová měna (CZK, EUR, USD)."},
                "na_menu": {"type": "string", "description": "Cílová měna (CZK, EUR, USD)."},
            },
            "required": ["castka", "z_meny", "na_menu"],
        },
    },
]

# ── Implementace nástrojů ─────────────────────────────────────────────────────

POCASI_DATA: dict[str, tuple[int, str]] = {
    "Praha": (18, "oblačno"),
    "Brno": (16, "slunečno"),
    "Ostrava": (13, "déšť"),
    "Plzeň": (17, "polojasno"),
    "Liberec": (11, "mlha"),
}

KURZY: dict[tuple[str, str], float] = {
    ("CZK", "EUR"): 0.04,
    ("EUR", "CZK"): 25.0,
    ("CZK", "USD"): 0.043,
    ("USD", "CZK"): 23.2,
    ("EUR", "USD"): 1.08,
    ("USD", "EUR"): 0.93,
}


def nastroj_kalkulator(vyraz: str) -> str:
    """Bezpečně vyhodnotí matematický výraz."""
    povolene = {
        "abs": abs,
        "round": round,
        "sqrt": math.sqrt,
        "pi": math.pi,
        "e": math.e,
    }
    try:
        vysledek = eval(vyraz, {"__builtins__": {}}, povolene)  # noqa: S307
        return f"{vysledek}"
    except Exception as chyba:
        return f"Chyba výpočtu: {chyba}"


def nastroj_pocasi(mesto: str) -> str:
    """Vrátí simulované počasí."""
    if mesto in POCASI_DATA:
        teplota, popis = POCASI_DATA[mesto]
    else:
        teplota = random.randint(8, 28)
        popis = random.choice(["slunečno", "oblačno", "déšť", "polojasno"])
    return f"{teplota} °C, {popis}"


def nastroj_preved_meny(castka: float, z_meny: str, na_menu: str) -> str:
    """Převede měnu pomocí pevného simulovaného kurzu."""
    z_meny = z_meny.upper()
    na_menu = na_menu.upper()
    if z_meny == na_menu:
        return f"{castka:.2f} {na_menu}"
    kurz = KURZY.get((z_meny, na_menu))
    if kurz is None:
        return f"Neznámý kurz {z_meny} → {na_menu}."
    vysledek = castka * kurz
    return f"{castka:.2f} {z_meny} = {vysledek:.2f} {na_menu} (kurz {kurz})"


def zavolej_nastroj(nazev: str, vstup: dict[str, Any]) -> str:
    """Dispečer nástrojů — přesměruje volání na správnou funkci."""
    if nazev == "kalkulator":
        return nastroj_kalkulator(vstup["vyraz"])
    if nazev == "pocasi":
        return nastroj_pocasi(vstup["mesto"])
    if nazev == "preved_meny":
        return nastroj_preved_meny(
            vstup["castka"], vstup["z_meny"], vstup["na_menu"]
        )
    return f"Neznámý nástroj: {nazev}"


# ── Simulace agenta bez API ───────────────────────────────────────────────────

@dataclass
class SimulovanyKrok:
    thought: str
    action: str | None = None
    action_input: dict[str, Any] | None = None
    observation: str | None = None
    final_answer: str | None = None


def simuluj_react_smycku(dotaz: str) -> list[SimulovanyKrok]:
    """
    Ručně simuluje ReAct smyčku pro demonstrační účely
    (bez volání skutečného API).
    """
    kroky: list[SimulovanyKrok] = []

    # Krok 1: kalkulátor
    krok1 = SimulovanyKrok(
        thought="Dotaz obsahuje matematický výraz. Zavolám kalkulátor.",
        action="kalkulator",
        action_input={"vyraz": "17 * 23"},
    )
    krok1.observation = zavolej_nastroj("kalkulator", {"vyraz": "17 * 23"})
    kroky.append(krok1)

    # Krok 2: počasí
    krok2 = SimulovanyKrok(
        thought="Teď potřebuji počasí v Brně. Zavolám nástroj pocasi.",
        action="pocasi",
        action_input={"mesto": "Brno"},
    )
    krok2.observation = zavolej_nastroj("pocasi", {"mesto": "Brno"})
    kroky.append(krok2)

    # Krok 3: závěr
    krok3 = SimulovanyKrok(
        thought="Mám obě informace. Sestavím odpověď.",
        final_answer=(
            f"17 × 23 = {krok1.observation}. "
            f"Počasí v Brně: {krok2.observation}."
        ),
    )
    kroky.append(krok3)

    return kroky


def vytiskni_react_kroky(kroky: list[SimulovanyKrok]) -> None:
    print("\n--- ReAct smyčka (simulace) ---")
    for i, krok in enumerate(kroky, 1):
        print(f"\n[Krok {i}]")
        print(f"  Thought   : {krok.thought}")
        if krok.action:
            print(f"  Action    : {krok.action}({json.dumps(krok.action_input, ensure_ascii=False)})")
        if krok.observation:
            print(f"  Observation: {krok.observation}")
        if krok.final_answer:
            print(f"  >>> Final Answer: {krok.final_answer}")


# ── Agent s reálným Anthropic API ────────────────────────────────────────────

@dataclass
class LogKroku:
    cislo: int
    typ: str          # "tool_call" nebo "final"
    detail: str


def spust_agenta_s_api(dotaz: str, verbose: bool = True) -> str:
    """
    Spustí agenta s reálným Anthropic API.
    Vyžaduje ANTHROPIC_API_KEY v prostředí.
    """
    try:
        import anthropic
    except ImportError:
        return "anthropic SDK není nainstalováno. Spusť: pip install anthropic"

    api_klic = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_klic:
        return "Chybí ANTHROPIC_API_KEY v prostředí."

    klient = anthropic.Anthropic(api_key=api_klic)
    zpravy: list[dict[str, Any]] = [{"role": "user", "content": dotaz}]
    log: list[LogKroku] = []
    cislo_kroku = 0

    for _ in range(10):  # ochrana proti nekonečné smyčce
        cislo_kroku += 1
        odpoved = klient.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            tools=SCHEMA_NASTROJU,
            messages=zpravy,
        )
        zpravy.append({"role": "assistant", "content": odpoved.content})

        if odpoved.stop_reason == "end_turn":
            text = next(
                (b.text for b in odpoved.content if hasattr(b, "text")), ""
            )
            log.append(LogKroku(cislo_kroku, "final", text))
            if verbose:
                _vytiskni_log(log)
            return text

        if odpoved.stop_reason == "tool_use":
            vysledky: list[dict[str, Any]] = []
            for blok in odpoved.content:
                if blok.type == "tool_use":
                    vysledek = zavolej_nastroj(blok.name, blok.input)
                    log.append(
                        LogKroku(
                            cislo_kroku,
                            "tool_call",
                            f"{blok.name}({blok.input}) → {vysledek}",
                        )
                    )
                    vysledky.append({
                        "type": "tool_result",
                        "tool_use_id": blok.id,
                        "content": vysledek,
                    })
            zpravy.append({"role": "user", "content": vysledky})

    return "Překročen maximální počet kroků agenta."


def _vytiskni_log(log: list[LogKroku]) -> None:
    print("\n--- Log agenta ---")
    for krok in log:
        znacka = "TOOL" if krok.typ == "tool_call" else "DONE"
        print(f"  [{krok.cislo}] {znacka}: {krok.detail}")


# ── Demo bez API ──────────────────────────────────────────────────────────────

def demo_nastroje() -> None:
    print("=== Demo jednotlivých nástrojů ===\n")

    vyrazy = ["2 ** 10", "sqrt(144)", "17 * 23 + 5", "round(3.14159, 2)"]
    print("Kalkulátor:")
    for v in vyrazy:
        print(f"  {v!r:30s} → {nastroj_kalkulator(v)}")

    print("\nPočasí:")
    for mesto in ["Praha", "Brno", "Ostrava", "Tokio"]:
        print(f"  {mesto:12s} → {nastroj_pocasi(mesto)}")

    print("\nPřevod měn:")
    prevody = [
        (1000, "CZK", "EUR"),
        (50, "EUR", "CZK"),
        (100, "USD", "CZK"),
    ]
    for castka, z_m, na_m in prevody:
        print(f"  {castka} {z_m} → {na_m}: {nastroj_preved_meny(castka, z_m, na_m)}")


def demo_react() -> None:
    print("\n=== Demo ReAct smyčky (simulace bez API) ===")
    dotaz = "Kolik je 17 * 23? A jaké je počasí v Brně?"
    print(f"Dotaz: {dotaz!r}")
    kroky = simuluj_react_smycku(dotaz)
    vytiskni_react_kroky(kroky)


def demo_api_agent() -> None:
    print("\n=== Agent s Anthropic API ===")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("  (přeskočeno — ANTHROPIC_API_KEY není nastaven)")
        print("  Nastav proměnnou a znovu spusť pro reálnou demonstraci.")
        return
    dotazy = [
        "Kolik je 123 * 456? A jaké je počasí v Praze a Ostravě?",
        "Převeď 5000 CZK na EUR a EUR na USD.",
    ]
    for dotaz in dotazy:
        print(f"\nDotaz: {dotaz!r}")
        odpoved = spust_agenta_s_api(dotaz)
        print(f"Odpověď: {odpoved}")


# ── Hlavní funkce ─────────────────────────────────────────────────────────────

def main() -> None:
    demo_nastroje()
    demo_react()
    demo_api_agent()


if __name__ == "__main__":
    main()

```
