# Lekce 2: REPL, skripty a `if __name__ == "__main__"`

## 🗣️ Dva způsoby, jak mluvit s robotem

Představ si, že máš kamaráda robota. Můžeš s ním komunikovat dvěma způsoby:

1. **Chat naživo** — ptáš se ho na věci po jedné a on hned odpovídá. Tomu se říká **REPL**.
2. **Uložený recept** — napíšeš mu celý seznam úkolů do sešitu (souboru) a on ho pak celý přečte a udělá. Tomu se říká **skript**.

---

## 💬 REPL — chatování s robotem

**REPL** znamená **R**ead – **E**val – **P**rint – **L**oop. V překladu: „přečti, vyhodnoť, vypiš, opakuj“. Prostě chat.

Spustíš ho v terminálu:

```bash
python3
```

Uvidíš trojitý šíp `>>>`. To znamená: „Poslouchám, co řekneš.“

```python
>>> 2 + 3
5
>>> jmeno = "Eliška"
>>> print("Ahoj", jmeno)
Ahoj Eliška
>>> exit()
```

**Kdy REPL použít?** Když si chceš něco **rychle zkusit** — třeba jestli funguje jeden řádek. Je to jako test hračky v obchodě, než si ji koupíš.

💡 **Tip:** Nainstaluj si `ipython` (`pip install ipython`) nebo `bpython` — je to vylepšený REPL s barvičkami a šipkama nahoru/dolů v historii.

---

## 📜 Skript — uložený recept

Otevři si textový editor (nejlíp **VS Code**) a vytvoř soubor `ahoj.py`:

```python
# ahoj.py
jmeno = input("Jak se jmenuješ? ")
print("Ahoj", jmeno, "! Vítej v Pythonu.")
```

Spustíš ho:

```bash
python3 ahoj.py
```

**Kdy skript použít?** Kdykoli chceš program **použít víckrát** nebo má **víc řádků**.

---

## 🎭 `if __name__ == "__main__"` — kouzelné zaklínadlo

Tohle je zvláštní řádek, který uvidíš skoro v každém Python souboru. Vypadá takhle:

```python
if __name__ == "__main__":
    print("Jsem spuštěný přímo!")
```

### Co to znamená česky?

Každý Python soubor má neviditelnou **jmenovku**. Ta jmenovka se jmenuje `__name__`.

- Když soubor **spustíš přímo** (`python3 ahoj.py`), jmenovka je `"__main__"` (jako „jsem hlavní“).
- Když ho někdo **jen použije jako knihovnu** (importuje ho), jmenovka je jméno souboru (třeba `"ahoj"`).

### Proč to potřebuješ?

Představ si, že napíšeš soubor `kalkulacka.py` s funkcí `secti(a, b)`. Chceš:

- **když soubor spustíš přímo** → ať to něco ukáže („Vítej v kalkulačce!“),
- **když ho jen importuješ** do jiného souboru → ať se ten uvítací text **nespustí**.

To ti řeší právě ta podmínka:

```python
# kalkulacka.py
def secti(a, b):
    return a + b

if __name__ == "__main__":
    # Tohle se spustí JEN když pustím přímo kalkulacka.py
    print("Vítej v kalkulačce!")
    print("2 + 3 =", secti(2, 3))
```

Je to jako cedulka na krabici: „Otevři mě, jen když si mě fakt kupuješ. Ne když mě jen přenášíš.“ 📦

---

## ✏️ Cvičení

1. **Chat:** Spusť `python3` a zkus: `10 * 10`, `"pes" * 3`, `len("Eliška")`. Co vrátí?
2. **Uložený recept:** Udělej soubor `pozdrav.py`, který se zeptá na jméno a věk, a vypíše: „Ahoj, *jméno*, za rok ti bude *věk+1*.“
3. **Zaklínadlo:** Napiš soubor `moje_knihovna.py` s funkcí `dvojnasobek(x)`. Dej tam `if __name__ == "__main__":` s testem. Pak udělej druhý soubor `pouziti.py`, který si to naimportuje (`from moje_knihovna import dvojnasobek`) — uvidíš, že testovací tisk se nespustil.
