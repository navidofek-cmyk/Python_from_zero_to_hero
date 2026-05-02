# Program — Lekce 1: Lekce 1: Instalace Pythonu, venv a pip

Patří k lekci [Lekce 1: Instalace Pythonu, venv a pip](../01_instalace_venv_pip.md).

## Jak spustit

```bash
python3 programy/l01_uv_demo.py
```

## Zdrojový kód

### `l01_uv_demo.py`

```py
"""Lekce 1 — ukázka: skript ke spuštění uvnitř venv/uv prostředí.

Spuštění:
    python3 l01_uv_demo.py
nebo přes uv:
    uv run l01_uv_demo.py
"""

import sys
import platform


def main() -> None:
    print("🤖 Robot Python hlásí:")
    print(f"  Verze:    {sys.version.split()[0]}")
    print(f"  Platform: {platform.system()} {platform.release()}")
    print(f"  Cesta:    {sys.executable}")
    print()
    print("✨ Pokud cesta obsahuje '.venv' nebo 'uv', jsi v krabičce!")


if __name__ == "__main__":
    main()

```
