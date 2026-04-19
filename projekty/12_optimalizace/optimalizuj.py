"""Mini-projekt po sekci XII: Najdi a oprav výkonový bottleneck.

Procvičuje: profilování (cProfile), measurement (timeit), optimization triky.
"""

import cProfile
import pstats
import time
from collections import Counter


# ❌ Pomalá verze
def pomalu(text: str) -> dict[str, int]:
    pocty = {}
    for slovo in text.split():
        if slovo in pocty:
            pocty[slovo] = pocty[slovo] + 1
        else:
            pocty[slovo] = 1
    return pocty


# ✅ Rychlá verze
def rychle(text: str) -> dict[str, int]:
    return dict(Counter(text.split()))


def vyrob_text(slov: int = 100_000) -> str:
    import random
    slovnik = ["pes", "kočka", "myš", "slon", "ryba", "pták", "králík"]
    return " ".join(random.choice(slovnik) for _ in range(slov))


def main() -> None:
    text = vyrob_text(200_000)

    for fn in [pomalu, rychle]:
        start = time.perf_counter()
        vysledek = fn(text)
        cas = time.perf_counter() - start
        print(f"{fn.__name__:8s}: {cas*1000:.1f} ms ({len(vysledek)} unik)")

    print("\n=== Profile pomalu ===")
    pr = cProfile.Profile()
    pr.enable()
    pomalu(text)
    pr.disable()
    pstats.Stats(pr).sort_stats("cumulative").print_stats(8)


if __name__ == "__main__":
    main()
