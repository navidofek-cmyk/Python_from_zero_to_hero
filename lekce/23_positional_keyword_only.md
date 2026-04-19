# Lekce 23: Positional-only `/` a keyword-only `*`

## 🚪 Co to je?

Někdy chceš **přinutit** uživatele, aby argument zadal **jen pozičně**, nebo **jen jménem**. Python na to má dva oddělovače:

- `/` = vše vlevo musí být **poziční** (positional-only)
- `*` = vše vpravo musí být **pojmenované** (keyword-only)

```python
def f(a, b, /, c, d, *, e, f):
    pass

f(1, 2, 3, 4, e=5, f=6)         # ✅ OK
f(a=1, b=2, c=3, d=4, e=5, f=6) # ❌ a, b musí být pozičně
f(1, 2, 3, 4, 5, 6)             # ❌ e, f musí být jménem
```

---

## 🤷 K čemu je to dobré?

### 1. Můžeš měnit jména parametrů, aniž bys rozbil cizí kód

```python
def vzdalenost(x1, y1, x2, y2, /):
    return ((x2-x1)**2 + (y2-y1)**2) ** 0.5

vzdalenost(0, 0, 3, 4)           # ✅ OK
vzdalenost(x1=0, y1=0, x2=3, y2=4)  # ❌ TypeError
```

Když to nikdo nevolá `vzdalenost(x1=...)`, můžeš si interně přejmenovat na `a, b, c, d` — nikomu se nic nerozbije.

### 2. Donutíš uživatele psát čitelně

```python
def odeslat(zprava, *, urgent=False, prijemce):
    ...

odeslat("Ahoj", prijemce="bob@example.com", urgent=True)   # ✅
odeslat("Ahoj", "bob", True)                                # ❌
```

Tohle je **mnohem čitelnější**. Když vidíš `urgent=True`, hned víš, co to znamená.

---

## 🎯 Reálné příklady ze stdlib

```python
# print() má oddělovače jako keyword-only:
print("a", "b", sep="-", end="\n", file=None, flush=False)

# sorted() má key a reverse jako keyword-only:
sorted(seznam, key=len, reverse=True)
```

Bez `*` bys mohl psát `sorted(seznam, len, True)` — ale to by nikdo nepřečetl.

---

## 🎓 Praktický vzor

```python
def vykresli_kruh(x, y, r, /, *, barva="černá", tloustka=1):
    """x, y, r jsou poziční (matematické). Barva a tloušťka jsou popisné."""
    ...

vykresli_kruh(10, 20, 5, barva="červená")     # ✅ čisté
```

---

## ✏️ Cvičení

1. **Pozici nebo jméno?** Napiš funkci `bod(x, y, /, *, jmeno)`. Zkus volat jí různě a uvidíš, co projde.
2. **Z print:** Vyrob vlastní `muj_print(*args, oddelovac="-", konec="\n")` s `*` aby vynutil pojmenování.
3. **Refaktor:** Vezmi funkci ze cvičení v lekci 22 a uprav ji s `/` a `*` tam, kde to dává smysl.
