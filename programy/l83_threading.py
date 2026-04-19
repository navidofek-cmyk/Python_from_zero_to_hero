"""Lekce 83 — threading + Lock."""

import threading
import time


pocet = 0
lock = threading.Lock()


def pricti():
    global pocet
    for _ in range(10_000):
        with lock:
            pocet += 1


def main() -> None:
    threads = [threading.Thread(target=pricti) for _ in range(10)]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"Počet: {pocet} (mělo by být 100000)")
    print(f"Čas: {time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    main()
