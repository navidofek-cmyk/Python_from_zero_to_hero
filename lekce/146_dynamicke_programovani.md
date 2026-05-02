# Lekce 146: Dynamické programování

DP = **rozděl problém na podproblémy, každý vyřeš jednou a zapamatuj si výsledek**. Klíčové koncepty: optimální substruktura + překrývající se podproblémy.

---

## 🧠 Memoizace vs Tabulace

```
Memoizace (top-down):  rekurze + cache výsledků
Tabulace (bottom-up):  iterace od nejmenších podproblémů
```

---

## 🐇 Fibonacci — ukázka obou přístupů

```python
import time
from functools import lru_cache

# ❌ Naivní rekurze — O(2^n)
def fib_naivni(n: int) -> int:
    if n <= 1:
        return n
    return fib_naivni(n - 1) + fib_naivni(n - 2)


# ✅ Memoizace — O(n)
@lru_cache(maxsize=None)
def fib_memo(n: int) -> int:
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)


# ✅ Tabulace — O(n) čas, O(n) paměť
def fib_tabulace(n: int) -> int:
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]


# ✅ Optimalizovaná tabulace — O(n) čas, O(1) paměť
def fib_optimal(n: int) -> int:
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


# Srovnání výkonu
n = 35
for nazev, fn in [("Naivní", fib_naivni), ("Memo", fib_memo),
                   ("Tabulace", fib_tabulace), ("Optimál", fib_optimal)]:
    start = time.perf_counter()
    result = fn(n)
    cas = (time.perf_counter() - start) * 1000
    print(f"  {nazev:12}: fib({n})={result}, {cas:.2f}ms")
```

---

## 🎒 0/1 Knapsack (batoh)

Klasický DP problém: máme N věcí s vahami a hodnotami, batoh s kapacitou W. Maximalizuj hodnotu.

```python
def knapsack(vahy: list[int], hodnoty: list[int], kapacita: int) -> tuple[int, list[int]]:
    """
    Vrátí (max_hodnota, indexy_vybranych_veci).
    O(n * W) čas a paměť.
    """
    n = len(vahy)
    # dp[i][w] = max hodnota pro prvních i věcí a kapacitu w
    dp = [[0] * (kapacita + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(kapacita + 1):
            # Nevezmu věc i
            dp[i][w] = dp[i-1][w]
            # Vezmu věc i (pokud se vejde)
            if vahy[i-1] <= w:
                dp[i][w] = max(dp[i][w], dp[i-1][w - vahy[i-1]] + hodnoty[i-1])

    # Rekonstrukce — které věci jsou vybrány
    vybrane = []
    w = kapacita
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            vybrane.append(i - 1)
            w -= vahy[i - 1]

    return dp[n][kapacita], list(reversed(vybrane))


vahy =   [2, 3, 4, 5, 1]
hodnoty = [3, 4, 5, 8, 2]
kapacita = 7

max_h, vybrane = knapsack(vahy, hodnoty, kapacita)
print(f"\nKnapsack (kapacita={kapacita}):")
print(f"  Max hodnota: {max_h}")
print(f"  Vybrané věci (indexy): {vybrane}")
print(f"  Celková váha: {sum(vahy[i] for i in vybrane)}")
```

---

## 📏 Longest Common Subsequence (LCS)

Nejdelší společná podposloupnost — základ pro diff, DNA analýzu.

```python
def lcs(s1: str, s2: str) -> tuple[int, str]:
    """Délka a samotná LCS."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    # Rekonstrukce
    i, j = m, n
    sekvence = []
    while i > 0 and j > 0:
        if s1[i-1] == s2[j-1]:
            sekvence.append(s1[i-1])
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1

    return dp[m][n], "".join(reversed(sekvence))


delka, sekvence = lcs("ABCBDAB", "BDCAB")
print(f"\nLCS('ABCBDAB', 'BDCAB'): délka={delka}, sekvence='{sekvence}'")
```

---

## 💰 Coin Change

Minimální počet mincí pro danou částku.

```python
def coin_change(mince: list[int], castka: int) -> int:
    """Minimální počet mincí. Vrátí -1 pokud není řešení."""
    dp = [float("inf")] * (castka + 1)
    dp[0] = 0

    for c in range(1, castka + 1):
        for mince_hodnota in mince:
            if mince_hodnota <= c:
                dp[c] = min(dp[c], dp[c - mince_hodnota] + 1)

    return dp[castka] if dp[castka] != float("inf") else -1


def coin_change_kombinace(mince: list[int], castka: int) -> int:
    """Počet způsobů jak složit částku (pořadí nezáleží)."""
    dp = [0] * (castka + 1)
    dp[0] = 1
    for mince_hodnota in mince:
        for c in range(mince_hodnota, castka + 1):
            dp[c] += dp[c - mince_hodnota]
    return dp[castka]


print(f"\nCoin Change [1,5,10,25] na 41 Kč:")
print(f"  Min mincí: {coin_change([1, 5, 10, 25], 41)}")     # 4
print(f"  Počet způsobů: {coin_change_kombinace([1, 5, 10, 25], 41)}")
```

---

## 📐 Edit Distance (Levenshteinova vzdálenost)

Minimální počet operací (vložení, smazání, nahrazení) pro přeměnu jednoho stringu na druhý.

```python
def edit_distance(s1: str, s2: str) -> int:
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Inicializace
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # smazání
                    dp[i][j-1],    # vložení
                    dp[i-1][j-1]   # nahrazení
                )

    return dp[m][n]


print(f"\nEdit distance:")
print(f"  'kitten' → 'sitting': {edit_distance('kitten', 'sitting')}")  # 3
print(f"  'python' → 'pithon':  {edit_distance('python', 'pithon')}")   # 1
print(f"  'abc' → 'abc':       {edit_distance('abc', 'abc')}")           # 0
```

---

## 🏃 Nejdelší rostoucí podposloupnost (LIS)

```python
def lis(arr: list[int]) -> tuple[int, list[int]]:
    """O(n log n) pomocí binary search."""
    import bisect
    n = len(arr)
    if not n:
        return 0, []

    tails = []      # tails[i] = nejmenší konec LIS délky i+1
    parent = [-1] * n
    index = [-1] * n  # kde v tails je arr[i]

    for i, x in enumerate(arr):
        pos = bisect.bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x
        index[i] = pos
        if pos > 0:
            parent[i] = next(j for j in range(i-1, -1, -1) if index[j] == pos-1)

    # Rekonstrukce
    delka = len(tails)
    pos = delka - 1
    sekvence = []
    for i in range(n-1, -1, -1):
        if index[i] == pos:
            sekvence.append(arr[i])
            pos -= 1
            if pos < 0:
                break

    return delka, list(reversed(sekvence))


arr = [10, 9, 2, 5, 3, 7, 101, 18]
delka, sekvence = lis(arr)
print(f"\nLIS({arr}):")
print(f"  Délka: {delka}, Sekvence: {sekvence}")
```

---

## ⚡ Paralelní DP s multiprocessing

```python
import multiprocessing as mp
from functools import partial

def knapsack_worker(args):
    """Worker pro jeden řádek DP tabulky."""
    i, vahy, hodnoty, kapacita, predchozi_radek = args
    radek = [0] * (kapacita + 1)
    for w in range(kapacita + 1):
        radek[w] = predchozi_radek[w]
        if vahy[i] <= w:
            radek[w] = max(radek[w], predchozi_radek[w - vahy[i]] + hodnoty[i])
    return radek


# Poznámka: Skutečná paralelizace DP je omezená závislostmi mezi řádky.
# Vhodné pro: nezávislé podproblémy, tabulace přes různé startovní body.
```

---

## 🎯 Kdy použít DP

| Problém | DP varianta |
|---------|-------------|
| Optimalizace (min/max) | Tabulace bottom-up |
| Počítání způsobů | Tabulace + sumace |
| Rekurzivní s opakováním | Memoizace + @lru_cache |
| Stringové problémy | 2D DP tabulka |
| Sekvence | 1D DP tabulka |

**Jak poznat DP problém:**
1. „Maximalizuj / minimalizuj / počet způsobů"
2. Rozhodnutí závisí na předchozích rozhodnutích
3. Existují překrývající se podproblémy

---

## ✏️ Cvičení

1. Implementuj **Matrix Chain Multiplication** — optimální závorkovatelnost maticového násobení.
2. Napiš **Word Break** — lze string rozložit na slova ze slovníku?
3. Implementuj **Egg Drop** — minimální pokusy pro zjištění kritického patra s k vejci.
4. Vyřeš **Traveling Salesman Problem** s DP bitmaskingem pro malý počet měst (n ≤ 20).
5. Paralelizuj výpočet Fibonacci pomocí `asyncio.gather` — měř zrychlení vs sekvenčního.
