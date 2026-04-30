# Python: From Zero to Hero

Kompletní kurz Pythonu v češtině — od absolutních základů po senior/architect úroveň.

**134 lekcí · 134 programů · 14 mini-projektů**

**Web:** https://navidofek-cmyk.github.io/Python_from_zero_to_hero/

---

## Struktura kurzu

```
python_from_zero_to_hero/
├── lekce/          ← teorie (.md soubory, jedna lekce = jeden soubor)
├── programy/       ← spustitelné ukázky ke každé lekci
├── projekty/       ← mini-projekty po každé sekci
└── 100_python_lekci.md  ← kompletní osnova
```

---

## Sekce

| Sekce | Lekce | Témata |
|-------|-------|--------|
| I. Základy | 1–10 | instalace, proměnné, typy, podmínky, cykly |
| II. Datové struktury | 11–20 | list, dict, set, collections, iterace |
| III. Funkce | 21–30 | args/kwargs, lambda, closure, dekorátory |
| IV. OOP | 31–42 | třídy, dědičnost, property, dataclasses, enum |
| V. Pokročilé OOP | 43–50 | deskriptory, metatřídy, context managers, Protocol |
| VI. Async | 51–60 | iterátory, generátory, asyncio, TaskGroup |
| VII. Výjimky | 61–66 | try/except, vlastní výjimky, logging |
| VIII. Moduly a stdlib | 67–82 | importy, pathlib, subprocess, json, argparse |
| IX. Konkurence | 83–87 | threading, multiprocessing, futures |
| X. Testování | 88–92 | pytest, mock, coverage, ruff, mypy |
| XI. Výkon | 93–96 | profiling, optimalizace, C rozšíření |
| XII. Specializace | 97–100 | FastAPI, NumPy/pandas, SQLite, Claude API |
| XIII. Architektura | 101–110 | SOLID, vzory, Clean Arch, DDD, CQRS |
| XIV. Produkce | 111–118 | 12-factor, observabilita, Docker, CI/CD, bezpečnost |
| XV. Výkon ve velkém | 119–124 | flame graphs, memory, GIL, async architektura |
| XVI. Data a ML | 125–128 | pipelines, stream processing, MLOps, LLMOps |
| XVII. Leadership | 129–130 | ADR, RFC, monorepo |
| Bonus | 131–134 | RAG, AI Agenti, MCP, Strukturované výstupy |

---

## Mini-projekty

| # | Název | Procvičuje |
|---|-------|-----------|
| 01 | Hádej číslo | základy, cykly |
| 02 | TODO list | soubory, JSON |
| 03 | Textová adventura | třídy, dědičnost |
| 04 | RPG postavy | OOP, dataclasses, enum |
| 05 | Mini ORM | deskriptory, metatřídy |
| 06 | Async scraper | asyncio, httpx |
| 07 | Robust CLI | argparse, logging |
| 08 | PyPI balíček | packaging, entry points |
| 09 | Log analyzer | pathlib, regex, generátory |
| 10 | Paralelní stahování | concurrent.futures |
| 11 | Otestovaná knihovna | pytest, mock, coverage |
| 12 | Optimalizace | cProfile, timeit |
| 13 | FastAPI + SQLite + Claude | FastAPI, SQLite, Anthropic API |
| 14 | Kurz reader | FastAPI, MkDocs, GitHub Pages |

---

## Jak začít

```bash
# Doporučeno: uv (rychlý správce prostředí)
pip install uv

# Vytvoř virtuální prostředí
uv venv
source .venv/bin/activate   # Linux/macOS
# nebo: .venv\Scripts\activate  (Windows)

# Spusť libovolný program
python programy/l01_uv_demo.py
python programy/l101_solid.py
python programy/l131_rag.py
```

Pro lekce vyžadující externí balíčky:

```bash
# FastAPI (lekce 97, projekt 13)
pip install "fastapi[standard]"

# Anthropic Claude (lekce 100, 131)
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# NumPy, pandas (lekce 98)
pip install numpy pandas matplotlib
```

---

## Doporučené pořadí

Kurz je navržen lineárně — každá lekce staví na předchozích.
Pokud znáš základy, přeskoč na sekci, která tě zajímá:

- **Nováček** → začni od lekce 1
- **Junior** → přeskoč na lekci 31 (OOP)
- **Intermediate** → přeskoč na lekci 51 (async) nebo 88 (testování)
- **Senior** → přeskoč na lekci 101 (architektura)

---

## Požadavky

- Python 3.11+
- Znalost češtiny (kurz je celý v češtině)
