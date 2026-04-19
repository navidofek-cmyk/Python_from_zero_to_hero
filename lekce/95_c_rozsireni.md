# Lekce 95: C rozšíření a FFI

## 🎯 Když Python nestačí

CPU-intenzivní úlohy v Pythonu jsou pomalé. Řešení: **napiš to v rychlejším jazyce a zavolej z Pythonu**.

---

## 🔌 `ctypes` — volání C knihoven

```python
import ctypes

libc = ctypes.CDLL("libc.so.6")
libc.printf(b"Ahoj z C\n")
```

Pro volání existujících `.so`/`.dll` knihoven.

---

## 🎨 `cffi` — modernější FFI

```bash
pip install cffi
```

```python
from cffi import FFI

ffi = FFI()
ffi.cdef("int abs(int);")
lib = ffi.dlopen(None)
print(lib.abs(-5))    # 5
```

Hezčí API než `ctypes`.

---

## 🐍 Cython — Python s typy → C

```bash
pip install cython
```

`mymath.pyx`:
```cython
def soucet(int n):
    cdef int s = 0
    cdef int i
    for i in range(n):
        s += i
    return s
```

Setup pro build → vznikne `mymath.so` co můžeš `import` jako Python modul.

---

## 🦀 PyO3 — Python rozšíření v Rustu

Moderní cesta. **Bezpečné, rychlé**, hezké API.

```rust
// lib.rs
use pyo3::prelude::*;

#[pyfunction]
fn soucet(n: u64) -> u64 {
    (0..n).sum()
}

#[pymodule]
fn mymath(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(soucet, m)?)?;
    Ok(())
}
```

Build s **`maturin`**:
```bash
pip install maturin
maturin develop
```

Pak v Pythonu:
```python
import mymath
mymath.soucet(1_000_000)
```

`ruff`, `pydantic-core`, `polars` — všechny psané v Rustu přes PyO3.

---

## 🎁 `pybind11` — pro C++

Pro projekty s velkou C++ kódovou základnou.

```cpp
#include <pybind11/pybind11.h>

int soucet(int n) {
    int s = 0;
    for (int i = 0; i < n; ++i) s += i;
    return s;
}

PYBIND11_MODULE(mymath, m) {
    m.def("soucet", &soucet);
}
```

---

## 🎯 Co kdy?

| | Cíl |
|---|---|
| `ctypes`/`cffi` | Volat hotovou C knihovnu |
| **PyO3** (Rust) | Nová výkonná knihovna |
| Cython | Postupné zrychlování existujícího Pythonu |
| pybind11 | Existující C++ kód |
| Numba | Ad-hoc JIT bez build kroku |

V 2026 je **Rust + PyO3** trend. ruff, pydantic, polars, uv — vše v Rustu.

---

## ✏️ Cvičení

1. **Ctypes:** Zavolej `libc.printf` (nebo equivalent na Windows).
2. **Numba:** Napiš funkci, dej jí `@jit`, srovnej čas.
3. **Cython:** Napiš jednoduchý `.pyx` modul a zkompiluj.
4. **PyO3 (extra):** Pokud znáš Rust, vyrob jednoduché rozšíření.
