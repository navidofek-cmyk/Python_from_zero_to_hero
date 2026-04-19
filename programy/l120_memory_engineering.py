"""Lekce 120 — Memory Engineering."""

from __future__ import annotations

import gc
import sys
import tracemalloc
import weakref
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any


# ── sys.getsizeof ─────────────────────────────────────────────────────────────

def demo_getsizeof() -> None:
    print("\n=== sys.getsizeof — přímá velikost objektů ===")

    objekty: list[tuple[str, object]] = [
        ("int(0)", 0),
        ("int(42)", 42),
        ("int(10**100)", 10**100),
        ("float", 3.14),
        ("str('')", ""),
        ("str('ahoj')", "ahoj"),
        ("str(x*100)", "x" * 100),
        ("list([])", []),
        ("list([1,2,3])", [1, 2, 3]),
        ("tuple([1,2,3])", (1, 2, 3)),
        ("dict({})", {}),
        ("set()", set()),
        ("bool", True),
    ]

    for popis, obj in objekty:
        print(f"  {popis:20s}: {sys.getsizeof(obj):5d} B")

    # Kontejner vs obsah
    print()
    velky_seznam = list(range(1000))
    print(f"  list(range(1000)) getsizeof: {sys.getsizeof(velky_seznam):5d} B  (pouze pointerů!)")
    print(f"  deep_sizeof:                 {deep_sizeof(velky_seznam):5d} B  (včetně obsahu)")


def deep_sizeof(obj: object, navstivene: set[int] | None = None) -> int:
    """Rekurzivní sizeof — počítá i obsah kontejnerů."""
    if navstivene is None:
        navstivene = set()
    obj_id = id(obj)
    if obj_id in navstivene:
        return 0
    navstivene.add(obj_id)
    velikost = sys.getsizeof(obj)
    if isinstance(obj, dict):
        velikost += sum(
            deep_sizeof(k, navstivene) + deep_sizeof(v, navstivene)
            for k, v in obj.items()
        )
    elif isinstance(obj, Iterable) and not isinstance(obj, (str, bytes, bytearray)):
        velikost += sum(deep_sizeof(i, navstivene) for i in obj)
    return velikost


# ── tracemalloc ───────────────────────────────────────────────────────────────

def demo_tracemalloc() -> None:
    print("\n=== tracemalloc — sledování alokací ===")

    tracemalloc.start()
    snap1 = tracemalloc.take_snapshot()

    # Alokujeme data
    data = [{"klic": i, "hodnota": "x" * 50} for i in range(5_000)]

    snap2 = tracemalloc.take_snapshot()
    top_diff = snap2.compare_to(snap1, "lineno")

    print("  Top 3 nárůsty alokací:")
    for stat in top_diff[:3]:
        print(f"    {stat}")

    tracemalloc.stop()
    del data

    # Detekce leaku — porovnání před a po
    print()
    print("  Simulace memory leaku:")
    tracemalloc.start()
    snap_pred = tracemalloc.take_snapshot()

    leaky_cache: list[bytes] = []
    for _ in range(500):
        leaky_cache.append(b"data_leak" * 200)

    snap_po = tracemalloc.take_snapshot()
    diff = snap_po.compare_to(snap_pred, "lineno")

    celkem_narust = sum(s.size_diff for s in diff if s.size_diff > 0)
    print(f"    Nárůst alokované paměti: {celkem_narust / 1024:.1f} KB")
    tracemalloc.stop()


# ── weakref ───────────────────────────────────────────────────────────────────

class TezkyObjekt:
    """Objekt, který notifikuje o svém uvolnění."""

    def __init__(self, nazev: str) -> None:
        self.nazev = nazev
        self.data = "x" * 10_000  # Simulace dat

    def __del__(self) -> None:
        print(f"    [{self.nazev}] uvolněn z paměti")


def demo_weakref() -> None:
    print("\n=== weakref — slabé reference ===")

    print("  Silná reference — objekt PŘEŽIJE del:")
    obj_a = TezkyObjekt("A")
    silna = obj_a
    del obj_a   # Nefunguje — silna ho stále drží
    print("    (objekt A stále žije)")
    del silna   # Teď se uvolní
    gc.collect()

    print()
    print("  Slabá reference — objekt NEPŘEŽIJE del:")
    obj_b = TezkyObjekt("B")
    slaba: weakref.ref[TezkyObjekt] = weakref.ref(obj_b)
    print(f"    Před del: slaba() = {slaba()}")
    del obj_b
    gc.collect()
    print(f"    Po del:   slaba() = {slaba()}")

    print()
    print("  WeakValueDictionary — cache bez zadržování objektů:")
    cache: weakref.WeakValueDictionary[str, TezkyObjekt] = weakref.WeakValueDictionary()
    obj_c = TezkyObjekt("C")
    cache["klic"] = obj_c
    print(f"    Cache před del: {cache.get('klic')}")
    del obj_c
    gc.collect()
    print(f"    Cache po del:   {cache.get('klic')}  (automaticky odstraněn)")


# ── __slots__ ─────────────────────────────────────────────────────────────────

class BezSlots:
    def __init__(self, x: int, y: int, z: int) -> None:
        self.x = x
        self.y = y
        self.z = z


class SeSlots:
    __slots__ = ("x", "y", "z")

    def __init__(self, x: int, y: int, z: int) -> None:
        self.x = x
        self.y = y
        self.z = z


def demo_slots() -> None:
    print("\n=== __slots__ — úspora paměti ===")

    bez = BezSlots(1, 2, 3)
    se = SeSlots(1, 2, 3)

    vel_bez = sys.getsizeof(bez) + sys.getsizeof(bez.__dict__)
    vel_se = sys.getsizeof(se)

    print(f"  BezSlots: {sys.getsizeof(bez)} B (objekt) + {sys.getsizeof(bez.__dict__)} B (dict) = {vel_bez} B")
    print(f"  SeSlots:  {vel_se} B (žádný dict)")
    print(f"  Úspora:   ~{vel_bez - vel_se} B na instanci")

    # Při milionech instancí
    n = 100_000
    tracemalloc.start()
    instance_bez = [BezSlots(i, i, i) for i in range(n)]
    snap_bez = tracemalloc.take_snapshot()
    del instance_bez

    instance_se = [SeSlots(i, i, i) for i in range(n)]
    snap_se = tracemalloc.take_snapshot()
    del instance_se
    tracemalloc.stop()

    # Statistiky pro naši třídu
    stats_bez = snap_bez.statistics("filename")
    stats_se = snap_se.statistics("filename")
    print(f"\n  ({n} instancí — celková alokace viz tracemalloc výše)")


# ── gc — object graph ─────────────────────────────────────────────────────────

class MujObjekt:
    pass


def demo_gc() -> None:
    print("\n=== gc — object graph a cyklické reference ===")

    gc.collect()
    pred = len([o for o in gc.get_objects() if isinstance(o, MujObjekt)])

    instance_a = MujObjekt()
    instance_b = MujObjekt()
    instance_c = MujObjekt()

    po = len([o for o in gc.get_objects() if isinstance(o, MujObjekt)])
    print(f"  Před vytvořením: {pred} instancí MujObjekt")
    print(f"  Po vytvoření:    {po} instancí MujObjekt")

    # Cyklická reference
    print()
    print("  Cyklická reference:")

    class Uzel:
        def __init__(self, nazev: str) -> None:
            self.nazev = nazev
            self.dalsi: Uzel | None = None

    u1 = Uzel("u1")
    u2 = Uzel("u2")
    u1.dalsi = u2
    u2.dalsi = u1  # Cyklus!

    del u1, u2
    pred_gc = gc.get_count()
    shromázdeno = gc.collect()
    print(f"    gc.collect() uvolnil {shromázdeno} objektů v cyklu")


# ── Hlavní funkce ──────────────────────────────────────────────────────────────

def main() -> None:
    print("╔══════════════════════════════════════════╗")
    print("║  Lekce 120 — Memory Engineering         ║")
    print("╚══════════════════════════════════════════╝")

    demo_getsizeof()
    demo_tracemalloc()
    demo_weakref()
    demo_slots()
    demo_gc()

    print("\nHotovo! Klíčové poznatky:")
    print("  • sys.getsizeof neměří obsah kontejnerů — použij deep_sizeof")
    print("  • tracemalloc (stdlib) ukáže kde se alokuje paměť")
    print("  • weakref umožňuje cache bez zadržování objektů")
    print("  • __slots__ ušetří ~200 B na instanci")
    print("  • gc.collect() uvolní cyklické reference")


if __name__ == "__main__":
    main()
