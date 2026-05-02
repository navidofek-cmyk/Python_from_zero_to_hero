# Program — Lekce 99: Lekce 99: Databáze — `sqlite3`, SQLAlchemy

Patří k lekci [Lekce 99: Databáze — `sqlite3`, SQLAlchemy](../99_databaze.md).

## Jak spustit

```bash
python3 programy/l99_sqlite.py
```

## Zdrojový kód

### `l99_sqlite.py`

```py
"""Lekce 99 — sqlite3 demo."""

import sqlite3
import tempfile
from pathlib import Path


def main() -> None:
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        cesta = Path(f.name)

    try:
        with sqlite3.connect(cesta) as con:
            con.execute("""
                CREATE TABLE uzivatele (
                    id INTEGER PRIMARY KEY,
                    jmeno TEXT NOT NULL,
                    vek INTEGER
                )
            """)
            data = [("Anna", 12), ("Bob", 11), ("Cyril", 13)]
            con.executemany(
                "INSERT INTO uzivatele (jmeno, vek) VALUES (?, ?)",
                data,
            )

            print("Všichni uživatelé:")
            for radek in con.execute("SELECT id, jmeno, vek FROM uzivatele"):
                print(f"  {radek}")

            print("\nMladší než 13:")
            for radek in con.execute(
                "SELECT jmeno, vek FROM uzivatele WHERE vek < ?",
                (13,),
            ):
                print(f"  {radek}")
    finally:
        cesta.unlink()


if __name__ == "__main__":
    main()

```
