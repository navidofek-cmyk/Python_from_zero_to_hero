# Lekce 35: Dědičnost a `super()`

## 👨‍👦 Co je dědičnost?

**Dědičnost** = nová třída **dědí** vlastnosti od existující.

Ze života: **Pes** je druh **Zvíře**. Všechno co umí zvíře (jíst, spát) umí i pes. Plus pes umí navíc štěkat.

```python
class Zvire:
    def __init__(self, jmeno: str):
        self.jmeno = jmeno

    def spi(self) -> None:
        print(f"{self.jmeno} chrápe.")


class Pes(Zvire):                    # ← (Zvire) znamená dědí od Zvire
    def steka(self) -> None:
        print(f"{self.jmeno}: Haf!")


rex = Pes("Rex")
rex.spi()         # Rex chrápe.   (zděděno!)
rex.steka()       # Rex: Haf!     (vlastní)
```

- `Zvire` = **rodičovská** (parent / base / super)
- `Pes` = **dceřinná** (child / derived / sub)

---

## 🪜 `super()` — volání rodiče

Když chceš v dítěti rozšířit, ale ne nahradit, voláš rodiče přes `super()`.

```python
class Zvire:
    def __init__(self, jmeno: str):
        self.jmeno = jmeno

class Pes(Zvire):
    def __init__(self, jmeno: str, plemeno: str):
        super().__init__(jmeno)       # zavolá Zvire.__init__
        self.plemeno = plemeno

rex = Pes("Rex", "labrador")
print(rex.jmeno, rex.plemeno)
```

Bez `super()` bys musel:
```python
self.jmeno = jmeno   # opakování kódu
```

---

## 🎭 Přepsání metody (overriding)

```python
class Zvire:
    def zvuk(self):
        print("nějaký zvuk")

class Pes(Zvire):
    def zvuk(self):                     # přepsáno!
        print("Haf!")

class Kocka(Zvire):
    def zvuk(self):
        print("Mňau!")

for z in [Pes(), Kocka(), Zvire()]:
    z.zvuk()
# Haf! Mňau! nějaký zvuk
```

To je **polymorfismus** — různé třídy mají stejnou metodu, ale chovají se jinak.

---

## 🔍 `isinstance` a `issubclass`

```python
isinstance(rex, Pes)        # True
isinstance(rex, Zvire)      # True   (Pes JE Zvire)
isinstance(rex, Kocka)      # False

issubclass(Pes, Zvire)      # True
issubclass(Pes, Kocka)      # False
```

Vždy preferuj `isinstance(x, T)` místo `type(x) is T` — `isinstance` rozumí dědičnosti.

---

## 🧬 MRO (Method Resolution Order)

Když je dědičnost složitá, Python má jasný **algoritmus** kde co hledat. Říká se mu **C3 linearizace** (lekce 35 pokročile).

```python
class A: 
    def kdo(self): print("A")

class B(A): 
    def kdo(self): print("B")

class C(A): 
    def kdo(self): print("C")

class D(B, C): pass

D.__mro__      # (D, B, C, A, object)
D().kdo()      # B  (najde v B první)
```

`__mro__` ti řekne přesně, v jakém pořadí Python hledá.

---

## 🌟 `object` — pradědek všeho

Každá třída v Pythonu nakonec dědí od `object`. Proto všechno má `__init__`, `__repr__` atd.

```python
class Pes: pass
issubclass(Pes, object)   # True
```

---

## ✏️ Cvičení

1. **Zvíře, Pes, Kočka:** Vyrob třídu `Zvire` se `spi()` a `jmeno`. Pak `Pes` a `Kocka` co dědí a každá má vlastní `zvuk()`.
2. **Super:** Přepiš `__init__` v Psovi tak, aby měl `plemeno` navíc. Použij `super()`.
3. **Vozidlo:** `Vozidlo`, `Auto(Vozidlo)`, `Motorka(Vozidlo)`. Společné: rychlost, hmotnost. Specifické: počet kol.
4. **MRO:** Vyrob hierarchii ABCD jako výše a vypiš `D.__mro__`.
5. **Polymorfismus:** Seznam různých zvířat — projdi smyčkou a zavolej `zvuk()`. Každé zaštěká/zamňouká po svém.
