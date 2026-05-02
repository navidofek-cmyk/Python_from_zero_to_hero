# Program — Lekce 75: Lekce 75: `os`, `shutil`, `tempfile`, `glob`

Patří k lekci [Lekce 75: `os`, `shutil`, `tempfile`, `glob`](../75_os_shutil.md).

## Jak spustit

```bash
python3 programy/l75_os_shutil.py
```

## Zdrojový kód

### `l75_os_shutil.py`

```py
"""Lekce 75 — os, shutil, tempfile."""

import os
import shutil
import tempfile
from pathlib import Path


def main() -> None:
    # Tempdir
    with tempfile.TemporaryDirectory() as slozka_str:
        slozka = Path(slozka_str)
        for i in range(3):
            (slozka / f"soubor_{i}.txt").write_text(f"obsah {i}")
        print(f"Soubory v {slozka}:")
        for f in slozka.iterdir():
            print(f"  {f.name}: {f.stat().st_size} B")

    print(f"\nPo with: existuje? {slozka.exists()}")

    # Disk usage
    total, used, free = shutil.disk_usage("/")
    print(f"\nDisk: {free / 1e9:.1f} GB volné z {total / 1e9:.1f} GB")

    # Which
    print(f"Python: {shutil.which('python3')}")


if __name__ == "__main__":
    main()

```
