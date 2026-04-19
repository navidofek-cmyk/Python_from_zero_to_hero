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
