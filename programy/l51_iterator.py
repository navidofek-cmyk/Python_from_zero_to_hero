"""Lekce 51 — vlastní iterátor."""


class Odpocet:
    def __init__(self, od: int):
        self.od = od

    def __iter__(self):
        self.aktualni = self.od
        return self

    def __next__(self):
        if self.aktualni < 0:
            raise StopIteration
        x = self.aktualni
        self.aktualni -= 1
        return x


def main() -> None:
    for i in Odpocet(5):
        print(i)
    print("BUM!")


if __name__ == "__main__":
    main()
