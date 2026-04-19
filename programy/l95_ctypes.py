"""Lekce 95 — ctypes demo."""

import ctypes
import sys


def main() -> None:
    if sys.platform.startswith("linux"):
        libc = ctypes.CDLL("libc.so.6")
    elif sys.platform == "darwin":
        libc = ctypes.CDLL("libc.dylib")
    else:
        print("Windows: zkus ctypes.CDLL('msvcrt')")
        return

    # abs z C
    libc.abs.restype = ctypes.c_int
    libc.abs.argtypes = [ctypes.c_int]
    print(f"libc.abs(-42) = {libc.abs(-42)}")


if __name__ == "__main__":
    main()
