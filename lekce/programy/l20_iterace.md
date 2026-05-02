# Program — Lekce 20: Lekce 20: Iterace — `enumerate`, `zip`, `reversed`, `sorted`

Patří k lekci [Lekce 20: Iterace — `enumerate`, `zip`, `reversed`, `sorted`](../20_iterace_enumerate_zip.md).

## Jak spustit

```bash
python3 programy/l20_iterace.py
```

## Zdrojový kód

### `l20_iterace.py`

```py
"""Lekce 20 — enumerate, zip, sorted."""


def main() -> None:
    # Enumerate
    konicky = ["čtení", "fotbal", "tanec", "hraní"]
    print("🎯 Mé koníčky:")
    for i, k in enumerate(konicky, 1):
        print(f"  {i}. {k}")

    # Zip
    jmena = ["Anna", "Bob", "Cyril"]
    veky = [10, 11, 12]
    mesta = ["Praha", "Brno", "Ostrava"]

    print("\n👥 Lidé:")
    for j, v, m in zip(jmena, veky, mesta):
        print(f"  {j} ({v}r, {m})")

    # Slovník ze zipu
    seznam = dict(zip(jmena, veky))
    print(f"\nSlovník: {seznam}")

    # Transpozice
    matice = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    print("\nTranspozice:")
    for radek in zip(*matice):
        print(f"  {radek}")

    # Sorted s key
    osoby = [
        {"jmeno": "Anna", "vek": 12},
        {"jmeno": "Bob",  "vek": 10},
        {"jmeno": "Cyril", "vek": 11},
    ]
    podle_veku = sorted(osoby, key=lambda o: o["vek"])
    print("\nPodle věku:")
    for o in podle_veku:
        print(f"  {o['jmeno']}: {o['vek']}")

    # All/Any
    cisla = [2, 4, 6, 8]
    print(f"\nVšechna sudá? {all(x % 2 == 0 for x in cisla)}")
    print(f"Aspoň jedno > 5? {any(x > 5 for x in cisla)}")


if __name__ == "__main__":
    main()

```
