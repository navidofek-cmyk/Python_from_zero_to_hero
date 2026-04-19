# Lekce 24: Lambda funkce

## 🦋 Co je lambda?

**Lambda** je **mini funkce na jeden řádek bez jména**. Jako poznámka místo plného sešitu.

```python
# Místo:
def na_druhou(x):
    return x * x

# Můžeš:
na_druhou = lambda x: x * x

print(na_druhou(5))    # 25
```

Syntaxe: `lambda parametry: vyraz`

- žádné `def`, žádné `return`
- jen **jeden výraz** (žádné víc řádků)

---

## 🎯 Kdy lambdu použít

Většinou jako **argument do jiné funkce**, kde si nechceš zakládat plnou `def`.

```python
slova = ["pes", "kočka", "myš", "slon"]

# Seřaď podle délky
sorted(slova, key=lambda s: len(s))

# Seřaď podle posledního písmene
sorted(slova, key=lambda s: s[-1])

# Seřaď slovníky podle věku
osoby = [{"j": "A", "v": 12}, {"j": "B", "v": 10}]
sorted(osoby, key=lambda o: o["v"])
```

S `map`/`filter` (i když comprehension je často lepší):

```python
ctverce = list(map(lambda x: x*x, [1, 2, 3]))
# Lépe: [x*x for x in [1, 2, 3]]

suda = list(filter(lambda x: x % 2 == 0, range(10)))
# Lépe: [x for x in range(10) if x % 2 == 0]
```

---

## 🚫 Kdy lambdu NEpoužívat

❌ **Když má jméno**:
```python
na_druhou = lambda x: x * x       # ❌
def na_druhou(x): return x * x    # ✅ jasnější
```

❌ **Pokud je delší než jeden výraz**:
```python
# Když potřebuješ víc kroků, použij def
```

❌ **Pro složitou logiku**:
```python
sorted(s, key=lambda x: (x.priority, -x.deadline, x.name.lower()))
# Když je lambda složitá, vytáhni ji do def funkce.
```

---

## 🎩 Trik s `key=str.lower`

Místo `lambda s: s.lower()` můžeš použít přímo metodu jako funkci:

```python
sorted(["Banán", "ananas", "Citron"], key=str.lower)
```

To je **jeste pythonštější**.

---

## ✏️ Cvičení

1. **Třídění:** Máš seznam tuple `[(1, 'b'), (2, 'a'), (3, 'c')]`. Seřaď podle druhého prvku pomocí `lambda`.
2. **Filter sudých:** Z `range(20)` vyber jen sudá čísla pomocí `filter`. (Pak to napiš i comprehension — která verze se ti líbí víc?)
3. **Map mocnin:** Vyrob seznam `[1, 4, 9, 16, 25]` přes `map(lambda x: x*x, ...)`.
4. **Triáž:** Máš seznam slovníků s ticketem (`priorita`, `vek`). Seřaď podle priority (1 první), pak podle stáří (starší dřív).
