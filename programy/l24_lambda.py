"""Lekce 24 — lambda."""


def main() -> None:
    osoby = [
        {"jmeno": "Anna", "vek": 12, "skore": 85},
        {"jmeno": "Bob",  "vek": 10, "skore": 92},
        {"jmeno": "Cyril", "vek": 11, "skore": 78},
    ]

    print("Podle věku:")
    for o in sorted(osoby, key=lambda o: o["vek"]):
        print(f"  {o['jmeno']} ({o['vek']})")

    print("\nPodle skóre (od nejvyššího):")
    for o in sorted(osoby, key=lambda o: -o["skore"]):
        print(f"  {o['jmeno']}: {o['skore']}")

    # Filter sudých
    suda = list(filter(lambda x: x % 2 == 0, range(20)))
    print(f"\nSudá 0-19: {suda}")

    # Map mocnin
    mocniny = list(map(lambda x: x * x, range(1, 6)))
    print(f"Čtverce 1-5: {mocniny}")

    # Lépe pythonic:
    print(f"Comprehension: {[x*x for x in range(1, 6)]}")


if __name__ == "__main__":
    main()
