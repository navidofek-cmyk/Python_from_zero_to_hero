# Program — Lekce 23: Lekce 23: Positional-only `/` a keyword-only `*`

Patří k lekci [Lekce 23: Positional-only `/` a keyword-only `*`](../23_positional_keyword_only.md).

## Jak spustit

```bash
python3 programy/l23_pos_kw_only.py
```

## Zdrojový kód

### `l23_pos_kw_only.py`

```py
"""Lekce 23 — positional-only / a keyword-only *."""


def vzdalenost(x1: float, y1: float, x2: float, y2: float, /) -> float:
    """Souřadnice musí být POZIČNĚ — nedovolíme volat s jmény."""
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def odeslat(zprava: str, *, prijemce: str, urgent: bool = False) -> None:
    """prijemce a urgent MUSÍ být jménem (pro čitelnost)."""
    znak = "🚨" if urgent else "📨"
    print(f"{znak} → {prijemce}: {zprava}")


def main() -> None:
    print(f"Vzdálenost (0,0)-(3,4) = {vzdalenost(0, 0, 3, 4)}")

    odeslat("Ahoj!", prijemce="bob@example.com")
    odeslat("Akutní!", prijemce="anna@example.com", urgent=True)

    # Pokus o nepovolené volání:
    try:
        vzdalenost(x1=0, y1=0, x2=3, y2=4)
    except TypeError as e:
        print(f"\n❌ Nelze pojmenovat: {e}")


if __name__ == "__main__":
    main()

```
