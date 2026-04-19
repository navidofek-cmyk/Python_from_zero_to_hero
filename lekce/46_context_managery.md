# Lekce 46: Context managery a `with`

## 🚪 Co je context manager?

Objekt, který má **`__enter__`** a **`__exit__`**. Používá se s `with`. Garantuje, že **úklid se vždycky stane** (i při výjimce).

Typický příklad — soubor:

```python
with open("data.txt") as f:
    obsah = f.read()
# Soubor se ZAVŘE i kdyby uvnitř blok spadnul!
```

---

## 🛠️ Vlastní context manager

```python
class Stopky:
    def __enter__(self):
        import time
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.uplynulo = time.perf_counter() - self.start
        print(f"⏱️  {self.uplynulo:.3f}s")
        # Když vrátíš True, výjimka se „spolkne“. Většinou nech False.
        return False


with Stopky():
    soucet = sum(range(10_000_000))
# ⏱️  0.234s
```

**Argumenty `__exit__`:**
- `exc_type` — typ výjimky (nebo None)
- `exc_val` — samotná výjimka
- `exc_tb` — traceback

---

## 🎩 `@contextmanager` — jednoduchá zkratka

Místo dvou metod můžeš použít generátor:

```python
from contextlib import contextmanager

@contextmanager
def stopky():
    import time
    start = time.perf_counter()
    yield                     # ← „mezi enter a exit“
    print(f"⏱️  {time.perf_counter() - start:.3f}s")


with stopky():
    soucet = sum(range(10_000_000))
```

Pokud chceš zachytit výjimky:

```python
@contextmanager
def stopky():
    import time
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"⏱️  {time.perf_counter() - start:.3f}s")
```

---

## 🧰 Užitečné z `contextlib`

```python
from contextlib import suppress, redirect_stdout, ExitStack
```

### `suppress` — spolkni výjimku

```python
with suppress(FileNotFoundError):
    os.remove("neexistujici.txt")
# Žádná chyba, i když soubor neexistuje
```

### `redirect_stdout` — přesměruj print

```python
import io
buffer = io.StringIO()
with redirect_stdout(buffer):
    print("Tohle nikam nejde do terminálu")
print(f"Zachytil jsem: {buffer.getvalue()!r}")
```

### `ExitStack` — víc context managerů dynamicky

```python
with ExitStack() as stack:
    soubory = [stack.enter_context(open(f)) for f in ["a.txt", "b.txt"]]
# Všechny se zavřou automaticky
```

---

## 🪆 Víc context managerů najednou

```python
with open("in.txt") as fin, open("out.txt", "w") as fout:
    fout.write(fin.read())
```

---

## 🎯 K čemu kontekst managery?

- **Soubory** — automatické zavírání
- **Locky** — automatické uvolnění
- **DB transakce** — commit/rollback
- **Měření času** — start/stop
- **Dočasné nastavení** — změň, vrať zpět
- **Logování** — start akce, konec akce

---

## ✏️ Cvičení

1. **Stopky:** Implementuj jako třídu i jako `@contextmanager`.
2. **Změna adresáře:** `with chdir("/tmp"): ...` co změní pracovní adresář a po skončení vrátí.
3. **Zachycení výjimky:** Context manager co spolkne výjimku a vypíše „Něco se pokazilo“.
4. **Tichý mód:** Manager co potlačí všechny `print` uvnitř.
5. **DB transakce:** Mock context manager `s transakci(): ...` co vypíše „BEGIN“/„COMMIT“ nebo „ROLLBACK“.
