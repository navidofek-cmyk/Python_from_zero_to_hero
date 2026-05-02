# Program — Lekce 47: Lekce 47: Introspekce a monkey patching

Patří k lekci [Lekce 47: Introspekce a monkey patching](../47_introspekce.md).

## Jak spustit

```bash
python3 programy/l47_introspekce.py
```

## Zdrojový kód

### `l47_introspekce.py`

```py
"""Lekce 47 — introspekce a monkey patch."""


class Pes:
    def stekni(self):
        print("Haf!")


def vrti(self):
    print("Vrtí ocasem 🐕")


def main() -> None:
    rex = Pes()
    print(f"Před patchem: {[m for m in dir(rex) if not m.startswith('_')]}")

    # Monkey patch
    Pes.vrti = vrti
    rex.vrti()
    print(f"Po patchi: {[m for m in dir(rex) if not m.startswith('_')]}")

    # getattr/hasattr
    for jmeno in ["stekni", "vrti", "leti"]:
        if hasattr(rex, jmeno):
            metoda = getattr(rex, jmeno)
            if callable(metoda):
                print(f"  ✅ {jmeno}: dostupné")
        else:
            print(f"  ❌ {jmeno}: chybí")


if __name__ == "__main__":
    main()

```
