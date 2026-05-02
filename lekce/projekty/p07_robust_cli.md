# Projekt 7: Robust CLI

Mini-projekt po **sekci VII (Výjimky)**. CLI nástroj, který načítá a validuje JSON konfiguraci — ukázka správného ošetření všech typů chyb.

**Použité koncepty:** vlastní výjimky (62), `raise from` (63), `ExceptionGroup` a `except*` (64), logging výjimek (65), EAFP (66), `argparse` (81).

## Jak spustit

```bash
# Vytvoř testovací config:
echo '{"host":"localhost","port":5432,"user":"admin"}' > config.json
python3 projekty/07_robust_cli/cli.py config.json

# Špatný config (chybí klíče):
echo '{"host":"localhost"}' > bad.json
python3 projekty/07_robust_cli/cli.py bad.json
```

## Zdrojový kód — `cli.py`

```python
"""Mini-projekt po sekci VII: Robust CLI s ošetřením všech chyb.

Procvičuje: vlastní výjimky, raise from, EAFP, logování, ExceptionGroup.
"""

import argparse
import json
import logging
import sys
from pathlib import Path


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


class CliError(Exception):
    """Bázová."""


class ConfigError(CliError):
    pass


class ValidationError(CliError):
    pass


def nacti_config(cesta: Path) -> dict:
    try:
        text = cesta.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise ConfigError(f"Konfigurace neexistuje: {cesta}") from e
    except PermissionError as e:
        raise ConfigError(f"Bez práv: {cesta}") from e

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Špatný JSON v {cesta}: {e}") from e


def validuj(config: dict) -> None:
    chyby: list[Exception] = []
    pozadovane = ["host", "port", "user"]

    for klic in pozadovane:
        if klic not in config:
            chyby.append(ValidationError(f"chybí '{klic}'"))

    if "port" in config and not isinstance(config["port"], int):
        chyby.append(ValidationError("'port' musí být int"))

    if chyby:
        raise ExceptionGroup("Validace konfigurace selhala", chyby)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    args = parser.parse_args()

    try:
        config = nacti_config(args.config)
        validuj(config)
    except ConfigError as e:
        log.error(str(e))
        return 1
    except* ValidationError as eg:
        log.error("Validační chyby:")
        for chyba in eg.exceptions:
            log.error(f"  - {chyba}")
        return 2
    except Exception:
        log.exception("Neočekávaná chyba")
        return 99

    log.info(f"✅ Config OK: {config}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
