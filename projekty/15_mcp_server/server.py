"""
Projekt 15 — Python Kurz MCP Server

Plnohodnotný MCP server pro kurz Python: From Zero to Hero.
Claude (nebo jiný AI asistent) může:
  - Vyhledávat lekce fulltextem
  - Číst obsah lekcí
  - Spouštět Python programy z kurzu
  - Zobrazit statistiky kurzu
  - Doporučit lekce podle tématu

Instalace:
    uv add mcp

Spuštění (stdio):
    python server.py

Konfigurace Claude Desktop (~/.claude/claude_desktop_config.json):
    {
      "mcpServers": {
        "python-kurz": {
          "command": "python",
          "args": ["/absolutni/cesta/k/projekty/15_mcp_server/server.py"]
        }
      }
    }
"""

import asyncio
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool, TextContent, Resource, ResourceContents,
        Prompt, PromptMessage, PromptArgument,
    )
except ImportError:
    print("Nainstaluj mcp: uv add mcp", file=sys.stderr)
    sys.exit(1)

# ── Cesty ──────────────────────────────────────────────────────────────────

BASE = Path(__file__).parent.parent.parent
LEKCE_DIR = BASE / "lekce"
PROGRAMY_DIR = BASE / "programy"

# ── Server ─────────────────────────────────────────────────────────────────

server = Server("python-kurz")


# ── Pomocné funkce ─────────────────────────────────────────────────────────

def nacti_lekce() -> list[dict]:
    lekce = []
    for f in sorted(LEKCE_DIR.glob("[0-9]*.md")):
        m = re.match(r"^(\d+)_(.*)", f.stem)
        if not m:
            continue
        cislo = int(m.group(1))
        try:
            prvni_radek = f.read_text(encoding="utf-8").splitlines()[0]
            nazev = prvni_radek[2:].strip() if prvni_radek.startswith("# ") else f.stem
        except Exception:
            nazev = f.stem
        lekce.append({"cislo": cislo, "nazev": nazev, "soubor": f.name})
    return lekce


def nacti_programy() -> list[dict]:
    programy = []
    for f in sorted(PROGRAMY_DIR.glob("l*.py")):
        m = re.match(r"^l(\d+)_(.*)", f.stem)
        if not m:
            continue
        cislo = int(m.group(1))
        programy.append({"cislo": cislo, "soubor": f.name, "cesta": str(f)})
    return programy


def hledej_v_lekcich(dotaz: str, limit: int = 5) -> list[dict]:
    dotaz_lower = dotaz.lower()
    vysledky = []
    for f in sorted(LEKCE_DIR.glob("[0-9]*.md")):
        try:
            text = f.read_text(encoding="utf-8")
            if dotaz_lower in text.lower():
                m = re.match(r"^(\d+)_(.*)", f.stem)
                if not m:
                    continue
                cislo = int(m.group(1))
                prvni = text.splitlines()[0]
                nazev = prvni[2:].strip() if prvni.startswith("# ") else f.stem
                # Najdi kontext kolem výskytu
                pos = text.lower().find(dotaz_lower)
                snippet = text[max(0, pos-100):pos+150].replace("\n", " ").strip()
                vysledky.append({
                    "cislo": cislo,
                    "nazev": nazev,
                    "soubor": f.name,
                    "snippet": snippet,
                })
        except Exception:
            continue
        if len(vysledky) >= limit:
            break
    return vysledky


# ── Resources ─────────────────────────────────────────────────────────────

@server.list_resources()
async def list_resources() -> list[Resource]:
    zdroje = [
        Resource(
            uri="kurz://statistiky",
            name="Statistiky kurzu",
            description="Celkové statistiky kurzu (počet lekcí, programů, projektů)",
            mimeType="application/json",
        ),
        Resource(
            uri="kurz://lekce/seznam",
            name="Seznam všech lekcí",
            description="Kompletní seznam lekcí s čísly a názvy",
            mimeType="application/json",
        ),
        Resource(
            uri="kurz://programy/seznam",
            name="Seznam všech programů",
            description="Kompletní seznam Python programů ke stažení",
            mimeType="application/json",
        ),
    ]
    # Přidej jednotlivé lekce jako resources
    for lekce in nacti_lekce()[:20]:  # prvních 20
        zdroje.append(Resource(
            uri=f"kurz://lekce/{lekce['cislo']}",
            name=f"Lekce {lekce['cislo']}: {lekce['nazev']}",
            description=f"Obsah lekce {lekce['cislo']}",
            mimeType="text/markdown",
        ))
    return zdroje


@server.read_resource()
async def read_resource(uri: str) -> ResourceContents:
    if uri == "kurz://statistiky":
        lekce = nacti_lekce()
        programy = nacti_programy()
        projekty = list((BASE / "projekty").iterdir()) if (BASE / "projekty").exists() else []
        stats = {
            "lekce": len(lekce),
            "programy": len(programy),
            "projekty": len([p for p in projekty if p.is_dir()]),
            "posledni_lekce": lekce[-1]["nazev"] if lekce else None,
        }
        return ResourceContents(uri=uri, mimeType="application/json",
                                text=json.dumps(stats, ensure_ascii=False, indent=2))

    if uri == "kurz://lekce/seznam":
        return ResourceContents(uri=uri, mimeType="application/json",
                                text=json.dumps(nacti_lekce(), ensure_ascii=False, indent=2))

    if uri == "kurz://programy/seznam":
        return ResourceContents(uri=uri, mimeType="application/json",
                                text=json.dumps(nacti_programy(), ensure_ascii=False, indent=2))

    # Jednotlivá lekce
    m = re.match(r"kurz://lekce/(\d+)$", uri)
    if m:
        cislo = int(m.group(1))
        candidates = list(LEKCE_DIR.glob(f"{cislo:02d}_*.md")) + list(LEKCE_DIR.glob(f"{cislo}_*.md"))
        if candidates:
            obsah = candidates[0].read_text(encoding="utf-8")
            return ResourceContents(uri=uri, mimeType="text/markdown", text=obsah)

    raise ValueError(f"Neznámý resource: {uri}")


# ── Tools ──────────────────────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="hledej_lekci",
            description="Vyhledá lekce podle klíčového slova nebo tématu",
            inputSchema={
                "type": "object",
                "properties": {
                    "dotaz": {"type": "string", "description": "Hledané téma nebo klíčové slovo"},
                    "limit": {"type": "integer", "description": "Max počet výsledků", "default": 5},
                },
                "required": ["dotaz"],
            },
        ),
        Tool(
            name="cti_lekci",
            description="Přečte kompletní obsah konkrétní lekce",
            inputSchema={
                "type": "object",
                "properties": {
                    "cislo": {"type": "integer", "description": "Číslo lekce (1-172)"},
                },
                "required": ["cislo"],
            },
        ),
        Tool(
            name="cti_program",
            description="Přečte zdrojový kód programu ke konkrétní lekci",
            inputSchema={
                "type": "object",
                "properties": {
                    "cislo": {"type": "integer", "description": "Číslo lekce"},
                },
                "required": ["cislo"],
            },
        ),
        Tool(
            name="spust_program",
            description="Spustí Python program ze kurzu a vrátí výstup",
            inputSchema={
                "type": "object",
                "properties": {
                    "cislo": {"type": "integer", "description": "Číslo lekce"},
                    "timeout": {"type": "integer", "description": "Timeout v sekundách", "default": 10},
                },
                "required": ["cislo"],
            },
        ),
        Tool(
            name="statistiky",
            description="Zobrazí statistiky kurzu",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="doporuc_lekce",
            description="Doporučí lekce pro danou úroveň nebo téma",
            inputSchema={
                "type": "object",
                "properties": {
                    "uroven": {
                        "type": "string",
                        "enum": ["zacatecnik", "junior", "intermediate", "senior"],
                        "description": "Úroveň studenta",
                    },
                    "tema": {"type": "string", "description": "Volitelné téma zájmu"},
                },
                "required": ["uroven"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:

    if name == "hledej_lekci":
        dotaz = arguments["dotaz"]
        limit = arguments.get("limit", 5)
        vysledky = hledej_v_lekcich(dotaz, limit)
        if not vysledky:
            return [TextContent(type="text", text=f"Žádné lekce nenalezeny pro '{dotaz}'")]
        text = f"Nalezeno {len(vysledky)} lekcí pro '{dotaz}':\n\n"
        for v in vysledky:
            text += f"**Lekce {v['cislo']}: {v['nazev']}**\n"
            text += f"  ...{v['snippet']}...\n\n"
        return [TextContent(type="text", text=text)]

    elif name == "cti_lekci":
        cislo = arguments["cislo"]
        candidates = (list(LEKCE_DIR.glob(f"{cislo:02d}_*.md")) +
                      list(LEKCE_DIR.glob(f"{cislo:03d}_*.md")) +
                      list(LEKCE_DIR.glob(f"{cislo}_*.md")))
        candidates = [f for f in candidates if f.parent == LEKCE_DIR]
        if not candidates:
            return [TextContent(type="text", text=f"Lekce {cislo} nenalezena")]
        obsah = candidates[0].read_text(encoding="utf-8")
        return [TextContent(type="text", text=obsah)]

    elif name == "cti_program":
        cislo = arguments["cislo"]
        candidates = (list(PROGRAMY_DIR.glob(f"l{cislo:02d}_*.py")) +
                      list(PROGRAMY_DIR.glob(f"l{cislo}_*.py")))
        if not candidates:
            return [TextContent(type="text", text=f"Program pro lekci {cislo} nenalezen")]
        kod = candidates[0].read_text(encoding="utf-8")
        return [TextContent(type="text", text=f"```python\n{kod}\n```")]

    elif name == "spust_program":
        cislo = arguments["cislo"]
        timeout = arguments.get("timeout", 10)
        candidates = (list(PROGRAMY_DIR.glob(f"l{cislo:02d}_*.py")) +
                      list(PROGRAMY_DIR.glob(f"l{cislo}_*.py")))
        if not candidates:
            return [TextContent(type="text", text=f"Program pro lekci {cislo} nenalezen")]
        try:
            result = subprocess.run(
                [sys.executable, str(candidates[0])],
                capture_output=True, text=True, timeout=timeout,
                cwd=str(BASE),
            )
            vystup = result.stdout or "(žádný výstup)"
            if result.stderr:
                vystup += f"\n\nSTDERR:\n{result.stderr[:500]}"
            return [TextContent(type="text", text=f"Výstup programu l{cislo}:\n\n{vystup}")]
        except subprocess.TimeoutExpired:
            return [TextContent(type="text", text=f"Program přesáhl timeout {timeout}s")]
        except Exception as e:
            return [TextContent(type="text", text=f"Chyba spuštění: {e}")]

    elif name == "statistiky":
        lekce = nacti_lekce()
        programy = nacti_programy()
        text = f"""📊 **Statistiky kurzu Python: From Zero to Hero**

- **Lekcí celkem:** {len(lekce)}
- **Programů:** {len(programy)}
- **Projektů:** 15
- **Sekce:** I–XX (20 sekcí)
- **Poslední lekce:** {lekce[-1]['nazev'] if lekce else '?'}

Kurz pokrývá:
- Základy Pythonu → OOP → Async → Architekturu
- Databáze: SQLite, PostgreSQL, Redis, MongoDB, DuckDB, ES, Vector DB, InfluxDB, Neo4j
- Algoritmy: řazení, stromy, grafy, DP, GA, NN, backprop, PyTorch
- Moderní nástroje: uv, Polars, PyO3, Kafka, gRPC, Celery
- ML/AI: Transformers, RL, LoRA fine-tuning
- Microservices + MCP servery
"""
        return [TextContent(type="text", text=text)]

    elif name == "doporuc_lekce":
        uroven = arguments["uroven"]
        tema = arguments.get("tema", "")
        doporuceni = {
            "zacatecnik": [(1, "Instalace, venv, pip"), (3, "Proměnné"), (8, "Podmínky"),
                           (9, "Smyčky"), (21, "Funkce základy")],
            "junior": [(31, "Třídy"), (56, "Async základy"), (88, "pytest"),
                       (97, "FastAPI"), (99, "Databáze")],
            "intermediate": [(101, "SOLID"), (103, "Clean Architecture"), (114, "Docker"),
                             (131, "RAG"), (143, "Řadící algoritmy")],
            "senior": [(104, "DDD"), (105, "CQRS"), (123, "Distribuované systémy"),
                       (160, "Kafka"), (171, "Microservices")],
        }
        lekce_pro_uroven = doporuceni.get(uroven, [])
        text = f"**Doporučení pro úroveň '{uroven}':**\n\n"
        for cislo, nazev in lekce_pro_uroven:
            text += f"  - Lekce {cislo}: {nazev}\n"
        if tema:
            text += f"\nPro téma '{tema}':\n"
            vysledky = hledej_v_lekcich(tema, 3)
            for v in vysledky:
                text += f"  - Lekce {v['cislo']}: {v['nazev']}\n"
        return [TextContent(type="text", text=text)]

    raise ValueError(f"Neznámý nástroj: {name}")


# ── Prompts ────────────────────────────────────────────────────────────────

@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    return [
        Prompt(
            name="vysvetli_lekci",
            description="Vysvětlí obsah lekce jednoduchými slovy",
            arguments=[
                PromptArgument(name="cislo", description="Číslo lekce", required=True),
                PromptArgument(name="uroven", description="Úroveň studenta", required=False),
            ],
        ),
        Prompt(
            name="quiz",
            description="Vytvoří quiz otázky pro procvičení lekce",
            arguments=[
                PromptArgument(name="cislo", description="Číslo lekce", required=True),
                PromptArgument(name="pocet", description="Počet otázek", required=False),
            ],
        ),
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> list[PromptMessage]:
    from mcp.types import PromptMessage

    if name == "vysvetli_lekci":
        cislo = arguments.get("cislo", "1")
        uroven = arguments.get("uroven", "intermediate")
        return [PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"Přečti lekci {cislo} z kurzu a vysvětli ji pro studenta úrovně '{uroven}'. "
                     f"Použij nástroj cti_lekci({cislo}) pro načtení obsahu."
            ),
        )]

    if name == "quiz":
        cislo = arguments.get("cislo", "1")
        pocet = arguments.get("pocet", "5")
        return [PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"Přečti lekci {cislo} a vytvoř {pocet} quiz otázek s odpověďmi. "
                     f"Použij nástroj cti_lekci({cislo}) pro načtení obsahu."
            ),
        )]

    raise ValueError(f"Neznámý prompt: {name}")


# ── Main ───────────────────────────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
