# Lekce 33: Metody — instance, `@classmethod`, `@staticmethod`

## 3️⃣ Tři druhy metod

```python
class Auto:
    pocet_aut = 0

    def __init__(self, znacka):
        self.znacka = znacka
        Auto.pocet_aut += 1

    # 1. Instance metoda — má self
    def popis(self) -> str:
        return f"Auto: {self.znacka}"

    # 2. Class metoda — má cls (třídu)
    @classmethod
    def kolik(cls) -> int:
        return cls.pocet_aut

    # 3. Statická metoda — bez self ani cls
    @staticmethod
    def je_validni_spz(spz: str) -> bool:
        return len(spz) == 7
```

---

## 🐶 Instance metoda

Pracuje s konkrétní instancí přes `self`. To je 90 % metod.

```python
auto = Auto("Škoda")
auto.popis()        # "Auto: Škoda"
```

---

## 🏭 `@classmethod` — pracuje s třídou (ne instancí)

Dostává `cls` (samotnou třídu), ne `self`.

```python
Auto.kolik()        # 0
Auto("Škoda")
Auto.kolik()        # 1
```

### Hlavní použití: alternativní konstruktory

```python
class Datum:
    def __init__(self, den, mesic, rok):
        self.den, self.mesic, self.rok = den, mesic, rok

    @classmethod
    def z_textu(cls, text: str):
        d, m, r = map(int, text.split("."))
        return cls(d, m, r)               # POUŽIJ cls, ne Datum (kvůli dědičnosti)

    @classmethod
    def dnes(cls):
        from datetime import date
        d = date.today()
        return cls(d.day, d.month, d.year)


vanoce = Datum(24, 12, 2025)
nove = Datum.z_textu("01.01.2026")
ted = Datum.dnes()
```

Místo `Datum(24, 12, 2025)` máš víc způsobů, jak vyrobit instanci. Hezky čitelné!

---

## 📐 `@staticmethod` — funkce, co tematicky patří do třídy

Nemá `self` ani `cls`. Je to **obyčejná funkce**, jen bydlí ve třídě (kvůli organizaci).

```python
class Matematika:
    @staticmethod
    def je_prvocislo(n: int) -> bool:
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

Matematika.je_prvocislo(7)    # True
```

Mohlo by to být klidně volná funkce. Jen ji organizačně uklidíme do třídy.

---

## 🎯 Kdy co použít?

| Druh | Když | První argument |
|---|---|---|
| Instance metoda | Pracuje s jednou instancí | `self` |
| `@classmethod` | Pracuje s třídou (alt. konstruktor, počítadlo, …) | `cls` |
| `@staticmethod` | Logicky souvisí s třídou, ale nepotřebuje ji | žádný |

**Tip:** Většina metod je instance. Občas classmethod (alternativní konstruktory). Static methody jen výjimečně.

---

## 🤝 Volání mezi sebou

```python
class Auto:
    def info(self):
        return f"{self.znacka} ({self.kolik()})"

    @classmethod
    def kolik(cls):
        return cls.pocet_aut
```

Z instance metody můžeš volat všechny ostatní (přes `self.`).

---

## ✏️ Cvičení

1. **Auto:** Třída `Auto` s počítadlem aut (classmethod `kolik`).
2. **Datum:** Vyrob `Datum` s alternativními konstruktory `z_textu` a `dnes`.
3. **Matematika:** Třída se statickými metodami `je_prvocislo`, `gcd`, `lcm`.
4. **Bod:** Třída `Bod(x, y)` s `@classmethod` `pocatek()` co vrátí `Bod(0, 0)`.
5. **From dict:** Třída `Osoba(jmeno, vek)` s `@classmethod from_dict(d)` co vyrobí osobu ze slovníku.
