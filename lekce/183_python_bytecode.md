# Lekce 183: Python bytecode a CPython internals (deep dive)

Jak Python skutečně funguje pod kapotou. Bytecode, frame objects, GC, paměťový model.

---

## 🔍 dis — disassembler

```python
import dis
import sys


def secti(a: int, b: int) -> int:
    return a + b


# Zobraz bytecode
dis.dis(secti)

# Výstup:
#   2           0 RESUME          0
#   3           2 LOAD_FAST       0 (a)
#               4 LOAD_FAST       1 (b)
#               6 BINARY_OP      0 (+)
#              10 RETURN_VALUE


# Kód objektu
code = secti.__code__
print(f"Jméno:          {code.co_name}")
print(f"Argcount:       {code.co_argcount}")
print(f"Lokální proměnné: {code.co_varnames}")
print(f"Konstanty:      {code.co_consts}")
print(f"Bytecode (hex): {code.co_code.hex()}")
```

---

## ⚡ Optimalizace viditelná v bytecodu

```python
# Peephole optimizer — CPython optimalizuje při kompilaci

import dis

# Konstantní výraz — vypočítá se při kompilaci
def k1():
    return 2 * 3 * 4   # bytecode: LOAD_CONST 24

dis.dis(k1)
# 0 RESUME 0
# 2 LOAD_CONST 24   ← už je 24, ne 2*3*4!
# 4 RETURN_VALUE


# String concatenation s f-stringy
def f1(x):
    return "Ahoj " + str(x)   # volá str()

def f2(x):
    return f"Ahoj {x}"        # FORMAT_VALUE — rychlejší

dis.dis(f1)
dis.dis(f2)
```

---

## 🏗️ Frame objects

```python
import sys
import inspect


def ukazej_frames():
    """Prozkoumej zásobník volání."""
    frame = sys._getframe()   # aktuální frame

    print("=== Zásobník volání ===")
    while frame is not None:
        print(f"  {frame.f_code.co_filename}:{frame.f_lineno} "
              f"in {frame.f_code.co_name}")
        frame = frame.f_back


def funkce_a():
    def funkce_b():
        ukazej_frames()
    funkce_b()


funkce_a()


# Introspekce proměnných
def debug_prostredi():
    x = 42
    jmeno = "Anna"
    frame = sys._getframe()
    print("Lokální proměnné:", frame.f_locals)
    print("Globální proměnné (prvních 5):", dict(list(frame.f_globals.items())[:5]))


debug_prostredi()
```

---

## 🧹 Garbage Collector

```python
import gc


# Referenční počítání — primární GC
import sys

x = [1, 2, 3]
print(f"Ref count: {sys.getrefcount(x)}")   # 2 (x + argument)

y = x
print(f"Ref count po y=x: {sys.getrefcount(x)}")   # 3

del y
print(f"Ref count po del y: {sys.getrefcount(x)}")   # 2


# Cyklické reference — potřebují GC
class Uzel:
    def __init__(self):
        self.ref = None
        self.__del__ = lambda: print("  Mazán")


print("\nCyklická reference:")
a = Uzel()
b = Uzel()
a.ref = b
b.ref = a   # cyklus!
del a, b    # ref count > 0, ale nedostupné

print(f"Před GC: {gc.collect()} objektů sesbíráno")


# Generace GC
print(f"\nGC generace: {gc.get_threshold()}")   # (700, 10, 10)
print(f"Počty: {gc.get_count()}")
gc.collect(0)   # gen 0
gc.collect(1)   # gen 0 + 1
gc.collect(2)   # všechny generace


# Sledování alokací
gc.set_debug(gc.DEBUG_STATS)
gc.collect()
gc.set_debug(0)
```

---

## 🔢 Paměťový model Pythonu

```python
# Interning — sdílení malých objektů
import sys

# Malá celá čísla (-5 až 256) jsou cached
a = 100
b = 100
print(f"id(100) == id(100): {a is b}")   # True — stejný objekt!

a = 1000
b = 1000
print(f"id(1000) == id(1000): {a is b}")  # False — různé objekty

# String interning
s1 = "python"
s2 = "python"
print(f"'python' is 'python': {s1 is s2}")   # True (interned)

s1 = "hello world"
s2 = "hello world"
print(f"'hello world' is: {s1 is s2}")        # True nebo False (záleží)

# Explicitní interning
import sys
s1 = sys.intern("moje_" * 100)
s2 = sys.intern("moje_" * 100)
print(f"Po intern: {s1 is s2}")   # True


# __slots__ vs __dict__
class SeSloty:
    __slots__ = ["x", "y"]
    def __init__(self, x, y): self.x = x; self.y = y

class BezSlotu:
    def __init__(self, x, y): self.x = x; self.y = y

se = SeSloty(1, 2)
bez = BezSlotu(1, 2)
print(f"\nPaměť se sloty:   {sys.getsizeof(se)} B")
print(f"Paměť bez slotů:  {sys.getsizeof(bez)} B")
try:
    print(f"__dict__ bez:     {sys.getsizeof(bez.__dict__)} B")
except: pass
```

---

## ⚡ AST — Abstract Syntax Tree

```python
import ast


kod = """
def factorialy(n):
    if n <= 1:
        return 1
    return n * factorialy(n - 1)
"""

tree = ast.parse(kod)
print(ast.dump(tree, indent=2)[:500])

# Vlastní AST transformace
class OptimalizujKonstanty(ast.NodeTransformer):
    """Nahradí x * 1 za x, x + 0 za x."""

    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Mult):
            if isinstance(node.right, ast.Constant) and node.right.value == 1:
                return node.left   # x * 1 → x
        if isinstance(node.op, ast.Add):
            if isinstance(node.right, ast.Constant) and node.right.value == 0:
                return node.left   # x + 0 → x
        return node


transformovany = OptimalizujKonstanty().visit(tree)
print("\nPo optimalizaci:")
print(ast.unparse(transformovany))
```

---

## 🔧 Vlastní dekorátor s bytecode patching

```python
# Pokročilé: modifikace bytecodu za běhu
import types


def prida_logging(func):
    """Obalí každé volání funkce logováním přes frame inspection."""
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        jmena = func.__code__.co_varnames[:func.__code__.co_argcount]
        argumenty = dict(zip(jmena, args))
        argumenty.update(kwargs)
        print(f"VOLÁNÍ {func.__name__}({argumenty})")
        result = func(*args, **kwargs)
        print(f"VRÁTÍ {func.__name__} → {result!r}")
        return result
    return wrapper


@prida_logging
def secti(a: int, b: int) -> int:
    return a + b


secti(3, 4)
```

---

## ✏️ Cvičení

1. Napiš AST transformer, který automaticky přidá `@functools.lru_cache` ke všem čistým funkcím.
2. Implementuj jednoduchý Python profiler pomocí `sys.settrace`.
3. Porovnej `__dict__` vs `__slots__` na 1M objektech — paměť a rychlost.
4. Napiš vlastní `import hook` (sys.meta_path) — loguj všechny importy.
5. Prozkoumej bytecode rozdíl: `for` loop vs `while` vs `map` vs list comprehension.
