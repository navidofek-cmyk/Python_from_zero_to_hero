"""Lekce 92 — debugger demo.

Spuštění:
    python3 l92_breakpoint_demo.py
    (V breakpointu zkus: l, p x, p y, n, c)
"""


def vypocet(x: int) -> int:
    y = x * 2
    z = y + 10
    # Odkomentuj pro debugger:
    # breakpoint()
    return z * x


def main() -> None:
    print(f"vypocet(5) = {vypocet(5)}")


if __name__ == "__main__":
    main()
