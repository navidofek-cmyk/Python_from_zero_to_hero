# Lekce 82: `socket`, `urllib`, `http.client`

## 🌐 Síť na nízké úrovni

Většinou používáme `httpx`/`requests` pro HTTP. Ale občas potřebuješ něco hluboko.

---

## 🔌 `socket` — TCP/UDP

### TCP klient

```python
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(("example.com", 80))
    s.sendall(b"GET / HTTP/1.0\r\nHost: example.com\r\n\r\n")
    data = s.recv(4096)
print(data.decode())
```

### TCP server

```python
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind(("", 8000))
    server.listen()
    while True:
        client, addr = server.accept()
        with client:
            data = client.recv(1024)
            client.sendall(data.upper())
```

Pro reálné servery použij `asyncio` (lekce 60) nebo framework (Flask/FastAPI).

---

## 🌍 `urllib` — stdlib HTTP

```python
from urllib.request import urlopen
from urllib.parse import urlencode, urlparse, urljoin

with urlopen("https://example.com") as r:
    html = r.read().decode()

# Parse URL
u = urlparse("https://example.com/path?a=1&b=2")
print(u.scheme, u.netloc, u.path, u.query)

# Encode params
params = urlencode({"a": "ahoj svete", "b": 1})
# → 'a=ahoj+svete&b=1'

# Join
urljoin("https://a.com/foo/", "bar")    # 'https://a.com/foo/bar'
```

---

## 📦 `urllib` POST

```python
from urllib.request import Request, urlopen

req = Request(
    "https://httpbin.org/post",
    data=b'{"x": 1}',
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urlopen(req) as r:
    print(r.read().decode())
```

(Pro 99 % případů: **používej `httpx` nebo `requests`**.)

---

## 🌐 `http.client` — ještě nižší úroveň

```python
import http.client

c = http.client.HTTPSConnection("example.com")
c.request("GET", "/")
r = c.getresponse()
print(r.status, r.reason)
print(r.read().decode())
```

---

## 🎯 Doporučení

| Co | Kdy |
|---|---|
| `requests` / `httpx` | 99 % HTTP případů |
| `urllib` | Když nechceš dependence |
| `socket` | TCP/UDP nebo experimenty |
| `http.client` | Skoro nikdy přímo |

---

## ✏️ Cvičení

1. **Urllib:** Stáhni titulek z nějaké webové stránky (regex `<title>...</title>`).
2. **URL parse:** Z URL `https://x.com/a/b?c=1` vytáhni doménu, cestu a query.
3. **Socket:** Implementuj jednoduchý echo server na portu 8000.
4. **HEAD request:** Pomocí `urllib` udělej HEAD request a vypiš headers.
