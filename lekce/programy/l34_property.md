# Program — Lekce 34: Lekce 34: `@property` — kouzelné atributy

Patří k lekci [Lekce 34: `@property` — kouzelné atributy](../34_property.md).

## Jak spustit

```bash
python3 programy/l34_property.py
```

## Zdrojový kód

### `l34_property.py`

```py
"""Lekce 34 — @property."""


class Teplota:
    def __init__(self, celsius: float = 0):
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, hodnota: float) -> None:
        if hodnota < -273.15:
            raise ValueError("Pod absolutní nulu nejde!")
        self._celsius = hodnota

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, hodnota: float) -> None:
        self.celsius = (hodnota - 32) * 5 / 9


def main() -> None:
    t = Teplota(20)
    print(f"{t.celsius}°C = {t.fahrenheit}°F")

    t.fahrenheit = 100
    print(f"{t.celsius:.2f}°C = {t.fahrenheit}°F")

    try:
        t.celsius = -300
    except ValueError as e:
        print(f"❌ {e}")


if __name__ == "__main__":
    main()

```
