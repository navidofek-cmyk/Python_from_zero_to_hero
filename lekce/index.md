# Python: From Zero to Hero

Kompletní kurz Pythonu v češtině — od absolutních základů po senior/architect úroveň.

**150 lekcí · 150 programů · 14 mini-projektů**

---

## Jak začít

### Možnost A — uv (doporučeno)

```bash
# Instalace uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Spusť libovolný program přímo
uv run programy/l01_uv_demo.py
uv run programy/l143_razici_algoritmy.py

# Programy s externími závislostmi
uv run --with redis programy/l136_redis.py
uv run --with duckdb,pandas programy/l138_duckdb.py
uv run --with chromadb programy/l140_vector_db.py
```

### Možnost B — klasické venv + pip

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

python3 programy/l01_uv_demo.py
```

### Lokální web (MkDocs)

```bash
pip install mkdocs-material
mkdocs serve
# → otevři http://127.0.0.1:9999
```

---

## Doporučené pořadí

| Úroveň | Začni od |
|--------|---------|
| Nováček | Lekce 1 — Instalace, venv, pip |
| Junior | Lekce 31 — Třídy |
| Intermediate | Lekce 51 — Async nebo 88 — Testování |
| Senior | Lekce 101 — SOLID, architektura |
| Databáze | Lekce 136 — Redis, MongoDB, DuckDB… |
| Algoritmy | Lekce 143 — Řazení, stromy, grafy, DP, GA |
| uv | Lekce 135 — Kompletní průvodce |

---

## Sekce kurzu

| Sekce | Lekce | Témata |
|-------|-------|--------|
| I. Základy | 1–10 | instalace, proměnné, typy, podmínky, cykly |
| II. Datové struktury | 11–20 | list, dict, set, collections |
| III. Funkce | 21–30 | args/kwargs, lambda, closure, dekorátory |
| IV. OOP | 31–42 | třídy, dědičnost, property, dataclasses, enum |
| V. Pokročilé OOP | 43–50 | deskriptory, metatřídy, Protocol |
| VI. Async | 51–60 | iterátory, generátory, asyncio, TaskGroup |
| VII. Výjimky | 61–66 | try/except, vlastní výjimky, ExceptionGroup |
| VIII. Moduly a stdlib | 67–82 | importy, pathlib, json, argparse, subprocess |
| IX. Konkurence | 83–87 | threading, multiprocessing, futures |
| X. Testování | 88–92 | pytest, mock, coverage, hypothesis |
| XI. Výkon | 93–96 | profiling, optimalizace, C rozšíření |
| XII. Specializace | 97–100 | FastAPI, NumPy/pandas, SQLite, Claude API |
| XIII. Architektura | 101–110 | SOLID, vzory, Clean Arch, DDD, CQRS |
| XIV. Produkce | 111–118 | 12-factor, Docker, Kubernetes, CI/CD |
| XV. Výkon ve velkém | 119–124 | flame graphs, memory, GIL, async arch. |
| XVI. Data a ML | 125–128 | pipelines, stream processing, MLOps |
| XVII. Leadership | 129–130 | ADR, RFC, monorepo |
| Bonus | 131–134 | RAG, AI Agenti, MCP, strukturované výstupy |
| XVIII. uv a nástroje | 135 | workspaces, tools, inline deps, CI/CD |
| XIX. Databáze — pokročilé | 136–142 | Redis, MongoDB, DuckDB, ES, Vector, InfluxDB, Neo4j |
| XX. Algoritmy | 143–148 | řazení, stromy, grafy, DP, genetické, evoluční |

---

## Mini-projekty

Po každé sekci je mini-projekt, který procvičuje naučené koncepty:

| # | Projekt | Sekce |
|---|---------|-------|
| [01](projekty/p01_hadej_cislo.md) | Hádej číslo | Základy |
| [02](projekty/p02_todo_list.md) | TODO list | Datové struktury |
| [03](projekty/p03_textova_adventura.md) | Textová adventura | Funkce |
| [04](projekty/p04_rpg_postavy.md) | RPG postavy | OOP |
| [05](projekty/p05_mini_orm.md) | Mini ORM | Pokročilé OOP |
| [06](projekty/p06_async_scraper.md) | Async scraper | Async |
| [07](projekty/p07_robust_cli.md) | Robust CLI | Výjimky |
| [08](projekty/p08_pypi_balicek.md) | PyPI balíček | Moduly |
| [09](projekty/p09_log_analyzer.md) | Log analyzer | Konkurence |
| [10](projekty/p10_paralelni_stahovani.md) | Paralelní stahování | Testování |
| [11](projekty/p11_otestovana_knihovna.md) | Otestovaná knihovna | Výkon |
| [12](projekty/p12_optimalizace.md) | Optimalizace | Specializace |
| [13](projekty/p13_fastapi_db_llm.md) | FastAPI + SQLite + Claude | Architektura |
| [14](projekty/p14_kurz_reader.md) | Kurz Reader | Produkce |
