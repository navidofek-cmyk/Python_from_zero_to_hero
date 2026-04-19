"""Lekce 17 — collections demo."""

from collections import Counter, defaultdict, deque, ChainMap


def main() -> None:
    # Counter — počítání
    text = "ahoj svete ahoj svete ahoj kamarade svete svete"
    c = Counter(text.split())
    print(f"Top 2 slova: {c.most_common(2)}")

    # Defaultdict — group by
    osoby = [("Praha", "Anna"), ("Brno", "Bob"), ("Praha", "Cyril")]
    podle_mest = defaultdict(list)
    for mesto, jmeno in osoby:
        podle_mest[mesto].append(jmeno)
    print(f"Podle měst: {dict(podle_mest)}")

    # Deque s limitem
    historie = deque(maxlen=5)
    for i in range(10):
        historie.append(f"akce-{i}")
    print(f"Posledních 5: {list(historie)}")

    # ChainMap — vrstvy konfigurace
    defaulty = {"barva": "modrá", "velikost": "M", "font": "Arial"}
    uzivatel = {"barva": "červená"}
    cli =      {"velikost": "L"}

    config = ChainMap(cli, uzivatel, defaulty)
    for klic in ["barva", "velikost", "font"]:
        print(f"  {klic}: {config[klic]}")


if __name__ == "__main__":
    main()
