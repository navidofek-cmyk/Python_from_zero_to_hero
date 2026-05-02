# Projekt 15: Python Kurz MCP Server

Plnohodnotný MCP server — Claude nebo jiný AI asistent se může dotazovat na obsah kurzu, číst lekce, spouštět programy a dostávat doporučení.

**Použité koncepty:** FastAPI (97), asyncio (56–57), MCP protokol (172), JSON-RPC, subprocess.

## Co server umí

| Funkce | Typ | Popis |
|--------|-----|-------|
| `hledej_lekci` | Tool | Fulltext vyhledávání přes všechny lekce |
| `cti_lekci` | Tool | Přečte obsah lekce |
| `cti_program` | Tool | Přečte zdrojový kód programu |
| `spust_program` | Tool | Spustí program a vrátí výstup |
| `statistiky` | Tool | Statistiky kurzu |
| `doporuc_lekce` | Tool | Doporučení podle úrovně |
| `kurz://lekce/{n}` | Resource | Obsah konkrétní lekce |
| `vysvetli_lekci` | Prompt | Vysvětlí lekci pro danou úroveň |
| `quiz` | Prompt | Vytvoří quiz otázky z lekce |

## Jak spustit

```bash
# Instalace
uv add mcp

# Spuštění
python projekty/15_mcp_server/server.py
```

## Konfigurace Claude Desktop

```json
{
  "mcpServers": {
    "python-kurz": {
      "command": "python",
      "args": ["/absolutni/cesta/projekty/15_mcp_server/server.py"]
    }
  }
}
```

Umístění konfigurace: `~/.claude/claude_desktop_config.json`

## Příklady dotazů na Claude

Po připojení se Clauda zeptej:
- *"Najdi lekce o asyncio"*
- *"Přečti lekci 172 o MCP serverech"*
- *"Spusť program l143 a ukaž výstup"*
- *"Jaké lekce doporučuješ pro seniora?"*
- *"Vytvoř quiz z lekce 151"*

## Zdrojový kód

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio

server = Server("python-kurz")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="hledej_lekci",
            description="Vyhledá lekce podle klíčového slova",
            inputSchema={
                "type": "object",
                "properties": {
                    "dotaz": {"type": "string"},
                    "limit": {"type": "integer", "default": 5},
                },
                "required": ["dotaz"],
            },
        ),
        # ... dalši tools
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "hledej_lekci":
        # fulltext vyhledávání přes lekce/
        ...
    # ...

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())

asyncio.run(main())
```

!!! note "Kompletní server"
    Plný zdrojový kód je v `projekty/15_mcp_server/server.py` (~300 řádků).
    Obsahuje Resources, Tools, Prompts a fulltext vyhledávání přes všechny lekce.
