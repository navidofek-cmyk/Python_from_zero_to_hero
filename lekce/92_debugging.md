# Lekce 92: Debugging — `pdb`, `breakpoint()`, `traceback`

## 🐛 `breakpoint()` — kouzelný stop

```python
def f(x):
    breakpoint()       # ← program se tady zastaví
    return x * 2
```

Dostaneš se do interaktivního debuggeru `pdb`. Můžeš:
- `n` (next) — další řádek
- `s` (step) — zanoř se do funkce
- `c` (continue) — pokračuj
- `l` (list) — zobraz okolní kód
- `p x` — vypiš proměnnou
- `pp x` — pretty print
- `w` (where) — zásobník volání
- `q` (quit) — konec

---

## 🛠️ `pdb.set_trace()` — starý styl

```python
import pdb; pdb.set_trace()
```

Stejné jako `breakpoint()`, ale starší. Použij `breakpoint()`.

---

## 🎨 Lepší debugger — `pdbpp`, `ipdb`

```bash
pip install pdbpp        # ihned hezčí
# nebo
pip install ipdb
PYTHONBREAKPOINT=ipdb.set_trace python ...
```

`PYTHONBREAKPOINT` — env proměnná určuje, **co `breakpoint()` zavolá**. Můžeš si zvolit.

---

## 📝 `traceback` — manuální zobrazení

```python
import traceback

try:
    1/0
except Exception:
    traceback.print_exc()              # na stderr
    s = traceback.format_exc()         # jako string
```

---

## 💥 `faulthandler` — chytí i C chyby

```python
import faulthandler
faulthandler.enable()
```

Když Python (nebo C rozšíření) shoří, vypíše stack trace místo tichého pádu.

---

## 🔍 `print` debugging — taky OK

Ne každý debugging vyžaduje `pdb`. Často stačí strategicky umístěný `print` nebo `logger.debug`.

```python
print(f"{x=}, {y=}")     # debug syntax (3.8+)
```

---

## 🪲 IDE debugger

VS Code, PyCharm — **breakpointy klikem**, watch window, condicial breakpoints. Pro velké projekty často lepší než `pdb`.

---

## 🚀 `rich.traceback` — krásné stack trace

```bash
pip install rich
```

```python
from rich.traceback import install
install(show_locals=True)
```

Tracebacky s **barvami** a **lokálními proměnnými**. Skvělé.

---

## 🎯 Strategie debugu

1. **Reprodukuj** problém minimálně (malý vstup co padá).
2. **Najdi obecný popis** — co je špatně.
3. **Hypotéza** kde je chyba.
4. **Ověř** přes print/breakpoint.
5. **Oprav.**
6. **Napiš test** aby se to nestalo zas.

---

## ✏️ Cvičení

1. **Breakpoint:** Vlož `breakpoint()` do funkce, projdi přes `n`, `p x`, `c`.
2. **Rich traceback:** Nainstaluj `rich`, vyvolej výjimku — porovnej s defaultem.
3. **PYTHONBREAKPOINT:** Nastav `PYTHONBREAKPOINT=0` — `breakpoint()` se vypne.
4. **Faulthandler:** Vyzkoušej `import faulthandler; faulthandler.enable()`.
