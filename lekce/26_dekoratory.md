# Lekce 26: Dekorátory funkcí

## 🎁 Co je dekorátor?

**Dekorátor** je **funkce, která obalí jinou funkci** něčím navíc — třeba zalogováním, měřením času, kontrolou oprávnění...

Představ si dárek: máš hračku (funkce) a obalíš ji **balícím papírem** (dekorátor). Hračka uvnitř je stejná, ale teď má i tu obálku.

---

## 🛠️ Nejjednodušší dekorátor

```python
def loguj(funkce):
    def obalka(*args, **kwargs):
        print(f"➡️  Volám {funkce.__name__}({args}, {kwargs})")
        vysledek = funkce(*args, **kwargs)
        print(f"⬅️  Vrátilo: {vysledek}")
        return vysledek
    return obalka


def secti(a, b):
    return a + b

secti = loguj(secti)        # obalíme

print(secti(2, 3))
# ➡️  Volám secti((2, 3), {})
# ⬅️  Vrátilo: 5
# 5
```

---

## ✨ Syntaxe se zavináčem `@`

`@dekorator` nad `def` je zkratka pro `f = dekorator(f)`:

```python
@loguj
def secti(a, b):
    return a + b

# Toto je TO SAMÉ jako:
def secti(a, b): ...
secti = loguj(secti)
```

Mnohem hezčí!

---

## 🏷️ `@functools.wraps` — povinná drobnost

Bez `wraps` ztratí obalená funkce své jméno a docstring:

```python
print(secti.__name__)   # "obalka"  ← :(
```

Použij `wraps`:

```python
from functools import wraps

def loguj(funkce):
    @wraps(funkce)
    def obalka(*args, **kwargs):
        ...
    return obalka

print(secti.__name__)   # "secti"  ✅
```

---

## ⏱️ Praktický příklad — měření času

```python
import time
from functools import wraps

def zmer_cas(funkce):
    @wraps(funkce)
    def obalka(*args, **kwargs):
        start = time.perf_counter()
        vysledek = funkce(*args, **kwargs)
        konec = time.perf_counter()
        print(f"⏱️  {funkce.__name__}: {konec-start:.3f}s")
        return vysledek
    return obalka


@zmer_cas
def pomalu():
    time.sleep(0.5)
    return "hotovo"

pomalu()    # ⏱️  pomalu: 0.501s
```

---

## 🎚️ Parametrizovaný dekorátor

Když chceš dekorátoru předat parametr (třeba kolikrát opakovat), potřebuješ **tři vrstvy**:

```python
def opakuj(kolikrat):
    def dekorator(funkce):
        @wraps(funkce)
        def obalka(*args, **kwargs):
            for _ in range(kolikrat):
                vysledek = funkce(*args, **kwargs)
            return vysledek
        return obalka
    return dekorator


@opakuj(3)
def pozdrav():
    print("Ahoj!")

pozdrav()
# Ahoj!
# Ahoj!
# Ahoj!
```

Přečteme zevnitř ven:
1. `opakuj(3)` vrátí `dekorator`
2. `dekorator(pozdrav)` vrátí `obalka`
3. `pozdrav` = `obalka`

---

## 🥞 Stackování dekorátorů

Můžeš jich navrstvit víc:

```python
@loguj
@zmer_cas
def neco():
    ...

# Spustí se: zmer_cas se aplikuje první, loguj druhý.
# Tedy: neco = loguj(zmer_cas(neco))
```

---

## 🎯 Časté dekorátory ze stdlib a knihoven

```python
@property                       # vlastnost (lekce 34)
@staticmethod / @classmethod    # statické metody (lekce 33)
@functools.lru_cache            # cache výsledků (lekce 27)
@dataclass                      # dataclass (lekce 41)
@pytest.fixture                 # test fixtura
@app.route("/")                 # Flask
```

---

## ✏️ Cvičení

1. **Loguj volání:** Napiš dekorátor `@loguj` co vypíše argumenty a výsledek.
2. **Změř čas:** Napiš `@zmer_cas` a aplikuj na funkci s `time.sleep(1)`.
3. **Cache:** Napiš jednoduchou cache: dekorátor `@cache` co si pamatuje výsledky podle argumentů ve slovníku.
4. **Opakuj N krát:** Napiš `@opakuj(n)`.
5. **Validace:** `@vyzaduj_kladne` — když je první argument záporný, vyhodí výjimku.
