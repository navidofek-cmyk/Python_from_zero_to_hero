"""Modul matematika v balíčku."""


def nasob(a: float, b: float) -> float:
    return a * b


def deli(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("dělení nulou")
    return a / b


def faktorial(n: int) -> int:
    if n == 0:
        return 1
    return n * faktorial(n - 1)
