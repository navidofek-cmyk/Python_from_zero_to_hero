"""Lekce 52 — generátory."""

from typing import Iterator


def fibonacci() -> Iterator[int]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def jen_suda(it):
    for x in it:
        if x % 2 == 0:
            yield x


def na_druhou(it):
    for x in it:
        yield x * x


def main() -> None:
    fib = fibonacci()
    print("Prvních 10 Fibonacci:", [next(fib) for _ in range(10)])

    # Pipeline
    pipeline = na_druhou(jen_suda(range(20)))
    print(f"Sudá^2 (do 19): {list(pipeline)}")

    # Úspora paměti
    soucet = sum(x * x for x in range(1_000_000))
    print(f"Σ čtverců (0..1M): {soucet:,}")


if __name__ == "__main__":
    main()
