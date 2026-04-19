"""Lekce 67 — demo balíček s re-exportem."""

from .matematika import nasob, deli, faktorial

__all__ = ["nasob", "deli", "faktorial"]
__version__ = "0.1.0"
