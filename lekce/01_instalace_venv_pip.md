# Lekce 1: Instalace Pythonu, venv a pip

## 🤖 Co je Python?

Představ si, že Python je **kouzelný robot-kuchař**, který bydlí v tvém počítači.

Ty mu napíšeš **recept** (to je tvůj program) a on ho uvaří — udělá přesně to, co je v receptu napsané. Třeba spočítá příklady, nakreslí obrázek nebo zahraje hru.

Aby ti robot mohl vařit, musíš si ho **nejdřív pozvat domů** — to znamená nainstalovat ho.

---

## 📥 1) Instalace Pythonu (pozvání robota domů)

Jdeš na stránku [python.org](https://www.python.org/downloads/) a stáhneš si Python 3.12 nebo novější.

Když ho instaluješ na **Windows**, je tam jedno super důležité políčko:

> ☑ **Add Python to PATH** ← MUSÍ být zaškrtnuté!

To je jako říct počítači: „Hele, kdykoli někdo zavolá ‚Pythone, pojď sem!‘, máš vědět, kde robot bydlí.“

Na **Linuxu** ho většinou už máš. Zkontroluješ to v terminálu:

```bash
python3 --version
```

Když ti to vypíše něco jako `Python 3.12.3`, robot je doma. 🎉

---

## 📦 2) `pip` — obchod s vychytávkami

Robot Python umí spoustu věcí sám. Ale někdy chceš **přídavky**, jako když si do Minecraftu stahuješ módy.

Třeba: „Chci, aby uměl kreslit grafy.“ Nebo: „Chci, aby uměl stahovat věci z internetu.“

Tyhle přídavky se jmenují **balíčky** a stahují se přes `pip` (to je takový obchoďák s balíčky).

Příklad — stáhneš si balíček `requests` (umí mluvit s internetem):

```bash
pip install requests
```

A je to. Teď tvůj robot umí stahovat věci z webu.

---

## 🏠 3) `venv` — vlastní pokojíček pro každý projekt

Tohle je důležitý trik. Představ si, že máš **doma LEGO**.

Stavíš si Hogwarts (jeden projekt) a vedle stavíš pirátskou loď (druhý projekt).

- Hogwarts potřebuje **černé dlaždičky** ve verzi 1.
- Pirátská loď potřebuje **černé dlaždičky** ve verzi 2 (jiný tvar).

Kdybys to měl všechno na jedné hromadě, **dílky by se ti pomíchaly** a nic by nepasovalo. 😱

Proto si pro každý projekt uděláš **vlastní krabičku** — tomu se v Pythonu říká **virtuální prostředí** (anglicky `virtual environment`, zkráceně `venv`).

### Jak na to (krok za krokem)

1. Otevřeš si terminál ve složce, kde máš projekt.
2. Vyrobíš krabičku:

```bash
python3 -m venv .venv
```

To znamená: „Pythone, vyrob mi krabičku, která se bude jmenovat `.venv`.“

3. **Vlezeš do krabičky** (aktivuješ ji):

**Linux / Mac:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

Když je krabička aktivní, na začátku řádku se ti objeví `(.venv)`. To je signál: „Teď jsem v krabičce, všechno, co stáhnu, zůstane jen tady.“

4. Teď klidně stahuj balíčky:

```bash
pip install requests
```

5. Až skončíš, **vylezeš z krabičky**:

```bash
deactivate
```

---

## 🎬 Celý příklad od začátku do konce (postaru, ručně)

```bash
# 1. Vytvořím si složku na projekt
mkdir muj_prvni_projekt
cd muj_prvni_projekt

# 2. Postavím krabičku
python3 -m venv .venv

# 3. Vlezu do krabičky
source .venv/bin/activate     # Linux/Mac
# nebo: .venv\Scripts\activate    # Windows

# 4. Stáhnu si balíček
pip install requests

# 5. Zkontroluju, co mám stažené
pip list

# 6. Až skončím, vylezu
deactivate
```

---

## 🚀 4) `uv` — moderní raketa místo šlapacího kola

Všechno, co jsme si dělali nahoře ručně (`venv`, `pip`, aktivace, deaktivace…), je jako **šlapací kolo**. Funguje. Ale jezdí se na něm pomalu.

**`uv`** (od firmy **Astral**) je **raketa**. 🚀

Je to **jeden nástroj**, který za tebe udělá všechno najednou:
- stáhne a nainstaluje správnou verzi **Pythonu** (nemusíš nic instalovat z python.org!),
- postaví **krabičku** (`venv`),
- stáhne **balíčky**,
- spustí tvůj **program**.

A je **10× až 100× rychlejší** než `pip`, protože je napsaný v jazyce **Rust**. Představ si, že místo čekání 30 sekund čekáš polovinu vteřiny. 🏎️💨

### Instalace uv (jednou za život)

**Linux / Mac:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Zkontroluj:
```bash
uv --version
```

### 🎮 Projekt s `uv` od nuly

Představ si, že si postavíš **nový svět v Minecraftu**. `uv` ti ten svět celý připraví jedním příkazem:

```bash
# 1. Vyrobím nový projekt (složku + soubory + krabičku)
uv init muj_raketa_projekt
cd muj_raketa_projekt
```

Po `uv init` máš ve složce:
- `pyproject.toml` — **seznam věcí, co projekt potřebuje** (jako nákupní seznam)
- `main.py` — připravený prázdný recept
- `.python-version` — která verze robota se má použít
- `README.md` — sešitek na poznámky

```bash
# 2. Přidám balíček (uv ho stáhne + zapíše do nákupního seznamu)
uv add requests

# 3. Spustím program
uv run main.py
```

**Všimni si** — vůbec jsme nemuseli ručně aktivovat žádnou krabičku! `uv` to dělá za tebe. Jako kdybys řekl kouzelnou hůlkou „spusť!“ a všechno se samo postavilo a rozběhlo. 🪄

### Hlavní kouzla `uv`

| Příkaz | Co udělá (jednoduše) |
|---|---|
| `uv init jmeno` | Vyrobí nový projekt (složku + všechno uvnitř) |
| `uv add balicek` | Přidá balíček do projektu |
| `uv remove balicek` | Odebere balíček |
| `uv run soubor.py` | Spustí tvůj program ve správné krabičce |
| `uv sync` | „Srovnej mi krabičku podle nákupního seznamu“ — doinstaluje, co chybí |
| `uv python install 3.12` | Stáhne konkrétní verzi Pythonu |
| `uv lock` | Zamkne přesné verze balíčků (aby to kamarádovi fungovalo stejně) |

### 📜 Co je `pyproject.toml`?

To je **nákupní seznam projektu**. Když ho pošleš kamarádovi, on napíše `uv sync` a má úplně stejný projekt jako ty. Ukázka:

```toml
[project]
name = "muj-raketa-projekt"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.31.0",
    "cowsay>=6.0",
]
```

Přeloženo do lidštiny: „Tenhle projekt se jmenuje _muj-raketa-projekt_, potřebuje Pythona verze aspoň 3.12 a dvě vychytávky: `requests` a `cowsay`.“

### 🆚 Starý způsob vs. uv — vedle sebe

| Úkol | Staře (pip + venv) | S `uv` |
|---|---|---|
| Nový projekt | `mkdir` + `python3 -m venv .venv` + aktivace | `uv init` |
| Přidat balíček | aktivovat venv + `pip install X` + zapsat do souboru | `uv add X` |
| Spustit program | aktivovat venv + `python main.py` | `uv run main.py` |
| Rychlost | 🐢 | 🚀 (10–100×) |

---

## 🧠 Co si zapamatovat

| Slovo | Co to je (jednoduše) |
|---|---|
| **Python** | Robot-kuchař, který umí číst tvoje recepty (programy) |
| **pip** | Obchoďák, kde si stahuješ vychytávky pro robota |
| **balíček** | Vychytávka navíc (mód do Minecraftu) |
| **venv** | Krabička jen pro jeden projekt, aby se vychytávky nepletly |
| **aktivovat** | Vlézt do krabičky |
| **deactivate** | Vylézt z krabičky |
| **uv** | Moderní raketa od Astralu — dělá venv + pip + spouštění naráz, a hodně rychle 🚀 |
| **pyproject.toml** | Nákupní seznam projektu (co všechno potřebuje) |

---

## ✏️ Cvičení

**Cvičení 1 — Robot je doma?**
Otevři terminál a napiš `python3 --version`. Co ti to vypsalo? Pokud je to číslo 3.10 nebo větší, jsi v pohodě.

**Cvičení 2 — Postav si krabičku**
Vytvoř si složku `pokus1`, v ní udělej virtuální prostředí, aktivuj ho a podívej se, co je v něm nainstalované (`pip list`). Mělo by tam být skoro nic — krabička je nová a prázdná.

**Cvičení 3 — Stáhni si balíček**
V aktivní krabičce stáhni balíček `cowsay` (`pip install cowsay`). Pak napiš:

```bash
python3 -c "import cowsay; cowsay.cow('Ahoj svete!')"
```

Měla by ti vyskočit kreslená kráva, co říká „Ahoj svete!“. 🐮

**Cvičení 4 — Druhá krabička**
Udělej druhou složku `pokus2` s vlastním venv. **Nestahuj** tam `cowsay`. Zkus `pip list` — vidíš, že `cowsay` tam není? To je kouzlo krabiček: každý projekt má svoje.

**Cvičení 5 — Projekt s `uv` 🚀**
Nainstaluj si `uv`. Pak udělej:

```bash
uv init muj_uv_pokus
cd muj_uv_pokus
uv add cowsay
uv run python -c "import cowsay; cowsay.cow('Jedu na raketě!')"
```

Porovnej: **jak moc** je to rychlejší než cvičení 2+3? A všimni si — ani jsi neaktivoval žádnou krabičku, `uv` to udělal sám. 🪄

**Cvičení 6 — Nákupní seznam**
Otevři si v `muj_uv_pokus` soubor `pyproject.toml`. Najdi tam řádek s `cowsay`. Přidej ručně do seznamu další balíček (třeba `"rich"`) a pak napiš `uv sync`. Co se stane? (Nápověda: `uv` ti ho automaticky stáhne do krabičky.)

---

## 🚀 V další lekci

Naučíme se, **jak vůbec spustit Python kód** — v REPLu (chatování s robotem) i jako skript (uložený recept).
