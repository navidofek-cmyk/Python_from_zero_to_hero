# Projekt 14: Python Kurz Reader

FastAPI webová aplikace pro pohodlné procházení tohoto kurzu. Zobrazuje lekce jako renderovaný Markdown, zdrojové kódy se zvýrazněním syntaxe a umožňuje fulltext vyhledávání.

**Použité koncepty:** FastAPI (97), Markdown rendering, Pygments syntax highlighting, fulltext search, responsive HTML/CSS inline šablony.

## Jak spustit

```bash
pip install "fastapi[standard]" markdown2 pygments
fastapi dev projekty/14_kurz_reader/app.py --port 8080
```

Otevři: [http://localhost:8080](http://localhost:8080)

## API endpointy

| Endpoint | Popis |
|----------|-------|
| `GET /` | Hlavní stránka — grid karet lekcí |
| `GET /lekce/{cislo}` | Detail lekce — Markdown → HTML |
| `GET /program/{cislo}` | Zdrojový kód s Pygments |
| `GET /hledej?q=xxx` | Fulltext vyhledávání |
| `GET /api/lekce` | JSON seznam lekcí s metadaty |

## Závislosti

| Balíček | Účel | Fallback |
|---------|------|---------|
| `fastapi[standard]` | Web framework | — povinné |
| `markdown2` | Markdown → HTML | stdlib regex fallback |
| `pygments` | Syntax highlighting | prostý `<pre>` |

## Zdrojový kód — `app.py`

```python
"""
Projekt 14 — Kurz Reader
FastAPI aplikace pro procházení Python kurzu (134 lekcí).

Spuštění:
    fastapi dev app.py
    # nebo
    uvicorn app:app --reload --port 8080
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse

# ---------------------------------------------------------------------------
# Volitelné závislosti — graceful fallback
# ---------------------------------------------------------------------------
try:
    import markdown2

    def render_markdown(text: str) -> str:
        return markdown2.markdown(
            text,
            extras=["fenced-code-blocks", "tables", "strike", "header-ids"],
        )

except ImportError:
    try:
        import mistune

        _md = mistune.create_markdown(plugins=["table", "strikethrough"])

        def render_markdown(text: str) -> str:
            return _md(text)

    except ImportError:
        import html as _html

        def render_markdown(text: str) -> str:
            escaped = _html.escape(text)
            escaped = re.sub(r"(?m)^### (.+)$", r"<h3>\1</h3>", escaped)
            escaped = re.sub(r"(?m)^## (.+)$", r"<h2>\1</h2>", escaped)
            escaped = re.sub(r"(?m)^# (.+)$", r"<h1>\1</h1>", escaped)
            escaped = re.sub(
                r"```[a-z]*\n(.*?)```",
                r"<pre><code>\1</code></pre>",
                escaped,
                flags=re.DOTALL,
            )
            escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
            escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
            escaped = re.sub(r"\*(.+?)\*", r"<em>\1</em>", escaped)
            parts = re.split(r"\n{2,}", escaped)
            result = []
            for p in parts:
                p = p.strip()
                if not p:
                    continue
                if p.startswith(("<h", "<pre", "<ul", "<ol", "<li")):
                    result.append(p)
                else:
                    result.append(f"<p>{p}</p>")
            return "\n".join(result)


try:
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import PythonLexer

    _PYGMENTS_CSS = HtmlFormatter(style="monokai").get_style_defs(".highlight")

    def highlight_python(code: str) -> str:
        return highlight(code, PythonLexer(), HtmlFormatter(style="monokai"))

except ImportError:
    import html as _html2

    _PYGMENTS_CSS = ""

    def highlight_python(code: str) -> str:
        return f'<pre class="plain-code"><code>{_html2.escape(code)}</code></pre>'


# ---------------------------------------------------------------------------
# Cesty
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
LEKCE_DIR = (BASE_DIR / "../../lekce").resolve()
PROGRAMY_DIR = (BASE_DIR / "../../programy").resolve()

# ---------------------------------------------------------------------------
# Parsování souborů lekcí
# ---------------------------------------------------------------------------

def _parse_lekce_soubory() -> list[dict]:
    lekce: list[dict] = []
    for md_file in LEKCE_DIR.glob("[0-9]*.md"):
        stem = md_file.stem
        match = re.match(r"^(\d+)_(.*)", stem)
        if not match:
            continue
        cislo = int(match.group(1))
        slug = match.group(2)
        nazev_slug = slug.replace("_", " ").capitalize()

        try:
            first_line = md_file.read_text(encoding="utf-8").split("\n")[0]
            if first_line.startswith("# "):
                nazev = first_line[2:].strip()
            else:
                nazev = f"Lekce {cislo}: {nazev_slug}"
        except Exception:
            nazev = f"Lekce {cislo}: {nazev_slug}"

        py_candidates = (
            list(PROGRAMY_DIR.glob(f"l{cislo}_*.py"))
            + list(PROGRAMY_DIR.glob(f"l{cislo:02d}_*.py"))
            + list(PROGRAMY_DIR.glob(f"l{cislo:03d}_*.py"))
        )
        ma_program = len(py_candidates) > 0

        lekce.append({
            "cislo": cislo,
            "slug": slug,
            "nazev": nazev,
            "md_soubor": md_file.name,
            "ma_program": ma_program,
            "py_soubor": py_candidates[0].name if ma_program else None,
        })
    return sorted(lekce, key=lambda x: x["cislo"])


def _najdi_md(cislo: int) -> Optional[Path]:
    results = (
        list(LEKCE_DIR.glob(f"{cislo:02d}_*.md"))
        + list(LEKCE_DIR.glob(f"{cislo:03d}_*.md"))
        + list(LEKCE_DIR.glob(f"{cislo}_*.md"))
    )
    return results[0] if results else None


def _najdi_py(cislo: int) -> Optional[Path]:
    results = (
        list(PROGRAMY_DIR.glob(f"l{cislo:02d}_*.py"))
        + list(PROGRAMY_DIR.glob(f"l{cislo:03d}_*.py"))
        + list(PROGRAMY_DIR.glob(f"l{cislo}_*.py"))
    )
    return results[0] if results else None


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Python Kurz Reader",
    description="Web reader pro Python kurz From Zero to Hero",
    version="1.0.0",
)

_LEKCE_CACHE: list[dict] = []


def get_lekce() -> list[dict]:
    global _LEKCE_CACHE
    if not _LEKCE_CACHE:
        _LEKCE_CACHE = _parse_lekce_soubory()
    return _LEKCE_CACHE


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    """Hlavní stránka — seznam všech lekcí."""
    lekce = get_lekce()
    # ... (inline HTML šablony — viz kompletní zdrojový kód v repozitáři)
    return f"<h1>Python Kurz Reader — {len(lekce)} lekcí</h1>"


@app.get("/api/lekce", response_class=JSONResponse)
async def api_lekce() -> list[dict]:
    """JSON API — seznam všech lekcí."""
    lekce = get_lekce()
    return [
        {
            "cislo": l["cislo"],
            "nazev": l["nazev"],
            "md_soubor": l["md_soubor"],
            "ma_program": l["ma_program"],
            "py_soubor": l["py_soubor"],
            "url_lekce": f"/lekce/{l['cislo']}",
            "url_program": f"/program/{l['cislo']}" if l["ma_program"] else None,
        }
        for l in lekce
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
```

!!! note "Kompletní zdrojový kód"
    Soubor `app.py` obsahuje přes 900 řádků inline HTML/CSS šablon. Kompletní verze je v repozitáři: `projekty/14_kurz_reader/app.py`.
