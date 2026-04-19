# Lekce 32: Atributy instance vs třídy

## 🏭 Dva druhy atributů

```python
class Pes:
    pocet_psu = 0           # ← atribut TŘÍDY (sdílený!)

    def __init__(self, jmeno: str):
        self.jmeno = jmeno  # ← atribut INSTANCE (vlastní pro každého psa)
        Pes.pocet_psu += 1


rex = Pes("Rex")
bonzo = Pes("Bonzo")

print(rex.jmeno)         # Rex
print(bonzo.jmeno)       # Bonzo
print(Pes.pocet_psu)     # 2  (sdílené!)
print(rex.pocet_psu)     # 2
print(bonzo.pocet_psu)   # 2
```

- **Atribut instance** = vlastní pro každý objekt (`self.jmeno`)
- **Atribut třídy** = jeden pro všechny (`Pes.pocet_psu`)

---

## ⚠️ Past s mutable atributem třídy

```python
class Pes:
    triky = []                # ❌ ŠPATNĚ — sdílený seznam!

    def nauc(self, trik):
        self.triky.append(trik)


rex = Pes()
bonzo = Pes()

rex.nauc("sedni")
print(bonzo.triky)        # ['sedni']  ← Co?!
```

Stejná past jako defaultní mutable parametr (lekce 21)!

**Správně:**
```python
class Pes:
    def __init__(self):
        self.triky = []       # vlastní pro každého
```

---

## 🔍 Jak Python hledá atributy

Když napíšeš `rex.neco`:
1. Hledá v **instanci** — má `rex` atribut `neco`?
2. Když ne, hledá v **třídě** `Pes`.
3. Když ne, hledá v **rodičovských třídách**.
4. Když ne → `AttributeError`.

```python
class Pes:
    druh = "savec"           # atribut třídy

rex = Pes()
print(rex.druh)              # "savec"  (z TŘÍDY!)

rex.druh = "robot"           # přepíšeš na instanci
print(rex.druh)              # "robot"
print(Pes.druh)              # "savec"  (třída se nemění)
```

---

## 🔢 Konstanty třídy

```python
class Kruh:
    PI = 3.14159              # KONSTANTA — VELKÁ písmena

    def __init__(self, r):
        self.r = r

    def obsah(self):
        return Kruh.PI * self.r ** 2
```

---

## 🎚️ Soukromé atributy (konvence)

Python nemá opravdu soukromé atributy. Místo toho **konvence**:

```python
class Ucet:
    def __init__(self, zustatek):
        self._zustatek = zustatek         # _ = "soukromé"
        self.__pin = "1234"                # __ = "fakt soukromé" (name mangling)

u = Ucet(100)
u._zustatek          # 100  (jde, ale neměl bys)
u.__pin              # ❌ AttributeError!
u._Ucet__pin         # 1234  (přes name mangling)
```

- `_x` → konvence „nedotýkej se“
- `__x` → Python přejmenuje na `_Trida__x` (jen pro vyhnutí kolize, ne bezpečnost)

---

## 🔍 `vars()` a `__dict__`

Každá instance má slovník svých atributů:

```python
class Pes:
    def __init__(self, jmeno, vek):
        self.jmeno = jmeno
        self.vek = vek

rex = Pes("Rex", 5)
print(rex.__dict__)        # {'jmeno': 'Rex', 'vek': 5}
print(vars(rex))            # totéž
```

---

## ✏️ Cvičení

1. **Počítadlo psů:** Třída `Pes` se sdíleným `pocet_psu` co se zvyšuje při každém `__init__`.
2. **Past:** Vyrob třídu se sdíleným seznamem (jako `triky` výše) a předveď past.
3. **Konstanta:** Třída `Kruh` s konstantou `PI`. Spočítej obsah pro 3 různé poloměry.
4. **Soukromé:** Třída `Trezor` s `_obsah` a metodou `otevri(pin)` co vrátí obsah jen po správném PIN.
5. **Vars:** Vypiš všechny atributy nějaké instance přes `vars()`.
