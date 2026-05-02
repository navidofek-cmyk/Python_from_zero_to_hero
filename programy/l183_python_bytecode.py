"""Lekce 183 — Python bytecode a CPython internals.
Spuštění: uv run l183_python_bytecode.py
"""

import dis
import sys
import ast
import gc
import types


def demo_dis():
    print("=" * 50)
    print("  🔬 Python Bytecode Demo")
    print("=" * 50)

    print("\n=== dis — disassembler ===")

    def secti(a, b): return a + b
    def podminka(x): return "kladné" if x > 0 else "záporné"
    def smycka(n): return [i**2 for i in range(n)]

    for fn in [secti, podminka, smycka]:
        print(f"\n  {fn.__name__}:")
        dis.dis(fn)
        code = fn.__code__
        print(f"    varnames={code.co_varnames}, consts={code.co_consts}")


def demo_peephole():
    print("\n=== Peephole optimalizace ===")

    def k1(): return 2 * 3 * 4      # → LOAD_CONST 24
    def k2(): return "a" + "b"      # → LOAD_CONST 'ab'
    def k3(x): return x + 0         # → x (není vždy)
    def k4(x): return x * 1         # → x (není vždy)

    for fn, popis in [(k1, "2*3*4"), (k2, "'a'+'b'")]:
        bytecodes = list(dis.get_instructions(fn))
        print(f"  {popis}: {[(i.opname, i.argval) for i in bytecodes if i.opname not in ('RESUME','RETURN_VALUE')]}")


def demo_frames():
    print("\n=== Frame objects ===")

    def funkce_c():
        frame = sys._getframe()
        stack = []
        f = frame
        while f:
            stack.append(f"{f.f_code.co_name}:{f.f_lineno}")
            f = f.f_back
        return stack[:4]

    def funkce_b(): return funkce_c()
    def funkce_a(): return funkce_b()

    stack = funkce_a()
    print("  Zásobník volání:")
    for s in stack: print(f"    {s}")

    # Lokální proměnné
    def debug_locals():
        x, y, jmeno = 42, 3.14, "Python"
        frame = sys._getframe()
        print(f"\n  Lokální proměnné: {dict(list(frame.f_locals.items())[:4])}")

    debug_locals()


def demo_gc():
    print("\n=== Garbage Collector ===")

    print(f"  Ref counting demo:")
    x = [1, 2, 3]
    print(f"  getrefcount([1,2,3]) = {sys.getrefcount(x)}")
    y = x
    print(f"  po y=x: {sys.getrefcount(x)}")
    del y
    print(f"  po del y: {sys.getrefcount(x)}")

    print(f"\n  GC generace threshold: {gc.get_threshold()}")
    print(f"  Aktuální počty: {gc.get_count()}")

    # Cyklická reference
    class N:
        def __init__(self): self.ref = None

    a, b = N(), N()
    a.ref = b; b.ref = a
    del a, b
    sesbrano = gc.collect()
    print(f"  Po cyklické ref + del: gc.collect() sesbral {sesbrano} objektů")


def demo_interning():
    print("\n=== Object interning ===")

    # Malá celá čísla jsou cached
    a, b = 100, 100
    print(f"  100 is 100: {a is b} (cached: -5 až 256)")
    a, b = 1000, 1000
    print(f"  1000 is 1000: {a is b} (new object každý raz)")

    # String interning
    s1, s2 = "python", "python"
    print(f"  'python' is 'python': {s1 is s2} (interned)")

    s1 = sys.intern("klíč_" * 50)
    s2 = sys.intern("klíč_" * 50)
    print(f"  sys.intern dlouhý string: {s1 is s2} (explicitní interning)")


def demo_slots():
    print("\n=== __slots__ vs __dict__ ===")

    class SeSloty:
        __slots__ = ["x", "y", "z"]
        def __init__(self): self.x = self.y = self.z = 0

    class BezSlotu:
        def __init__(self): self.x = self.y = self.z = 0

    se = SeSloty()
    bez = BezSlotu()
    print(f"  Se sloty:  {sys.getsizeof(se)} B")
    print(f"  Bez slotů: {sys.getsizeof(bez)} B + {sys.getsizeof(bez.__dict__)} B (__dict__)")
    print(f"  Úspora:    ~{sys.getsizeof(bez.__dict__)} B na objekt")

    import timeit
    t_se = timeit.timeit("se.x = 1", setup="se = SeSloty()", globals={"SeSloty": SeSloty})
    t_bez = timeit.timeit("bez.x = 1", setup="bez = BezSlotu()", globals={"BezSlotu": BezSlotu})
    print(f"\n  Přístup se sloty:  {t_se*1e6:.0f}ns")
    print(f"  Přístup bez slotů: {t_bez*1e6:.0f}ns")


def demo_ast():
    print("\n=== AST transformace ===")

    kod = "result = x * 1 + y + 0"
    tree = ast.parse(kod)
    print(f"  Původní: {kod}")
    print(f"  AST: {ast.dump(tree)[:100]}...")

    class OptAST(ast.NodeTransformer):
        def visit_BinOp(self, node):
            self.generic_visit(node)
            if isinstance(node.op, ast.Mult) and isinstance(node.right, ast.Constant) and node.right.value == 1:
                return node.left
            if isinstance(node.op, ast.Add) and isinstance(node.right, ast.Constant) and node.right.value == 0:
                return node.left
            return node

    optimized = OptAST().visit(tree)
    ast.fix_missing_locations(optimized)
    print(f"  Po optimalizaci: {ast.unparse(optimized)}")


def main():
    demo_dis()
    demo_peephole()
    demo_frames()
    demo_gc()
    demo_interning()
    demo_slots()
    demo_ast()
    print("\n✅ Demo dokončeno!")
    print("\nZajímavé moduly: dis, ast, gc, sys, inspect, types, ctypes")
    print("Pokročilé: bytecode (uv add bytecode), codetransformer")


if __name__ == "__main__":
    main()
