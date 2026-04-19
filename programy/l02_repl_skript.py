"""Lekce 2 — ukázka skriptu s `if __name__ == "__main__"`.

Spustíš přímo:        python3 l02_repl_skript.py
Importuješ jinde:     from l02_repl_skript import dvojnasobek
"""


def dvojnasobek(x: int) -> int:
    return x * 2


def trojnasobek(x: int) -> int:
    return x * 3


if __name__ == "__main__":
    print("🚀 Skript spuštěný přímo!")
    print(f"dvojnasobek(7) = {dvojnasobek(7)}")
    print(f"trojnasobek(7) = {trojnasobek(7)}")
