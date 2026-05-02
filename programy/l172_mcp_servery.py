"""Lekce 172 — MCP Servery: Model Context Protocol.

Tento soubor demonstruje MCP koncepty a jak spustit MCP server.

Skutečný MCP server:
    viz projekty/15_mcp_server/server.py

Spuštění MCP serveru:
    uv run --with mcp projekty/15_mcp_server/server.py

Konfigurace Claude Desktop:
    ~/.claude/claude_desktop_config.json
"""

import json
import asyncio


def demo_mcp_koncepty():
    print("=" * 55)
    print("  🔌 Model Context Protocol (MCP) Demo")
    print("=" * 55)

    print("""
MCP Architektura:
  ┌─────────────────┐
  │   AI Asistent   │  (Claude, Cursor, ...)
  │   (MCP Client)  │
  └────────┬────────┘
           │ JSON-RPC přes stdio/HTTP
  ┌────────▼────────┐
  │   MCP Server    │  (tvůj Python server)
  │                 │
  │  Resources      │  → soubory, DB, URL
  │  Tools          │  → funkce k volání
  │  Prompts        │  → šablony
  └─────────────────┘

Příklad komunikace:
  Klient: {"jsonrpc":"2.0","method":"tools/call",
           "params":{"name":"hledej_lekci","arguments":{"dotaz":"python"}}}
  Server: {"result":{"content":[{"type":"text","text":"Nalezeno 5 lekcí..."}]}}
""")


def demo_mcp_server_kod():
    print("=== MCP Server kód ===")
    print("""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio

server = Server("muj-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="pozdrav",
            description="Pozdraví uživatele",
            inputSchema={
                "type": "object",
                "properties": {"jmeno": {"type": "string"}},
                "required": ["jmeno"],
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "pozdrav":
        return [TextContent(type="text", text=f"Ahoj, {arguments['jmeno']}!")]
    raise ValueError(f"Neznámý nástroj: {name}")

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())

asyncio.run(main())
""")


def demo_konfigurace():
    print("=== Konfigurace Claude Desktop ===")
    config = {
        "mcpServers": {
            "python-kurz": {
                "command": "python",
                "args": ["/abs/cesta/projekty/15_mcp_server/server.py"],
            },
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user"],
            },
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..."},
            },
        }
    }
    print(json.dumps(config, indent=2))
    print("\nUmístění: ~/.claude/claude_desktop_config.json")


async def demo_mcp_simulace():
    print("\n=== Simulace MCP komunikace ===")

    # Simulace bez skutečného MCP
    tools_registry = {}
    resources_registry = {}

    def tool(func):
        tools_registry[func.__name__] = func
        return func

    def resource(uri: str):
        def decorator(func):
            resources_registry[uri] = func
            return func
        return decorator

    @tool
    async def hledej_lekci(dotaz: str, limit: int = 3) -> str:
        lekce_db = [
            "Lekce 1: Instalace Pythonu, venv a pip",
            "Lekce 97: FastAPI — moderní web framework",
            "Lekce 143: Řadící algoritmy — bubble, merge, quick sort",
            "Lekce 172: MCP servery — Model Context Protocol",
        ]
        nalezene = [l for l in lekce_db if dotaz.lower() in l.lower()][:limit]
        if not nalezene:
            return f"Nenalezeno pro '{dotaz}'"
        return "\n".join(f"  - {l}" for l in nalezene)

    @resource("kurz://statistiky")
    async def statistiky() -> dict:
        return {"lekce": 172, "programy": 172, "projekty": 15}

    # Simulace volání
    print("\n  1. list_tools():")
    for name in tools_registry:
        print(f"     - {name}")

    print("\n  2. call_tool('hledej_lekci', {'dotaz': 'FastAPI'}):")
    result = await tools_registry["hledej_lekci"](dotaz="FastAPI")
    print(f"     {result}")

    print("\n  3. read_resource('kurz://statistiky'):")
    stats = await resources_registry["kurz://statistiky"]()
    print(f"     {stats}")


def main():
    demo_mcp_koncepty()
    demo_mcp_server_kod()
    demo_konfigurace()
    asyncio.run(demo_mcp_simulace())

    print("\n✅ Demo dokončeno!")
    print("\nSkutečný MCP server: projekty/15_mcp_server/server.py")
    print("Instalace: uv add mcp")
    print("Dokumentace: https://modelcontextprotocol.io/")


if __name__ == "__main__":
    main()
