"""Lekce 54 — generátorové korutiny."""


def prubezny_prumer():
    celkem = 0.0
    pocet = 0
    prumer = None
    while True:
        x = yield prumer
        celkem += x
        pocet += 1
        prumer = celkem / pocet


def main() -> None:
    p = prubezny_prumer()
    next(p)  # rozjedi
    for x in [10, 20, 30, 40]:
        print(f"po {x}: průměr = {p.send(x)}")


if __name__ == "__main__":
    main()
