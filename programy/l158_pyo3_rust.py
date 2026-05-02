"""Lekce 158 — PyO3: Rust rozšíření pro Python.

Tento soubor ukazuje jak volat Rust z Pythonu po buildu.
Spuštění:
    uv run l158_pyo3_rust.py
"""

import subprocess
import sys
import time


def fib_python(n: int) -> int:
    if n <= 1: return n
    a, b = 0, 1
    for _ in range(2, n+1): a, b = b, a+b
    return b


def primes_python(limit: int) -> list[int]:
    """Eratosthenovo síto."""
    sito = [True] * (limit+1)
    sito[0] = sito[1] = False
    for i in range(2, int(limit**0.5)+1):
        if sito[i]:
            for j in range(i*i, limit+1, i):
                sito[j] = False
    return [i for i in range(2, limit+1) if sito[i]]


def main():
    print("=" * 55)
    print("  🦀 PyO3 — Rust rozšíření pro Python")
    print("=" * 55)

    # Ukázka Python výkonu (co by Rust zrychlil)
    print("\n=== Python benchmark (Rust by byl ~10-50× rychlejší) ===")

    for n in [35, 40]:
        start = time.perf_counter()
        r = fib_python(n)
        t = time.perf_counter()-start
        print(f"  fib({n}) = {r}  ({t*1000:.3f}ms)")

    start = time.perf_counter()
    primes = primes_python(1_000_000)
    t = time.perf_counter()-start
    print(f"  Prvočísla do 1M: {len(primes)} ({t*1000:.0f}ms)")

    print("\n=== Rust projekt struktura ===")
    rust_struktura = """
moje_rozsireni/
├── Cargo.toml
├── pyproject.toml
└── src/
    └── lib.rs         ← Rust kód

src/lib.rs:
    #[pyfunction]
    fn fibonacci(n: u64) -> u64 { ... }

    #[pymodule]
    fn moje_rozsireni(_py: Python, m: &PyModule) -> PyResult<()> {
        m.add_function(wrap_pyfunction!(fibonacci, m)?)?;
        Ok(())
    }

Cargo.toml:
    [dependencies]
    pyo3 = { version = "0.21", features = ["extension-module"] }

Build:
    maturin develop    # vývoj
    maturin build      # release .whl

Po buildu:
    import moje_rozsireni
    moje_rozsireni.fibonacci(50)  # ~50× rychlejší než Python
    """
    print(rust_struktura)

    print("=== Instalace ===")
    print("  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")
    print("  uv add maturin")
    print("  maturin new --bindings pyo3 moje_rozsireni")
    print("  cd moje_rozsireni && maturin develop")

    print("\n✅ Demo dokončeno!")
    print("Alternativy k PyO3: Cython, cffi, ctypes (lekce 95)")


if __name__ == "__main__":
    main()
