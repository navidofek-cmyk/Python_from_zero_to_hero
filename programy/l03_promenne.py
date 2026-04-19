"""Lekce 3 — proměnné, reference, is vs ==."""


def main() -> None:
    a = [1, 2, 3]
    b = a            # b je další nálepka NA STEJNÉ krabici
    c = a.copy()     # c je nová krabice se stejným obsahem

    b.append(4)

    print(f"a = {a}")  # [1, 2, 3, 4]  ← b změnilo i a!
    print(f"b = {b}")  # [1, 2, 3, 4]
    print(f"c = {c}")  # [1, 2, 3]     ← c zůstalo

    print()
    print(f"id(a) = {id(a)}")
    print(f"id(b) = {id(b)}  (stejné jako a)")
    print(f"id(c) = {id(c)}  (jiné — nová krabice)")

    print()
    print(f"a == c: {a == c}  (obsah?)   → False (a má 4 navíc)")
    print(f"a is b: {a is b}  (stejná krabice?) → True")
    print(f"a is c: {a is c}  (stejná krabice?) → False")


if __name__ == "__main__":
    main()
