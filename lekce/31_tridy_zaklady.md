# Lekce 31: Třídy a instance

## 🏭 Co je třída?

**Třída** je **šablona** (formička, plán). **Instance** je **konkrétní výrobek** podle té šablony.

Příklad ze života: třída = **plán domu**, instance = **konkrétní postavený dům**. Z jednoho plánu můžeš postavit X domů, každý jiný (jiná barva, jiní obyvatelé), ale všechny mají stejnou strukturu.

```python
class Pes:
    def __init__(self, jmeno: str, vek: int):
        self.jmeno = jmeno
        self.vek = vek

    def stekni(self) -> None:
        print(f"{self.jmeno}: Haf!")


# Vytvoření instancí
rex = Pes("Rex", 5)
bonzo = Pes("Bonzo", 3)

rex.stekni()       # Rex: Haf!
bonzo.stekni()     # Bonzo: Haf!

print(rex.jmeno)   # Rex
```

---

## 🔧 `__init__` — konstruktor

`__init__` se zavolá **automaticky při vytvoření instance**. Je to jako recept na sestavení.

```python
class Bod:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

p = Bod(3, 5)        # __init__ se zavolá s (self=p, x=3, y=5)
print(p.x, p.y)      # 3 5
```

---

## 🪞 Co je `self`?

`self` je **odkaz na sama sebe** — na konkrétní instanci, na které metoda běží. Python ho přidává automaticky.

```python
rex.stekni()
# Python si pod kapotou udělá: Pes.stekni(rex)
# To rex je to self.
```

Nemusíš se jmenovat `self` — je to jen konvence (silně dodržovaná).

---

## 🛠️ Metody

**Metoda** = funkce uvnitř třídy. Vždy má jako první parametr `self`.

```python
class Kruh:
    def __init__(self, polomer: float):
        self.polomer = polomer

    def obsah(self) -> float:
        return 3.14159 * self.polomer ** 2

    def obvod(self) -> float:
        return 2 * 3.14159 * self.polomer

k = Kruh(5)
print(k.obsah())     # 78.5
print(k.obvod())     # 31.4
```

---

## 🏷️ Atributy

**Atribut** = proměnná uvnitř instance. Přidáváš je přes `self.`.

```python
class Kniha:
    def __init__(self, nazev: str, autor: str):
        self.nazev = nazev
        self.autor = autor
        self.precteno = False     # default

k = Kniha("Hobit", "Tolkien")
k.precteno = True                  # můžeš měnit
k.poznamka = "Super!"              # můžeš i přidávat nové (zatím)
```

---

## 🖼️ `__repr__` — jak se třída vypíše

```python
class Pes:
    def __init__(self, jmeno):
        self.jmeno = jmeno

print(Pes("Rex"))   # <__main__.Pes object at 0x7f...>   ← ošklivé
```

Přidáme `__repr__`:

```python
class Pes:
    def __init__(self, jmeno):
        self.jmeno = jmeno

    def __repr__(self):
        return f"Pes({self.jmeno!r})"

print(Pes("Rex"))   # Pes('Rex')   ✅
```

(Více v lekci 37 o dunder metodách.)

---

## 📜 Konvence pojmenování

- Třídy: `PascalCase` — `Pes`, `BankovniUcet`, `HtmlParser`
- Metody a atributy: `snake_case` — `stekni`, `pocet_kosti`
- "Soukromé" (jen pro vnitřek třídy): `_zacina_podtrzitkem`

---

## 🎯 OOP v jedné větě

> **Spojíme data (atributy) a chování (metody), které spolu souvisejí, do jednoho objektu.**

Místo `udelej_stekani(pes_data)` → `pes.stekni()`. Hezčí, organizovanější.

---

## ✏️ Cvičení

1. **Třída Auto:** `__init__(znacka, model, rok)` + metoda `popis()` co vypíše „Škoda Octavia (2020)“.
2. **Kruh:** Třída `Kruh(polomer)` s metodami `obsah()` a `obvod()`.
3. **Bankovní účet:** `__init__(majitel, zustatek=0)`, metody `vloz(castka)`, `vyber(castka)`, `zustatek()`.
4. **Repr:** Přidej `__repr__` ke všem třídám výše.
5. **Slovník vs třída:** Vyrob 3 psy jednou jako slovníky a jednou jako instance třídy. Co se ti zdá hezčí?
