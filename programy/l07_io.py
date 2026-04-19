"""Lekce 7 — vstup, výstup, sep, end, flush."""

import sys
import time


def main() -> None:
    # Tisk se sep
    print("a", "b", "c", sep="-")          # a-b-c
    print("První", "Druhá", "Třetí", sep="\n")

    # Animace teček
    print("\nNačítám", end="", flush=True)
    for _ in range(5):
        print(".", end="", flush=True)
        time.sleep(0.3)
    print(" hotovo!")

    # Tisk do stderr
    print("Toto je chybová hláška", file=sys.stderr)

    # Vstup s převodem
    a = int(input("\nPrvní číslo: "))
    b = int(input("Druhé číslo: "))
    print(f"{a} + {b} = {a + b}")
    print(f"{a} * {b} = {a * b}")


if __name__ == "__main__":
    main()
