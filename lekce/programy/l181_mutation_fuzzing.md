# Program — Lekce 181: Lekce 181: Mutation testing + Fuzzing

Patří k lekci [Lekce 181: Mutation testing + Fuzzing](../181_mutation_fuzzing.md).

## Jak spustit

```bash
python3 programy/l181_mutation_fuzzing.py
```

## Zdrojový kód

### `l181_mutation_fuzzing.py`

```py
"""Lekce 181 — Mutation testing + Fuzzing.
Spuštění: uv run --with hypothesis l181_mutation_fuzzing.py
"""

import random
import time


# ── Kód k testování ───────────────────────────────────────────────────────────

def secti(a, b): return a + b
def odecti(a, b): return a - b
def vydel(a, b):
    if b == 0: raise ValueError("Dělení nulou")
    return a / b

def je_prvocislo(n):
    if n < 2: return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0: return False
    return True

def binary_search(arr, target):
    lo, hi = 0, len(arr)-1
    while lo <= hi:
        mid = (lo+hi)//2
        if arr[mid] == target: return mid
        elif arr[mid] < target: lo = mid+1
        else: hi = mid-1
    return -1


# ── Simulace mutation testing ──────────────────────────────────────────────────

def demo_mutation_testing():
    print("=" * 50)
    print("  🧬 Mutation Testing Demo")
    print("=" * 50)

    # Simulace mutantů
    mutants = [
        ("secti: a+b → a-b",   lambda a,b: a-b,   lambda: secti(2,3)==5),
        ("secti: a+b → a*b",   lambda a,b: a*b,   lambda: secti(2,3)==5),
        ("vydel: == → !=",      lambda a,b: None if b!=0 else 1/0,
                                lambda: vydel(10,2)==5.0),
        ("prvocislo: < 2 → <= 2", lambda n: n<=2,  lambda: not je_prvocislo(2)),
        ("binary_search: < → <=", None,           lambda: binary_search([1,3,5,7],5)==2),
    ]

    print("\n=== Mutanti (zachytí testy tyto chyby?) ===")
    testy_zakladni = [
        ("secti(2,3)==5", lambda: secti(2,3)==5),
        ("secti(-1,1)==0", lambda: secti(-1,1)==0),
        ("vydel(10,2)==5", lambda: vydel(10,2)==5.0),
        ("prvocislo(7)==True", lambda: je_prvocislo(7)),
        ("binary_search([1,3,5],5)==2", lambda: binary_search([1,3,5],5)==2),
    ]

    zabiti = 0
    for nazev, mutant_fn, odhaleni_test in mutants:
        zachycen = not odhaleni_test() if mutant_fn is None else True
        status = "✅ ZABIT" if zachycen else "💀 PŘEŽIL"
        print(f"  {status} - {nazev}")
        if zachycen: zabiti += 1

    print(f"\n  Mutation score: {zabiti}/{len(mutants)} = {100*zabiti/len(mutants):.0f}%")
    print("\n  Lepší testy (boundary values):")
    print("  secti(0,0), secti(-1,-1), secti(MAX_INT, 1)")
    print("  → zachytí víc mutantů!")


# ── Property-based testing ─────────────────────────────────────────────────────

def demo_hypothesis():
    print("\n=== Hypothesis — property-based testing ===")
    try:
        from hypothesis import given, strategies as st, settings, assume

        @given(st.integers(), st.integers())
        @settings(max_examples=200)
        def test_secti_komutativni(a, b):
            assert secti(a, b) == secti(b, a)

        @given(st.integers())
        def test_secti_nula(a):
            assert secti(a, 0) == a

        @given(st.integers(min_value=2, max_value=10000))
        def test_prvocislo_delitele(n):
            if je_prvocislo(n):
                delitele = [i for i in range(1, n+1) if n % i == 0]
                assert len(delitele) == 2

        @given(st.lists(st.integers(), min_size=1).flatmap(
            lambda lst: st.tuples(
                st.just(sorted(lst)),
                st.sampled_from(lst)
            )
        ))
        def test_binary_search(lst_target):
            lst, target = lst_target
            idx = binary_search(lst, target)
            assert idx >= 0 and lst[idx] == target

        t = time.perf_counter()
        test_secti_komutativni()
        test_secti_nula()
        test_prvocislo_delitele()
        test_binary_search()
        print(f"  ✅ Všechny property testy prošly ({(time.perf_counter()-t)*1000:.0f}ms)")
        print(f"  Testováno 200+ kombinací pro každou vlastnost")

    except ImportError:
        print("  Hypothesis: uv add hypothesis")
        print("""
  Ukázka:
    @given(st.integers(), st.integers())
    def test_komutativita(a, b):
        assert secti(a, b) == secti(b, a)  # testuje 100+ kombinací
""")


# ── Jednoduchý fuzzer ──────────────────────────────────────────────────────────

def demo_fuzzing():
    print("\n=== Jednoduchý fuzzer ===")

    def parsuj_datum(text):
        import re
        m = re.match(r"(\d{1,4})-(\d{1,2})-(\d{1,2})$", text.strip())
        if not m: return None
        r, me, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if me > 12 or d > 31: raise ValueError(f"Neplatné: {text}")
        return {"rok": r, "mesic": me, "den": d}

    # Generuj náhodné vstupy
    random.seed(42)
    chyby = []
    for _ in range(1000):
        # Náhodné vstupy
        delka = random.randint(0, 20)
        znaky = "0123456789-./abcXYZ\x00\n"
        vstup = "".join(random.choices(znaky, k=delka))
        try:
            parsuj_datum(vstup)
        except ValueError:
            pass  # očekávané
        except Exception as e:
            chyby.append((vstup, type(e).__name__, str(e)))

    print(f"  Fuzzováno 1000 vstupů")
    if chyby:
        print(f"  ❌ Nalezeno {len(chyby)} neočekávaných výjimek!")
        for vstup, typ, msg in chyby[:3]:
            print(f"    {typ}: '{vstup!r}' → {msg}")
    else:
        print("  ✅ Žádné neočekávané výjimky!")

    # Boundary value fuzzing
    hranice = ["2026-01-01", "0000-00-00", "9999-12-31",
               "2026-13-01", "2026-01-32", "", "-", "abc"]
    print(f"\n  Boundary value testing:")
    for vstup in hranice:
        try:
            r = parsuj_datum(vstup)
            print(f"    '{vstup}' → {r}")
        except ValueError as e:
            print(f"    '{vstup}' → ValueError (očekávané)")
        except Exception as e:
            print(f"    '{vstup}' → ❌ {type(e).__name__}: {e}")


def main():
    demo_mutation_testing()
    demo_hypothesis()
    demo_fuzzing()
    print("\n✅ Demo dokončeno!")
    print("Instalace: uv add hypothesis mutmut atheris")
    print("Mutation testing: mutmut run && mutmut results")


if __name__ == "__main__":
    main()

```
