"""Lekce 73 — pathlib."""

from pathlib import Path


def main() -> None:
    cwd = Path.cwd()
    print(f"Aktuální adresář: {cwd}")
    print(f"Domov: {Path.home()}")

    # Najdi .py soubory
    py_soubory = list(cwd.glob("*.py"))
    print(f"\nPython souborů v cwd: {len(py_soubory)}")
    for p in py_soubory[:5]:
        print(f"  {p.name} ({p.stat().st_size} B)")

    # Vytvoř / smaž
    test = Path("/tmp/test_pathlib")
    test.mkdir(exist_ok=True)
    (test / "ahoj.txt").write_text("Ahoj svete!", encoding="utf-8")
    print(f"\nSoubor: {(test / 'ahoj.txt').read_text(encoding='utf-8')}")
    (test / "ahoj.txt").unlink()
    test.rmdir()


if __name__ == "__main__":
    main()
