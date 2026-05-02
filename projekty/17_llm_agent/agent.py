"""
Projekt 17 — LLM Agent s nástroji

Autonomní agent který: vyhledává lekce, spouští Python kód,
počítá matematiku, odpovídá na otázky o kurzu.

Spuštění:
    uv add anthropic
    export ANTHROPIC_API_KEY=sk-ant-...
    python projekty/17_llm_agent/agent.py
"""

import subprocess
import sys
import json
import math
import re
from pathlib import Path
from typing import Callable, Any

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

BASE_DIR = Path(__file__).parent.parent.parent

# ── Nástroje ──────────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "hledej_lekci",
        "description": "Vyhledá lekce v kurzu Python podle klíčového slova",
        "input_schema": {
            "type": "object",
            "properties": {
                "dotaz": {"type": "string", "description": "Hledané slovo nebo téma"},
                "limit": {"type": "integer", "default": 3},
            },
            "required": ["dotaz"],
        },
    },
    {
        "name": "cti_lekci",
        "description": "Přečte obsah konkrétní lekce (prvních 2000 znaků)",
        "input_schema": {
            "type": "object",
            "properties": {
                "cislo": {"type": "integer", "description": "Číslo lekce"},
            },
            "required": ["cislo"],
        },
    },
    {
        "name": "spust_python",
        "description": "Spustí Python kód a vrátí výstup (max 10s)",
        "input_schema": {
            "type": "object",
            "properties": {
                "kod": {"type": "string", "description": "Python kód"},
            },
            "required": ["kod"],
        },
    },
    {
        "name": "vypocitej",
        "description": "Vyhodnotí matematický výraz (bezpečně)",
        "input_schema": {
            "type": "object",
            "properties": {
                "vraz": {"type": "string", "description": "Matematický výraz"},
            },
            "required": ["vraz"],
        },
    },
    {
        "name": "statistiky_kurzu",
        "description": "Vrátí statistiky kurzu (počet lekcí, programů, projektů)",
        "input_schema": {"type": "object", "properties": {}},
    },
]


# ── Implementace nástrojů ─────────────────────────────────────────────────────

def hledej_lekci(dotaz: str, limit: int = 3) -> str:
    lekce_dir = BASE_DIR / "lekce"
    vysledky = []
    for f in sorted(lekce_dir.glob("[0-9]*.md")):
        try:
            obsah = f.read_text(encoding="utf-8", errors="ignore")
            if dotaz.lower() in obsah.lower():
                prvni = obsah.splitlines()[0]
                nazev = prvni[2:].strip() if prvni.startswith("# ") else f.stem
                vysledky.append(f"- {f.stem}: {nazev}")
                if len(vysledky) >= limit:
                    break
        except Exception:
            continue
    if not vysledky:
        return f"Nenalezeny lekce pro '{dotaz}'"
    return f"Nalezeno {len(vysledky)} lekcí pro '{dotaz}':\n" + "\n".join(vysledky)


def cti_lekci(cislo: int) -> str:
    lekce_dir = BASE_DIR / "lekce"
    candidates = (list(lekce_dir.glob(f"{cislo:02d}_*.md")) +
                  list(lekce_dir.glob(f"{cislo}_*.md")))
    if not candidates:
        return f"Lekce {cislo} nenalezena"
    return candidates[0].read_text(encoding="utf-8")[:2000] + "\n[...zkráceno...]"


def spust_python(kod: str) -> str:
    try:
        result = subprocess.run(
            [sys.executable, "-c", kod],
            capture_output=True, text=True, timeout=10,
            cwd=str(BASE_DIR),
        )
        return result.stdout or result.stderr or "(žádný výstup)"
    except subprocess.TimeoutExpired:
        return "Timeout (>10s)"
    except Exception as e:
        return f"Chyba: {e}"


def vypocitej(vraz: str) -> str:
    allowed = {k: v for k, v in vars(math).items() if not k.startswith("_")}
    allowed["abs"] = abs
    try:
        return str(eval(vraz, {"__builtins__": {}}, allowed))
    except Exception as e:
        return f"Chyba: {e}"


def statistiky_kurzu() -> str:
    lekce = len(list((BASE_DIR / "lekce").glob("[0-9]*.md")))
    programy = len(list((BASE_DIR / "programy").glob("l*.py")))
    projekty = len([d for d in (BASE_DIR / "projekty").iterdir() if d.is_dir()])
    return json.dumps({"lekce": lekce, "programy": programy, "projekty": projekty})


TOOL_IMPL: dict[str, Callable] = {
    "hledej_lekci": hledej_lekci,
    "cti_lekci": cti_lekci,
    "spust_python": spust_python,
    "vypocitej": vypocitej,
    "statistiky_kurzu": statistiky_kurzu,
}


# ── Agent loop ────────────────────────────────────────────────────────────────

def run_agent(dotaz: str, verbose: bool = True) -> str:
    if not ANTHROPIC_AVAILABLE:
        return "Nainstaluj: uv add anthropic"

    client = anthropic.Anthropic()
    zpravy = [{"role": "user", "content": dotaz}]

    if verbose:
        print(f"\n[Agent] Dotaz: {dotaz}")

    for kolo in range(10):  # max 10 kol
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2000,
            system="""Jsi asistent pro kurz Python: From Zero to Hero.
Máš přístup k nástrojům pro vyhledávání lekcí, spouštění kódu a počítání.
Odpovídej v češtině. Použij nástroje pro konkrétní informace.""",
            tools=TOOLS,
            messages=zpravy,
        )

        zpravy.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Finální odpověď
            text = next((b.text for b in response.content if hasattr(b, "text")), "")
            if verbose:
                print(f"[Agent] Odpověď: {text}")
            return text

        # Zpracuj tool calls
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                if verbose:
                    print(f"[Agent] Volám nástroj: {block.name}({block.input})")
                fn = TOOL_IMPL.get(block.name)
                if fn:
                    try:
                        result = fn(**block.input)
                    except Exception as e:
                        result = f"Chyba nástroje: {e}"
                else:
                    result = f"Neznámý nástroj: {block.name}"
                if verbose:
                    print(f"[Agent] Výsledek: {str(result)[:200]}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })

        if tool_results:
            zpravy.append({"role": "user", "content": tool_results})

    return "Max kol překročeno"


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  🤖 LLM Agent — Python Kurz Asistent")
    print("=" * 55)

    if not ANTHROPIC_AVAILABLE:
        print("Nainstaluj: uv add anthropic")
        print("Export: export ANTHROPIC_API_KEY=sk-ant-...")
        print("\nDemo bez API (simulace):")
        print(f"  Statistiky: {statistiky_kurzu()}")
        print(f"  Vyhledávání 'asyncio': {hledej_lekci('asyncio')}")
        print(f"  Výpočet: {vypocitej('2**10 + math.pi')}")
        return

    import os
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Nastav: export ANTHROPIC_API_KEY=sk-ant-...")
        return

    dotazy = [
        "Kolik lekcí má kurz a co pokrývá?",
        "Najdi lekce o asyncio a spusť ukázku async kódu",
        "Spočítej sumu prvočísel do 100",
    ]

    for dotaz in dotazy:
        print(f"\n{'='*50}")
        run_agent(dotaz)


if __name__ == "__main__":
    main()
