# Python: From Zero to Hero — kontext pro Claude

Kurz Pythonu v češtině. **183 lekcí, 183 programů, 18 mini-projektů**. Nasazeno na GitHub Pages přes MkDocs Material.

**Web:** https://navidofek-cmyk.github.io/Python_from_zero_to_hero/
**Repo:** https://github.com/navidofek-cmyk/Python_from_zero_to_hero

---

## Struktura

```
lekce/           ← markdown lekce (docs_dir pro MkDocs)
  index.md       ← hlavní stránka webu (auto-update přes gen_programy.py)
  projekty/      ← stránky 15 mini-projektů
  programy/      ← auto-generované stránky programů (NEUPRAVUJ ručně)
programy/        ← spustitelné .py soubory (l01_*.py … l172_*.py)
projekty/        ← zdrojové kódy projektů (15 složek)
  15_mcp_server/ ← funkční MCP server pro Claude Desktop
gen_programy.py  ← HLAVNÍ generátor (viz níže)
mkdocs.yml       ← nav konfigurace (4 taby)
```

---

## Klíčové pravidlo: gen_programy.py

**Po každém přidání nové lekce nebo programu VŽDY spusť:**
```bash
python3 gen_programy.py
```

Co dělá:
1. Generuje `lekce/programy/l*.md` pro každý soubor v `programy/`
2. Aktualizuje sekci `"Programy"` v `mkdocs.yml`
3. **Automaticky aktualizuje počet lekcí v `lekce/index.md`**

Proč: Dříve se `lekce/index.md` zapomínalo aktualizovat ručně — stalo se 2×. Skript to teď dělá automaticky.

---

## Navigace webu (4 taby)

```
Úvod | Projekty | Lekce | Programy
```

Proč 4 taby, ne 20+: `navigation.tabs` v MkDocs Material přetéká při 20+ top-level sekcích. Všechny lekce (I–XXIII) jsou pod jediným tabem "Lekce" v levém sidebaru.

Projekty jsou **2. tab** (ne na konci) — dříve byly za 20+ sekcemi a prakticky nepřístupné.

---

## Čísla sekcí a lekcí

| Sekce | Lekce | Obsah |
|-------|-------|-------|
| I–XVII | 1–130 | Základy → Leadership |
| Bonus | 131–134 | RAG, AI Agenti, MCP, structured outputs |
| XVIII | 135 | uv kompletní průvodce |
| XIX | 136–142 | Databáze: Redis, MongoDB, DuckDB, ES, Vector DB, InfluxDB, Neo4j |
| XX | 143–172 | Algoritmy, NN, backprop, PyTorch, Transformers, RL, LoRA, Polars, PyO3, Kafka, gRPC, Celery, WebSockets, GraphQL, JWT, Crypto, Spark, CV, NLP, Quantum, Microservices, MCP |
| XXI | 173–177 | Airflow, dbt, OpenTelemetry, Prometheus+Grafana, Alembic |
| XXII | 178–180 | LangChain, Pydantic AI, Ollama |
| XXIII | 181–183 | Mutation testing+Fuzzing, py-spy+memray, Python bytecode |

---

## Přidání nové lekce — postup

```bash
# 1. Vytvoř lekci
echo "obsah" > lekce/173_nova_lekce.md

# 2. Vytvoř program
echo "print('hello')" > programy/l173_nova_lekce.py

# 3. Přidej do nav (lekce/173_nova_lekce.md pod správnou sekci v mkdocs.yml)

# 4. Vygeneruj stránky + aktualizuj index
python3 gen_programy.py

# 5. Ověř build
python3 -m mkdocs build

# 6. Commit + push (GitHub Actions automaticky nasadí)
git add -A && git commit -m "Add: lekce 173 — ..."
git push origin main
```

---

## Projekt 15: MCP Server

Funkční MCP server — Claude se může dotazovat na obsah kurzu.

**Soubor:** `projekty/15_mcp_server/server.py`

Schopnosti:
- Tools: `hledej_lekci`, `cti_lekci`, `cti_program`, `spust_program`, `statistiky`, `doporuc_lekce`
- Resources: `kurz://lekce/{cislo}`, `kurz://statistiky`, `kurz://lekce/seznam`
- Prompts: `vysvetli_lekci`, `quiz`

Konfigurace Claude Desktop (`~/.claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "python-kurz": {
      "command": "python",
      "args": ["/abs/cesta/projekty/15_mcp_server/server.py"]
    }
  }
}
```

---

## Deployment

GitHub Actions (`.github/workflows/deploy.yml`):
- Trigger: push na `main`
- Build: `mkdocs gh-deploy --force`
- Čas: ~30 sekund
- Verze: `actions/checkout@v5`, `actions/setup-python@v6` (Node.js 24)

---

## Časté chyby a řešení

| Chyba | Řešení |
|-------|--------|
| Web nezobrazuje nové lekce | Spusť `gen_programy.py`, zkontroluj `mkdocs.yml` nav |
| YAML parse error v mkdocs.yml | Zkontroluj backticky nebo uvozovky v názvech lekcí |
| `lekce/index.md` má starý počet | Spusť `gen_programy.py` — opravuje automaticky |
| GitHub Actions selžou | Zkontroluj `gh run list` |

---

## Tech stack

- **MkDocs Material** — statický web
- **GitHub Pages** — hosting (branch `gh-pages`)
- **uv** — správce Pythonu a závislostí
- **MCP** (`uv add mcp`) — pro projekt 15
