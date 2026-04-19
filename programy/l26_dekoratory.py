"""Lekce 26 — dekorátory."""

import time
from functools import wraps


def loguj(funkce):
    @wraps(funkce)
    def obalka(*args, **kwargs):
        print(f"➡️  {funkce.__name__}({args}, {kwargs})")
        vysledek = funkce(*args, **kwargs)
        print(f"⬅️  → {vysledek}")
        return vysledek
    return obalka


def zmer_cas(funkce):
    @wraps(funkce)
    def obalka(*args, **kwargs):
        start = time.perf_counter()
        vysledek = funkce(*args, **kwargs)
        konec = time.perf_counter()
        print(f"⏱️  {funkce.__name__}: {konec-start:.3f}s")
        return vysledek
    return obalka


def opakuj(kolikrat: int):
    def dekorator(funkce):
        @wraps(funkce)
        def obalka(*args, **kwargs):
            vysledek = None
            for _ in range(kolikrat):
                vysledek = funkce(*args, **kwargs)
            return vysledek
        return obalka
    return dekorator


@loguj
@zmer_cas
def secti(a: int, b: int) -> int:
    time.sleep(0.1)
    return a + b


@opakuj(3)
def pozdrav() -> None:
    print("Ahoj!")


def main() -> None:
    print(secti(2, 3))
    print()
    pozdrav()


if __name__ == "__main__":
    main()
