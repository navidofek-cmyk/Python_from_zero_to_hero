# Lekce 65: Kontextové výjimky a logování stack trace

## 📜 Logování výjimky

Místo `print(e)` použij **`logger.exception`** — vypíše i traceback.

```python
import logging

logger = logging.getLogger(__name__)

try:
    risk()
except Exception:
    logger.exception("Něco selhalo")
    # vypíše: "Něco selhalo" + celý traceback
```

`logger.exception` je `logger.error(..., exc_info=True)` — funguje **uvnitř `except`** automaticky.

---

## 🎯 `traceback` modul

Když potřebuješ traceback ručně:

```python
import traceback

try:
    risk()
except Exception:
    print(traceback.format_exc())          # jako string
    traceback.print_exc()                  # rovnou na stderr
```

Z výjimky:

```python
try: ...
except Exception as e:
    tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
```

---

## 🔍 Kontextové informace

Když logguješ chybu, **přidej kontext**:

```python
try:
    process_user(user_id)
except Exception:
    logger.exception(f"Selhalo zpracování uživatele {user_id}")
```

Lepší než:

```python
logger.error("Něco se stalo")    # 🤷 který uživatel?
```

---

## 🚨 Strukturované logování

V moderním Pythonu používáme **`structlog`** (lekce 80):

```python
log.error("user_processing_failed", user_id=42, error=str(e))
```

Logy jsou pak v JSONu — lépe se s nimi pracuje v ELK/Loki/Datadogu.

---

## 🎯 Sentry / observabilita

Pro produkci běž instalovat **Sentry** (`pip install sentry-sdk`) — automaticky logguje výjimky se stack tracem, kontextem a uživatelem. Lekce 112 pro detaily.

---

## ✏️ Cvičení

1. **Logger.exception:** Zachyť výjimku a logguj přes `logger.exception` — porovnej výstup s `print(e)`.
2. **Traceback string:** Získej traceback jako string a ulož ho do souboru.
3. **Kontext:** Funkce co loguje chybu s informací o vstupních argumentech.
