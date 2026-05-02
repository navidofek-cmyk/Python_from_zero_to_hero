# Program — Lekce 45: Lekce 45: `__new__` vs `__init__`

Patří k lekci [Lekce 45: `__new__` vs `__init__`](../45_new_vs_init.md).

## Jak spustit

```bash
python3 programy/l45_singleton.py
```

## Zdrojový kód

### `l45_singleton.py`

```py
"""Lekce 45 — Singleton přes __new__ + Vek dědící od int."""


class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.data = {}
        return cls._instance


class Vek(int):
    def __new__(cls, hodnota: int):
        if hodnota < 0:
            raise ValueError("Záporný věk")
        return super().__new__(cls, hodnota)


def main() -> None:
    a = Singleton()
    b = Singleton()
    a.data["x"] = 99
    print(f"a is b: {a is b}")
    print(f"b.data: {b.data}")

    v = Vek(25)
    print(f"\nVek: {v}, typ: {type(v).__name__}, +5 = {v + 5}")
    try:
        Vek(-1)
    except ValueError as e:
        print(f"❌ {e}")


if __name__ == "__main__":
    main()

```
