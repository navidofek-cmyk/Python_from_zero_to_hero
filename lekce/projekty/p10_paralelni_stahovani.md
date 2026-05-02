# Projekt 10: Paralelní stahování souborů

Mini-projekt po **sekci X (Testování)**. Stahuje soubory paralelně pomocí `ThreadPoolExecutor` se semaforem pro omezení souběžnosti.

**Použité koncepty:** `threading` (83), `ThreadPoolExecutor` (85), `as_completed` (85), semafor (86), `urllib.request`.

## Jak spustit

```bash
python3 projekty/10_paralelni_stahovani/stahovac.py
# nebo s parametry:
python3 projekty/10_paralelni_stahovani/stahovac.py --out /tmp/stazene --workers 4
```

Stažené soubory se uloží do `./stazene/`.

## Zdrojový kód — `stahovac.py`

```python
"""Mini-projekt po sekci X: Paralelní stahování souborů.

Procvičuje: threading, ThreadPoolExecutor, queue, semafor, progress.
"""

import argparse
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse


URLS_DEMO = [
    f"https://httpbin.org/bytes/{n}"
    for n in [1024, 4096, 8192, 2048, 1024, 16384, 4096, 8192]
]


def stahni(url: str, kam: Path, sem: threading.Semaphore) -> tuple[str, int]:
    import urllib.request
    with sem:
        nazev = Path(urlparse(url).path).name or f"file_{abs(hash(url))}"
        cesta = kam / nazev
        try:
            urllib.request.urlretrieve(url, cesta)
            return url, cesta.stat().st_size
        except Exception as e:
            print(f"❌ {url}: {e}")
            return url, 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("./stazene"))
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    args.out.mkdir(exist_ok=True)
    sem = threading.Semaphore(args.workers)

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.workers * 2) as ex:
        futures = {ex.submit(stahni, u, args.out, sem): u for u in URLS_DEMO}

        celkem = 0
        for f in as_completed(futures):
            url, velikost = f.result()
            celkem += velikost
            print(f"  ✅ {url} → {velikost} B")

    cas = time.perf_counter() - start
    print(f"\n📊 Hotovo: {len(URLS_DEMO)} souborů, {celkem} B za {cas:.2f}s")


if __name__ == "__main__":
    main()
```
