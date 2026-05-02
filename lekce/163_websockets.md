# Lekce 163: WebSockets — real-time komunikace

WebSocket = persistentní bi-directional spojení mezi klientem a serverem. Ideální pro chat, live notifikace, real-time dashboardy, multiplayer hry.

---

## 🚀 Instalace

```bash
uv add "fastapi[standard]" websockets
```

---

## 🔌 Základy WebSocket

```python
import asyncio
import websockets
import json


# Jednoduchý echo server
async def echo_handler(websocket):
    print(f"Nové spojení: {websocket.remote_address}")
    try:
        async for zprava in websocket:
            print(f"  Přijato: {zprava}")
            await websocket.send(f"Echo: {zprava}")
    except websockets.exceptions.ConnectionClosedOK:
        print("Klient se odpojil")


async def spust_echo_server():
    async with websockets.serve(echo_handler, "localhost", 8765):
        print("WebSocket server na ws://localhost:8765")
        await asyncio.Future()   # běž navždy


# Klient
async def ws_klient():
    async with websockets.connect("ws://localhost:8765") as ws:
        await ws.send("Ahoj!")
        odpoved = await ws.recv()
        print(f"Server řekl: {odpoved}")
```

---

## 🏗️ FastAPI WebSocket

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json
import asyncio
from datetime import datetime

app = FastAPI()


class SpravceSpojeni:
    """Správa aktivních WebSocket spojení."""

    def __init__(self):
        self.aktivni: dict[str, WebSocket] = {}

    async def pripoj(self, ws: WebSocket, client_id: str):
        await ws.accept()
        self.aktivni[client_id] = ws
        print(f"Připojen: {client_id} (celkem: {len(self.aktivni)})")

    def odpoj(self, client_id: str):
        self.aktivni.pop(client_id, None)
        print(f"Odpojen: {client_id}")

    async def posli(self, client_id: str, zprava: dict):
        if ws := self.aktivni.get(client_id):
            await ws.send_json(zprava)

    async def broadcast(self, zprava: dict, vyjma: str = None):
        """Pošli všem připojeným klientům."""
        odpojen = []
        for cid, ws in self.aktivni.items():
            if cid == vyjma:
                continue
            try:
                await ws.send_json(zprava)
            except WebSocketDisconnect:
                odpojen.append(cid)
        for cid in odpojen:
            self.odpoj(cid)


spravce = SpravceSpojeni()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(ws: WebSocket, client_id: str):
    await spravce.pripoj(ws, client_id)
    try:
        while True:
            data = await ws.receive_json()
            typ = data.get("typ")

            if typ == "zprava":
                # Broadcast všem ostatním
                await spravce.broadcast({
                    "typ": "zprava",
                    "od": client_id,
                    "text": data["text"],
                    "cas": datetime.now().isoformat(),
                }, vyjma=client_id)

            elif typ == "ping":
                await ws.send_json({"typ": "pong"})

    except WebSocketDisconnect:
        spravce.odpoj(client_id)
        await spravce.broadcast({
            "typ": "system",
            "text": f"{client_id} se odpojil",
        })
```

---

## 📡 Live dashboard — server push

```python
import random

@app.websocket("/ws/metriky")
async def metriky_stream(ws: WebSocket):
    """Server pravidelně posílá metriky bez požadavku od klienta."""
    await ws.accept()
    try:
        while True:
            metriky = {
                "cpu": round(random.uniform(10, 90), 1),
                "ram": round(random.uniform(40, 80), 1),
                "requests_per_sec": random.randint(50, 500),
                "cas": datetime.now().isoformat(),
            }
            await ws.send_json(metriky)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Dashboard klient odpojen")
```

---

## 🎮 Multiplayer game room

```python
from typing import Optional

@dataclass
class Hrac:
    id: str
    jmeno: str
    ws: WebSocket
    skore: int = 0


class HerniMistnost:
    def __init__(self, id: str, max_hracu: int = 4):
        self.id = id
        self.hraci: dict[str, Hrac] = {}
        self.max_hracu = max_hracu
        self.stav = "cekani"   # cekani, hra, konec

    async def pripoj_hrace(self, hrac: Hrac) -> bool:
        if len(self.hraci) >= self.max_hracu:
            return False
        self.hraci[hrac.id] = hrac
        await self.broadcast({"typ": "hrac_pripojen", "jmeno": hrac.jmeno})
        if len(self.hraci) == self.max_hracu:
            await self.zacni_hru()
        return True

    async def zacni_hru(self):
        self.stav = "hra"
        await self.broadcast({"typ": "start_hry", "hraci": list(self.hraci.keys())})

    async def broadcast(self, data: dict):
        odpojen = []
        for hid, hrac in self.hraci.items():
            try: await hrac.ws.send_json(data)
            except: odpojen.append(hid)
        for hid in odpojen: self.hraci.pop(hid)
```

---

## 🔐 Autentizace WebSocket

```python
from fastapi import Query, HTTPException

@app.websocket("/ws/auth")
async def autorizovany_ws(
    ws: WebSocket,
    token: str = Query(...),
):
    """WebSocket s JWT autentizací přes query parametr."""
    # Ověř token
    try:
        payload = overit_jwt(token)
        user_id = payload["sub"]
    except Exception:
        await ws.close(code=4001, reason="Neplatný token")
        return

    await ws.accept()
    try:
        async for data in ws.iter_json():
            await ws.send_json({"echo": data, "user": user_id})
    except WebSocketDisconnect:
        pass


def overit_jwt(token: str) -> dict:
    # Viz lekce 165 (OAuth2/JWT)
    return {"sub": "user_123"}
```

---

## 🎯 WebSocket vs SSE vs Polling

| | WebSocket | SSE | Long Polling |
|---|-----------|-----|-------------|
| Směr | obousměrný | jen server→klient | jen server→klient |
| Protokol | WS (TCP) | HTTP | HTTP |
| Latency | nejnižší | nízká | vysoká |
| Overhead | nízký | střední | vysoký |
| Load balancer | náročnější | přímočaré | přímočaré |
| Ideální | chat, hry, live data | notifikace, feed | jednoduchý polling |

---

## ✏️ Cvičení

1. Postav real-time chat aplikaci — místnosti, přezdívky, history posledních 50 zpráv.
2. Implementuj **live collaborative editor** — více uživatelů edituje text najednou (CRDT/OT).
3. Napiš WebSocket load tester — 1000 paralelních spojení, měř latency.
4. Postav real-time dashboard pro monitorování Celery workerů.
5. Implementuj **reconnection logic** na straně klienta s exponential backoff.
