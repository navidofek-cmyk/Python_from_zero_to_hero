# Lekce 80: `logging` — místo `print`

## 📣 Proč logging místo `print`?

| | `print` | `logging` |
|---|---|---|
| Úrovně (debug, info, error) | ❌ | ✅ |
| Vypnutí v produkci | Musíš mazat | `setLevel` |
| Soubor + konzole | Manuálně | Snadno |
| Časová značka, jméno | Manuálně | Auto |
| Strukturované | ❌ | ✅ |

---

## 🛠️ Základ

```python
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

logging.debug("debug zpráva")
logging.info("info zpráva")
logging.warning("varování!")
logging.error("chyba!")
logging.critical("kritické!")
```

---

## 🎚️ Úrovně

```
DEBUG (10) → INFO (20) → WARNING (30) → ERROR (40) → CRITICAL (50)
```

`level=logging.INFO` znamená **„zobraz INFO a víc“** — debug se neukáže.

---

## 🏷️ Vlastní logger

```python
log = logging.getLogger(__name__)

log.info("něco")
```

`__name__` = jméno modulu. Použij **vždy** jako jméno loggeru — pak filtruješ logy podle modulu.

---

## 🎯 Plná konfigurace

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(),    # konzole
    ],
)
```

---

## 🏗️ Strukturované — `structlog`

Pro produkci `pip install structlog`:

```python
import structlog

log = structlog.get_logger()
log.info("user_login", user_id=42, ip="1.2.3.4")
```

Výstup je JSON nebo barevný — záleží na konfiguraci. Skvělé pro ELK/Loki/Datadog.

---

## 🎯 Best practice

✅ `getLogger(__name__)` — ne `logging.info(...)` přímo.
✅ Konfiguraci jen na **jednom místě** (entry point).
✅ Hierarchie loggerů přes `.` v jméně (`mojeapp.db`, `mojeapp.api`).
✅ `logger.exception` v `except` (lekce 65).
✅ Strukturované pro produkci.

❌ Žádné `print` v knihovnách.
❌ Logy nikdy nelogují **PII** (osobní údaje, hesla, tokeny).

---

## ✏️ Cvičení

1. **Základ:** Konfiguruj logging na INFO, vypiš všechny úrovně, sleduj které se zobrazí.
2. **Module logger:** Vytvoř `log = getLogger(__name__)` ve dvou modulech a sleduj jméno v logu.
3. **Soubor + konzole:** Pošli logy do souboru i konzole.
4. **Format:** Přidej do logu název funkce a číslo řádku (`%(funcName)s`, `%(lineno)d`).
5. **Structlog:** Nainstaluj a vyzkoušej structlog s JSON výstupem.
