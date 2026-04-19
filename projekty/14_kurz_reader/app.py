"""
Projekt 14 — Kurz Reader
FastAPI aplikace pro procházení Python kurzu (131 lekcí).

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
    import markdown2  # pip install markdown2

    def render_markdown(text: str) -> str:
        return markdown2.markdown(
            text,
            extras=["fenced-code-blocks", "tables", "strike", "header-ids"],
        )

except ImportError:
    try:
        import mistune  # pip install mistune

        _md = mistune.create_markdown(plugins=["table", "strikethrough"])

        def render_markdown(text: str) -> str:  # type: ignore[misc]
            return _md(text)

    except ImportError:
        # Stdlib fallback — pouze escape + základní formátování
        import html as _html

        def render_markdown(text: str) -> str:  # type: ignore[misc]
            escaped = _html.escape(text)
            # Nadpisy
            escaped = re.sub(r"(?m)^### (.+)$", r"<h3>\1</h3>", escaped)
            escaped = re.sub(r"(?m)^## (.+)$", r"<h2>\1</h2>", escaped)
            escaped = re.sub(r"(?m)^# (.+)$", r"<h1>\1</h1>", escaped)
            # Code bloky
            escaped = re.sub(
                r"```[a-z]*\n(.*?)```",
                r"<pre><code>\1</code></pre>",
                escaped,
                flags=re.DOTALL,
            )
            # Inline kód
            escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
            # Tučné / kurzíva
            escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
            escaped = re.sub(r"\*(.+?)\*", r"<em>\1</em>", escaped)
            # Odstavce (prázdný řádek = oddělovač)
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

    def highlight_python(code: str) -> str:  # type: ignore[misc]
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
    """Vrátí seřazený seznam slovníků s info o každé lekci."""
    lekce: list[dict] = []
    for md_file in LEKCE_DIR.glob("[0-9]*.md"):
        stem = md_file.stem  # např. "01_instalace_venv_pip"
        match = re.match(r"^(\d+)_(.*)", stem)
        if not match:
            continue
        cislo = int(match.group(1))
        slug = match.group(2)
        nazev_slug = slug.replace("_", " ").capitalize()

        # Zkus přečíst první nadpis ze souboru
        try:
            first_line = md_file.read_text(encoding="utf-8").split("\n")[0]
            if first_line.startswith("# "):
                nazev = first_line[2:].strip()
            else:
                nazev = f"Lekce {cislo}: {nazev_slug}"
        except Exception:
            nazev = f"Lekce {cislo}: {nazev_slug}"

        # Kontrola existence .py souboru
        py_file = PROGRAMY_DIR / f"l{cislo:02d}_{slug}.py"
        # Zkus také bez paddingu
        py_candidates = list(PROGRAMY_DIR.glob(f"l{cislo}_*.py")) + list(
            PROGRAMY_DIR.glob(f"l{cislo:02d}_*.py")
        ) + list(PROGRAMY_DIR.glob(f"l{cislo:03d}_*.py"))
        ma_program = len(py_candidates) > 0

        lekce.append(
            {
                "cislo": cislo,
                "slug": slug,
                "nazev": nazev,
                "md_soubor": md_file.name,
                "ma_program": ma_program,
                "py_soubor": py_candidates[0].name if ma_program else None,
            }
        )
    return sorted(lekce, key=lambda x: x["cislo"])


def _najdi_md(cislo: int) -> Optional[Path]:
    results = list(LEKCE_DIR.glob(f"{cislo:02d}_*.md")) + list(
        LEKCE_DIR.glob(f"{cislo:03d}_*.md")
    ) + list(LEKCE_DIR.glob(f"{cislo}_*.md"))
    return results[0] if results else None


def _najdi_py(cislo: int) -> Optional[Path]:
    results = list(PROGRAMY_DIR.glob(f"l{cislo:02d}_*.py")) + list(
        PROGRAMY_DIR.glob(f"l{cislo:03d}_*.py")
    ) + list(PROGRAMY_DIR.glob(f"l{cislo}_*.py"))
    return results[0] if results else None


# ---------------------------------------------------------------------------
# HTML šablony (inline)
# ---------------------------------------------------------------------------

def _base_html(
    title: str,
    content: str,
    sidebar_items: list[dict],
    active_cislo: Optional[int] = None,
    extra_head: str = "",
) -> str:
    sidebar_links = []
    for item in sidebar_items:
        active_class = ' class="active"' if item["cislo"] == active_cislo else ""
        icon = "📄" if not item["ma_program"] else "🐍"
        sidebar_links.append(
            f'<li{active_class}>'
            f'<a href="/lekce/{item["cislo"]}" title="{item["nazev"]}">'
            f'<span class="num">{item["cislo"]}</span>'
            f'<span class="tit">{item["nazev"]}</span>'
            f"</a></li>"
        )
    sidebar_html = "\n".join(sidebar_links)

    return f"""<!DOCTYPE html>
<html lang="cs">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Python Kurz Reader</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg:        #1e1e1e;
      --bg2:       #252526;
      --bg3:       #2d2d30;
      --border:    #3e3e42;
      --accent:    #569cd6;
      --accent2:   #4ec9b0;
      --text:      #d4d4d4;
      --text-dim:  #858585;
      --green:     #6a9955;
      --yellow:    #dcdcaa;
      --red:       #f44747;
      --sidebar-w: 280px;
    }}

    html, body {{
      height: 100%;
      background: var(--bg);
      color: var(--text);
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      font-size: 15px;
      line-height: 1.6;
    }}

    /* ---- Layout ---- */
    .layout {{
      display: flex;
      height: 100vh;
      overflow: hidden;
    }}

    /* ---- Sidebar ---- */
    .sidebar {{
      width: var(--sidebar-w);
      min-width: var(--sidebar-w);
      background: var(--bg2);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}
    .sidebar-header {{
      padding: 16px 12px 12px;
      border-bottom: 1px solid var(--border);
      flex-shrink: 0;
    }}
    .sidebar-header h1 {{
      font-size: 13px;
      font-weight: 600;
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: .08em;
      margin-bottom: 8px;
    }}
    .sidebar-header a.home-link {{
      display: block;
      color: var(--text-dim);
      text-decoration: none;
      font-size: 12px;
      margin-bottom: 6px;
    }}
    .sidebar-header a.home-link:hover {{ color: var(--text); }}

    .search-box {{
      width: 100%;
      background: var(--bg3);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 6px 8px;
      border-radius: 4px;
      font-size: 12px;
      outline: none;
    }}
    .search-box:focus {{ border-color: var(--accent); }}

    .sidebar-list {{
      overflow-y: auto;
      flex: 1;
      padding: 4px 0;
    }}
    .sidebar-list::-webkit-scrollbar {{ width: 6px; }}
    .sidebar-list::-webkit-scrollbar-track {{ background: var(--bg2); }}
    .sidebar-list::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}

    .sidebar-list ul {{ list-style: none; }}
    .sidebar-list li a {{
      display: flex;
      align-items: baseline;
      gap: 6px;
      padding: 5px 12px;
      text-decoration: none;
      color: var(--text-dim);
      font-size: 12px;
      border-left: 2px solid transparent;
      transition: background .1s, color .1s;
      white-space: nowrap;
      overflow: hidden;
    }}
    .sidebar-list li a:hover {{
      background: var(--bg3);
      color: var(--text);
    }}
    .sidebar-list li.active a {{
      background: var(--bg3);
      color: var(--accent);
      border-left-color: var(--accent);
    }}
    .sidebar-list li a .num {{
      min-width: 26px;
      color: var(--text-dim);
      font-size: 11px;
      flex-shrink: 0;
    }}
    .sidebar-list li.active a .num {{ color: var(--accent); }}
    .sidebar-list li a .tit {{
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}

    /* ---- Main content ---- */
    .main {{
      flex: 1;
      overflow-y: auto;
      padding: 0;
      display: flex;
      flex-direction: column;
    }}
    .main::-webkit-scrollbar {{ width: 8px; }}
    .main::-webkit-scrollbar-track {{ background: var(--bg); }}
    .main::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 4px; }}

    .topbar {{
      position: sticky;
      top: 0;
      background: var(--bg2);
      border-bottom: 1px solid var(--border);
      padding: 10px 24px;
      display: flex;
      align-items: center;
      gap: 12px;
      z-index: 10;
      flex-shrink: 0;
    }}
    .topbar .breadcrumb {{
      font-size: 12px;
      color: var(--text-dim);
    }}
    .topbar .breadcrumb a {{
      color: var(--accent);
      text-decoration: none;
    }}
    .topbar .breadcrumb a:hover {{ text-decoration: underline; }}
    .topbar .nav-btns {{
      margin-left: auto;
      display: flex;
      gap: 8px;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 5px 12px;
      border-radius: 4px;
      font-size: 12px;
      text-decoration: none;
      border: 1px solid var(--border);
      color: var(--text);
      background: var(--bg3);
      cursor: pointer;
      transition: background .1s, border-color .1s;
    }}
    .btn:hover {{ background: var(--border); border-color: var(--accent); }}
    .btn.primary {{ background: var(--accent); color: #1e1e1e; border-color: var(--accent); }}
    .btn.primary:hover {{ background: #6ab0eb; }}

    .content-area {{
      padding: 28px 40px 60px;
      max-width: 900px;
      width: 100%;
    }}

    /* ---- Markdown styles ---- */
    .md-content h1 {{ font-size: 1.8em; color: var(--yellow); margin: 0 0 16px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
    .md-content h2 {{ font-size: 1.3em; color: var(--accent2); margin: 28px 0 10px; }}
    .md-content h3 {{ font-size: 1.1em; color: var(--accent); margin: 20px 0 8px; }}
    .md-content h4 {{ font-size: 1em; color: var(--text); margin: 16px 0 6px; }}
    .md-content p {{ margin: 0 0 12px; }}
    .md-content ul, .md-content ol {{ margin: 0 0 12px 24px; }}
    .md-content li {{ margin: 3px 0; }}
    .md-content a {{ color: var(--accent); }}
    .md-content a:hover {{ color: var(--accent2); }}
    .md-content code {{
      background: var(--bg3);
      border: 1px solid var(--border);
      padding: 1px 5px;
      border-radius: 3px;
      font-family: 'Cascadia Code', 'Fira Code', Consolas, monospace;
      font-size: .88em;
      color: var(--accent2);
    }}
    .md-content pre {{
      background: var(--bg3);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 14px 16px;
      overflow-x: auto;
      margin: 0 0 16px;
    }}
    .md-content pre code {{
      background: none;
      border: none;
      padding: 0;
      color: var(--text);
      font-size: .87em;
    }}
    .md-content blockquote {{
      border-left: 3px solid var(--accent);
      padding: 8px 16px;
      margin: 0 0 12px;
      background: var(--bg3);
      border-radius: 0 4px 4px 0;
      color: var(--text-dim);
    }}
    .md-content table {{
      border-collapse: collapse;
      width: 100%;
      margin: 0 0 16px;
    }}
    .md-content th {{
      background: var(--bg3);
      border: 1px solid var(--border);
      padding: 7px 12px;
      text-align: left;
      color: var(--accent);
      font-size: .9em;
    }}
    .md-content td {{
      border: 1px solid var(--border);
      padding: 6px 12px;
      font-size: .9em;
    }}
    .md-content tr:nth-child(even) td {{ background: var(--bg2); }}
    .md-content hr {{ border: none; border-top: 1px solid var(--border); margin: 20px 0; }}
    .md-content strong {{ color: var(--yellow); }}
    .md-content em {{ color: var(--text-dim); font-style: italic; }}

    /* Pygments (monokai) wrapper */
    .highlight {{
      background: #272822 !important;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 14px 16px;
      overflow-x: auto;
      margin: 0 0 16px;
      font-family: 'Cascadia Code', 'Fira Code', Consolas, monospace;
      font-size: .87em;
      line-height: 1.5;
    }}
    .plain-code {{
      background: var(--bg3);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 14px 16px;
      overflow-x: auto;
      font-family: 'Cascadia Code', 'Fira Code', Consolas, monospace;
      font-size: .87em;
      line-height: 1.5;
    }}

    /* ---- Index page ---- */
    .lekce-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 10px;
      margin-top: 20px;
    }}
    .lekce-card {{
      background: var(--bg2);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 12px 14px;
      transition: border-color .15s, background .15s;
    }}
    .lekce-card:hover {{
      border-color: var(--accent);
      background: var(--bg3);
    }}
    .lekce-card a {{
      text-decoration: none;
      color: var(--text);
      display: block;
    }}
    .lekce-card .card-num {{
      font-size: 11px;
      color: var(--text-dim);
      margin-bottom: 4px;
    }}
    .lekce-card .card-title {{
      font-size: 13px;
      color: var(--accent);
      margin-bottom: 6px;
      line-height: 1.4;
    }}
    .lekce-card .card-badges {{
      display: flex;
      gap: 6px;
    }}
    .badge {{
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 3px;
      border: 1px solid var(--border);
      color: var(--text-dim);
    }}
    .badge.py {{ border-color: var(--accent2); color: var(--accent2); }}

    /* ---- Search results ---- */
    .search-result {{
      background: var(--bg2);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 14px 16px;
      margin-bottom: 10px;
    }}
    .search-result:hover {{ border-color: var(--accent); }}
    .search-result h3 {{ font-size: 14px; margin-bottom: 6px; }}
    .search-result h3 a {{ color: var(--accent); text-decoration: none; }}
    .search-result h3 a:hover {{ text-decoration: underline; }}
    .search-result .snippet {{
      font-size: 12px;
      color: var(--text-dim);
      line-height: 1.5;
    }}
    .search-result .snippet mark {{
      background: #3a3a00;
      color: var(--yellow);
      border-radius: 2px;
      padding: 0 2px;
    }}

    /* ---- Hero (index) ---- */
    .hero {{
      background: linear-gradient(135deg, #1a3a5c 0%, #1e1e1e 60%);
      border-bottom: 1px solid var(--border);
      padding: 28px 40px 20px;
    }}
    .hero h1 {{ font-size: 1.6em; color: var(--accent); margin-bottom: 6px; }}
    .hero p {{ color: var(--text-dim); font-size: 13px; }}
    .hero .stats {{
      display: flex;
      gap: 20px;
      margin-top: 12px;
    }}
    .hero .stat {{
      font-size: 12px;
      color: var(--text-dim);
    }}
    .hero .stat span {{ color: var(--accent2); font-weight: 600; }}

    /* ---- Program view ---- */
    .program-header {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
    }}
    .file-badge {{
      background: var(--bg3);
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 3px 8px;
      font-size: 11px;
      font-family: monospace;
      color: var(--text-dim);
    }}

    /* ---- Responsivní ---- */
    @media (max-width: 720px) {{
      .sidebar {{ display: none; }}
      .content-area {{ padding: 16px 16px 40px; }}
      .topbar {{ padding: 8px 16px; }}
      .hero {{ padding: 16px; }}
    }}
  </style>
  {extra_head}
</head>
<body>
<div class="layout">
  <aside class="sidebar">
    <div class="sidebar-header">
      <h1>Python Kurz</h1>
      <a class="home-link" href="/">↩ Všechny lekce</a>
      <input
        class="search-box"
        type="search"
        placeholder="Hledat v lekcích…"
        id="quick-search"
        onkeydown="if(event.key==='Enter')window.location='/hledej?q='+encodeURIComponent(this.value)"
      >
    </div>
    <nav class="sidebar-list">
      <ul>{sidebar_html}</ul>
    </nav>
  </aside>
  <div class="main">
    {content}
  </div>
</div>
<script>
  // Scroll aktivní položku do viditelné oblasti
  const active = document.querySelector('.sidebar-list li.active a');
  if (active) active.scrollIntoView({{block: 'center'}});
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Python Kurz Reader",
    description="Web reader pro Python kurz From Zero to Hero",
    version="1.0.0",
)

# Cachujeme seznam lekcí při startu
_LEKCE_CACHE: list[dict] = []


def get_lekce() -> list[dict]:
    global _LEKCE_CACHE
    if not _LEKCE_CACHE:
        _LEKCE_CACHE = _parse_lekce_soubory()
    return _LEKCE_CACHE


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    """Hlavní stránka — seznam všech lekcí."""
    lekce = get_lekce()

    cards = []
    for item in lekce:
        py_badge = (
            '<span class="badge py">🐍 program</span>' if item["ma_program"] else ""
        )
        cards.append(
            f'<div class="lekce-card">'
            f'<a href="/lekce/{item["cislo"]}">'
            f'<div class="card-num">Lekce {item["cislo"]}</div>'
            f'<div class="card-title">{item["nazev"]}</div>'
            f'<div class="card-badges">'
            f'<span class="badge">📄 lekce</span>'
            f"{py_badge}"
            f"</div>"
            f"</a></div>"
        )

    grid = f'<div class="lekce-grid">{"".join(cards)}</div>'

    hero = f"""
    <div class="hero">
      <h1>🐍 Python: From Zero to Hero</h1>
      <p>Kompletní kurz Pythonu v češtině — od absolutních základů po senior/architect úroveň.</p>
      <div class="stats">
        <div class="stat">Lekcí: <span>{len(lekce)}</span></div>
        <div class="stat">Programů: <span>{sum(1 for l in lekce if l["ma_program"])}</span></div>
      </div>
    </div>
    <div class="content-area">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
        <h2 style="color:var(--accent2);font-size:1.1em;">Všechny lekce</h2>
        <form method="get" action="/hledej" style="margin-left:auto;display:flex;gap:6px;">
          <input name="q" class="search-box" style="width:200px;" placeholder="Fulltext hledání…">
          <button type="submit" class="btn primary">Hledat</button>
        </form>
      </div>
      {grid}
    </div>
    """

    return _base_html("Všechny lekce", hero, lekce)


@app.get("/lekce/{cislo}", response_class=HTMLResponse)
async def lekce_detail(cislo: int) -> str:
    """Detail lekce — renderovaný Markdown."""
    lekce = get_lekce()
    md_path = _najdi_md(cislo)
    if md_path is None:
        raise HTTPException(status_code=404, detail=f"Lekce {cislo} nenalezena")

    raw = md_path.read_text(encoding="utf-8")
    html_body = render_markdown(raw)

    # Navigace prev/next
    cisla = [l["cislo"] for l in lekce]
    idx = cisla.index(cislo) if cislo in cisla else -1
    prev_link = (
        f'<a class="btn" href="/lekce/{cisla[idx-1]}">← {cisla[idx-1]}</a>'
        if idx > 0
        else '<span></span>'
    )
    next_link = (
        f'<a class="btn" href="/lekce/{cisla[idx+1]}">{cisla[idx+1]} →</a>'
        if idx >= 0 and idx < len(cisla) - 1
        else '<span></span>'
    )

    # Tlačítko na program
    py_btn = ""
    py_path = _najdi_py(cislo)
    if py_path:
        py_btn = f'<a class="btn primary" href="/program/{cislo}">🐍 Zobrazit program</a>'

    # Nadpis ze souboru
    nazev = next((l["nazev"] for l in lekce if l["cislo"] == cislo), f"Lekce {cislo}")

    topbar = f"""
    <div class="topbar">
      <div class="breadcrumb">
        <a href="/">Lekce</a> › <strong style="color:var(--text);">Lekce {cislo}</strong>
      </div>
      <div class="nav-btns">
        {py_btn}
        {prev_link}
        {next_link}
      </div>
    </div>
    """

    content = f"""
    {topbar}
    <div class="content-area">
      <div class="md-content">{html_body}</div>
    </div>
    """

    return _base_html(nazev, content, lekce, active_cislo=cislo)


@app.get("/program/{cislo}", response_class=HTMLResponse)
async def program_detail(cislo: int) -> str:
    """Zobrazení zdrojového kódu programu se zvýrazněním syntaxe."""
    lekce = get_lekce()
    py_path = _najdi_py(cislo)
    if py_path is None:
        raise HTTPException(status_code=404, detail=f"Program pro lekci {cislo} nenalezen")

    code = py_path.read_text(encoding="utf-8")
    highlighted = highlight_python(code)

    nazev = next((l["nazev"] for l in lekce if l["cislo"] == cislo), f"Lekce {cislo}")

    topbar = f"""
    <div class="topbar">
      <div class="breadcrumb">
        <a href="/">Lekce</a> ›
        <a href="/lekce/{cislo}">Lekce {cislo}</a> ›
        <strong style="color:var(--text);">Program</strong>
      </div>
      <div class="nav-btns">
        <a class="btn" href="/lekce/{cislo}">📄 Zpět na lekci</a>
      </div>
    </div>
    """

    content = f"""
    {topbar}
    <div class="content-area">
      <div class="program-header">
        <h2 style="color:var(--yellow);font-size:1.1em;">{nazev}</h2>
        <span class="file-badge">{py_path.name}</span>
      </div>
      {highlighted}
    </div>
    """

    extra_head = f"<style>{_PYGMENTS_CSS}</style>" if _PYGMENTS_CSS else ""
    return _base_html(f"Program — {nazev}", content, lekce, active_cislo=cislo, extra_head=extra_head)


@app.get("/hledej", response_class=HTMLResponse)
async def hledej(q: str = Query(default="", min_length=0)) -> str:
    """Fulltext vyhledávání přes všechny .md soubory."""
    lekce = get_lekce()
    q = q.strip()
    results = []

    if q:
        q_lower = q.lower()
        for item in lekce:
            md_path = _najdi_md(item["cislo"])
            if md_path is None:
                continue
            try:
                text = md_path.read_text(encoding="utf-8")
            except Exception:
                continue

            if q_lower not in text.lower():
                continue

            # Najdi úryvek kolem prvního výskytu
            pos = text.lower().find(q_lower)
            start = max(0, pos - 120)
            end = min(len(text), pos + 120)
            snippet = text[start:end].replace("\n", " ").strip()

            # Zvýrazni hledaný výraz (case-insensitive)
            import html as _html_mod
            snippet_esc = _html_mod.escape(snippet)
            snippet_hl = re.sub(
                re.escape(_html_mod.escape(q)),
                lambda m: f"<mark>{m.group()}</mark>",
                snippet_esc,
                flags=re.IGNORECASE,
            )

            results.append(
                f'<div class="search-result">'
                f'<h3><a href="/lekce/{item["cislo"]}">Lekce {item["cislo"]}: {item["nazev"]}</a></h3>'
                f'<div class="snippet">…{snippet_hl}…</div>'
                f"</div>"
            )

    results_html = "".join(results) if results else (
        f'<p style="color:var(--text-dim);">Žádné výsledky pro „{q}".</p>' if q else ""
    )

    topbar = """
    <div class="topbar">
      <div class="breadcrumb"><a href="/">Lekce</a> › Vyhledávání</div>
    </div>
    """

    content = f"""
    {topbar}
    <div class="content-area">
      <h2 style="color:var(--accent2);font-size:1.2em;margin-bottom:16px;">🔍 Hledání</h2>
      <form method="get" action="/hledej" style="display:flex;gap:8px;margin-bottom:20px;">
        <input
          name="q"
          class="search-box"
          style="flex:1;font-size:14px;padding:8px 12px;"
          placeholder="Zadejte hledaný výraz…"
          value="{q}"
          autofocus
        >
        <button type="submit" class="btn primary" style="padding:8px 16px;">Hledat</button>
      </form>
      {"<p style='color:var(--text-dim);font-size:13px;margin-bottom:16px;'>Nalezeno výsledků: <strong style='color:var(--accent2);'>" + str(len(results)) + "</strong></p>" if q and results else ""}
      {results_html}
    </div>
    """

    return _base_html("Hledání", content, lekce)


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


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
