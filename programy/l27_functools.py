"""Lekce 27 — functools demo."""

from functools import cache, partial, reduce, singledispatch


@cache
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


@singledispatch
def popis(co) -> str:
    return f"Něco neznámého: {co!r}"


@popis.register
def _(co: int) -> str:
    return f"Číslo: {co}"


@popis.register
def _(co: str) -> str:
    return f"Text délky {len(co)}: {co!r}"


@popis.register
def _(co: list) -> str:
    return f"Seznam o {len(co)} prvcích"


def main() -> None:
    # Cache
    print(f"fib(100) = {fib(100)}")
    print(f"Cache info: {fib.cache_info()}")

    # Partial
    print_pomlckou = partial(print, sep="-")
    print_pomlckou("a", "b", "c", "d")

    ctverec = partial(pow, exp=2)
    print(f"\nctverec(7) = {ctverec(7)}")

    # Reduce — součin
    soucin = reduce(lambda a, b: a * b, range(1, 6))
    print(f"5! = {soucin}")

    # Singledispatch
    print()
    for x in [42, "ahoj", [1, 2, 3], 3.14]:
        print(popis(x))


if __name__ == "__main__":
    main()
