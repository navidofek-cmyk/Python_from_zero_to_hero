# Lekce 144: Stromy — BST, AVL, Trie, Heap

Stromy jsou hierarchické datové struktury. Základ pro databázové indexy, parsery, kompresní algoritmy, priority queues a mnoho dalšího.

---

## 🌳 Základní pojmy

```
        8          ← kořen (root)
       / \
      3   10       ← vnitřní uzly
     / \    \
    1   6   14     ← listy (leaves)
       / \
      4   7

Hloubka uzlu 6 = 2 (počet hran od kořene)
Výška stromu = 3 (nejdelší cesta od kořene k listu)
Stupeň uzlu 3 = 2 (počet potomků)
```

---

## 🔍 Binary Search Tree (BST)

**Invariant:** levý podstrom < uzel < pravý podstrom

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Iterator


@dataclass
class Uzel:
    hodnota: int
    levy: Optional[Uzel] = field(default=None, repr=False)
    pravy: Optional[Uzel] = field(default=None, repr=False)


class BST:
    def __init__(self):
        self.koren: Optional[Uzel] = None

    def vloz(self, hodnota: int) -> None:
        self.koren = self._vloz(self.koren, hodnota)

    def _vloz(self, uzel: Optional[Uzel], hodnota: int) -> Uzel:
        if uzel is None:
            return Uzel(hodnota)
        if hodnota < uzel.hodnota:
            uzel.levy = self._vloz(uzel.levy, hodnota)
        elif hodnota > uzel.hodnota:
            uzel.pravy = self._vloz(uzel.pravy, hodnota)
        return uzel  # duplikáty ignorujeme

    def hledej(self, hodnota: int) -> bool:
        uzel = self.koren
        while uzel:
            if hodnota == uzel.hodnota:
                return True
            uzel = uzel.levy if hodnota < uzel.hodnota else uzel.pravy
        return False

    def smaz(self, hodnota: int) -> None:
        self.koren = self._smaz(self.koren, hodnota)

    def _smaz(self, uzel: Optional[Uzel], hodnota: int) -> Optional[Uzel]:
        if uzel is None:
            return None
        if hodnota < uzel.hodnota:
            uzel.levy = self._smaz(uzel.levy, hodnota)
        elif hodnota > uzel.hodnota:
            uzel.pravy = self._smaz(uzel.pravy, hodnota)
        else:
            # Uzel nalezen
            if uzel.levy is None:
                return uzel.pravy
            if uzel.pravy is None:
                return uzel.levy
            # Dva potomci — nahraď in-order nástupcem (minimum pravého podstromu)
            nastupce = self._minimum(uzel.pravy)
            uzel.hodnota = nastupce.hodnota
            uzel.pravy = self._smaz(uzel.pravy, nastupce.hodnota)
        return uzel

    def _minimum(self, uzel: Uzel) -> Uzel:
        while uzel.levy:
            uzel = uzel.levy
        return uzel

    # Průchody stromem
    def inorder(self) -> Iterator[int]:
        """Vrací prvky seřazeně (levý → kořen → pravý)."""
        yield from self._inorder(self.koren)

    def _inorder(self, uzel: Optional[Uzel]) -> Iterator[int]:
        if uzel:
            yield from self._inorder(uzel.levy)
            yield uzel.hodnota
            yield from self._inorder(uzel.pravy)

    def preorder(self) -> Iterator[int]:
        """Kořen → levý → pravý (kopírování stromu)."""
        yield from self._preorder(self.koren)

    def _preorder(self, uzel: Optional[Uzel]) -> Iterator[int]:
        if uzel:
            yield uzel.hodnota
            yield from self._preorder(uzel.levy)
            yield from self._preorder(uzel.pravy)

    def postorder(self) -> Iterator[int]:
        """Levý → pravý → kořen (mazání stromu)."""
        yield from self._postorder(self.koren)

    def _postorder(self, uzel: Optional[Uzel]) -> Iterator[int]:
        if uzel:
            yield from self._postorder(uzel.levy)
            yield from self._postorder(uzel.pravy)
            yield uzel.hodnota

    def vyska(self) -> int:
        return self._vyska(self.koren)

    def _vyska(self, uzel: Optional[Uzel]) -> int:
        if uzel is None:
            return 0
        return 1 + max(self._vyska(uzel.levy), self._vyska(uzel.pravy))

    def bfs(self) -> list[int]:
        """Průchod do šířky (level-order)."""
        from collections import deque
        if not self.koren:
            return []
        fronta = deque([self.koren])
        vysledek = []
        while fronta:
            uzel = fronta.popleft()
            vysledek.append(uzel.hodnota)
            if uzel.levy:
                fronta.append(uzel.levy)
            if uzel.pravy:
                fronta.append(uzel.pravy)
        return vysledek


# Použití
bst = BST()
for h in [8, 3, 10, 1, 6, 14, 4, 7]:
    bst.vloz(h)

print("Inorder (seřazeno):", list(bst.inorder()))   # [1, 3, 4, 6, 7, 8, 10, 14]
print("BFS (level-order):", bst.bfs())              # [8, 3, 10, 1, 6, 14, 4, 7]
print("Hledej 6:", bst.hledej(6))                  # True
print("Výška:", bst.vyska())                       # 4
bst.smaz(3)
print("Po smazání 3:", list(bst.inorder()))         # [1, 4, 6, 7, 8, 10, 14]
```

---

## ⚖️ AVL Strom — samovyvažující BST

BST se může degenerovat na lineární seznam. AVL strom udržuje výšku O(log n) rotacemi.

```python
@dataclass
class AVLUzel:
    hodnota: int
    levy: Optional[AVLUzel] = field(default=None, repr=False)
    pravy: Optional[AVLUzel] = field(default=None, repr=False)
    vyska: int = 1


class AVLStrom:
    def __init__(self):
        self.koren: Optional[AVLUzel] = None

    def _vyska(self, uzel) -> int:
        return uzel.vyska if uzel else 0

    def _balance(self, uzel) -> int:
        return self._vyska(uzel.levy) - self._vyska(uzel.pravy) if uzel else 0

    def _obnov_vysku(self, uzel: AVLUzel) -> None:
        uzel.vyska = 1 + max(self._vyska(uzel.levy), self._vyska(uzel.pravy))

    def _rotuj_vpravo(self, y: AVLUzel) -> AVLUzel:
        x = y.levy
        T2 = x.pravy
        x.pravy = y
        y.levy = T2
        self._obnov_vysku(y)
        self._obnov_vysku(x)
        return x

    def _rotuj_vlevo(self, x: AVLUzel) -> AVLUzel:
        y = x.pravy
        T2 = y.levy
        y.levy = x
        x.pravy = T2
        self._obnov_vysku(x)
        self._obnov_vysku(y)
        return y

    def _vyvaz(self, uzel: AVLUzel) -> AVLUzel:
        self._obnov_vysku(uzel)
        balance = self._balance(uzel)

        # Levé těžké
        if balance > 1:
            if self._balance(uzel.levy) < 0:   # Levo-pravý případ
                uzel.levy = self._rotuj_vlevo(uzel.levy)
            return self._rotuj_vpravo(uzel)

        # Pravé těžké
        if balance < -1:
            if self._balance(uzel.pravy) > 0:  # Pravo-levý případ
                uzel.pravy = self._rotuj_vpravo(uzel.pravy)
            return self._rotuj_vlevo(uzel)

        return uzel

    def vloz(self, hodnota: int) -> None:
        self.koren = self._vloz(self.koren, hodnota)

    def _vloz(self, uzel, hodnota: int):
        if not uzel:
            return AVLUzel(hodnota)
        if hodnota < uzel.hodnota:
            uzel.levy = self._vloz(uzel.levy, hodnota)
        elif hodnota > uzel.hodnota:
            uzel.pravy = self._vloz(uzel.pravy, hodnota)
        else:
            return uzel
        return self._vyvaz(uzel)

    def vyska(self) -> int:
        return self._vyska(self.koren)


# AVL vs BST — vyvažování
bst_deg = BST()
avl = AVLStrom()
for i in range(1, 11):   # seřazená data = worst case pro BST
    bst_deg.vloz(i)
    avl.vloz(i)

print(f"\nPo vložení 1..10 seřazeně:")
print(f"  BST výška: {bst_deg.vyska()} (degenerovaný!)")  # 10
print(f"  AVL výška: {avl.vyska()} (vyvážený)")           # 4
```

---

## 📝 Trie — prefixový strom

Ideální pro autocomplete, slovníky a prefix hledání.

```python
class TrieUzel:
    def __init__(self):
        self.deti: dict[str, TrieUzel] = {}
        self.je_konec: bool = False


class Trie:
    def __init__(self):
        self.koren = TrieUzel()

    def vloz(self, slovo: str) -> None:
        uzel = self.koren
        for pismeno in slovo:
            if pismeno not in uzel.deti:
                uzel.deti[pismeno] = TrieUzel()
            uzel = uzel.deti[pismeno]
        uzel.je_konec = True

    def hledej(self, slovo: str) -> bool:
        uzel = self.koren
        for pismeno in slovo:
            if pismeno not in uzel.deti:
                return False
            uzel = uzel.deti[pismeno]
        return uzel.je_konec

    def zacina_na(self, prefix: str) -> bool:
        uzel = self.koren
        for pismeno in prefix:
            if pismeno not in uzel.deti:
                return False
            uzel = uzel.deti[pismeno]
        return True

    def autocomplete(self, prefix: str) -> list[str]:
        """Vrátí všechna slova začínající prefixem."""
        uzel = self.koren
        for pismeno in prefix:
            if pismeno not in uzel.deti:
                return []
            uzel = uzel.deti[pismeno]
        vysledky = []
        self._sbírej(uzel, prefix, vysledky)
        return vysledky

    def _sbírej(self, uzel: TrieUzel, prefix: str, vysledky: list[str]) -> None:
        if uzel.je_konec:
            vysledky.append(prefix)
        for pismeno, dite in uzel.deti.items():
            self._sbírej(dite, prefix + pismeno, vysledky)


trie = Trie()
for slovo in ["python", "pythonik", "pytest", "pip", "pandas", "polars", "poetry"]:
    trie.vloz(slovo)

print("\nTrie autocomplete:")
print("  'py' →", trie.autocomplete("py"))   # ['python', 'pythonik', 'pytest']
print("  'po' →", trie.autocomplete("po"))   # ['polars', 'poetry']
print("  Hledej 'pip':", trie.hledej("pip")) # True
print("  Hledej 'pi':", trie.hledej("pi"))   # False (není celé slovo)
```

---

## 🏔️ Heap (Halda) — Priority Queue

```python
import heapq

# Min-heap (Python default)
halda = []
heapq.heappush(halda, 3)
heapq.heappush(halda, 1)
heapq.heappush(halda, 4)
heapq.heappush(halda, 1)
heapq.heappush(halda, 5)

print("\nMin-heap:")
while halda:
    print(f"  {heapq.heappop(halda)}", end=" ")   # 1 1 3 4 5
print()

# Max-heap — neguj hodnoty
max_halda = []
for x in [3, 1, 4, 1, 5, 9, 2]:
    heapq.heappush(max_halda, -x)
print("Max-heap:", [-heapq.heappop(max_halda) for _ in range(3)])  # [9, 5, 4]

# Prioritní fronta s objekty
from dataclasses import dataclass, field

@dataclass(order=True)
class Uloha:
    priorita: int
    nazev: str = field(compare=False)

fronta = []
heapq.heappush(fronta, Uloha(3, "Deploy"))
heapq.heappush(fronta, Uloha(1, "Opravit bug P0"))
heapq.heappush(fronta, Uloha(2, "Code review"))

print("\nPrioritní fronta:")
while fronta:
    u = heapq.heappop(fronta)
    print(f"  [{u.priorita}] {u.nazev}")

# K největších prvků
data = [1, 8, 3, 7, 2, 9, 4, 6, 5]
print("\n3 největší:", heapq.nlargest(3, data))   # [9, 8, 7]
print("3 nejmenší:", heapq.nsmallest(3, data))   # [1, 2, 3]
```

---

## 🎯 Kdy použít který strom

| Struktura | Vložení | Hledání | Ideální pro |
|-----------|---------|---------|-------------|
| BST | O(log n) avg | O(log n) avg | jednoduché hledání |
| AVL | O(log n) | O(log n) | časté vyhledávání, málo insertů |
| Red-Black | O(log n) | O(log n) | časté inserty/delety (std::map) |
| Trie | O(k) | O(k) | prefix search, autocomplete |
| Min-heap | O(log n) | O(1) min | priority queue, Dijkstra |
| B-tree | O(log n) | O(log n) | databázové indexy |

---

## ✏️ Cvičení

1. Implementuj **LCA** (Lowest Common Ancestor) pro BST — nejnižší společný předek dvou uzlů.
2. Ověř jestli je BST validní (splňuje BST invariant) bez rekurze.
3. Serializuj a deserializuj BST do/ze stringu (pre-order + marker pro null).
4. Implementuj **interval tree** — ukládá intervaly [lo, hi] a najde všechny překrývající se.
5. Postav autocomplete systém nad slovníkem českých slov pomocí Trie — měř čas vs lineárního vyhledávání.
