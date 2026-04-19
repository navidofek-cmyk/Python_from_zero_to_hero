"""Lekce 93 — timeit + cProfile."""

import cProfile
import io
import pstats
import timeit


def varianta_a(n: int) -> list[int]:
    return [x * x for x in range(n)]


def varianta_b(n: int) -> list[int]:
    return list(map(lambda x: x * x, range(n)))


def varianta_c(n: int) -> int:
    return sum(x * x for x in range(n))


def main() -> None:
    n = 100_000

    for fn in [varianta_a, varianta_b, varianta_c]:
        t = timeit.timeit(lambda: fn(n), number=20)
        print(f"  {fn.__name__:12s} {t:.3f}s")

    print("\n=== cProfile ===")
    pr = cProfile.Profile()
    pr.enable()
    varianta_a(1_000_000)
    pr.disable()
    s = io.StringIO()
    pstats.Stats(pr, stream=s).sort_stats("cumulative").print_stats(5)
    print(s.getvalue())


if __name__ == "__main__":
    main()
