# Program — Lekce 49: Lekce 49: Dynamické vytváření tříd

Patří k lekci [Lekce 49: Dynamické vytváření tříd](../49_dynamicke_tridy.md).

## Jak spustit

```bash
python3 programy/l49_dynamicke_tridy.py
```

## Zdrojový kód

### `l49_dynamicke_tridy.py`

```py
"""Lekce 49 — dynamické vytváření tříd."""


def udelej_tridu(jmeno: str, atributy: dict[str, type]):
    annotations = atributy

    def __init__(self, **kwargs):
        for nazev in atributy:
            setattr(self, nazev, kwargs.get(nazev))

    def __repr__(self):
        attrs = ", ".join(f"{k}={getattr(self, k)!r}" for k in atributy)
        return f"{jmeno}({attrs})"

    return type(jmeno, (), {
        "__init__": __init__,
        "__repr__": __repr__,
        "__annotations__": annotations,
    })


def main() -> None:
    Uzivatel = udelej_tridu("Uzivatel", {"jmeno": str, "vek": int, "email": str})
    Produkt = udelej_tridu("Produkt", {"nazev": str, "cena": float})

    u = Uzivatel(jmeno="Anna", vek=12, email="anna@example.com")
    p = Produkt(nazev="Hračka", cena=199.0)

    print(u)
    print(p)
    print(f"Annotations: {Uzivatel.__annotations__}")


if __name__ == "__main__":
    main()

```
