# Program — Lekce 94: Lekce 94: Optimalizace

Patří k lekci [Lekce 94: Optimalizace](../94_optimalizace.md).

## Jak spustit

```bash
python3 programy/l94_optimalizace.py
```

## Zdrojový kód

### `l94_optimalizace.py`

```py
"""Lekce 94 — optimalizace tipy."""

import timeit


def main() -> None:
    n = 10_000

    # comprehension vs for+append
    t1 = timeit.timeit(
        "r = []\nfor x in range(N): r.append(x*x)",
        globals={"N": n}, number=100,
    )
    t2 = timeit.timeit("[x*x for x in range(N)]", globals={"N": n}, number=100)
    print(f"for+append: {t1:.3f}s")
    print(f"comp:       {t2:.3f}s ({t1/t2:.1f}× rychlejší)")

    # set vs list lookup
    velky_list = list(range(100_000))
    velky_set = set(velky_list)
    target = 99_999

    t3 = timeit.timeit(lambda: target in velky_list, number=100)
    t4 = timeit.timeit(lambda: target in velky_set, number=100)
    print(f"\nlookup list: {t3:.4f}s")
    print(f"lookup set:  {t4:.6f}s ({t3/t4:.0f}× rychlejší)")

    # str join vs +=
    kusy = ["abc"] * 10_000
    t5 = timeit.timeit("s=''\nfor k in K: s+=k", globals={"K": kusy}, number=10)
    t6 = timeit.timeit("''.join(K)", globals={"K": kusy}, number=10)
    print(f"\nstr +=:    {t5:.3f}s")
    print(f"str.join:  {t6:.3f}s ({t5/t6:.0f}× rychlejší)")


if __name__ == "__main__":
    main()

```
