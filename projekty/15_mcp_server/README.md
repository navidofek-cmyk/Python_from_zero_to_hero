# Projekt 15 — Python Kurz MCP Server

Plnohodnotný MCP server pro kurz **Python: From Zero to Hero**.
Claude (nebo jiný AI asistent) může vyhledávat lekce, číst jejich obsah, spouštět programy a doporučovat učební plán.

---

## Co server umí

### Resources (data)
- `kurz://statistiky` — celkové statistiky kurzu
- `kurz://lekce/seznam` — seznam všech lekcí
- `kurz://lekce/{cislo}` — obsah konkrétní lekce

### Tools (nástroje)
| Nástroj | Popis |
|---------|-------|
| `hledej_lekci` | fulltext vyhledávání přes všechny lekce |
| `cti_lekci` | přečte obsah lekce |
| `cti_program` | přečte zdrojový kód programu |
| `spust_program` | spustí program a vrátí výstup |
| `statistiky` | zobrazí statistiky kurzu |
| `doporuc_lekce` | doporučí lekce pro danou úroveň |

### Prompts (šablony)
- `vysvetli_lekci` — vysvětlí lekci pro danou úroveň
- `quiz` — vytvoří quiz otázky z lekce

---

## Instalace

```bash
uv add mcp
```

---

## Spuštění (standalone test)

```bash
# Z adresáře projektu:
python projekty/15_mcp_server/server.py
```

---

## Konfigurace Claude Desktop

Přidej do `~/.claude/claude_desktop_config.json`:

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

Restartuj Claude Desktop — server se automaticky připojí.

---

## Příklady použití s Claude

Po připojení se Clauda zeptej:
- *"Najdi lekce o asyncio"*
- *"Přečti lekci 151 o neuronových sítích"*
- *"Spusť program l143 (řadící algoritmy)"*
- *"Jaké lekce doporučuješ pro juniora?"*
- *"Vytvoř quiz z lekce 145"*

---

## Technické detaily

- Transport: **stdio** (JSON-RPC přes stdin/stdout)
- Protokol: MCP 1.0
- Python: 3.11+
- Závislosti: `mcp`
