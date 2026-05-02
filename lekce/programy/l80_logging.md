# Program — Lekce 80: Lekce 80: `logging` — místo `print`

Patří k lekci [Lekce 80: `logging` — místo `print`](../80_logging.md).

## Jak spustit

```bash
python3 programy/l80_logging.py
```

## Zdrojový kód

### `l80_logging.py`

```py
"""Lekce 80 — logging."""

import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)8s] %(name)s.%(funcName)s:%(lineno)d - %(message)s",
    datefmt="%H:%M:%S",
)

log = logging.getLogger(__name__)


def zpracuj(x: int) -> int:
    log.debug(f"Vstup: {x}")
    if x < 0:
        log.warning("Záporná hodnota!")
    if x == 0:
        log.error("Nula nepřípustná")
        raise ValueError("nula")
    log.info(f"Výsledek: {x * 2}")
    return x * 2


def main() -> None:
    for x in [5, -3, 10]:
        try:
            zpracuj(x)
        except ValueError:
            log.exception("Selhalo")


if __name__ == "__main__":
    main()

```
