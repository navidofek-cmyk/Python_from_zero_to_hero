# Lekce 166: Kryptografie

Kryptografie chrání data před neoprávněným přístupem. Python's `cryptography` knihovna je de-facto standard.

---

## 🚀 Instalace

```bash
uv add cryptography
```

---

## 🔑 Symetrická kryptografie (AES)

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
import os, base64


def sifrovani_aes_gcm(klic: bytes, zprava: bytes, aad: bytes = b"") -> tuple[bytes, bytes]:
    """AES-256-GCM — autentizované šifrování."""
    aesgcm = AESGCM(klic)
    nonce = os.urandom(12)   # 96 bitů, unikátní pro každou zprávu!
    sifrovano = aesgcm.encrypt(nonce, zprava, aad)
    return nonce, sifrovano


def desifrovani_aes_gcm(klic: bytes, nonce: bytes, sifrovano: bytes, aad: bytes = b"") -> bytes:
    aesgcm = AESGCM(klic)
    return aesgcm.decrypt(nonce, sifrovano, aad)


# Použití
klic = AESGCM.generate_key(bit_length=256)   # 32 bytů
zprava = b"Tajná zpráva pro Annu"

nonce, sifrovano = sifrovani_aes_gcm(klic, zprava)
print(f"Šifrováno: {base64.b64encode(sifrovano).decode()}")

desifrovano = desifrovani_aes_gcm(klic, nonce, sifrovano)
print(f"Dešifrováno: {desifrovano.decode()}")
```

---

## 🔒 Asymetrická kryptografie (RSA)

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes


def generuj_rsa_klic(bits: int = 2048) -> tuple:
    """Generuje RSA klíčový pár."""
    soukromy = rsa.generate_private_key(
        public_exponent=65537,
        key_size=bits,
    )
    verejny = soukromy.public_key()
    return soukromy, verejny


def rsa_sifrovani(verejny_klic, zprava: bytes) -> bytes:
    return verejny_klic.encrypt(
        zprava,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def rsa_desifrovani(soukromy_klic, sifrovano: bytes) -> bytes:
    return soukromy_klic.decrypt(
        sifrovano,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


soukromy, verejny = generuj_rsa_klic()
zprava = b"RSA šifrovaná zpráva"
sifrovano = rsa_sifrovani(verejny, zprava)
desifrovano = rsa_desifrovani(soukromy, sifrovano)
print(f"RSA: {desifrovano.decode()}")
```

---

## ✍️ Digitální podpisy

```python
from cryptography.hazmat.primitives.asymmetric import ec


def ec_podpis() -> None:
    """ECDSA — rychlejší než RSA pro podpisy."""
    soukromy = ec.generate_private_key(ec.SECP256R1())
    verejny = soukromy.public_key()

    zprava = b"Tuto zprávu podepisuji"
    podpis = soukromy.sign(zprava, ec.ECDSA(hashes.SHA256()))
    print(f"Podpis: {base64.b64encode(podpis).decode()[:40]}...")

    # Ověření
    try:
        verejny.verify(podpis, zprava, ec.ECDSA(hashes.SHA256()))
        print("✅ Podpis platný")
    except Exception:
        print("❌ Podpis neplatný")

    # Pokud změníme zprávu
    try:
        verejny.verify(podpis, b"Pozměněná zpráva", ec.ECDSA(hashes.SHA256()))
    except Exception:
        print("✅ Detekována manipulace!")


ec_podpis()
```

---

## 🔑 Derivace klíčů (KDF)

```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


def derivuj_klic_z_hesla(heslo: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """PBKDF2 — derivuje šifrovací klíč z hesla."""
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480_000,   # NIST doporučení 2024
    )
    klic = kdf.derive(heslo.encode())
    return klic, salt


def derivuj_klic_scrypt(heslo: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """scrypt — memory-hard, odolnější vůči GPU útokům."""
    if salt is None:
        salt = os.urandom(16)
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    return kdf.derive(heslo.encode()), salt


klic, salt = derivuj_klic_z_hesla("moje-heslo")
print(f"Odvozený klíč: {base64.b64encode(klic).decode()}")
```

---

## 🌐 TLS certifikáty

```python
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime


def vytvor_self_signed_cert() -> tuple:
    """Vytvoří self-signed TLS certifikát."""
    soukromy = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "CZ"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Moje Firma"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(soukromy.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]),
            critical=False,
        )
        .sign(soukromy, hashes.SHA256())
    )

    return soukromy, cert


soukromy_klic, cert = vytvor_self_signed_cert()
print(f"Certifikát vytvořen: CN={cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value}")
print(f"Platný do: {cert.not_valid_after_utc}")
```

---

## 🔄 Fernet — jednoduché symetrické šifrování

```python
from cryptography.fernet import Fernet, MultiFernet


# Fernet = AES-128-CBC + HMAC-SHA256, base64 encoded
klic = Fernet.generate_key()
f = Fernet(klic)

zprava = b"Tajná databázová URL"
token = f.encrypt(zprava)
print(f"Fernet token: {token[:40]}...")

desifrovano = f.decrypt(token)
print(f"Dešifrováno: {desifrovano.decode()}")

# Rotace klíčů
stary_klic = Fernet.generate_key()
novy_klic = Fernet.generate_key()
multi_f = MultiFernet([Fernet(novy_klic), Fernet(stary_klic)])
# Šifruje novým, dešifruje oběma
```

---

## ✏️ Cvičení

1. Implementuj šifrované úložiště hesel — AES-GCM + PBKDF2 derivace z master hesla.
2. Napiš systém pro **bezpečnou výměnu zpráv** — RSA pro výměnu AES klíče (hybrid šifrování).
3. Implementuj **digitální podpis souborů** — podpiš soubor, ověř integritu.
4. Vytvoř jednoduchou **PKI** — CA certifikát, vydej klientský certifikát, ověř řetězec.
5. Benchmark: AES-128 vs AES-256 vs ChaCha20-Poly1305 — rychlost a bezpečnost.
