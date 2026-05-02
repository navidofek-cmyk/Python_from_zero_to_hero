# Lekce 158: PyO3 — Rust rozšíření pro Python

PyO3 umožňuje psát Python moduly v Rustu. Výsledek: **rychlost C/Rustu s pohodlím Pythonu**. Ideální pro CPU-heavy výpočty kde NumPy nestačí.

---

## 🚀 Instalace

```bash
# Potřebuješ Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Maturin — build tool pro PyO3
uv add maturin

# Nový projekt
maturin new --bindings pyo3 moje_rozsireni
cd moje_rozsireni
```

---

## 🦀 Základní Rust extension

`src/lib.rs`:

```rust
use pyo3::prelude::*;

/// Součet čísel v listu — rychlejší než Python loop
#[pyfunction]
fn soucet(seznam: Vec<f64>) -> f64 {
    seznam.iter().sum()
}

/// Fibonacci číslo — rychlé rekurzivní počítání
#[pyfunction]
fn fibonacci(n: u64) -> u64 {
    if n <= 1 { return n; }
    let mut a = 0u64;
    let mut b = 1u64;
    for _ in 2..=n {
        let c = a + b;
        a = b;
        b = c;
    }
    b
}

/// Řazení bubble sort v Rustu
#[pyfunction]
fn bubble_sort(mut data: Vec<i64>) -> Vec<i64> {
    let n = data.len();
    for i in 0..n {
        for j in 0..n-i-1 {
            if data[j] > data[j+1] {
                data.swap(j, j+1);
            }
        }
    }
    data
}

/// Python modul
#[pymodule]
fn moje_rozsireni(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(soucet, m)?)?;
    m.add_function(wrap_pyfunction!(fibonacci, m)?)?;
    m.add_function(wrap_pyfunction!(bubble_sort, m)?)?;
    Ok(())
}
```

`Cargo.toml`:

```toml
[package]
name = "moje_rozsireni"
version = "0.1.0"
edition = "2021"

[lib]
name = "moje_rozsireni"
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.21", features = ["extension-module"] }
```

Build a instalace:

```bash
maturin develop   # vývoj — rychlý build
maturin build     # release build (.whl)
```

---

## 🐍 Použití v Pythonu

```python
# Po maturin develop:
# import moje_rozsireni as mr
# print(mr.fibonacci(50))
# print(mr.soucet([1.0, 2.0, 3.0]))

# Benchmark
import time

def fib_python(n):
    if n <= 1: return n
    a, b = 0, 1
    for _ in range(2, n+1): a, b = b, a+b
    return b

n = 40
start = time.perf_counter()
r_py = fib_python(n)
t_py = time.perf_counter() - start

# start = time.perf_counter()
# r_rs = mr.fibonacci(n)
# t_rs = time.perf_counter() - start
# print(f"Python: {t_py*1000:.3f}ms")
# print(f"Rust:   {t_rs*1000:.3f}ms  ({t_py/t_rs:.0f}× rychlejší)")
print(f"Python fib({n}) = {r_py} za {t_py*1000:.3f}ms")
print("Rust verze by byla ~10-50x rychlejší")
```

---

## 🏗️ Třídy v Rustu

```rust
use pyo3::prelude::*;

/// Python třída implementovaná v Rustu
#[pyclass]
struct Pocitadlo {
    hodnota: i64,
    krok: i64,
}

#[pymethods]
impl Pocitadlo {
    #[new]
    fn new(pocatecni: i64, krok: i64) -> Self {
        Pocitadlo { hodnota: pocatecni, krok }
    }

    fn increment(&mut self) -> i64 {
        self.hodnota += self.krok;
        self.hodnota
    }

    fn reset(&mut self) { self.hodnota = 0; }

    #[getter]
    fn hodnota(&self) -> i64 { self.hodnota }

    fn __repr__(&self) -> String {
        format!("Pocitadlo(hodnota={}, krok={})", self.hodnota, self.krok)
    }
}
```

Python použití:
```python
# c = mr.Pocitadlo(0, 5)
# print(c)           # Pocitadlo(hodnota=0, krok=5)
# c.increment()      # 5
# c.increment()      # 10
```

---

## ⚡ NumPy integrace

```rust
use pyo3::prelude::*;
use numpy::{PyArray1, PyReadonlyArray1};

#[pyfunction]
fn numpy_soucet<'py>(py: Python<'py>, arr: PyReadonlyArray1<'py, f64>) -> f64 {
    arr.as_array().sum()
}

#[pyfunction]
fn numpy_transform<'py>(
    py: Python<'py>,
    arr: PyReadonlyArray1<'py, f64>,
) -> &'py PyArray1<f64> {
    let result: Vec<f64> = arr.as_array()
        .iter()
        .map(|&x| x * x + 2.0 * x + 1.0)  // x² + 2x + 1
        .collect();
    PyArray1::from_vec(py, result)
}
```

`Cargo.toml` dodatek:
```toml
numpy = "0.21"
```

---

## 📦 Distribuce

```bash
# Build pro všechny platformy (cross-compilation)
maturin build --release --target x86_64-unknown-linux-gnu

# Publish na PyPI
maturin publish

# GitHub Actions workflow
```

```yaml
# .github/workflows/build.yml
- uses: PyO3/maturin-action@v1
  with:
    command: build
    args: --release --out dist
- uses: actions/upload-artifact@v3
  with:
    name: wheels
    path: dist
```

---

## 🎯 Kdy PyO3

| Případ | Doporučení |
|--------|-----------|
| CPU-heavy výpočty | ✅ PyO3 |
| Existující Rust knihovna | ✅ PyO3 |
| Jednoduchá optimalizace | NumPy/Cython |
| I/O bound | async Python |
| Rychlý prototyp | čistý Python |
| 10–100× zrychlení nutné | ✅ PyO3 |

---

## ✏️ Cvičení

1. Napiš Rust funkci pro počítání prvočísel (Sieve of Eratosthenes) — benchmark vs Python.
2. Implementuj Rust třídu `MatrixMul` pro násobení matic — porovnej s NumPy.
3. Vytvoř Rust funkci pro parsování velkých CSV souborů.
4. Použij `rayon` crate pro paralelní zpracování v Rustu.
5. Publikuj modul na TestPyPI pomocí `maturin publish`.
