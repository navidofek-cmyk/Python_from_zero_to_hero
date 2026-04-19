# Lekce 71: Publikace na PyPI

## 📦 Co je PyPI?

**PyPI** (čti „pajpi“) = **Python Package Index** — centrální registr balíčků. Když napíšeš `pip install requests`, jde to z PyPI.

Můžeš tam přidat i **svůj** balíček — zdarma a otevřeně.

---

## 🛠️ Build

### S `hatch` (jednoduché)

```bash
pip install hatch
hatch build
# Vytvoří dist/muj_projekt-0.1.0-py3-none-any.whl + tar.gz
```

### S `build`

```bash
pip install build
python -m build
```

### S `uv`

```bash
uv build
```

---

## 🚀 Upload na PyPI

### 1. Test PyPI (nejdřív)

[test.pypi.org](https://test.pypi.org/) je sandbox.

```bash
pip install twine
twine upload --repository testpypi dist/*
```

Vytvoř si účet a token v Test PyPI.

### 2. Skutečné PyPI

```bash
twine upload dist/*
```

Token z [pypi.org/manage/account/](https://pypi.org/manage/account/).

### S `uv`

```bash
uv publish
```

---

## 🎯 Před publikací check

✅ **Unikátní jméno** (zkus `pip search` / web — teď už nesmí být obsazené)
✅ **README.md** — co dělá, jak nainstalovat, příklad
✅ **LICENSE** (MIT, Apache 2.0, BSD...)
✅ **Verze** (PEP 440 / semver: 1.2.3)
✅ **Otestováno** (pytest passed)
✅ **Žádné credentials** v souborech!

---

## 📜 Verzování

Sleduj **semver**:
- `1.0.0` → `1.0.1` — patch (bugfix, kompatibilní)
- `1.0.0` → `1.1.0` — minor (nová feature, kompatibilní)
- `1.0.0` → `2.0.0` — major (breaking change)

Před `1.0.0` je „pre-release“ — můžeš lámat cokoli.

---

## 🎁 Trusted publishing (modernější)

Místo tokenů: GitHub Actions s OIDC publikuje přímo. Vyhneš se kradení tokenů.

```yaml
# .github/workflows/publish.yml
- uses: pypa/gh-action-pypi-publish@release/v1
```

(Bez API tokenu.)

---

## ✏️ Cvičení

1. **Build:** Vyrob `pyproject.toml`, postav s `uv build`. Co je v `dist/`?
2. **Test PyPI:** Vytvoř účet na test.pypi.org. Uploadni svůj test balíček.
3. **Install z Test PyPI:** `pip install --index-url https://test.pypi.org/simple/ moje-jmeno`.
4. **Verze:** Aktualizuj verzi v `pyproject.toml` na 0.2.0 a zkus znovu.
