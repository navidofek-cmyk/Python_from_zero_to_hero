# RESUME — Jak obnovit projekt

> Tento soubor přečti na začátku nové sese. Dává ti kompletní kontext.

---

## Kde jsme skončili (2026-05-02)

Kurz je **hotový a nasazený**. Poslední commit: `71563b2`.

**Stav:** 183 lekcí · 183 programů · 18 mini-projektů · sekce I–XXIII

Web běží: https://navidofek-cmyk.github.io/Python_from_zero_to_hero/

---

## Struktura projektu

```
lekce/           ← markdown lekce 01–183 + index.md + projekty/ + programy/
programy/        ← spustitelné .py soubory l01–l183
projekty/        ← 18 projektů (01–18)
gen_programy.py  ← HLAVNÍ skript — spusť po každé změně
mkdocs.yml       ← 4 taby: Úvod | Projekty | Lekce | Programy
CLAUDE.md        ← kontext pro Claude (tento soubor je navíc)
.github/workflows/deploy.yml  ← auto-deploy na GitHub Pages
```

---

## Workflow po přidání nové lekce

```bash
# 1. Vytvoř lekci
echo "# Lekce 184: ..." > lekce/184_nova_lekce.md

# 2. Vytvoř program
echo "print('hello')" > programy/l184_nova_lekce.py

# 3. Přidej do nav v mkdocs.yml (pod správnou sekci)

# 4. Vygeneruj + aktualizuj vše
python3 gen_programy.py

# 5. Ověř build
python3 -m mkdocs build

# 6. Commit a push
git add -A && git commit -m "Add: lekce 184 — ..."
git push origin main
# GitHub Actions nasadí za ~30s automaticky
```

---

## Sekce kurzu (přehled)

| Sekce | Lekce | Obsah |
|-------|-------|-------|
| I–XVII | 1–130 | Základy → Leadership |
| Bonus | 131–134 | RAG, AI Agenti, MCP, structured outputs |
| XVIII | 135 | uv |
| XIX | 136–142 | Redis, MongoDB, DuckDB, ES, Vector DB, InfluxDB, Neo4j |
| XX | 143–172 | Algoritmy, NN, PyTorch, Transformers, RL, LoRA, Polars, PyO3, Kafka, gRPC, Celery, WebSockets, GraphQL, JWT, Crypto, Spark, CV, NLP, Quantum, Microservices, MCP |
| XXI | 173–177 | Airflow, dbt, OpenTelemetry, Prometheus+Grafana, Alembic |
| XXII | 178–180 | LangChain, Pydantic AI, Ollama |
| XXIII | 181–183 | Mutation testing+Fuzzing, py-spy+memray, Python bytecode |

---

## Projekty

| # | Název | Tech |
|---|-------|------|
| 01–14 | Základní projekty | viz projekty/index.md |
| 15 | MCP Server | `projekty/15_mcp_server/server.py` |
| 16 | E-shop API | `projekty/16_eshop_api/app.py` |
| 17 | LLM Agent | `projekty/17_llm_agent/agent.py` |
| 18 | Data Pipeline | `projekty/18_data_pipeline/pipeline.py` |

---

## Důležitá pravidla

1. **gen_programy.py** — spusť vždy po přidání lekce. Aktualizuje:
   - `lekce/programy/l*.md` (stránky se zdrojovým kódem)
   - sekci `"Programy"` v `mkdocs.yml`
   - počet lekcí v `lekce/index.md`

2. **Nav = 4 taby** — Úvod | Projekty | Lekce | Programy
   - Projekty jsou 2. tab (přístupné hned)
   - Všechny lekce jsou pod "Lekce" tabem v sidebaru

3. **Deployment** — automatický přes GitHub Actions po push na `main`

4. **README.md** — aktualizuj ručně při změně počtu lekcí/projektů

---

## Uživatelovy preference

- Pracuje paralelně — více věcí najednou
- Nepotřebuje potvrzení — rovnou dělej
- Píše česky nebo velmi krátce
- Chce vždy vše kompletní

---

## Stav git

```
Větev: main
Poslední commit: 71563b2
Vzdálené repo: navidofek-cmyk/Python_from_zero_to_hero
```
