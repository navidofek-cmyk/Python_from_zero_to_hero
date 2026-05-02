# Projekt 17: LLM Agent s nástroji

Autonomní Claude agent s nástroji pro vyhledávání lekcí, spouštění kódu a odpovídání na otázky o kurzu.

**Použité koncepty:** Anthropic API (100), tool use (100), asyncio (56), MCP (172).

## Spuštění

```bash
uv add anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python projekty/17_llm_agent/agent.py
```

## Dostupné nástroje

- `hledej_lekci` — fulltext vyhledávání
- `cti_lekci` — obsah lekce
- `spust_python` — spuštění kódu
- `vypocitej` — matematika
- `statistiky_kurzu` — přehled kurzu

Zdrojový kód: `projekty/17_llm_agent/agent.py`
