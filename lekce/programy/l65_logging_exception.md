# Program — Lekce 65: Lekce 65: Kontextové výjimky a logování stack trace

Patří k lekci [Lekce 65: Kontextové výjimky a logování stack trace](../65_logging_exceptions.md).

## Jak spustit

```bash
python3 programy/l65_logging_exception.py
```

## Zdrojový kód

### `l65_logging_exception.py`

```py
"""Lekce 65 — logging.exception."""

import logging
import traceback


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def riskantni(x: int) -> int:
    return 100 // x


def main() -> None:
    try:
        riskantni(0)
    except Exception:
        log.exception("Selhalo s argumentem x=0")

    print("\n--- Traceback jako string ---")
    try:
        riskantni(0)
    except Exception:
        s = traceback.format_exc()
        print(s)


if __name__ == "__main__":
    main()

```
