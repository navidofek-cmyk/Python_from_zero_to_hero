# Mini-projekty

Každá sekce kurzu končí mini-projektem, který spojuje naučené koncepty do funkčního programu.

| # | Projekt | Sekce | Klíčové koncepty |
|---|---------|-------|-----------------|
| [01](p01_hadej_cislo.md) | Hádej číslo | I. Základy | proměnné, smyčky, podmínky |
| [02](p02_todo_list.md) | TODO list s ukládáním | II. Datové struktury | list, dict, JSON |
| [03](p03_textova_adventura.md) | Textová adventura | III. Funkce | funkce, dekorátory, dispatch |
| [04](p04_rpg_postavy.md) | RPG postavy | IV. OOP | třídy, dědičnost, Enum |
| [05](p05_mini_orm.md) | Mini ORM / validátor | V. Pokročilé OOP | deskriptory, `__init_subclass__` |
| [06](p06_async_scraper.md) | Async web scraper | VI. Async | `async/await`, semafor |
| [07](p07_robust_cli.md) | Robust CLI | VII. Výjimky | vlastní výjimky, `ExceptionGroup` |
| [08](p08_pypi_balicek.md) | PyPI balíček | VIII. Moduly | `pyproject.toml`, entry points |
| [09](p09_log_analyzer.md) | Log analyzer | IX. Konkurence | regex, `Counter`, `argparse` |
| [10](p10_paralelni_stahovani.md) | Paralelní stahování | X. Testování | `ThreadPoolExecutor`, semafor |
| [11](p11_otestovana_knihovna.md) | Otestovaná knihovna | XI. Výkon | pytest, hypothesis, coverage |
| [12](p12_optimalizace.md) | Optimalizace | XII. Specializace | `cProfile`, `timeit` |
| [13](p13_fastapi_db_llm.md) | FastAPI + SQLite + Claude | XIII. Architektura | FastAPI, SQLite, AI |
| [14](p14_kurz_reader.md) | Kurz Reader | XIV. Produkce | FastAPI, Markdown, fulltext |
| [15](p15_mcp_server.md) | MCP Server | XX. Algoritmy + MCP | MCP, asyncio, tools, resources, prompts |

## Jak spouštět projekty

```bash
# Z kořenového adresáře repozitáře:
python3 projekty/01_hadej_cislo/hra.py
python3 projekty/02_todo_list/todo.py
# atd.
```

Projekty s externími závislostmi mají instrukce na svých stránkách.
