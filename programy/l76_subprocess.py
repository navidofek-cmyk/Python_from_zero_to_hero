"""Lekce 76 — subprocess."""

import subprocess


def main() -> None:
    # ls -la
    r = subprocess.run(["ls", "-la"], capture_output=True, text=True, timeout=5)
    print(f"Exit: {r.returncode}")
    print(f"Prvních 5 řádků:\n{chr(10).join(r.stdout.splitlines()[:5])}")

    # Pipe: ls | grep .py (ručně)
    ls = subprocess.run(["ls"], capture_output=True, text=True)
    py_only = [r for r in ls.stdout.splitlines() if r.endswith(".py")]
    print(f"\n.py soubory: {py_only}")

    # Timeout demo
    try:
        subprocess.run(["sleep", "5"], timeout=0.5)
    except subprocess.TimeoutExpired:
        print("\n⏰ Sleep překročil timeout")


if __name__ == "__main__":
    main()
