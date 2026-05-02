# Lekce 172: MCP Servery — Model Context Protocol

MCP (Model Context Protocol) je otevřený standard pro připojení AI asistentů k externím nástrojům a datům. Claude, Cursor, a další AI nástroje ho používají.

---

## 🧠 Co je MCP?

```
Bez MCP:
  Claude → odpovídá jen z trénovacích dat

S MCP:
  Claude → [MCP Server: Databáze]    → SELECT * FROM orders
         → [MCP Server: GitHub]      → čte issues, PR
         → [MCP Server: FileSystem]  → čte soubory
         → [MCP Server: Web Search]  → vyhledává online
         → [MCP Server: vlastní API] → tvoje firemní data
```

MCP server vystavuje:
- **Resources** — data (soubory, DB záznamy, URL)
- **Tools** — funkce (spusť SQL, odešli email, zavolej API)
- **Prompts** — šablony pro AI

---

## 🚀 Instalace

```bash
uv add mcp
# nebo
uv add "mcp[cli]"
```

---

## 🔧 Základní MCP server

```python
# mcp_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool, TextContent, Resource, ResourceContents,
    CallToolResult, ListToolsResult, ListResourcesResult,
)
import json
import asyncio


# Vytvoř MCP server
server = Server("muj-kurz-server")


# ── Resources — data k přečtení ────────────────────────────────────────────

@server.list_resources()
async def list_resources() -> list[Resource]:
    """Vypiš dostupné zdroje."""
    return [
        Resource(
            uri="kurz://lekce/seznam",
            name="Seznam lekcí",
            description="Kompletní seznam všech lekcí kurzu",
            mimeType="application/json",
        ),
        Resource(
            uri="kurz://statistiky",
            name="Statistiky kurzu",
            description="Počet lekcí, programů, projektů",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> ResourceContents:
    """Načti obsah zdroje."""
    if uri == "kurz://lekce/seznam":
        # Simulace — v produkci by četl skutečná data
        lekce = [
            {"cislo": i, "nazev": f"Lekce {i}", "sekce": "XX. Algoritmy"}
            for i in range(143, 153)
        ]
        return ResourceContents(
            uri=uri,
            mimeType="application/json",
            text=json.dumps(lekce, ensure_ascii=False, indent=2),
        )

    if uri == "kurz://statistiky":
        stats = {
            "lekce": 172,
            "programy": 172,
            "projekty": 15,
            "sekce": 20,
        }
        return ResourceContents(
            uri=uri,
            mimeType="application/json",
            text=json.dumps(stats, ensure_ascii=False),
        )

    raise ValueError(f"Neznámý resource: {uri}")


# ── Tools — funkce k volání ────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Vypiš dostupné nástroje."""
    return [
        Tool(
            name="hledej_lekci",
            description="Vyhledá lekce podle klíčového slova",
            inputSchema={
                "type": "object",
                "properties": {
                    "dotaz": {
                        "type": "string",
                        "description": "Klíčové slovo pro vyhledávání",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximální počet výsledků",
                        "default": 5,
                    },
                },
                "required": ["dotaz"],
            },
        ),
        Tool(
            name="spust_python",
            description="Spustí Python kód a vrátí výstup",
            inputSchema={
                "type": "object",
                "properties": {
                    "kod": {
                        "type": "string",
                        "description": "Python kód k spuštění",
                    }
                },
                "required": ["kod"],
            },
        ),
        Tool(
            name="preved_markdown",
            description="Převede Markdown na HTML",
            inputSchema={
                "type": "object",
                "properties": {
                    "markdown": {"type": "string", "description": "Markdown text"},
                },
                "required": ["markdown"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Zpracuj volání nástroje."""

    if name == "hledej_lekci":
        dotaz = arguments["dotaz"].lower()
        limit = arguments.get("limit", 5)

        # Simulace databáze lekcí
        vsechny_lekce = [
            {"cislo": 143, "nazev": "Řadící algoritmy", "popis": "bubble, merge, quick sort"},
            {"cislo": 144, "nazev": "Stromy", "popis": "BST, AVL, Trie, Heap"},
            {"cislo": 145, "nazev": "Grafové algoritmy", "popis": "BFS, DFS, Dijkstra"},
            {"cislo": 151, "nazev": "Neuronové sítě od nuly", "popis": "NumPy, backprop"},
            {"cislo": 153, "nazev": "PyTorch", "popis": "tensory, autograd, MNIST"},
            {"cislo": 157, "nazev": "Polars", "popis": "rychlá DataFrame knihovna"},
            {"cislo": 172, "nazev": "MCP servery", "popis": "Model Context Protocol"},
        ]

        nalezene = [
            l for l in vsechny_lekce
            if dotaz in l["nazev"].lower() or dotaz in l["popis"].lower()
        ][:limit]

        if not nalezene:
            return [TextContent(type="text", text=f"Žádné lekce nenalezeny pro '{dotaz}'")]

        result = f"Nalezeno {len(nalezene)} lekcí:\n"
        for l in nalezene:
            result += f"  {l['cislo']}: {l['nazev']} — {l['popis']}\n"
        return [TextContent(type="text", text=result)]

    elif name == "spust_python":
        kod = arguments["kod"]
        import io, sys
        output = io.StringIO()
        try:
            sys.stdout = output
            exec(kod, {"__builtins__": __builtins__})
            sys.stdout = sys.__stdout__
            return [TextContent(type="text", text=output.getvalue() or "(žádný výstup)")]
        except Exception as e:
            sys.stdout = sys.__stdout__
            return [TextContent(type="text", text=f"Chyba: {e}")]

    elif name == "preved_markdown":
        markdown = arguments["markdown"]
        try:
            import markdown
            html = markdown.markdown(markdown)
            return [TextContent(type="text", text=html)]
        except ImportError:
            # Jednoduchá fallback konverze
            html = markdown.replace("**", "<strong>").replace("*", "<em>")
            return [TextContent(type="text", text=html)]

    raise ValueError(f"Neznámý nástroj: {name}")


# ── Spuštění serveru ───────────────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
```

---

## ⚙️ Konfigurace v Claude Desktop

`~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "kurz-server": {
      "command": "python",
      "args": ["/cesta/k/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/cesta/k/projektu"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projekty"]
    }
  }
}
```

---

## 🔌 HTTP MCP server (SSE transport)

```python
from mcp.server.sse import SseServerTransport
from fastapi import FastAPI
import uvicorn

app = FastAPI()
transport = SseServerTransport("/messages")


@app.get("/sse")
async def sse_endpoint(request):
    """SSE endpoint pro MCP přes HTTP."""
    async with transport.connect_sse(request.scope, request.receive, request._send) as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())


@app.post("/messages")
async def handle_message(request):
    """Zpracuj zprávy od klienta."""
    await transport.handle_post_message(request.scope, request.receive, request._send)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

---

## 🧪 Testování MCP serveru

```python
# test_mcp.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_server():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Inicializace
            await session.initialize()

            # Vypiš dostupné nástroje
            tools = await session.list_tools()
            print("Dostupné nástroje:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Zavolej nástroj
            result = await session.call_tool("hledej_lekci", {"dotaz": "python"})
            print(f"\nVýsledek vyhledávání:")
            print(result.content[0].text)

            # Přečti resource
            resources = await session.list_resources()
            print(f"\nDostupné zdroje: {[r.name for r in resources.resources]}")


asyncio.run(test_server())
```

---

## 🎯 MCP ekosystém

| Server | Funkce | Zdroj |
|--------|--------|-------|
| Filesystem | čtení/zápis souborů | Anthropic |
| GitHub | issues, PR, code | Anthropic |
| Postgres | SQL dotazy | Anthropic |
| Brave Search | web vyhledávání | Anthropic |
| Slack | zprávy, kanály | komunita |
| Jira | issues, projekty | komunita |
| vlastní | cokoliv | ty! |

---

## ✏️ Cvičení

1. Postav MCP server pro **PostgreSQL** — Claude může spouštět SQL dotazy.
2. Vytvoř MCP server pro **GitHub Issues** — Claude čte a vytváří issues.
3. Napíš MCP server pro **kalkulačku s historií** — ukládá výpočty, Claude je může zobrazit.
4. Implementuj MCP server s **autentizací** — jen ověřený klient může volat nástroje.
5. Postav MCP server pro **kurz** — Claude dokáže vyhledávat lekce, číst kód a spouštět programy.
