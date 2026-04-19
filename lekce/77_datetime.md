# Lekce 77: `datetime`, `zoneinfo`, `time`

## 📅 `datetime` — moderní práce s datem/časem

```python
from datetime import datetime, date, time, timedelta
```

---

## 🛠️ Vytvoření

```python
date(2026, 4, 18)                       # 2026-04-18
datetime(2026, 4, 18, 14, 30)           # 2026-04-18 14:30:00
datetime.now()                          # teď (lokální)
datetime.utcnow()                       # ⚠️ deprecated v 3.12
datetime.now(tz=ZoneInfo("UTC"))        # ✅ správně
date.today()
```

---

## 🕰️ Časové zóny — `zoneinfo`

```python
from datetime import datetime
from zoneinfo import ZoneInfo

praha = datetime.now(ZoneInfo("Europe/Prague"))
ny = praha.astimezone(ZoneInfo("America/New_York"))

print(praha)    # 2026-04-18 14:30:00+02:00
print(ny)       # 2026-04-18 08:30:00-04:00
```

**Pravidlo:** Vždy s **timezone-aware** datetime, nikdy s **naive** (bez tz). Naive datetime jsou zdroj bugů.

---

## ⏱️ `timedelta` — rozdíl času

```python
zitra = date.today() + timedelta(days=1)
za_hodinu = datetime.now() + timedelta(hours=1)
za_minutu = datetime.now() + timedelta(minutes=1)

# Rozdíl mezi dvěma datumy
narozen = date(2014, 5, 10)
vek_dni = (date.today() - narozen).days
```

---

## 📝 Formátování (`strftime`) a parsování (`strptime`)

```python
ted = datetime.now()
ted.strftime("%Y-%m-%d %H:%M:%S")    # 2026-04-18 14:30:00
ted.strftime("%d. %B %Y")             # 18. April 2026
ted.isoformat()                        # 2026-04-18T14:30:00.123456

# Parsování
datetime.strptime("18.04.2026", "%d.%m.%Y")
datetime.fromisoformat("2026-04-18T14:30:00")
```

Hlavní formáty:

| Symbol | Význam |
|---|---|
| `%Y` | rok 4 cifry |
| `%m` | měsíc 2 cifry |
| `%d` | den 2 cifry |
| `%H` | hodina 24h |
| `%M` | minuta |
| `%S` | sekunda |
| `%A` | den v týdnu (pondělí) |
| `%B` | název měsíce |

---

## ⏲️ `time` — nízkoúrovňové

```python
import time

time.time()                    # unix timestamp (sekundy od 1970)
time.time_ns()                 # nanosekundy
time.perf_counter()            # pro měření času (přesný)
time.sleep(2)                   # počkej 2 sekundy
time.monotonic()               # nejde zpět (pro timeouty)
```

Pro měření výkonu **vždy `perf_counter`**, ne `time.time` (skok času na NTP).

---

## 📅 `calendar`

```python
import calendar

calendar.month(2026, 4)         # vypíše kalendářní mřížku
calendar.isleap(2024)           # True (přestupný)
calendar.day_name[0]            # "Monday"
```

---

## 🎯 Best practice

✅ Vždy **timezone-aware** datetime
✅ Storage: **UTC**, display: lokální
✅ ISO 8601 formát (`isoformat()`)
✅ `perf_counter` pro měření výkonu
❌ `datetime.utcnow()` (deprecated 3.12+)

---

## ✏️ Cvičení

1. **Věk:** Spočítej kolik dní žiješ.
2. **Časové zóny:** Vypiš co je za čas v Praze, NY a Tokyu.
3. **Formátování:** Vypiš dnešek jako "Pondělí, 18. dubna 2026". (Locale česky je trochu jiná otázka — viz `locale`.)
4. **Měření:** Změř, jak dlouho trvá `sum(range(10_000_000))` přes `perf_counter`.
5. **Parsování:** Z textu `"2026-04-18 14:30"` vyrob datetime.
