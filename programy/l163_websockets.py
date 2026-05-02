"""Lekce 163 — WebSockets: real-time komunikace.

Demo serveru:
    uv run --with "fastapi[standard]" l163_websockets.py

Klient test (v jiném terminálu):
    python -c "
import asyncio, websockets, json
async def test():
    async with websockets.connect('ws://localhost:8765') as ws:
        await ws.send(json.dumps({'typ':'zprava','text':'Ahoj!'}))
        print(await ws.recv())
asyncio.run(test())
"
"""

import asyncio
import json
import time

try:
    import websockets
    WS_AVAILABLE = True
except ImportError:
    WS_AVAILABLE = False


class ConnectionManager:
    """Správa WebSocket spojení."""

    def __init__(self):
        self.aktivni: dict[str, any] = {}
        self.zpravy: list[dict] = []

    async def pripoj(self, ws, client_id: str):
        self.aktivni[client_id] = ws
        print(f"  Připojen: {client_id} (celkem: {len(self.aktivni)})")

    def odpoj(self, client_id: str):
        self.aktivni.pop(client_id, None)

    async def broadcast(self, zprava: dict, vyjma: str = None):
        for cid, ws in list(self.aktivni.items()):
            if cid != vyjma:
                try:
                    await ws.send(json.dumps(zprava, ensure_ascii=False))
                except Exception:
                    self.odpoj(cid)


manager = ConnectionManager()


async def chat_handler(websocket, path="/"):
    client_id = f"user_{id(websocket) % 10000}"
    await manager.pripoj(websocket, client_id)
    await manager.broadcast({"typ": "system", "text": f"{client_id} se připojil"}, vyjma=client_id)
    await websocket.send(json.dumps({"typ": "welcome", "id": client_id}))

    try:
        async for message in websocket:
            data = json.loads(message)
            typ = data.get("typ")

            if typ == "zprava":
                zprava = {
                    "typ": "zprava",
                    "od": client_id,
                    "text": data["text"],
                    "cas": time.strftime("%H:%M:%S"),
                }
                manager.zpravy.append(zprava)
                await manager.broadcast(zprava)
            elif typ == "ping":
                await websocket.send(json.dumps({"typ": "pong"}))

    except Exception:
        pass
    finally:
        manager.odpoj(client_id)
        await manager.broadcast({"typ": "system", "text": f"{client_id} se odpojil"})


async def metriky_handler(websocket, path="/metriky"):
    """Server push — metriky každou sekundu."""
    import random
    try:
        while True:
            metriky = {
                "cpu": round(random.uniform(10, 90), 1),
                "ram": round(random.uniform(40, 80), 1),
                "req_per_sec": random.randint(50, 500),
            }
            await websocket.send(json.dumps(metriky))
            await asyncio.sleep(1)
    except Exception:
        pass


async def demo_echo_server():
    """Jednoduchý echo server pro testování."""
    if not WS_AVAILABLE:
        print("  websockets není dostupný: uv add websockets")
        return

    async def echo(ws, path="/"):
        async for msg in ws:
            await ws.send(f"Echo: {msg}")

    print("  Spouštím echo server na ws://localhost:8766...")
    async with websockets.serve(echo, "localhost", 8766):
        # Test: klient pošle 3 zprávy
        await asyncio.sleep(0.1)
        async with websockets.connect("ws://localhost:8766") as client:
            for i in range(3):
                await client.send(f"Zpráva {i}")
                odpoved = await client.recv()
                print(f"  Server odpověděl: {odpoved}")


def ukazka_fastapi():
    print("\n=== FastAPI WebSocket kód ===")
    print("""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws/{client_id}")
async def ws_endpoint(ws: WebSocket, client_id: str):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_json()
            await ws.send_json({"echo": data, "od": client_id})
    except WebSocketDisconnect:
        print(f"{client_id} odpojen")

# Spuštění: fastapi dev app.py
# Test: wscat -c ws://localhost:8000/ws/anna
""")


async def main():
    print("=" * 50)
    print("  🔌 WebSockets Demo")
    print("=" * 50)

    print("\n=== Echo server test ===")
    await demo_echo_server()

    print("\n=== Simulace chat zpráv ===")
    # Simulace bez skutečného WebSocket
    zpravy_sim = [
        ("anna", "Ahoj všichni!"),
        ("bob", "Ahoj Anno!"),
        ("carol", "Jak se máte?"),
    ]
    for user, text in zpravy_sim:
        zprava = {"typ": "zprava", "od": user, "text": text, "cas": time.strftime("%H:%M:%S")}
        manager.zpravy.append(zprava)
        print(f"  [{zprava['cas']}] {user}: {text}")

    ukazka_fastapi()
    print("\n✅ Demo dokončeno!")
    print("Instalace: uv add 'fastapi[standard]' websockets")


if __name__ == "__main__":
    asyncio.run(main())
