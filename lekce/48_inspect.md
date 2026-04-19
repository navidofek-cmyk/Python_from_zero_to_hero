# Lekce 48: Modul `inspect`

## 🔬 Co umí `inspect`?

Modul `inspect` poskytuje **detailní introspekci**: signatury funkcí, zdrojový kód, frame objekty atd.

```python
import inspect
```

---

## 📝 `inspect.signature`

```python
def secti(a: int, b: int = 0, *args, **kwargs) -> int:
    return a + b

sig = inspect.signature(secti)
print(sig)             # (a: int, b: int = 0, *args, **kwargs) -> int

for jmeno, param in sig.parameters.items():
    print(f"  {jmeno}: kind={param.kind}, default={param.default}")
```

Skvělé pro:
- Dokumentaci API
- Validaci argumentů
- Wrappery a dekorátory

---

## 📄 `inspect.getsource`

```python
print(inspect.getsource(secti))
```

Vypíše skutečný **zdrojový kód** funkce. (Funguje, jen když je k dispozici .py soubor.)

---

## 🌳 `inspect.getmembers`

```python
import math

for jmeno, hodnota in inspect.getmembers(math):
    if inspect.isfunction(hodnota):
        print(jmeno)
```

Filtruj podle typu: `isfunction`, `isclass`, `ismethod`, `iscoroutinefunction`...

---

## 📋 Frame objekty

```python
def kdo_me_zavolal():
    frame = inspect.currentframe().f_back
    print(f"Volá mě: {frame.f_code.co_name} ze souboru {frame.f_code.co_filename}")

def main():
    kdo_me_zavolal()    # Volá mě: main z ...
```

Užitečné pro logging, debug. (V produkci opatrně — frame objekty drží referenční cyklus.)

---

## 🔄 `inspect.iscoroutinefunction`

```python
async def fetch(): ...
def normalni(): ...

inspect.iscoroutinefunction(fetch)      # True
inspect.iscoroutinefunction(normalni)   # False
```

---

## ✏️ Cvičení

1. **Signature:** Vypiš všechny parametry funkce `print` přes `inspect.signature(print)`.
2. **Get source:** Vypiš zdroj nějaké funkce ze stdlib (třeba `re.match`).
3. **Get members:** Vypiš všechny funkce z `math` modulu.
4. **Caller:** Funkce co vypíše, kdo ji zavolal (přes `currentframe`).
