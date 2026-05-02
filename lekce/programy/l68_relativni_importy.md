# Program — Lekce 68: Lekce 68: Relativní vs absolutní importy, kruhové importy

Patří k lekci [Lekce 68: Relativní vs absolutní importy, kruhové importy](../68_relativni_importy.md).

## Jak spustit

```bash
python3 programy/l68_relativni_importy.py
```

## Zdrojový kód

### `l68_relativni_importy.py`

```py
"""Lekce 68 — Relativní vs absolutní importy, kruhové importy."""

from __future__ import annotations

import importlib
import sys
import types


# ── Absolutní vs relativní importy — vysvětlení ──────────────────────────────

VYSVETLENI = """
Absolutní import:
    from muj_projekt.modul_a import funkce
    → plná cesta od kořene projektu, preferovaný způsob

Relativní import:
    from .modul_a import funkce       # ze stejného balíčku
    from ..jiny_balicek import x      # o úroveň výš
    → funguje JEN uvnitř balíčku, ne ve standalone skriptu
"""


# ── Simulace balíčkové struktury v paměti ────────────────────────────────────

def vytvor_fake_balik(nazev: str, kod: str) -> types.ModuleType:
    mod = types.ModuleType(nazev)
    exec(compile(kod, nazev, "exec"), mod.__dict__)
    sys.modules[nazev] = mod
    return mod


def demo_importy() -> None:
    print("--- Dynamický import (importlib) ---")

    # importlib.import_module — programatický absolutní import
    math = importlib.import_module("math")
    print(f"  math.pi = {math.pi:.4f}")

    os_path = importlib.import_module("os.path")
    print(f"  os.path.sep = {os_path.sep!r}")

    print("\n--- Podmíněný import (try/except) ---")
    try:
        import ujson as json_mod   # rychlejší varianta
        print("  Používám ujson")
    except ImportError:
        import json as json_mod    # fallback na stdlib
        print("  Používám stdlib json (ujson není nainstalován)")

    data = json_mod.dumps({"klíč": "hodnota", "číslo": 42})
    print(f"  {data}")

    print("\n--- Lazy import (import až při potřebě) ---")
    _heavy: types.ModuleType | None = None

    def nacti_heavy() -> types.ModuleType:
        nonlocal _heavy
        if _heavy is None:
            _heavy = importlib.import_module("statistics")
            print("  [statistics] načten (lazy)")
        return _heavy

    stats = nacti_heavy()
    print(f"  mean([1,2,3,4,5]) = {stats.mean([1, 2, 3, 4, 5])}")

    print("\n--- Introspekce importovaných modulů ---")
    for nazev, modul in list(sys.modules.items())[:5]:
        print(f"  {nazev}: {type(modul).__name__}")


# ── Kruhové importy — jak se vyhnout ─────────────────────────────────────────

def demo_kruhove_importy() -> None:
    print("\n--- Kruhové importy — simulace problému a řešení ---")

    # Problém: A importuje B, B importuje A → AttributeError
    print("""
  ❌ Kruhový import (problém):
     a.py: from b import funkce_b
     b.py: from a import funkce_a   ← Python A ještě nedokončil načítání!

  ✅ Řešení 1 — přesunout import dovnitř funkce:
     def funkce_b():
         from a import funkce_a    ← import při prvním volání, ne při načtení
         ...

  ✅ Řešení 2 — extrahovat sdílený kód do třetího modulu (common.py)

  ✅ Řešení 3 — TYPE_CHECKING guard (jen pro type hints):
     from __future__ import annotations
     from typing import TYPE_CHECKING
     if TYPE_CHECKING:
         from a import TypA        ← za běhu se nespustí
""")


# ── Přehled import systému ────────────────────────────────────────────────────

def demo_sys_path() -> None:
    print("--- sys.path — kde Python hledá moduly ---")
    for i, cesta in enumerate(sys.path[:5]):
        print(f"  [{i}] {cesta or '(aktuální adresář)'}")
    print(f"  ... celkem {len(sys.path)} cest")

    print("\n--- Počet načtených modulů ---")
    print(f"  sys.modules obsahuje {len(sys.modules)} modulů")


def main() -> None:
    print("=== Lekce 68: Importy ===")
    print(VYSVETLENI)
    demo_importy()
    demo_kruhove_importy()
    demo_sys_path()


if __name__ == "__main__":
    main()

```
