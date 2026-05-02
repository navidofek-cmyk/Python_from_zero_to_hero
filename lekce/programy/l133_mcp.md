# Program — Lekce 133: Lekce 133: MCP — Model Context Protocol

Patří k lekci [Lekce 133: MCP — Model Context Protocol](../133_mcp.md).

## Jak spustit

```bash
python3 programy/l133_mcp.py
```

## Zdrojový kód

### `l133_mcp.py`

```py
"""Lekce 133 — MCP (Model Context Protocol).

Demonstrace architektury MCP:
  - Simulace MCP serveru (resources / tools / prompts) bez závislosti na SDK
  - Ukázka reálného MCP serveru přes try/except ImportError
  - Spustitelné bez jakýchkoli externích balíčků

Pro reálný MCP server:
  pip install mcp
  Viz třídu RealniMcpServer níže.
"""

from __future__ import annotations

import asyncio
import json
import math
import os
from dataclasses import dataclass, field
from typing import Any, Callable


# ── Simulace MCP primitiv ─────────────────────────────────────────────────────

@dataclass
class Resource:
    uri: str
    name: str
    mime_type: str
    popis: str = ""


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass
class Prompt:
    name: str
    description: str
    arguments: list[dict[str, str]] = field(default_factory=list)


@dataclass
class ToolResult:
    obsah: str
    chyba: bool = False


# ── Jednoduchý simulovaný MCP server ─────────────────────────────────────────

class SimulovanyMcpServer:
    """
    Simuluje chování MCP serveru bez závislosti na mcp balíčku.
    Vystavuje resources, tools a prompts stejně jako reálný MCP server.
    """

    def __init__(self, nazev: str) -> None:
        self.nazev = nazev
        self._resources: dict[str, tuple[Resource, Callable[[], str]]] = {}
        self._tools: dict[str, tuple[Tool, Callable[..., str]]] = {}
        self._prompts: dict[str, tuple[Prompt, Callable[..., str]]] = {}

    # --- Registrace ---

    def pridej_resource(
        self,
        uri: str,
        name: str,
        mime_type: str,
        getter: Callable[[], str],
        popis: str = "",
    ) -> None:
        self._resources[uri] = (Resource(uri, name, mime_type, popis), getter)

    def pridej_tool(
        self,
        name: str,
        description: str,
        schema: dict[str, Any],
        handler: Callable[..., str],
    ) -> None:
        self._tools[name] = (Tool(name, description, schema), handler)

    def pridej_prompt(
        self,
        name: str,
        description: str,
        arguments: list[dict[str, str]],
        sablona: Callable[..., str],
    ) -> None:
        self._prompts[name] = (Prompt(name, description, arguments), sablona)

    # --- MCP primitivy ---

    def list_resources(self) -> list[Resource]:
        return [r for r, _ in self._resources.values()]

    def read_resource(self, uri: str) -> str:
        if uri not in self._resources:
            raise KeyError(f"Resource nenalezen: {uri!r}")
        _, getter = self._resources[uri]
        return getter()

    def list_tools(self) -> list[Tool]:
        return [t for t, _ in self._tools.values()]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        if name not in self._tools:
            return ToolResult(f"Neznámý nástroj: {name!r}", chyba=True)
        _, handler = self._tools[name]
        try:
            vysledek = handler(**arguments)
            return ToolResult(str(vysledek))
        except Exception as exc:
            return ToolResult(f"Chyba: {exc}", chyba=True)

    def list_prompts(self) -> list[Prompt]:
        return [p for p, _ in self._prompts.values()]

    def get_prompt(self, name: str, arguments: dict[str, str]) -> str:
        if name not in self._prompts:
            raise KeyError(f"Prompt nenalezen: {name!r}")
        _, sablona = self._prompts[name]
        return sablona(**arguments)

    def info(self) -> str:
        return (
            f"Server: {self.nazev!r}  |  "
            f"Resources: {len(self._resources)}  |  "
            f"Tools: {len(self._tools)}  |  "
            f"Prompts: {len(self._prompts)}"
        )


# ── Konkrétní server: Kalkulačka + Počasí ────────────────────────────────────

POCASI_DB: dict[str, dict[str, Any]] = {
    "Praha":   {"teplota": 18, "stav": "oblačno",  "vlhkost": 65},
    "Brno":    {"teplota": 16, "stav": "slunečno", "vlhkost": 55},
    "Ostrava": {"teplota": 13, "stav": "déšť",     "vlhkost": 80},
}


def _resource_konfigurace() -> str:
    konfig = {"verze": "1.0.0", "max_kroky": 10, "debug": False}
    return json.dumps(konfig, ensure_ascii=False, indent=2)


def _resource_pocasi_json() -> str:
    return json.dumps(POCASI_DB, ensure_ascii=False, indent=2)


def _tool_kalkulator(vyraz: str) -> str:
    ns: dict[str, Any] = {
        "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
        "pi": math.pi, "e": math.e, "abs": abs, "round": round,
        "__builtins__": {},
    }
    return str(eval(vyraz, ns))  # noqa: S307


def _tool_pocasi(mesto: str) -> str:
    data = POCASI_DB.get(mesto)
    if data is None:
        return f"Město {mesto!r} nenalezeno v databázi."
    return f"{data['teplota']} °C, {data['stav']}, vlhkost {data['vlhkost']} %"


def _tool_preved_teplotu(hodnota: float, z_jednotky: str, na_jednotku: str) -> str:
    z = z_jednotky.upper()
    na = na_jednotku.upper()
    if z == "C" and na == "F":
        return f"{hodnota * 9/5 + 32:.2f} °F"
    if z == "F" and na == "C":
        return f"{(hodnota - 32) * 5/9:.2f} °C"
    if z == "C" and na == "K":
        return f"{hodnota + 273.15:.2f} K"
    if z == "K" and na == "C":
        return f"{hodnota - 273.15:.2f} °C"
    if z == na:
        return f"{hodnota:.2f} {na}"
    return f"Nepodporovaný převod: {z} → {na}"


def _prompt_shrn_dokument(text: str) -> str:
    return f"Shrň tento dokument do maximálně 3 vět:\n\n{text}"


def _prompt_porovnej_produkty(produkt_a: str, produkt_b: str) -> str:
    return (
        f"Porovnej tyto dva produkty z hlediska klíčových vlastností, "
        f"ceny a vhodnosti pro průměrného uživatele:\n\n"
        f"Produkt A: {produkt_a}\nProdukt B: {produkt_b}\n\n"
        f"Uveď výhody a nevýhody každého a doporuč jeden z nich."
    )


def vytvor_server() -> SimulovanyMcpServer:
    server = SimulovanyMcpServer("demo-mcp-server")

    # Resources
    server.pridej_resource(
        "config://app/konfigurace",
        "Konfigurace aplikace",
        "application/json",
        _resource_konfigurace,
        "Základní nastavení aplikace.",
    )
    server.pridej_resource(
        "data://pocasi/mesta",
        "Databáze počasí",
        "application/json",
        _resource_pocasi_json,
        "Simulovaná databáze aktuálního počasí.",
    )

    # Tools
    server.pridej_tool(
        "kalkulator",
        "Vypočítá matematický výraz (sqrt, sin, cos, pi…).",
        {
            "type": "object",
            "properties": {"vyraz": {"type": "string"}},
            "required": ["vyraz"],
        },
        _tool_kalkulator,
    )
    server.pridej_tool(
        "pocasi",
        "Vrátí počasí pro zadané město.",
        {
            "type": "object",
            "properties": {"mesto": {"type": "string"}},
            "required": ["mesto"],
        },
        _tool_pocasi,
    )
    server.pridej_tool(
        "preved_teplotu",
        "Převede teplotu mezi Celsius, Fahrenheit a Kelvin (C/F/K).",
        {
            "type": "object",
            "properties": {
                "hodnota": {"type": "number"},
                "z_jednotky": {"type": "string"},
                "na_jednotku": {"type": "string"},
            },
            "required": ["hodnota", "z_jednotky", "na_jednotku"],
        },
        _tool_preved_teplotu,
    )

    # Prompts
    server.pridej_prompt(
        "shrn_dokument",
        "Shrne zadaný text do 3 vět.",
        [{"name": "text", "description": "Text k shrnutí", "required": "true"}],
        _prompt_shrn_dokument,
    )
    server.pridej_prompt(
        "porovnej_produkty",
        "Porovná dva produkty.",
        [
            {"name": "produkt_a", "description": "První produkt", "required": "true"},
            {"name": "produkt_b", "description": "Druhý produkt", "required": "true"},
        ],
        _prompt_porovnej_produkty,
    )

    return server


# ── Simulace MCP klienta ──────────────────────────────────────────────────────

class SimulovanyMcpKlient:
    """Simuluje MCP klienta připojeného k serveru (in-process pro demo)."""

    def __init__(self, server: SimulovanyMcpServer) -> None:
        self._server = server

    def initialize(self) -> None:
        print(f"  Připojeno k serveru: {self._server.info()}")

    def vypis_resources(self) -> None:
        print("\n  [Resources]")
        for r in self._server.list_resources():
            print(f"    {r.uri}")
            print(f"      Název: {r.name} | MIME: {r.mime_type}")

    def cti_resource(self, uri: str) -> None:
        try:
            obsah = self._server.read_resource(uri)
            print(f"\n  Obsah resource {uri!r}:")
            for radek in obsah.splitlines():
                print(f"    {radek}")
        except KeyError as exc:
            print(f"  Chyba: {exc}")

    def vypis_tools(self) -> None:
        print("\n  [Tools]")
        for t in self._server.list_tools():
            pozadovane = t.input_schema.get("required", [])
            print(f"    {t.name}({', '.join(pozadovane)})")
            print(f"      {t.description}")

    def zavolej_tool(self, name: str, **kwargs: Any) -> None:
        vysledek = self._server.call_tool(name, kwargs)
        stav = "CHYBA" if vysledek.chyba else "OK"
        print(f"\n  call_tool({name!r}, {kwargs}) → [{stav}] {vysledek.obsah}")

    def vypis_prompts(self) -> None:
        print("\n  [Prompts]")
        for p in self._server.list_prompts():
            parametry = [a["name"] for a in p.arguments]
            print(f"    {p.name}({', '.join(parametry)})")
            print(f"      {p.description}")

    def get_prompt(self, name: str, **kwargs: str) -> None:
        try:
            text = self._server.get_prompt(name, kwargs)
            print(f"\n  get_prompt({name!r}):")
            print(f"    {text[:120]}{'…' if len(text) > 120 else ''}")
        except KeyError as exc:
            print(f"  Chyba: {exc}")


# ── Reálný MCP server (vyžaduje pip install mcp) ─────────────────────────────

def vypis_realny_priklad() -> None:
    """Vytiskne kód reálného MCP serveru jako ukázku."""
    kod = '''
# Reálný MCP server — spusť jako standalone skript
# pip install mcp

import asyncio, math
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("kalkulacka")

@server.list_tools()
async def tools() -> list[Tool]:
    return [Tool(
        name="vypocitej",
        description="Matematické výpočty",
        inputSchema={"type": "object",
                     "properties": {"vyraz": {"type": "string"}},
                     "required": ["vyraz"]},
    )]

@server.call_tool()
async def call(name: str, arguments: dict) -> list[TextContent]:
    ns = {"sqrt": math.sqrt, "pi": math.pi, "__builtins__": {}}
    result = eval(arguments["vyraz"], ns)
    return [TextContent(type="text", text=str(result))]

async def run():
    async with stdio_server() as (r, w):
        await server.run(r, w, server.create_initialization_options())

asyncio.run(run())
'''
    print("\n--- Ukázka reálného MCP serveru (vyžaduje: pip install mcp) ---")
    print(kod)

    try:
        import mcp  # noqa: F401
        print("  mcp balíček je nainstalován — server lze spustit.")
    except ImportError:
        print("  mcp balíček NENÍ nainstalován. Spusť: pip install mcp")


# ── Demo ──────────────────────────────────────────────────────────────────────

def demo_server_klient() -> None:
    print("=== Simulace MCP Server + Klient ===\n")

    server = vytvor_server()
    klient = SimulovanyMcpKlient(server)

    print("1) Inicializace:")
    klient.initialize()

    print("\n2) Dostupné resources:")
    klient.vypis_resources()

    print("\n3) Čtení resource:")
    klient.cti_resource("config://app/konfigurace")

    print("\n4) Dostupné nástroje:")
    klient.vypis_tools()

    print("\n5) Volání nástrojů:")
    klient.zavolej_tool("kalkulator", vyraz="sqrt(225) + pi")
    klient.zavolej_tool("pocasi", mesto="Praha")
    klient.zavolej_tool("pocasi", mesto="Tokio")
    klient.zavolej_tool("preved_teplotu", hodnota=100.0, z_jednotky="C", na_jednotku="F")
    klient.zavolej_tool("preved_teplotu", hodnota=0.0, z_jednotky="C", na_jednotku="K")

    print("\n6) Dostupné prompts:")
    klient.vypis_prompts()

    print("\n7) Načtení promptu:")
    klient.get_prompt("shrn_dokument", text="Python je interpretovaný jazyk...")
    klient.get_prompt(
        "porovnej_produkty",
        produkt_a="iPhone 16 Pro",
        produkt_b="Samsung Galaxy S25",
    )


def demo_mcp_vs_tool_use() -> None:
    print("\n=== MCP vs. přímé tool use — srovnání ===\n")

    srovnani = [
        ("Rychlost prototypu",    "Rychlé — kód v aplikaci",    "Pomalejší — separátní server"),
        ("Znovupoužitelnost",     "Nízká",                      "Vysoká — sdílí více klientů"),
        ("Izolace kódu",          "Nástroj v aplikaci",         "Separátní proces"),
        ("Vzdálený přístup",      "Složitější",                 "Nativní (HTTP/SSE)"),
        ("Hotový ekosystém",      "Ne",                         "Ano (GitHub, DB, FS…)"),
        ("Kdy použít",            "Jednoduché app-specific nástroje",
                                  "Sdílené integrace více apps"),
    ]

    print(f"  {'Kritérium':<28} {'Přímé tool use':<38} {'MCP'}")
    print(f"  {'-'*28} {'-'*38} {'-'*35}")
    for rad in srovnani:
        print(f"  {rad[0]:<28} {rad[1]:<38} {rad[2]}")


# ── Hlavní funkce ─────────────────────────────────────────────────────────────

def main() -> None:
    demo_server_klient()
    demo_mcp_vs_tool_use()
    vypis_realny_priklad()


if __name__ == "__main__":
    main()

```
