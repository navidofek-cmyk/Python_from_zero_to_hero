# Projekt 14 — Python Kurz Reader

FastAPI webová aplikace pro pohodlné procházení kurzu **Python: From Zero to Hero**.
Zobrazuje 131 lekcí ve formátu Markdown renderovaném jako HTML, zdrojové kódy programů
se zvýrazněním syntaxe a umožňuje fulltext vyhledávání.

---

## Co projekt dělá

| Endpoint | Popis |
|---|---|
| `GET /` | Hlavní stránka — přehled všech lekcí jako karty |
| `GET /lekce/{cislo}` | Detail lekce — Markdown renderovaný jako HTML |
| `GET /program/{cislo}` | Zdrojový kód programu se zvýrazněním syntaxe (Pygments/monokai) |
| `GET /hledej?q=xxx` | Fulltext vyhledávání přes všechny `.md` soubory |
| `GET /api/lekce` | JSON API — seznam všech lekcí s metadaty |

---

## Jak spustit

### 1. Nainstaluj závislosti

```bash
pip install "fastapi[standard]" markdown2 pygments
```

### 2. Spusť aplikaci

```bash
# Z adresáře projektu (projekty/14_kurz_reader/)
fastapi dev app.py --port 8080

# nebo
uvicorn app:app --reload --port 8080

# nebo přímo
python app.py
```

### 3. Otevři v prohlížeči

```
http://localhost:8080
```

---

## Závislosti

| Balíček | Důvod | Fallback |
|---|---|---|
| `fastapi[standard]` | Web framework + uvicorn | — (povinné) |
| `markdown2` | Renderování Markdown → HTML | `mistune`, nebo stdlib regex |
| `pygments` | Syntax highlighting Pythonu | prostý `<pre><code>` |

Aplikace funguje i bez `markdown2` a `pygments` — použije stdlib fallback.

---

## ASCII art — layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Hlavní stránka (GET /)                                         │
├──────────────┬──────────────────────────────────────────────────┤
│  SIDEBAR     │  HERO                                            │
│              │  🐍 Python: From Zero to Hero                    │
│  Python Kurz │  Kompletní kurz v češtině · 131 lekcí           │
│  ↩ Všechny  │  ─────────────────────────────────────────────── │
│  [🔍 hledat]│  GRID KARET (2–4 sloupce, responzivní)           │
│              │  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  1  Instalac │  │ Lekce 1  │ │ Lekce 2  │ │ Lekce 3  │        │
│  2  REPL     │  │ Instalace│ │ REPL     │ │ Proměnné │        │
│  3  Proměnné │  │ 📄 🐍    │ │ 📄 🐍    │ │ 📄 🐍    │        │
│  4  Typy     │  └──────────┘ └──────────┘ └──────────┘        │
│  5  Řetězce  │  ...                                             │
│  ...         │                                                   │
│  (scroll)    │                                                   │
└──────────────┴──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Detail lekce (GET /lekce/1)                                    │
├──────────────┬──────────────────────────────────────────────────┤
│  SIDEBAR     │  TOPBAR: Lekce › Lekce 1  [🐍 Program] [←] [→] │
│  (stejný)    │  ─────────────────────────────────────────────── │
│              │  # Lekce 1: Instalace Pythonu, venv a pip        │
│  1 ◄ aktivní │                                                   │
│  2           │  ## Co je Python?                                 │
│  3           │  Představ si, že Python je kouzelný robot...      │
│  ...         │                                                   │
│              │  ```bash                                          │
│              │  python3 --version                                │
│              │  ```                                              │
│              │  (Markdown renderovaný jako HTML)                 │
└──────────────┴──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Program (GET /program/1)                                       │
├──────────────┬──────────────────────────────────────────────────┤
│  SIDEBAR     │  TOPBAR: Lekce › Lekce 1 › Program  [↩ Lekce]  │
│  (stejný)    │  ─────────────────────────────────────────────── │
│              │  Lekce 1: Instalace…   [l01_uv_demo.py]          │
│              │                                                   │
│              │  ┌── Pygments monokai syntax highlight ────────┐ │
│              │  │ import subprocess                            │ │
│              │  │ from pathlib import Path                     │ │
│              │  │ ...                                          │ │
│              │  └─────────────────────────────────────────────┘ │
└──────────────┴──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Vyhledávání (GET /hledej?q=dekorator)                          │
├──────────────┬──────────────────────────────────────────────────┤
│  SIDEBAR     │  TOPBAR: Lekce › Vyhledávání                    │
│  (stejný)    │  ─────────────────────────────────────────────── │
│              │  🔍 Hledání                                      │
│              │  [ dekorator                          ] [Hledat] │
│              │  Nalezeno výsledků: 4                            │
│              │  ─────────────────────────────────────────────── │
│              │  Lekce 26: Dekorátory                            │
│              │  …použití **dekorátoru** v praxi. Funkce…        │
│              │                                                   │
│              │  Lekce 27: functools                             │
│              │  …lru_cache je interně implementován jako…       │
└──────────────┴──────────────────────────────────────────────────┘
```

---

## Struktura projektu

```
projekty/14_kurz_reader/
├── app.py          ← celá aplikace (inline HTML šablony)
└── README.md       ← tato dokumentace

# Cesty k datům (relativní od app.py):
../../lekce/        → 131 souborů .md
../../programy/     → 131 souborů .py
```

---

## Technické poznámky

- **Inline šablony** — žádné externí `.html` soubory, vše v `app.py`
- **Dark theme** — VS Code–like paleta (`#1e1e1e` bg, monokai pro kód)
- **Graceful degradation** — funguje i bez `markdown2`/`pygments`
- **Cache** — seznam lekcí se parsuje jednou při prvním požadavku
- **Navigace** — sidebar se scrolluje na aktivní lekci, tlačítka ← →
- **Responzivní** — sidebar se skryje na mobilech (< 720 px)
