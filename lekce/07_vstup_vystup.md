# Lekce 7: Vstup a výstup — `input()` a `print()`

## 🗣️ `input()` — robot se tě ptá

```python
jmeno = input("Jak se jmenuješ? ")
print("Ahoj", jmeno)
```

Robot čeká, až něco napíšeš, stiskneš Enter, a to, cos napsal, ti vrátí jako **text**.

### ⚠️ DŮLEŽITÉ: `input()` vždy vrací text!

```python
vek = input("Věk: ")   # napíšeš 10
print(vek + 1)          # ❌ CHYBA! "10" + 1 nejde
print(int(vek) + 1)     # ✅ OK, 11
```

Musíš ho převést na číslo přes `int()` nebo `float()`.

---

## 📣 `print()` — robot ti něco řekne

```python
print("Ahoj")                # Ahoj
print("Ahoj", "světe", 42)   # Ahoj světe 42   (mezery mezi argumenty)
```

### Argumenty `sep` a `end`

```python
# sep = co dát MEZI argumenty (default je mezera)
print("a", "b", "c", sep="-")        # a-b-c
print("a", "b", "c", sep="\n")       # každé na svém řádku

# end = co dát NA KONEC (default je nový řádek \n)
print("bez odřádkování", end="")
print("na stejný řádek")
# → bez odřádkovánína stejný řádek

print("tečka", end=".\n")
# → tečka.
```

### Argument `file` — kam tisknout

Defaultně tiskne do terminálu. Ale můžeš i do souboru:

```python
with open("log.txt", "w") as f:
    print("Ahoj deníčku", file=f)
```

Do standardního chybového výstupu (pro chyby):

```python
import sys
print("Pozor, chyba!", file=sys.stderr)
```

### Argument `flush` — vytlač hned

`print` někdy drží text v bufferu (krabičce). `flush=True` ho donutí vytlačit okamžitě — užitečné u animací a pokroku:

```python
import time
for i in range(5):
    print(".", end="", flush=True)
    time.sleep(0.5)
print(" hotovo!")
```

---

## 🎨 Hezčí výstup — `rich`

Základní `print` je černobílý. Ale knihovna **`rich`** (`pip install rich`) umí barvičky, tabulky, pokrok…

```python
from rich import print
print("[bold red]Červený tučný text[/]")
print("[green]✓[/] Hotovo!")
```

Zatím to není nutné, ale je to paráda.

---

## 🧯 Časté chyby začátečníků

### 1. Zapomenuté převedení na číslo

```python
a = input("první číslo: ")
b = input("druhé číslo: ")
print(a + b)  # ❌ spojí texty! "5" + "3" = "53"
```

Správně:
```python
print(int(a) + int(b))
```

### 2. Netečný uživatel

Pokud uživatel napíše nesmysl:

```python
vek = int(input("věk: "))   # uživatel napíše "deset" → PÁD programu
```

V lekci o výjimkách se naučíme, jak to ošetřit.

---

## ✏️ Cvičení

1. **Seznam:** Zeptej se na tři jména a vypiš je tak, že budou oddělená `-` (použij `print(..., sep="-")`).
2. **Kalkulačka:** Zeptej se na dvě čísla a vypiš součet, rozdíl, součin, podíl. Pozor na převod na `int`!
3. **Animovaná tečkovaná čára:** Vytiskni 20 teček za sebou, každou po 0.2 vteřinách, tak aby se objevovaly postupně. (Použij `end=""`, `flush=True`, `time.sleep`.)
4. **Tabulka:** Vypiš jednoduchou tabulku (jména a věky) s pomocí `sep="\t"` na tabulátory.
