# Reverzní prompt — Python From Zero to Hero

Použij tento prompt pro pokračování práce na kurzu v nové Claude Code session.

---

## Prompt

```
Pracujeme na Python kurzu v češtině uloženém v:
/home/ivand/projects/learning_python/python_from_zero_to_hero/

Struktura projektu:
- lekce/        → 131 .md souborů s teorií (01–131)
- programy/     → 131 .py souborů, spustitelné ukázky ke každé lekci
- projekty/     → 13 mini-projektů (01–13)
- mkdocs.yml    → MkDocs Material konfigurace, port 9999
- start.sh      → bash skript pro spuštění (Linux)
- start.ps1     → PowerShell skript pro spuštění (Windows)
- README.md     → přehled kurzu

Konvence pojmenování:
- lekce:    NNN_nazev.md         (např. 101_solid.md)
- programy: lNNN_nazev.py        (např. l101_solid.py)
- každý program má: docstring, from __future__ import annotations,
  sekce s # ── Název ─── komentáři, main() funkci + if __name__ == "__main__"

Stav kurzu:
- Lekce 1–131:   HOTOVO
- Programy 1–131: HOTOVO
- Mini-projekty 1–13: HOTOVO
- MkDocs web:    HOTOVO (./start.sh nebo ./start.ps1)

Sekce kurzu:
I.    Základy (1–10)
II.   Datové struktury (11–20)
III.  Funkce (21–30)
IV.   OOP (31–42)
V.    Pokročilé OOP (43–50)
VI.   Async (51–60)
VII.  Výjimky (61–66)
VIII. Moduly a stdlib (67–82)
IX.   Konkurence (83–87)
X.    Testování (88–92)
XI.   Výkon (93–96)
XII.  Specializace (97–100)
XIII. Architektura / SOLID, vzory, Clean Arch, DDD, CQRS (101–110)
XIV.  Produkce / Docker, K8s, CI/CD, bezpečnost (111–118)
XV.   Výkon ve velkém / flames, memory, GIL, async arch (119–124)
XVI.  Data a ML / pipelines, MLOps, LLMOps (125–128)
XVII. Leadership / ADR, monorepo (129–130)
Bonus: RAG (131)

Jazyk: vše česky, type hints všude, pouze stdlib pokud není uvedeno jinak.
```

---

## Co přidat dál (nápady)

- Projekt 14: FastAPI web reader s menu pro procházení lekcí
- Lekce 132: Agents (AI agenti s nástroji)
- Lekce 133: MCP (Model Context Protocol)
- Lekce 134: Structured outputs a JSON mode
- Git repozitář + GitHub Pages pro veřejné nasazení kurzu
