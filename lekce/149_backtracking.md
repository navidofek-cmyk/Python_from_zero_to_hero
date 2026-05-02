# Lekce 149: Backtracking — rekurzivní prohledávání

Backtracking = **zkoušej, a když to nefunguje, vrať se a zkus jinak**. Systematicky prochází stavový prostor a ořezává větve, které nemohou vést k řešení.

```
Backtracking šablona:
    def vyres(stav):
        if je_reseni(stav):
            uloz(stav)
            return
        for kandidat in kandidati(stav):
            if je_validni(stav, kandidat):
                aplikuj(stav, kandidat)
                vyres(stav)          ← rekurze
                odvolej(stav, kandidat)   ← backtrack
```

---

## ♟️ N-Queens — N dam na šachovnici

Rozmísti N dam tak, aby se žádné dvě neohrožovaly.

```python
from typing import Iterator


def n_queens(n: int) -> list[list[int]]:
    """Vrátí všechna řešení. Každé řešení = list kde reseni[i] = sloupec dámy v řadě i."""
    reseni = []

    def backtrack(radek: int, sloupce: set, diag1: set, diag2: set, rozmisteni: list[int]):
        if radek == n:
            reseni.append(rozmisteni[:])
            return
        for sloupec in range(n):
            if sloupec in sloupce or (radek - sloupec) in diag1 or (radek + sloupec) in diag2:
                continue
            sloupce.add(sloupec)
            diag1.add(radek - sloupec)
            diag2.add(radek + sloupec)
            rozmisteni.append(sloupec)

            backtrack(radek + 1, sloupce, diag1, diag2, rozmisteni)

            sloupce.remove(sloupec)
            diag1.remove(radek - sloupec)
            diag2.remove(radek + sloupec)
            rozmisteni.pop()

    backtrack(0, set(), set(), set(), [])
    return reseni


def zobraz_sachovnici(reseni: list[int]) -> str:
    n = len(reseni)
    radky = []
    for radek in range(n):
        radky.append(" ".join("♛" if reseni[radek] == s else "·" for s in range(n)))
    return "\n".join(radky)


# Příklad
vsechna = n_queens(8)
print(f"8-Queens: {len(vsechna)} řešení")
print(f"\nJedno řešení:\n{zobraz_sachovnici(vsechna[0])}")

# Počty řešení pro různá N
for n in range(1, 10):
    print(f"  {n}-Queens: {len(n_queens(n))} řešení")
```

---

## 🔢 Sudoku Solver

```python
def sudoku_solver(grid: list[list[int]]) -> bool:
    """Vyplní Sudoku in-place. Vrátí True pokud existuje řešení."""

    def je_validni(grid, radek, sloupec, cislo):
        # Kontrola řádku
        if cislo in grid[radek]:
            return False
        # Kontrola sloupce
        if cislo in (grid[r][sloupec] for r in range(9)):
            return False
        # Kontrola 3×3 bloku
        br, bs = 3 * (radek // 3), 3 * (sloupec // 3)
        for r in range(br, br + 3):
            for s in range(bs, bs + 3):
                if grid[r][s] == cislo:
                    return False
        return True

    def najdi_prazdne(grid):
        for r in range(9):
            for s in range(9):
                if grid[r][s] == 0:
                    return r, s
        return None

    prazdne = najdi_prazdne(grid)
    if prazdne is None:
        return True   # žádné prázdné = vyřešeno

    radek, sloupec = prazdne
    for cislo in range(1, 10):
        if je_validni(grid, radek, sloupec, cislo):
            grid[radek][sloupec] = cislo
            if sudoku_solver(grid):
                return True
            grid[radek][sloupec] = 0   # backtrack

    return False


def zobraz_sudoku(grid):
    for i, radek in enumerate(grid):
        if i % 3 == 0 and i > 0:
            print("------+-------+------")
        print(" ".join(
            str(x) if x != 0 else "·"
            for j, x in enumerate(radek)
        ).replace(" ", "", 0))


sudoku = [
    [5,3,0, 0,7,0, 0,0,0],
    [6,0,0, 1,9,5, 0,0,0],
    [0,9,8, 0,0,0, 0,6,0],
    [8,0,0, 0,6,0, 0,0,3],
    [4,0,0, 8,0,3, 0,0,1],
    [7,0,0, 0,2,0, 0,0,6],
    [0,6,0, 0,0,0, 2,8,0],
    [0,0,0, 4,1,9, 0,0,5],
    [0,0,0, 0,8,0, 0,7,9],
]
import copy
grid = copy.deepcopy(sudoku)
if sudoku_solver(grid):
    print("\nSudoku vyřešeno:")
    zobraz_sudoku(grid)
```

---

## 🔀 Permutace a kombinace

```python
def permutace(prvky: list) -> list[list]:
    """Všechny permutace seznamu."""
    if len(prvky) <= 1:
        return [prvky[:]]
    vysledky = []
    for i, prvek in enumerate(prvky):
        zbytek = prvky[:i] + prvky[i+1:]
        for perm in permutace(zbytek):
            vysledky.append([prvek] + perm)
    return vysledky


def kombinace(prvky: list, k: int) -> list[list]:
    """Všechny kombinace délky k."""
    vysledky = []
    def backtrack(start: int, aktualni: list):
        if len(aktualni) == k:
            vysledky.append(aktualni[:])
            return
        for i in range(start, len(prvky)):
            aktualni.append(prvky[i])
            backtrack(i + 1, aktualni)
            aktualni.pop()
    backtrack(0, [])
    return vysledky


def podmnoziny(prvky: list) -> list[list]:
    """Všechny podmnožiny (power set)."""
    vysledky = []
    def backtrack(start: int, aktualni: list):
        vysledky.append(aktualni[:])
        for i in range(start, len(prvky)):
            aktualni.append(prvky[i])
            backtrack(i + 1, aktualni)
            aktualni.pop()
    backtrack(0, [])
    return vysledky


prvky = [1, 2, 3, 4]
print(f"\nPermutace {prvky}: {len(permutace(prvky))} výsledků")
print(f"Kombinace {prvky} k=2: {kombinace(prvky, 2)}")
print(f"Podmnožiny {prvky[:3]}: {podmnoziny(prvky[:3])}")
```

---

## 🌀 Generátorová verze (lazy, bez ukládání)

```python
from typing import Iterator


def permutace_gen(prvky: list) -> Iterator[list]:
    """Generátor permutací — nespotřebovává paměť pro ukládání všech."""
    if len(prvky) <= 1:
        yield prvky[:]
        return
    for i in range(len(prvky)):
        prvky[0], prvky[i] = prvky[i], prvky[0]
        for perm in permutace_gen(prvky[1:]):
            yield [prvky[0]] + perm
        prvky[0], prvky[i] = prvky[i], prvky[0]


# Počítej bez ukládání
n = 8
pocet = sum(1 for _ in permutace_gen(list(range(n))))
print(f"\nPermutace {n} prvků: {pocet} (= {n}!)")
```

---

## 🏃 Bludiště (maze solver)

```python
def vyres_bludiste(bludiste: list[list[int]], start: tuple, cil: tuple) -> list[tuple] | None:
    """
    Najde cestu bludištěm.
    0 = volno, 1 = zeď
    """
    radky, sloupce = len(bludiste), len(bludiste[0])
    navstivene = set()

    def backtrack(pozice: tuple, cesta: list) -> bool:
        if pozice == cil:
            return True
        r, s = pozice
        for dr, ds in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, ns = r+dr, s+ds
            nova = (nr, ns)
            if (0 <= nr < radky and 0 <= ns < sloupce
                    and bludiste[nr][ns] == 0
                    and nova not in navstivene):
                navstivene.add(nova)
                cesta.append(nova)
                if backtrack(nova, cesta):
                    return True
                cesta.pop()
                navstivene.remove(nova)
        return False

    navstivene.add(start)
    cesta = [start]
    if backtrack(start, cesta):
        return cesta
    return None


bludiste = [
    [0, 1, 0, 0, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 0, 1, 0],
    [1, 1, 0, 0, 0],
    [0, 0, 0, 1, 0],
]
cesta = vyres_bludiste(bludiste, (0,0), (4,4))
print(f"\nBludiště — cesta: {cesta}")

# Vizualizace
if cesta:
    cesta_set = set(cesta)
    for r in range(len(bludiste)):
        radek = ""
        for s in range(len(bludiste[0])):
            if (r,s) in cesta_set:
                radek += "● "
            elif bludiste[r][s] == 1:
                radek += "█ "
            else:
                radek += "· "
        print(" ", radek)
```

---

## 🔤 Word Search

```python
def word_search(board: list[list[str]], slovo: str) -> bool:
    """Najde slovo v mřížce (horizontálně, vertikálně, diagonálně)."""
    radky, sloupce = len(board), len(board[0])

    def dfs(r: int, s: int, index: int, navstivene: set) -> bool:
        if index == len(slovo):
            return True
        if (r < 0 or r >= radky or s < 0 or s >= sloupce
                or (r, s) in navstivene
                or board[r][s] != slovo[index]):
            return False
        navstivene.add((r, s))
        for dr, ds in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            if dfs(r+dr, s+ds, index+1, navstivene):
                navstivene.remove((r, s))
                return True
        navstivene.remove((r, s))
        return False

    return any(
        dfs(r, s, 0, set())
        for r in range(radky)
        for s in range(sloupce)
    )


board = [
    ['P','Y','T','H','O','N'],
    ['R','E','K','U','R','Z'],
    ['E','A','L','G','O','E'],
    ['T','K','T','O','R','E'],
    ['S','T','R','O','M','Y'],
]
print(f"\nWord Search:")
for slovo in ["PYTHON", "REKURZE", "STROM", "ALGO", "XYZ"]:
    print(f"  '{slovo}': {'✅ nalezeno' if word_search(board, slovo) else '❌ nenalezeno'}")
```

---

## ⚡ Async backtracking (paralelní N-Queens)

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor


def n_queens_od_prvniho_sloupce(args: tuple) -> list[list[int]]:
    """Řeší N-Queens začínaje daným sloupcem v první řadě."""
    n, prvni_sloupec = args
    reseni = []

    def backtrack(radek, sloupce, d1, d2, rozmisteni):
        if radek == n:
            reseni.append(rozmisteni[:])
            return
        for s in range(n):
            if s in sloupce or (radek-s) in d1 or (radek+s) in d2:
                continue
            sloupce.add(s); d1.add(radek-s); d2.add(radek+s)
            rozmisteni.append(s)
            backtrack(radek+1, sloupce, d1, d2, rozmisteni)
            sloupce.remove(s); d1.remove(radek-s); d2.remove(radek+s)
            rozmisteni.pop()

    backtrack(1, {prvni_sloupec}, {0-prvni_sloupec}, {0+prvni_sloupec}, [prvni_sloupec])
    return reseni


async def n_queens_parallel(n: int) -> list[list[int]]:
    """Paralelní N-Queens — každý sloupec první řady v separátním procesu."""
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as ex:
        vysledky = await asyncio.gather(*[
            loop.run_in_executor(ex, n_queens_od_prvniho_sloupce, (n, s))
            for s in range(n)
        ])
    return [r for castecne in vysledky for r in castecne]
```

---

## 🎯 Kdy použít backtracking

| Případ | Příklad |
|--------|---------|
| Kombinatorické hledání | permutace, kombinace, podmnožiny |
| Constraint satisfaction | Sudoku, N-Queens, barvení grafu |
| Cesty v grafu/mřížce | bludiště, word search |
| Parsing | regulární výrazy, gramatiky |
| Optimalizace | TSP (malé instance) |

**Optimalizace backtrackingu:**
- **Pruning** — ořezávej větve co nejdříve
- **Forward checking** — zkontroluj důsledky před rekurzí
- **Most Constrained Variable** — začni s nejomezenějšími proměnnými
- **Lazy generátory** — generuj řešení postupně místo ukládání všech

---

## ✏️ Cvičení

1. Implementuj **barvení grafu** — obarvi vrcholy N barvami tak, aby žádné sousední vrcholy neměly stejnou barvu.
2. Vyřeš **Knight's Tour** — projdi šachovnicí jezdcem (koněm) tak, aby každé pole bylo navštíveno právě jednou.
3. Implementuj **Cryptarithmetic** solver — `SEND + MORE = MONEY` (každé písmeno = číslice).
4. Paralelizuj Sudoku solver — rozděl počáteční možnosti první prázdné buňky mezi procesy.
5. Napiš **regex engine** pomocí backtrackingu — zvládni `.` (libovolný znak) a `*` (opakování).
