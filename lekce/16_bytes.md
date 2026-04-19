# Lekce 16: `bytes`, `bytearray`, `memoryview`

## 0️⃣1️⃣ Co jsou bytes?

Počítač uvnitř pracuje jen s **nulami a jedničkami**. Osm jedniček/nul = jeden **byte**. Text musí na byty někdo přeložit.

```python
text = "Ahoj"
b = text.encode("utf-8")    # b'Ahoj'   (typ bytes)
print(b)                     # b'Ahoj'
print(b[0])                  # 65  (byte = číslo 0–255!)

zpet = b.decode("utf-8")     # "Ahoj"
```

`bytes` vypadají jako řetězec s `b` před uvozovkou. **Jsou neměnné.**

---

## 🛠️ `bytearray` — měnitelná verze

```python
ba = bytearray(b"Ahoj")
ba[0] = 66                  # 'B'
print(ba)                    # bytearray(b'Bhoj')
ba.append(33)                # '!'
print(ba.decode())           # "Bhoj!"
```

---

## 🪟 `memoryview` — okno do bytů bez kopírování

Když máš velký kus dat a chceš s ním pracovat **bez kopírování**, použij `memoryview`:

```python
data = bytearray(b"obrovska_data" * 10000)
mv = memoryview(data)

prvnich_100 = mv[:100]       # NEKOPÍRUJE — jen okénko
```

Pro běžnou práci to nepotřebuješ. Důležité hlavně u velkých binárních dat (obrázky, video, síťové buffery).

---

## 🌍 Kódování — proč existuje?

| Kódování | K čemu |
|---|---|
| **ASCII** | Jen základní anglická abeceda (0–127). Žádná diakritika. |
| **UTF-8** | ✅ Standard. Umí všechno (čeština, čínština, emoji 🐍). |
| **latin-2 / cp1250** | Stará, československá. Neumí emoji. Vyhni se. |

```python
"Příšerně".encode("utf-8")     # b'P\xc5\x99\xc3\xad...'
"Příšerně".encode("ascii")     # ❌ UnicodeEncodeError
```

---

## 📂 Čtení binárních souborů

```python
with open("obrazek.png", "rb") as f:    # "rb" = read binary
    data = f.read()                      # bytes
print(type(data))                        # <class 'bytes'>
print(len(data), "bytů")
```

Zápis:
```python
with open("kopie.png", "wb") as f:
    f.write(data)
```

---

## 🔢 Hex a base64

```python
b = b"Ahoj"
b.hex()                          # "41686f6a"   (heximální)
bytes.fromhex("41686f6a")        # b'Ahoj'

import base64
base64.b64encode(b)              # b'QWhvag=='
base64.b64decode(b"QWhvag==")    # b'Ahoj'
```

Base64 se používá, když chceš poslat binární data v textu (např. v emailu nebo v JSON).

---

## ✏️ Cvičení

1. **Čeština:** Zakóduj slovo `"Příšerně"` do UTF-8 a vypiš počet bytů. (Bude víc než písmen — diakritika zabírá víc!)
2. **Bytearray:** Vyrob `bytearray(b"hello")`, změň první písmeno na velké (kód `H` je 72).
3. **Hex:** Převeď text své jméno do hex pomocí `.encode().hex()`.
4. **Base64:** Zakóduj malý obrázek z disku do base64 a zpět.
