# Lekce 10: Komentáře, docstringy, PEP 8 a typové hinty

## 💬 Komentáře — vzkazy pro lidi

Komentáře jsou **vzkazy v kódu, které robot ignoruje**. Jsou pro lidi, co budou kód číst (i pro tebe za měsíc!).

```python
# Tohle je komentář na celém řádku
x = 5  # tohle je komentář na konci řádku
```

### Kdy psát komentář?

✅ **Ano** — když říkáš **PROČ** kód něco dělá:
```python
# Násobíme 1.21 kvůli DPH 21%
cena_s_dph = cena * 1.21
```

❌ **Ne** — když jen opakuješ, **CO** kód dělá:
```python
x = x + 1  # zvýším x o jedna   ← zbytečné, vidím to!
```

Dobré pojmenování proměnných nahradí komentář:
```python
# špatně
n = 50  # počet pokusů

# líp
pocet_pokusu = 50
```

---

## 📚 Docstringy — návod ke kódu

Docstring je speciální komentář **uvnitř** funkce, třídy nebo modulu, popisující, k čemu slouží. Píše se v trojitých uvozovkách hned na začátku.

```python
def secti(a: int, b: int) -> int:
    """Sečte dvě čísla a vrátí výsledek."""
    return a + b
```

Můžeš si ho zobrazit přes `help()`:

```python
help(secti)
```

Pro delší dokumentaci:

```python
def vypocet_dph(cena: float, sazba: float = 0.21) -> float:
    """Spočítá cenu včetně DPH.

    Args:
        cena: Cena bez DPH v Kč.
        sazba: Sazba DPH (0.21 pro 21%, 0.15 pro 15%).

    Returns:
        Cena včetně DPH zaokrouhlená na haléře.
    """
    return round(cena * (1 + sazba), 2)
```

---

## 🎨 PEP 8 — pravidla krásného kódu

**PEP 8** je oficiální „pravopis Pythonu“. Všichni Pythonisté ho dodržují, abychom si všichni rozuměli.

### Hlavní pravidla:

1. **Odsazení = 4 mezery** (ne tabulátor!)
2. **Maximální délka řádku ~79 znaků** (nebo 88, podle nástroje)
3. **Prázdné řádky** — 2 mezi funkcemi/třídami, 1 mezi metodami
4. **Mezery kolem operátorů**: `x = 5` (NE `x=5`)
5. **Bez mezer uvnitř závorek**: `funkce(a, b)` (NE `funkce( a, b )`)
6. **Pojmenování:**
   - proměnné a funkce: `snake_case`
   - třídy: `PascalCase`
   - konstanty: `VELKE_PISMENA`
   - „soukromé“: `_zacina_podtrzitkem`

### Nástroje, které to ohlídají za tebe

```bash
pip install ruff
ruff check .       # najde chyby
ruff format .      # automaticky srovná
```

`ruff` je super rychlý linter+formátter. Doporučuji každému!

---

## 🏷️ Typové hinty — nálepky s typem

V Pythonu nemusíš říkat, jakého typu má proměnná být. Ale **můžeš to napsat jako nápovědu**:

```python
jmeno: str = "Eliška"
vek: int = 10
hodnoty: list[int] = [1, 2, 3]

def pozdrav(jmeno: str, vykricnik: bool = False) -> str:
    konec = "!" if vykricnik else "."
    return f"Ahoj {jmeno}{konec}"
```

### K čemu to je?

- **Robot je nepoužije** při běhu — nezkontroluje, jestli sedí.
- **Ale tvůj editor (VS Code, PyCharm) ti pomůže** — našeptává, varuje před chybami.
- **Nástroje jako `mypy` nebo `pyright`** ti najdou nesedící typy ještě než program spustíš.

### Základní typy v anotacích

```python
x: int = 5
y: float = 3.14
z: str = "ahoj"
b: bool = True
n: None = None
seznam: list[int] = [1, 2, 3]
slovnik: dict[str, int] = {"a": 1}
```

### Volitelné a více možností

```python
from typing import Optional

vek: int | None = None      # buď int, nebo None (od Python 3.10)
vek: Optional[int] = None   # totéž (starší zápis)

barva: str | int = "modrá"  # buď text, nebo číslo
```

---

## 🎯 Shrnutí pro krásný kód

```python
"""Modul na výpočet DPH.

Použití:
    from dph import vypocet_dph
    cena = vypocet_dph(100, sazba=0.21)
"""

DEFAULTNI_SAZBA: float = 0.21


def vypocet_dph(cena: float, sazba: float = DEFAULTNI_SAZBA) -> float:
    """Spočítá cenu včetně DPH."""
    return round(cena * (1 + sazba), 2)


if __name__ == "__main__":
    print(vypocet_dph(100))   # 121.0
```

---

## ✏️ Cvičení

1. **Docstring:** Napiš funkci `obvod_obdelniku(a, b)` s docstringem a typovými hinty.
2. **Ruff:** Nainstaluj `ruff` a pusť ho na svoje předchozí cvičení. Co najde?
3. **Pojmenování:** Vezmi nějaký svůj starší kód a přejmenuj proměnné z `n`, `x`, `tmp` na popisné názvy. Vidíš, jak méně je potřeba komentářů?
4. **Typy:** Doplň typové anotace ke všem funkcím z lekce 7 a 8.
