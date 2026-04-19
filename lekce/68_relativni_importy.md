# Lekce 68: Relativní vs absolutní importy, kruhové importy

## 🌍 Absolutní vs relativní

### Absolutní (preferované)

```python
from muj_projekt.modul_a import funkce
```

Plná cesta od **kořene projektu**. Funguje vždy, ale je dlouhá.

### Relativní

```python
from .modul_a import funkce       # ze stejného balíčku
from ..jiny_balicek import x      # o úroveň výš
```

`.` = aktuální balíček, `..` = nadřazený. **Funguje JEN uvnitř balíčku** (ne ve standalone skriptu).

---

## 🎯 Kdy co?

| | Absolutní | Relativní |
|---|---|---|
| Čitelnost | Dobrá | Krátké, méně psaní |
| Refaktoring | Hůř (musíš změnit) | Přežije přesun |
| Standalone skripty | Funguje | ❌ |
| Doporučení PEP 8 | ✅ Preferuj | OK uvnitř balíčku |

V praxi: **většinou absolutní, relativní jen krátce uvnitř balíčku**.

---

## 🔁 Kruhový import — peklo začátečníků

```python
# a.py
from b import x

# b.py
from a import y
```

**Boom!** `ImportError`. Python vidí, že `a` se snaží importovat `b`, který chce `a`...

### Řešení 1: Reorganizovat

Najdi společnou třetí věc a vytáhni ji do `c.py`. Většinou je kruhový import **signál špatné architektury**.

### Řešení 2: Pozdní import

```python
# a.py
def funkce():
    from b import x       # uvnitř funkce — import až při volání
    use(x)
```

### Řešení 3: TYPE_CHECKING

Pro typové hinty (kdy nepotřebuješ skutečně importovat za běhu):

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from b import X        # importuje JEN pro typový checker

def funkce(x: "X"):       # string anotace
    ...
```

---

## 🎯 Best practice

✅ **Absolutní** importy v hlavě souboru.
✅ Plně kvalifikované cesty.
❌ Žádné `from x import *` (zatemňuje původ).
❌ Žádné importy uprostřed funkce (kromě řešení kruhových).

---

## ✏️ Cvičení

1. **Balíček:** Vytvoř balíček s 2 moduly co se vzájemně volají. Použij relativní importy.
2. **Kruhový:** Schválně si vyrob kruhový import a spusť — uvidíš chybu. Pak ji oprav.
3. **TYPE_CHECKING:** Použij ho pro typové hinty bez skutečného importu.
