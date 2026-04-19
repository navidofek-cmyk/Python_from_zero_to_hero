"""Lekce 87 — kontrola GIL stavu."""

import sys


def main() -> None:
    print(f"Python: {sys.version}")
    if hasattr(sys, "_is_gil_enabled"):
        print(f"GIL enabled: {sys._is_gil_enabled()}")
    else:
        print("GIL je vždy enabled (Python <3.13).")


if __name__ == "__main__":
    main()
