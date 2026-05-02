# Lekce 161: gRPC — high-performance RPC

gRPC (Google Remote Procedure Call) používá **Protocol Buffers** pro serializaci a **HTTP/2** pro transport. 5–10× rychlejší než JSON/REST, bi-directional streaming.

---

## 🚀 Instalace

```bash
uv add grpcio grpcio-tools protobuf
```

---

## 📋 Protobuf definice

`proto/kurz.proto`:

```protobuf
syntax = "proto3";

package kurz;

// Zprávy
message LekceRequest {
  int32 cislo = 1;
}

message LekceResponse {
  int32 cislo = 1;
  string nazev = 2;
  string obsah = 3;
  repeated string tagy = 4;
}

message VyhledatRequest {
  string dotaz = 1;
  int32 limit = 2;
}

message StreamRequest {
  int32 od = 1;
  int32 do = 2;
}

// Service
service KurzService {
  // Unary RPC
  rpc GetLekce(LekceRequest) returns (LekceResponse);

  // Server streaming — server posílá stream
  rpc StreamLekce(StreamRequest) returns (stream LekceResponse);

  // Client streaming — klient posílá stream
  rpc UploadLekce(stream LekceResponse) returns (LekceRequest);

  // Bidirectional streaming
  rpc Chat(stream VyhledatRequest) returns (stream LekceResponse);
}
```

Generování Python kódu:

```bash
python -m grpc_tools.protoc \
  -I proto \
  --python_out=. \
  --grpc_python_out=. \
  proto/kurz.proto
```

---

## 🖥️ Server

```python
import grpc
import asyncio
from concurrent import futures

# Importy generovaného kódu:
# import kurz_pb2
# import kurz_pb2_grpc

# Simulace databáze
LEKCE_DB = {
    i: {"cislo": i, "nazev": f"Lekce {i}", "obsah": f"Obsah lekce {i}", "tagy": ["python"]}
    for i in range(1, 11)
}


class KurzServicer:  # (kurz_pb2_grpc.KurzServiceServicer)
    """Implementace gRPC service."""

    def GetLekce(self, request, context):
        """Unary RPC."""
        lekce = LEKCE_DB.get(request.cislo)
        if not lekce:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Lekce {request.cislo} neexistuje")
            return None  # kurz_pb2.LekceResponse()
        print(f"  GetLekce({request.cislo})")
        return None  # kurz_pb2.LekceResponse(**lekce)

    def StreamLekce(self, request, context):
        """Server streaming RPC."""
        for cislo in range(request.od, request.do + 1):
            if context.is_active():
                lekce = LEKCE_DB.get(cislo)
                if lekce:
                    print(f"  Stream: posílám lekci {cislo}")
                    yield None  # kurz_pb2.LekceResponse(**lekce)
            else:
                break


def spust_server(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # kurz_pb2_grpc.add_KurzServiceServicer_to_server(KurzServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"gRPC server běží na portu {port}")
    server.wait_for_termination()
```

---

## 📱 Klient

```python
def vytvor_kanal(adresa: str = "localhost:50051") -> grpc.Channel:
    return grpc.insecure_channel(adresa)


def grpc_klient_demo():
    channel = vytvor_kanal()
    # stub = kurz_pb2_grpc.KurzServiceStub(channel)

    # Unary call
    # response = stub.GetLekce(kurz_pb2.LekceRequest(cislo=5))
    # print(f"Lekce: {response.nazev}")

    # Server streaming
    # for lekce in stub.StreamLekce(kurz_pb2.StreamRequest(od=1, do=5)):
    #     print(f"  Stream: {lekce.nazev}")

    # Metadata (jako HTTP headers)
    # metadata = [("authorization", "Bearer token123")]
    # response = stub.GetLekce(request, metadata=metadata)

    # Timeout
    # try:
    #     response = stub.GetLekce(request, timeout=5.0)
    # except grpc.RpcError as e:
    #     print(f"Status: {e.code()}, Detail: {e.details()}")

    channel.close()
    print("gRPC klient demo — viz komentáře pro spuštění se serverem")
```

---

## ⚡ Async gRPC

```python
import grpc.aio


async def async_grpc_demo():
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        # stub = kurz_pb2_grpc.KurzServiceStub(channel)

        # Async unary
        # response = await stub.GetLekce(kurz_pb2.LekceRequest(cislo=1))

        # Async server streaming
        # async for lekce in stub.StreamLekce(kurz_pb2.StreamRequest(od=1, do=10)):
        #     print(f"  Async stream: {lekce.nazev}")
        pass

    print("Async gRPC demo připraven")
```

---

## 🔒 TLS + Interceptors

```python
# TLS
def grpc_tls_kanal(cert_cesta: str) -> grpc.Channel:
    with open(cert_cesta, "rb") as f:
        cert = f.read()
    credentials = grpc.ssl_channel_credentials(root_certificates=cert)
    return grpc.secure_channel("api.example.com:443", credentials)


# Interceptor — jako middleware
class AuthInterceptor(grpc.UnaryUnaryClientInterceptor):
    def __init__(self, token: str): self.token = token

    def intercept_unary_unary(self, continuation, client_call_details, request):
        # Přidej auth token ke každému requestu
        metadata = list(client_call_details.metadata or [])
        metadata.append(("authorization", f"Bearer {self.token}"))
        new_details = client_call_details._replace(metadata=metadata)
        return continuation(new_details, request)
```

---

## 📊 gRPC vs REST

| | gRPC | REST |
|---|------|------|
| Protokol | HTTP/2 | HTTP/1.1 |
| Serializace | Protobuf (binary) | JSON (text) |
| Rychlost | 5–10× rychlejší | baseline |
| Streaming | ✅ bi-directional | SSE/WebSocket |
| Schéma | ✅ povinné (.proto) | OpenAPI (volitelné) |
| Browser support | ❌ (grpc-web proxy) | ✅ |
| Čitelnost | ❌ binární | ✅ human-readable |
| Ideální pro | microservices interní | public API |

---

## ✏️ Cvičení

1. Vytvoř `.proto` pro Todo service (CRUD) a implementuj server + klient.
2. Implementuj **bidirectional streaming** chat — klient i server posílají proudy zpráv.
3. Napiš **server-side interceptor** pro logování všech RPC volání.
4. Benchmarkuj gRPC vs REST (FastAPI) na 10 000 requestech — latency a throughput.
5. Napiš **health check** service (`grpc.health.v1`) pro Kubernetes readiness probe.
