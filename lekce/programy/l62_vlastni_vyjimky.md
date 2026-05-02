# Program — Lekce 62: Lekce 62: Vlastní výjimky

Patří k lekci [Lekce 62: Vlastní výjimky](../62_vlastni_vyjimky.md).

## Jak spustit

```bash
python3 programy/l62_vlastni_vyjimky.py
```

## Zdrojový kód

### `l62_vlastni_vyjimky.py`

```py
"""Lekce 62 — vlastní výjimky."""


class BankaError(Exception):
    """Bázová výjimka banky."""


class NedostatekProstredku(BankaError):
    def __init__(self, zustatek: float, pozadovano: float):
        super().__init__(f"Chybí {pozadovano - zustatek:.2f} Kč")
        self.zustatek = zustatek
        self.pozadovano = pozadovano


class UcetNeexistuje(BankaError):
    pass


class Ucet:
    def __init__(self, zustatek: float = 0):
        self._zustatek = zustatek

    def vyber(self, castka: float) -> None:
        if castka > self._zustatek:
            raise NedostatekProstredku(self._zustatek, castka)
        self._zustatek -= castka


def main() -> None:
    u = Ucet(500)
    try:
        u.vyber(1000)
    except NedostatekProstredku as e:
        print(f"❌ {e}")
        print(f"   Měl: {e.zustatek}, chtěl: {e.pozadovano}")

    # Chytíme bázovou
    try:
        u.vyber(2000)
    except BankaError as e:
        print(f"\n💼 Banka error: {e}")


if __name__ == "__main__":
    main()

```
