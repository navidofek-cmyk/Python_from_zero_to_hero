# Program — Lekce 161: Lekce 161: gRPC — high-performance RPC

Patří k lekci [Lekce 161: gRPC — high-performance RPC](../161_grpc.md).

## Jak spustit

```bash
python3 programy/l161_grpc.py
```

## Zdrojový kód

### `l161_grpc.py`

```py
"""Lekce 161 — gRPC: high-performance RPC.

Spuštění:
    uv run l161_grpc.py

Pro plné demo s .proto:
    uv run --with grpcio,grpcio-tools l161_grpc.py
"""

import asyncio
import json
import time


def demo_grpc_architektura():
    print("=" * 50)
    print("  📡 gRPC Architektura Demo")
    print("=" * 50)

    print("""
gRPC vs REST:
  REST:  JSON/HTTP1.1   → ~5ms latency, text protokol
  gRPC:  Protobuf/HTTP2 → ~0.5ms latency, binární protokol

4 typy gRPC volání:
  1. Unary:              klient → server, server → klient
  2. Server streaming:   klient → server, server → stream
  3. Client streaming:   klient → stream, server → klient
  4. Bidirectional:      klient → stream, server → stream

Proto definice:
  service KurzService {
    rpc GetLekce(LekceRequest) returns (LekceResponse);
    rpc StreamLekce(StreamRequest) returns (stream LekceResponse);
    rpc Chat(stream ChatRequest) returns (stream ChatResponse);
  }
""")


async def demo_grpc_simulace():
    """Simulace gRPC komunikace bez skutečného serveru."""
    print("=== gRPC simulace (bez skutečného serveru) ===")

    # Simulace Unary call
    async def unary_call(request: dict) -> dict:
        await asyncio.sleep(0.001)   # simulace síťové latency
        return {"cislo": request["cislo"], "nazev": f"Lekce {request['cislo']}", "obsah": "..."}

    # Simulace Server streaming
    async def server_stream(od: int, do: int):
        for i in range(od, do+1):
            await asyncio.sleep(0.001)
            yield {"cislo": i, "nazev": f"Lekce {i}"}

    # Unary
    print("\nUnary call:")
    start = time.perf_counter()
    resp = await unary_call({"cislo": 42})
    t = (time.perf_counter()-start)*1000
    print(f"  GetLekce(42) → {resp['nazev']} ({t:.2f}ms)")

    # Server streaming
    print("\nServer streaming:")
    async for lekce in server_stream(1, 5):
        print(f"  → {lekce['cislo']}: {lekce['nazev']}")

    # Benchmark: 100 parallel unary calls
    print("\nBenchmark: 100 paralelních unary calls:")
    start = time.perf_counter()
    results = await asyncio.gather(*[unary_call({"cislo": i}) for i in range(100)])
    t = (time.perf_counter()-start)*1000
    print(f"  100 calls za {t:.1f}ms ({1000/t*100:.0f} calls/s)")


def demo_proto_kod():
    print("\n=== Vygenerovaný kód z .proto ===")
    print("""
# Generování: python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/kurz.proto

# Klient:
import grpc
import kurz_pb2 as pb
import kurz_pb2_grpc as pb_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = pb_grpc.KurzServiceStub(channel)

# Unary
response = stub.GetLekce(pb.LekceRequest(cislo=42))
print(response.nazev)

# Server streaming
for lekce in stub.StreamLekce(pb.StreamRequest(od=1, do=10)):
    print(lekce.nazev)

# Async
async with grpc.aio.insecure_channel('localhost:50051') as ch:
    stub = pb_grpc.KurzServiceStub(ch)
    resp = await stub.GetLekce(pb.LekceRequest(cislo=1))
""")


def main():
    demo_grpc_architektura()
    asyncio.run(demo_grpc_simulace())
    demo_proto_kod()
    print("\n✅ Demo dokončeno!")
    print("Instalace: uv add grpcio grpcio-tools protobuf")


if __name__ == "__main__":
    main()

```
