# Lekce 87: Free-threaded Python (3.13+) a `subinterpreters`

## 🆕 Co je free-threaded Python?

Python 3.13 přinesl **experimentální build bez GILu** (PEP 703). Vlákna teď můžou běžet **opravdu paralelně**, i pro CPU.

```bash
# Build s no-GIL
./configure --disable-gil
make
```

Nebo distribuce: `python3.13t` (s `t` na konci = free-threaded).

```python
import sys
print(sys._is_gil_enabled())   # False na free-threaded buildu
```

---

## 🚀 Co se mění

✅ **CPU-bound threading** — efektivní, jako `multiprocessing` ale s sdílenou pamětí.
✅ Žádný overhead picklingu.
✅ Stejný API jako klasické threading.

⚠️ Knihovny musí být thread-safe (numpy, pandas se přizpůsobují).
⚠️ Trochu pomalejší jednovláknový kód (~5–10 %).

---

## 🆕 Subinterpreters (PEP 684, Python 3.12+)

**Subinterpreter** = další Python interpret v jednom procesu, **každý se svým GILem**.

```python
import _interpreters as interp

interp.run_string(interp.create(), "print('Ahoj z jiného interpretu')")
```

V Python 3.13+ stabilní API přes modul `interpreters`. Slibný směr — paralelismus bez procesů.

---

## 🎯 Co to znamená pro tebe

V 2026: free-threaded je **opt-in**. Většina knihoven se k tomu připravuje.

V 2027–2028: nejspíš se stane defaultem.

---

## 🆚 Souhrn — kdy co

| Úloha | 2025 | 2026+ free-threaded |
|---|---|---|
| I/O síťová | asyncio nebo threading | threading |
| CPU pure-Python | multiprocessing | threading (no-GIL) |
| CPU NumPy/PyTorch | thread-safe knihovna | totéž |
| Web server | gunicorn worker procesy | threads/asyncio |

---

## ✏️ Cvičení

1. **Zjisti:** Pusť `python -c "import sys; print(sys._is_gil_enabled())"`. Co máš?
2. **Free-threaded:** Pokud máš `python3.13t`, srovnej rychlost CPU úlohy v 4 vláknech vs 1.
3. **Sledování:** [PEP 703](https://peps.python.org/pep-0703/) si přečti pro přehled.
