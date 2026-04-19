# Lekce 72: Entry points a CLI skripty

## 🎯 Entry point = automatický CLI příkaz

Když je v `pyproject.toml`:

```toml
[project.scripts]
moje-cli = "muj_projekt.cli:main"
```

Po `pip install` se vytvoří v PATH příkaz `moje-cli` co zavolá funkci `main` v modulu `muj_projekt.cli`.

```bash
$ moje-cli --help
```

---

## 🛠️ Plný příklad

`src/muj_projekt/cli.py`:

```python
import argparse


def main():
    parser = argparse.ArgumentParser(prog="moje-cli")
    parser.add_argument("jmeno")
    parser.add_argument("--vykricnik", action="store_true")
    args = parser.parse_args()

    konec = "!" if args.vykricnik else "."
    print(f"Ahoj {args.jmeno}{konec}")


if __name__ == "__main__":
    main()
```

`pyproject.toml`:

```toml
[project.scripts]
pozdrav = "muj_projekt.cli:main"
```

Po `pip install -e .`:
```bash
pozdrav Eliško --vykricnik
# Ahoj Eliško!
```

---

## 🎁 Plugin entry points

Druhý druh — **plugin systém**. Tvoje knihovna umí načíst pluginy z jiných balíčků.

`pyproject.toml` *pluginu*:
```toml
[project.entry-points."moje_app.plugins"]
audio = "audio_plugin:Plugin"
```

V *aplikaci*:
```python
from importlib.metadata import entry_points

for ep in entry_points(group="moje_app.plugins"):
    plugin_class = ep.load()
    plugin_class().start()
```

Tak fungují pluginy v Pelican, MkDocs, pytest atd.

---

## 🚀 Konzole vs GUI

```toml
[project.scripts]
moje-cli = "..."           # konzole

[project.gui-scripts]
moje-gui = "..."           # GUI (Windows nepustí konzoli)
```

---

## 🎯 Doporučované CLI knihovny

- `argparse` — stdlib, OK
- `click` — krásné dekorátorové CLI
- `typer` — typed CLI postavené na click
- `rich-click` — barevné click

---

## ✏️ Cvičení

1. **Pozdrav CLI:** Vyrob projekt s `pozdrav` entry pointem.
2. **Click:** Předělej do `click` (`pip install click`).
3. **Typer:** Předělej do `typer` (`pip install typer`).
4. **Plugin:** Vyrob plugin systém přes entry points.
