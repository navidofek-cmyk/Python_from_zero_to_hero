"""Lekce 14 — množiny."""


def je_anagram(a: str, b: str) -> bool:
    return sorted(a.lower()) == sorted(b.lower())


def main() -> None:
    # Bez duplikátů
    cisla = [1, 2, 2, 3, 3, 3, 4, 5, 5]
    print(f"S duplikáty: {cisla}")
    print(f"Bez duplikátů: {list(set(cisla))}")

    # Společní kamarádi
    moji = {"Anna", "Petr", "Eva", "Tom"}
    tvoji = {"Petr", "Eva", "Lukáš"}

    print(f"\nSpolečné: {moji & tvoji}")
    print(f"Jen moji: {moji - tvoji}")
    print(f"Jen tvoji: {tvoji - moji}")
    print(f"Všichni:  {moji | tvoji}")
    print(f"XOR:      {moji ^ tvoji}")

    # Anagram
    print(f"\nje 'sluha' anagram 'lusha'? {je_anagram('sluha', 'lusha')}")
    print(f"je 'pes' anagram 'kočka'? {je_anagram('pes', 'kočka')}")

    # Unikátní písmena
    text = "Příšerně žluťoučký kůň úpěl ďábelské ódy"
    print(f"\nText: {text}")
    print(f"Unikátních písmen: {len(set(text.lower()) - {' '})}")


if __name__ == "__main__":
    main()
