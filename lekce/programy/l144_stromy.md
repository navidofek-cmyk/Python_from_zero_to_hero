# Program — Lekce 144: Lekce 144: Stromy — BST, AVL, Trie, Heap

Patří k lekci [Lekce 144: Stromy — BST, AVL, Trie, Heap](../144_stromy.md).

## Jak spustit

```bash
python3 programy/l144_stromy.py
```

## Zdrojový kód

### `l144_stromy.py`

```py
"""Lekce 144 — Stromy: BST, AVL, Trie, Heap.

Spuštění:
    uv run l144_stromy.py
"""

from __future__ import annotations
import heapq
import random
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, Iterator


# ── BST ──────────────────────────────────────────────────────────────────────

@dataclass
class Uzel:
    hodnota: int
    levy: Optional[Uzel] = field(default=None, repr=False)
    pravy: Optional[Uzel] = field(default=None, repr=False)


class BST:
    def __init__(self): self.koren: Optional[Uzel] = None

    def vloz(self, h: int) -> None:
        self.koren = self._vloz(self.koren, h)

    def _vloz(self, u, h):
        if u is None: return Uzel(h)
        if h < u.hodnota: u.levy = self._vloz(u.levy, h)
        elif h > u.hodnota: u.pravy = self._vloz(u.pravy, h)
        return u

    def hledej(self, h: int) -> bool:
        u = self.koren
        while u:
            if h == u.hodnota: return True
            u = u.levy if h < u.hodnota else u.pravy
        return False

    def inorder(self) -> list[int]:
        def _io(u):
            if u: yield from _io(u.levy); yield u.hodnota; yield from _io(u.pravy)
        return list(_io(self.koren))

    def bfs(self) -> list[int]:
        if not self.koren: return []
        q, r = deque([self.koren]), []
        while q:
            u = q.popleft(); r.append(u.hodnota)
            if u.levy: q.append(u.levy)
            if u.pravy: q.append(u.pravy)
        return r

    def vyska(self) -> int:
        def _v(u): return 0 if u is None else 1 + max(_v(u.levy), _v(u.pravy))
        return _v(self.koren)


# ── AVL ──────────────────────────────────────────────────────────────────────

@dataclass
class AVLUzel:
    hodnota: int
    levy: Optional[AVLUzel] = field(default=None, repr=False)
    pravy: Optional[AVLUzel] = field(default=None, repr=False)
    vyska: int = 1


class AVL:
    def __init__(self): self.koren = None

    def _h(self, u): return u.vyska if u else 0
    def _bal(self, u): return self._h(u.levy) - self._h(u.pravy) if u else 0

    def _upd(self, u):
        u.vyska = 1 + max(self._h(u.levy), self._h(u.pravy))

    def _rr(self, y):
        x = y.levy; T2 = x.pravy; x.pravy = y; y.levy = T2
        self._upd(y); self._upd(x); return x

    def _rl(self, x):
        y = x.pravy; T2 = y.levy; y.levy = x; x.pravy = T2
        self._upd(x); self._upd(y); return y

    def _fix(self, u):
        self._upd(u); b = self._bal(u)
        if b > 1:
            if self._bal(u.levy) < 0: u.levy = self._rl(u.levy)
            return self._rr(u)
        if b < -1:
            if self._bal(u.pravy) > 0: u.pravy = self._rr(u.pravy)
            return self._rl(u)
        return u

    def vloz(self, h): self.koren = self._vloz(self.koren, h)

    def _vloz(self, u, h):
        if not u: return AVLUzel(h)
        if h < u.hodnota: u.levy = self._vloz(u.levy, h)
        elif h > u.hodnota: u.pravy = self._vloz(u.pravy, h)
        else: return u
        return self._fix(u)

    def vyska(self): return self._h(self.koren)


# ── Trie ─────────────────────────────────────────────────────────────────────

class TrieUzel:
    def __init__(self): self.deti: dict = {}; self.konec = False

class Trie:
    def __init__(self): self.koren = TrieUzel()

    def vloz(self, slovo: str):
        u = self.koren
        for p in slovo:
            if p not in u.deti: u.deti[p] = TrieUzel()
            u = u.deti[p]
        u.konec = True

    def hledej(self, slovo: str) -> bool:
        u = self.koren
        for p in slovo:
            if p not in u.deti: return False
            u = u.deti[p]
        return u.konec

    def autocomplete(self, prefix: str) -> list[str]:
        u = self.koren
        for p in prefix:
            if p not in u.deti: return []
            u = u.deti[p]
        vysledky = []
        def sbírej(uzel, cur):
            if uzel.konec: vysledky.append(cur)
            for p, d in uzel.deti.items(): sbírej(d, cur + p)
        sbírej(u, prefix)
        return sorted(vysledky)


# ── Heap ─────────────────────────────────────────────────────────────────────

def demo_heap():
    print("\n=== Min-heap (heapq) ===")
    h = []
    for x in [5, 3, 7, 1, 8, 2, 4]: heapq.heappush(h, x)
    print("  Výstup:", [heapq.heappop(h) for _ in range(7)])

    print("\n=== Max-heap ===")
    mh = []
    for x in [5, 3, 7, 1, 8, 2, 4]: heapq.heappush(mh, -x)
    print("  Výstup:", [-heapq.heappop(mh) for _ in range(7)])

    print("\n=== k-largest / k-smallest ===")
    data = [random.randint(1, 100) for _ in range(20)]
    print(f"  Data: {sorted(data)}")
    print(f"  5 největších: {heapq.nlargest(5, data)}")
    print(f"  5 nejmenších: {heapq.nsmallest(5, data)}")


def main():
    print("=" * 50)
    print("  🌳 Stromy Demo")
    print("=" * 50)

    print("\n=== BST ===")
    bst = BST()
    for h in [8, 3, 10, 1, 6, 14, 4, 7]: bst.vloz(h)
    print(f"  Inorder (seřazeně): {bst.inorder()}")
    print(f"  BFS (level-order):  {bst.bfs()}")
    print(f"  Výška: {bst.vyska()}")
    print(f"  Hledej 6: {bst.hledej(6)}, Hledej 5: {bst.hledej(5)}")

    print("\n=== BST vs AVL (degenerovaný input) ===")
    bst_deg, avl = BST(), AVL()
    for i in range(1, 16):
        bst_deg.vloz(i); avl.vloz(i)
    print(f"  BST výška (1..15 seřazeně): {bst_deg.vyska()} ← degenerovaný!")
    print(f"  AVL výška (1..15 seřazeně): {avl.vyska()} ← vyvážený")

    print("\n=== Trie (autocomplete) ===")
    trie = Trie()
    for s in ["python", "pythonik", "pytest", "pip", "pandas", "polars", "poetry", "pydantic"]:
        trie.vloz(s)
    print(f"  'py' → {trie.autocomplete('py')}")
    print(f"  'po' → {trie.autocomplete('po')}")
    print(f"  Hledej 'pip': {trie.hledej('pip')}")
    print(f"  Hledej 'pi': {trie.hledej('pi')}")

    demo_heap()
    print("\n✅ Demo dokončeno!")


if __name__ == "__main__":
    main()

```
