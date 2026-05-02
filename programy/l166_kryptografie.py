"""Lekce 166 — Kryptografie: AES, RSA, digitální podpisy.

Spuštění:
    uv run --with cryptography l166_kryptografie.py
"""

import os, base64, time

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Nainstaluj: uv add cryptography")


def demo_aes():
    print("\n=== AES-256-GCM (symetrická) ===")
    klic = AESGCM.generate_key(256)
    aesgcm = AESGCM(klic)
    zprava = b"Tajná zpráva pro Annu — authenticated encryption"
    nonce = os.urandom(12)
    sifrovano = aesgcm.encrypt(nonce, zprava, b"AAD")
    desifrovano = aesgcm.decrypt(nonce, sifrovano, b"AAD")
    print(f"  Zpráva: {zprava.decode()}")
    print(f"  Šifrováno: {base64.b64encode(sifrovano[:20]).decode()}... ({len(sifrovano)} B)")
    print(f"  Dešifrováno: {desifrovano.decode()}")
    print(f"  ✅ Identické: {zprava == desifrovano}")

    # Tamper detection
    sifrovano_zmeneno = sifrovano[:-1] + bytes([sifrovano[-1] ^ 0xFF])
    try:
        aesgcm.decrypt(nonce, sifrovano_zmeneno, b"AAD")
    except Exception:
        print("  ✅ Manipulace detekována (GCM tag ověření)")


def demo_rsa():
    print("\n=== RSA-2048 (asymetrická) ===")
    soukromy = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    verejny = soukromy.public_key()

    zprava = b"RSA šifrovaná zpráva"
    sifrovano = verejny.encrypt(zprava, padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(), label=None
    ))
    desifrovano = soukromy.decrypt(sifrovano, padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(), label=None
    ))
    print(f"  Šifrováno: {len(sifrovano)} bytů (vždy 256 B pro RSA-2048)")
    print(f"  Dešifrováno: {desifrovano.decode()}")


def demo_podpis():
    print("\n=== ECDSA digitální podpis ===")
    soukromy = ec.generate_private_key(ec.SECP256R1())
    verejny = soukromy.public_key()

    zprava = b"Tuto zprávu podepisuji svým klíčem"
    podpis = soukromy.sign(zprava, ec.ECDSA(hashes.SHA256()))
    print(f"  Podpis: {base64.b64encode(podpis[:20]).decode()}... ({len(podpis)} B)")

    try:
        verejny.verify(podpis, zprava, ec.ECDSA(hashes.SHA256()))
        print("  ✅ Podpis platný")
    except Exception:
        print("  ❌ Neplatný podpis")

    try:
        verejny.verify(podpis, b"Pozměněná zpráva", ec.ECDSA(hashes.SHA256()))
    except Exception:
        print("  ✅ Manipulace s textem detekována")


def demo_kdf():
    print("\n=== PBKDF2 derivace klíče ===")
    heslo = "moje-tajne-heslo"
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480_000)
    klic = kdf.derive(heslo.encode())
    print(f"  Heslo → klíč: {base64.b64encode(klic).decode()}")

    start = time.perf_counter()
    PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480_000).derive(heslo.encode())
    print(f"  Čas derivace: {(time.perf_counter()-start)*1000:.0f}ms (záměrně pomalé)")


def demo_fernet():
    print("\n=== Fernet (vysokoúrovňové šifrování) ===")
    klic = Fernet.generate_key()
    f = Fernet(klic)
    zprava = b"Fernet = AES-128-CBC + HMAC-SHA256 + base64"
    token = f.encrypt(zprava)
    print(f"  Token: {token[:40].decode()}...")
    print(f"  Dešifrováno: {f.decrypt(token).decode()}")


def main():
    print("=" * 50)
    print("  🔒 Kryptografie Demo")
    print("=" * 50)

    if not CRYPTO_AVAILABLE:
        print("Nainstaluj: uv add cryptography")
        return

    demo_aes()
    demo_rsa()
    demo_podpis()
    demo_kdf()
    demo_fernet()

    print("\n✅ Demo dokončeno!")
    print("\nSouhrn algoritmů:")
    print("  AES-GCM     → symetrické šifrování (rychlé, malé klíče)")
    print("  RSA-OAEP    → asymetrické šifrování (pomalé, velká data)")
    print("  ECDSA       → digitální podpisy (rychlejší než RSA)")
    print("  PBKDF2/scrypt → derivace klíče z hesla (úmyslně pomalé)")
    print("  Fernet      → high-level API (doporučeno pro začátečníky)")


if __name__ == "__main__":
    main()
