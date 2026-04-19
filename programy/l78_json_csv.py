"""Lekce 78 — JSON, CSV."""

import csv
import json
import tempfile
from pathlib import Path


def main() -> None:
    data = [
        {"jmeno": "Anna", "vek": 12, "koniky": ["čtení", "fotbal"]},
        {"jmeno": "Bob", "vek": 11, "koniky": ["matematika"]},
    ]

    with tempfile.TemporaryDirectory() as tmp:
        slozka = Path(tmp)

        # JSON
        json_p = slozka / "data.json"
        json_p.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        nacteno = json.loads(json_p.read_text(encoding="utf-8"))
        print(f"JSON: {nacteno[0]['jmeno']} má {len(nacteno[0]['koniky'])} koníčků")

        # CSV — bez listů (CSV neumí)
        csv_p = slozka / "data.csv"
        with csv_p.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["jmeno", "vek"])
            w.writeheader()
            for o in data:
                w.writerow({"jmeno": o["jmeno"], "vek": o["vek"]})

        with csv_p.open(encoding="utf-8") as f:
            r = csv.DictReader(f)
            for radek in r:
                print(f"  CSV: {radek}")


if __name__ == "__main__":
    main()
