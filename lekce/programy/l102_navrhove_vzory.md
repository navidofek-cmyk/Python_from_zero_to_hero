# Program — Lekce 102: Lekce 102: Návrhové vzory pythonicky

Patří k lekci [Lekce 102: Návrhové vzory pythonicky](../102_navrhove_vzory.md).

## Jak spustit

```bash
python3 programy/l102_navrhove_vzory.py
```

## Zdrojový kód

### `l102_navrhove_vzory.py`

```py
"""Lekce 102 — Návrhové vzory pythonicky."""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import singledispatch
from typing import Callable


# ── 1. Strategy — přes funkce ─────────────────────────────────────────────────

SortFn = Callable[[list], list]

def zpracuj(data: list, sorter: SortFn) -> list:
    return sorter(data)


# ── 2. Singleton — přes modul (simulace) ─────────────────────────────────────

class _AppConfig:
    debug: bool = False
    db_url: str = "sqlite:///app.db"
    max_connections: int = 10

app_config = _AppConfig()   # jediná instance — importuje se odkudkoliv


# ── 3. Factory — přes __init_subclass__ ──────────────────────────────────────

class Tvar:
    _registry: dict[str, type] = {}

    def __init_subclass__(cls, typ: str = "", **kw):
        super().__init_subclass__(**kw)
        if typ:
            Tvar._registry[typ] = cls

    @classmethod
    def vytvor(cls, typ: str, **kw) -> "Tvar":
        if typ not in cls._registry:
            raise ValueError(f"Neznámý typ: {typ!r}. Dostupné: {list(cls._registry)}")
        return cls._registry[typ](**kw)

    def obsah(self) -> float:
        return 0.0


class Kruh(Tvar, typ="kruh"):
    def __init__(self, r: float): self.r = r
    def obsah(self) -> float: return 3.14159 * self.r ** 2
    def __repr__(self): return f"Kruh(r={self.r})"


class Ctverec(Tvar, typ="ctverec"):
    def __init__(self, a: float): self.a = a
    def obsah(self) -> float: return self.a ** 2
    def __repr__(self): return f"Ctverec(a={self.a})"


class Obdelnik(Tvar, typ="obdelnik"):
    def __init__(self, w: float, h: float): self.w, self.h = w, h
    def obsah(self) -> float: return self.w * self.h
    def __repr__(self): return f"Obdelnik(w={self.w}, h={self.h})"


# ── 4. Observer — přes callable seznam ───────────────────────────────────────

class Udalost:
    def __init__(self, nazev: str):
        self.nazev = nazev
        self._posluchaci: list[Callable] = []

    def prihlas(self, fn: Callable) -> None:
        self._posluchaci.append(fn)

    def odprihlas(self, fn: Callable) -> None:
        self._posluchaci.remove(fn)

    def spust(self, *args, **kwargs) -> None:
        for fn in self._posluchaci:
            fn(*args, **kwargs)


# ── 5. State — přes třídy stavů ───────────────────────────────────────────────

class StavObjednavky(ABC):
    @abstractmethod
    def dalsi(self, obj: "Objednavka") -> None: ...
    @abstractmethod
    def __str__(self) -> str: ...


class Cekajici(StavObjednavky):
    def dalsi(self, obj: "Objednavka") -> None:
        print("  ✓ Objednávka schválena")
        obj.stav = Schvalena()
    def __str__(self): return "Čekající"


class Schvalena(StavObjednavky):
    def dalsi(self, obj: "Objednavka") -> None:
        print("  ✓ Objednávka odeslána")
        obj.stav = Odeslana()
    def __str__(self): return "Schválená"


class Odeslana(StavObjednavky):
    def dalsi(self, obj: "Objednavka") -> None:
        print("  ✗ Již odeslána, nelze pokračovat")
    def __str__(self): return "Odeslaná"


class Objednavka:
    def __init__(self, id: int):
        self.id = id
        self.stav: StavObjednavky = Cekajici()

    def dalsi_krok(self) -> None:
        self.stav.dalsi(self)

    def __repr__(self): return f"Objednavka(id={self.id}, stav={self.stav})"


# ── 6. Visitor — přes singledispatch ─────────────────────────────────────────

class Cislo:
    def __init__(self, h: float): self.h = h

class Text:
    def __init__(self, s: str): self.s = s

class Seznam:
    def __init__(self, polozky: list): self.polozky = polozky


@singledispatch
def tiskni(uzel) -> str:
    raise TypeError(f"Neznámý typ: {type(uzel).__name__}")

@tiskni.register
def _(uzel: Cislo) -> str:
    return f"Číslo({uzel.h})"

@tiskni.register
def _(uzel: Text) -> str:
    return f"Text('{uzel.s}')"

@tiskni.register
def _(uzel: Seznam) -> str:
    return f"Seznam[{', '.join(tiskni(p) for p in uzel.polozky)}]"


# ── Demo ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=== 1. Strategy ===")
    data = [5, 2, 8, 1, 9]
    print(f"  sorted:   {zpracuj(data, sorted)}")
    print(f"  reversed: {zpracuj(data, lambda d: sorted(d, reverse=True))}")

    print("\n=== 2. Singleton (config) ===")
    app_config.debug = True
    print(f"  debug={app_config.debug}, db={app_config.db_url}")

    print("\n=== 3. Factory ===")
    for spec in [("kruh", {"r": 3}), ("ctverec", {"a": 4}), ("obdelnik", {"w": 5, "h": 2})]:
        t = Tvar.vytvor(spec[0], **spec[1])
        print(f"  {t}  obsah={t.obsah():.2f}")

    print("\n=== 4. Observer ===")
    on_login = Udalost("login")
    on_login.prihlas(lambda u: print(f"  Vítej, {u}!"))
    on_login.prihlas(lambda u: print(f"  [LOG] přihlášen: {u}"))
    on_login.spust("Anna")

    print("\n=== 5. State ===")
    obj = Objednavka(42)
    print(f"  {obj}")
    for _ in range(3):
        obj.dalsi_krok()
        print(f"  {obj}")

    print("\n=== 6. Visitor (singledispatch) ===")
    uzly = [
        Cislo(42),
        Text("ahoj"),
        Seznam([Cislo(1), Text("dva"), Cislo(3)]),
    ]
    for u in uzly:
        print(f"  {tiskni(u)}")


if __name__ == "__main__":
    main()

```
