# Projekt 17 — LLM Agent s nástroji

Autonomní AI agent který může vyhledávat lekce, spouštět Python kód a odpovídá na otázky o kurzu.

## Spuštění

```bash
uv add anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python projekty/17_llm_agent/agent.py
```

## Dostupné nástroje

| Nástroj | Popis |
|---------|-------|
| `hledej_lekci` | Fulltext vyhledávání v lekcích |
| `cti_lekci` | Přečte obsah lekce |
| `spust_python` | Spustí Python kód |
| `vypocitej` | Matematické výrazy |
| `statistiky_kurzu` | Statistiky kurzu |

## Příklady dotazů

```python
run_agent("Kolik lekcí má kurz?")
run_agent("Najdi lekce o asyncio a ukaž příklad")
run_agent("Spočítej sumu prvočísel do 1000")
run_agent("Co je LoRA fine-tuning?")
```
