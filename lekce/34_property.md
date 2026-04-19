# Lekce 34: `@property` — kouzelné atributy

## 🎩 Co je property?

**Property** je atribut, **který vypadá jako proměnná, ale uvnitř je funkce**.

Příklad: `osoba.vek` — vypadá jako čtení atributu, ale ve skutečnosti zavolá funkci, která třeba spočítá věk z data narození.

```python
from datetime import date

class Osoba:
    def __init__(self, jmeno: str, narozen: date):
        self.jmeno = jmeno
        self.narozen = narozen

    @property
    def vek(self) -> int:
        dnes = date.today()
        return dnes.year - self.narozen.year

eliska = Osoba("Eliška", date(2014, 5, 10))
print(eliska.vek)        # 11   ← jako proměnná, ale počítá se!
# eliska.vek = 99        # ❌ AttributeError — můžeš jen ČÍST
```

---

## 🛠️ Setter — možnost zápisu

```python
class Teplota:
    def __init__(self, celsius=0):
        self._celsius = celsius

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, hodnota):
        if hodnota < -273.15:
            raise ValueError("Pod absolutní nulu nejde!")
        self._celsius = hodnota

    @property
    def fahrenheit(self):
        return self._celsius * 9/5 + 32

    @fahrenheit.setter
    def fahrenheit(self, hodnota):
        self.celsius = (hodnota - 32) * 5/9


t = Teplota(20)
print(t.celsius)       # 20
print(t.fahrenheit)    # 68.0

t.fahrenheit = 100      # nastavíš F
print(t.celsius)        # 37.78  (přepočítalo se)

t.celsius = -300        # ❌ ValueError!
```

---

## 🗑️ Deleter — možnost smazat

```python
class Cache:
    def __init__(self):
        self._data = {}

    @property
    def data(self):
        return self._data

    @data.deleter
    def data(self):
        self._data = {}

c = Cache()
c.data["x"] = 1
del c.data            # zavolá deleter
print(c.data)         # {}
```

(Deletery jsou vzácné, používají se málo.)

---

## 💎 K čemu property?

### 1. Validace

```python
class Vek:
    def __init__(self):
        self._hodnota = 0

    @property
    def hodnota(self):
        return self._hodnota

    @hodnota.setter
    def hodnota(self, x):
        if not 0 <= x <= 150:
            raise ValueError("Věk musí být 0–150")
        self._hodnota = x
```

### 2. Počítané hodnoty

```python
class Obdelnik:
    def __init__(self, a, b):
        self.a, self.b = a, b

    @property
    def obsah(self):
        return self.a * self.b
```

### 3. Změna implementace bez rozbití kódu

Když z `self.x` uděláš `@property`, **nikdo si ničeho nevšimne**! Volání zůstane stejné. Krása!

---

## 🆚 Když potřebuješ jen "lepší atribut"

Pro **jednoduchou cache spočítané hodnoty** je lepší `@functools.cached_property`:

```python
from functools import cached_property

class Obrazek:
    def __init__(self, soubor):
        self.soubor = soubor

    @cached_property
    def velikost(self):
        # Drahá operace — udělá se JEN JEDNOU.
        return len(open(self.soubor, "rb").read())

img = Obrazek("foto.png")
img.velikost     # spočítá
img.velikost     # vrátí cached
```

---

## ✏️ Cvičení

1. **Teplota:** Implementuj `Teplota` s vlastnostmi `celsius` a `fahrenheit` (jako výše).
2. **Vek:** Třída s validací (0–150) přes setter.
3. **Obdelnik:** Třída s atributy `a, b` a `@property` `obsah`, `obvod`.
4. **CachedProperty:** Třída `Soubor` s `cached_property` `obsah` (drahé čtení ze souboru).
5. **Heslo:** Třída `Uzivatel` s `@property` `heslo`. Setter ho zaheshuje. Getter ho vrátí jako `***`.
