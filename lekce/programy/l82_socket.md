# Program — Lekce 82: Lekce 82: `socket`, `urllib`, `http.client`

Patří k lekci [Lekce 82: `socket`, `urllib`, `http.client`](../82_socket_http.md).

## Jak spustit

```bash
python3 programy/l82_socket.py
```

## Zdrojový kód

### `l82_socket.py`

```py
"""Lekce 82 — socket TCP echo server."""

import socket
import threading


def handle(client):
    with client:
        data = client.recv(1024)
        client.sendall(data.upper())


def server(port=8765, max_klientu=3):
    with socket.socket() as s:
        s.bind(("127.0.0.1", port))
        s.listen()
        print(f"🌐 Echo server na :{port}")
        for _ in range(max_klientu):
            client, addr = s.accept()
            print(f"📞 Připojen {addr}")
            threading.Thread(target=handle, args=(client,)).start()


def klient(port=8765, zprava=b"ahoj"):
    with socket.socket() as s:
        s.connect(("127.0.0.1", port))
        s.sendall(zprava)
        odpoved = s.recv(1024)
        print(f"📬 Odpověď: {odpoved.decode()}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        server()
    else:
        # Spustí server v threadu, pak klient
        threading.Thread(target=server, args=(8765, 1), daemon=True).start()
        import time
        time.sleep(0.3)
        klient(zprava=b"ahoj svete")

```
