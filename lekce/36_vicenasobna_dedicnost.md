# Lekce 36: Vícenásobná dědičnost a mixiny

## 👨‍👨‍👦 Třída může mít víc rodičů

```python
class Plavec:
    def plav(self):
        print("Plavu!")

class Letec:
    def let(self):
        print("Letím!")

class Kachna(Plavec, Letec):
    pass

k = Kachna()
k.plav()      # Plavu!
k.let()       # Letím!
```

Kachna je **plavec i letec** zároveň. To se v jednoduché dědičnosti nedá.

---

## 💎 Diamantový problém

Co když dva rodiče mají stejnou metodu?

```python
class A:
    def kdo(self): print("A")

class B(A):
    def kdo(self): print("B")

class C(A):
    def kdo(self): print("C")

class D(B, C):
    pass

D().kdo()    # B
D.__mro__    # (D, B, C, A, object)
```

Python zvolí **podle MRO** — zleva doprava. `D` → `B` (rodič vlevo) → `C` → `A` → `object`.

To je **C3 linearizace** — algoritmus zaručující konzistentní pořadí.

---

## 🤝 `super()` ve vícenásobné dědičnosti

`super()` neznamená vždy „rodič vlevo“ — znamená **„další v MRO“**.

```python
class A:
    def kdo(self): print("A")

class B(A):
    def kdo(self):
        print("B")
        super().kdo()

class C(A):
    def kdo(self):
        print("C")
        super().kdo()

class D(B, C):
    def kdo(self):
        print("D")
        super().kdo()

D().kdo()
# D → B → C → A   (každé volá super = další v MRO)
```

Tomu se říká **kooperativní dědičnost**. Důležité: každá metoda volá `super().kdo()`!

---

## 🧩 Mixiny — malé „přídavky“

**Mixin** = třída navržená **k přimíchání** (ne k samostatné existenci). Přidává jednu konkrétní schopnost.

```python
class JsonMixin:
    def to_json(self):
        import json
        return json.dumps(self.__dict__)

class ReprMixin:
    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{type(self).__name__}({attrs})"


class Pes(JsonMixin, ReprMixin):
    def __init__(self, jmeno, vek):
        self.jmeno = jmeno
        self.vek = vek

rex = Pes("Rex", 5)
print(rex)              # Pes(jmeno='Rex', vek=5)
print(rex.to_json())    # {"jmeno": "Rex", "vek": 5}
```

**Konvence:** mixiny mají často `Mixin` v názvu.

---

## 🎯 Kdy mixin, kdy normální dědičnost?

- **Dědičnost**: „Pes JE Zvíře.“ (is-a)
- **Mixin**: „Tahle třída UMÍ něco navíc.“ (-able)

`JsonSerializable`, `Comparable`, `Loggable` jsou typické mixiny.

---

## ⚠️ Vícenásobná dědičnost je komplikovaná

V Pythonu je možná, ale snadno se v ní ztratíš. **Většinou stačí**:
1. Jedna normální dědičnost
2. + pár mixinů s jasnou rolí

Pokud se ti to motá, zvaž **kompozici** (objekt obsahuje jiný objekt) místo dědičnosti.

---

## ✏️ Cvičení

1. **Mixin Loggable:** Vyrob mixin co přidá metodu `loguj(zprava)` co vypíše `[Trida.jmeno] zprava`.
2. **Diamantový problém:** Vytvoř `A`, `B`, `C`, `D` jako výše a sleduj MRO.
3. **Kachna:** Plavec, Letec, Kachna. Přidej Pingvin (jen plavec) a Vrabec (jen letec).
4. **JSON Mixin:** Mixin co umí `to_json()` a `from_json()`.
5. **Equality Mixin:** Mixin co implementuje `__eq__` na základě všech atributů.
