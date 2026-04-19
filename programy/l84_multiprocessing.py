"""Lekce 84 — multiprocessing pool."""

import multiprocessing as mp
import time


def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def main() -> None:
    cisla = [33, 34, 35, 33]   # CPU bound

    start = time.perf_counter()
    [fib(n) for n in cisla]
    sekvenc = time.perf_counter() - start

    start = time.perf_counter()
    with mp.Pool(processes=4) as pool:
        pool.map(fib, cisla)
    paralel = time.perf_counter() - start

    print(f"Sekvenčně:  {sekvenc:.2f}s")
    print(f"Paralelně:  {paralel:.2f}s ({sekvenc/paralel:.1f}× rychlejší)")


if __name__ == "__main__":
    main()
