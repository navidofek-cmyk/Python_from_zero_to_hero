"""Lekce 16 — bytes a kódování."""

import base64


def main() -> None:
    text = "Příšerně žluťoučký kůň 🐎"

    utf8 = text.encode("utf-8")
    print(f"Text:       {text}")
    print(f"UTF-8 bytů: {len(utf8)} (písmen: {len(text)})")
    print(f"Hex:        {utf8.hex()}")
    print(f"Base64:     {base64.b64encode(utf8).decode()}")

    # Zpět
    zpet = utf8.decode("utf-8")
    print(f"Zpět:       {zpet}")

    # Bytearray
    ba = bytearray(b"hello")
    ba[0] = 72   # 'H'
    ba.append(33)  # '!'
    print(f"\nBytearray: {ba.decode()}")


if __name__ == "__main__":
    main()
