# Lekce 64: `ExceptionGroup` a `except*` (Python 3.11+)

## 🎒 Víc výjimek najednou

V async kódu nebo paralelním zpracování může spadnout **víc úloh najednou**. Co s tím? Tradičně to byl problém — vyhoditi jen jednu.

Python 3.11 přinesl **`ExceptionGroup`** — výjimka, co obsahuje **víc výjimek** uvnitř.

```python
eg = ExceptionGroup("Stahování selhalo", [
    ValueError("URL 1 špatná"),
    TimeoutError("URL 2 vypršelo"),
    ConnectionError("URL 3 odmítnuto"),
])
raise eg
```

---

## 🎯 `except*` — chytni jen některé typy

```python
try:
    raise ExceptionGroup("Mix", [
        ValueError("v"),
        TypeError("t"),
        KeyError("k"),
    ])
except* ValueError as eg:
    print(f"Hodnoty: {eg.exceptions}")
except* TypeError as eg:
    print(f"Typy: {eg.exceptions}")
# Zbytek (KeyError) se znovu vyhodí
```

Hvězdička `*` říká: „**Vyber z group jen tyhle typy.**“

---

## 🚀 Kde se to objevuje?

### `asyncio.TaskGroup`

```python
async with asyncio.TaskGroup() as tg:
    tg.create_task(uloha1())
    tg.create_task(uloha2())
# Pokud spadnou obě → ExceptionGroup
```

### Vlastní paralelní kód

```python
chyby = []
for u in url_list:
    try:
        zpracuj(u)
    except Exception as e:
        chyby.append(e)

if chyby:
    raise ExceptionGroup("Některé selhaly", chyby)
```

---

## 🎁 Iterace přes group

```python
def projdi(eg):
    for vyjimka in eg.exceptions:
        if isinstance(vyjimka, ExceptionGroup):
            projdi(vyjimka)              # rekurze (groupy mohou být vnořené)
        else:
            print(vyjimka)
```

---

## ⚠️ Detaily

- `except*` **neudělá `break`** ze smyčky — uvnitř groupu chyceno.
- Jednotlivé `except*` můžou chytit **své části**.
- Funguje od Python 3.11.

---

## ✏️ Cvičení

1. **Vyrob skupinu:** ExceptionGroup s 3 různými výjimkami.
2. **Filtr:** Chytni `except* ValueError` — zbytek nech projít.
3. **Async:** Vyrob TaskGroup s 2 úlohami co padnou — odchyť ExceptionGroup.
4. **Validátor:** Funkce co projde data, sbírá chyby a na konci raisne ExceptionGroup.
