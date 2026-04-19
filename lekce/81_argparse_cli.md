# Lekce 81: `argparse`, `click`, `typer` — CLI

## 📋 `argparse` — stdlib

```python
import argparse

parser = argparse.ArgumentParser(prog="moje-app", description="Co dělá")
parser.add_argument("vstup", help="vstupní soubor")
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("-n", "--pocet", type=int, default=10)
parser.add_argument("--mod", choices=["a", "b", "c"], default="a")

args = parser.parse_args()
print(args.vstup, args.verbose, args.pocet, args.mod)
```

```bash
$ python app.py data.txt --verbose -n 20 --mod b
```

### Subkomandy (jako `git commit`, `git push`)

```python
parser = argparse.ArgumentParser()
sub = parser.add_subparsers(dest="cmd", required=True)

p_add = sub.add_parser("add")
p_add.add_argument("polozka")

p_list = sub.add_parser("list")

args = parser.parse_args()
if args.cmd == "add":
    pridej(args.polozka)
```

---

## 🎨 `click` — moderní (3rd party)

```bash
pip install click
```

```python
import click

@click.command()
@click.argument("vstup")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-n", "--pocet", type=int, default=10)
def main(vstup, verbose, pocet):
    """Co dělá moje CLI."""
    click.echo(f"Soubor: {vstup}")

if __name__ == "__main__":
    main()
```

### Subkomandy

```python
@click.group()
def cli(): pass

@cli.command()
@click.argument("polozka")
def add(polozka):
    click.echo(f"Přidáno: {polozka}")

@cli.command()
def list_():
    click.echo("Vše:")
```

`click.echo` lépe respektuje encoding/Windows než `print`.

---

## ⌨️ `typer` — typed CLI

```bash
pip install typer
```

```python
import typer

app = typer.Typer()

@app.command()
def add(polozka: str, priorita: int = 1):
    """Přidá položku."""
    typer.echo(f"+ {polozka} ({priorita})")

@app.command()
def list_():
    """Vypíše vše."""
    typer.echo("...")

if __name__ == "__main__":
    app()
```

Typer **vyrobí CLI z typových anotací** — krásné, čisté.

---

## 🎯 Co kdy?

| | argparse | click | typer |
|---|---|---|---|
| Stdlib | ✅ | ❌ | ❌ |
| Boilerplate | Hodně | Málo | Nejméně |
| Type-driven | ❌ | Trochu | ✅ |
| Subcommands | OK | Dobré | Dobré |
| Křivka učení | Střední | Mírná | Mírná |

**Doporučení:** Pro malé CLI `argparse`. Pro větší **`typer`**.

---

## ✏️ Cvičení

1. **Argparse:** Napiš CLI co dostane soubor a `--upper` flag, vrátí obsah velkými písmeny.
2. **Click:** To samé v click.
3. **Typer:** To samé v typer.
4. **Subkomandy:** Vyrob `todo add X`, `todo list`, `todo done N` v argparse.
