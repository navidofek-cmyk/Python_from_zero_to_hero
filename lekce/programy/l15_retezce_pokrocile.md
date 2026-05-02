# Program — Lekce 15: Lekce 15: Řetězce do hloubky

Patří k lekci [Lekce 15: Řetězce do hloubky](../15_retezce_pokrocile.md).

## Jak spustit

```bash
python3 programy/l15_retezce_pokrocile.py
```

## Zdrojový kód

### `l15_retezce_pokrocile.py`

```py
"""Lekce 15 — pokročilé řetězce."""

from string import Template


def cenzor_samohlasek(text: str) -> str:
    tabulka = str.maketrans("aeiouAEIOU", "**********")
    return text.translate(tabulka)


def je_pin(text: str) -> bool:
    return len(text) == 4 and text.isdigit()


def main() -> None:
    text = "ahoj svete jak se mas"
    print(f"Title:   {text.title()}")
    print(f"Cenzor:  {cenzor_samohlasek(text)}")

    # Šablona
    dopis = Template("Milý/á $jmeno,\nje ti $vek let. Krásný den!\n— $podpis")
    print()
    print(dopis.substitute(jmeno="Eliško", vek=10, podpis="Bob"))

    # PIN
    for s in ["1234", "12a4", "12345", "0000"]:
        print(f"\n'{s}' je PIN? {je_pin(s)}")


if __name__ == "__main__":
    main()

```
