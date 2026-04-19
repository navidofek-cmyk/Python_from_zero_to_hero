"""Lekce 96 — dis bytecode + refcount."""

import dis
import gc
import sys
import weakref


def secti(a, b):
    return a + b


def main() -> None:
    print("=== Bytecode secti(a, b) ===")
    dis.dis(secti)

    print("\n=== Refcount ===")
    obj = [1, 2, 3]
    print(f"po vytvoření:    {sys.getrefcount(obj)}")
    b = obj
    print(f"po přiřazení b:  {sys.getrefcount(obj)}")
    del b
    print(f"po del b:        {sys.getrefcount(obj)}")

    print("\n=== Weakref ===")
    class Velka:
        pass

    o = Velka()
    ref = weakref.ref(o)
    print(f"ref(): {ref()}")
    del o
    gc.collect()
    print(f"po del: ref() = {ref()}")

    print("\n=== Sizeof ===")
    for x in [42, "ahoj", [], {}, [1, 2, 3]]:
        print(f"  {type(x).__name__:6s} {x!r:15s} {sys.getsizeof(x)} B")


if __name__ == "__main__":
    main()
