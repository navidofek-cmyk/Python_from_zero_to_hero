# Lekce 76: `subprocess` — spouštění procesů

## 🚀 `subprocess.run` — moderní cesta

```python
import subprocess

vysledek = subprocess.run(
    ["ls", "-la"],
    capture_output=True,
    text=True,
    timeout=10,
    check=True,
)

print(vysledek.stdout)
print(vysledek.stderr)
print(vysledek.returncode)
```

### Klíčové parametry

- `capture_output=True` → zachytí stdout/stderr
- `text=True` → vrátí string místo bytes
- `timeout=N` → po N sekundách `TimeoutExpired`
- `check=True` → při nenulovém exit code `CalledProcessError`
- `cwd="/path"` → spuštění v jiném adresáři
- `env={...}` → env proměnné

---

## ⚠️ NIKDY nepoužívej `shell=True` s user inputem!

```python
# ❌ NEBEZPEČNÉ — shell injection
subprocess.run(f"rm {filename}", shell=True)
# Když filename = "; rm -rf /" → katastrofa

# ✅ BEZPEČNĚ — list argumentů
subprocess.run(["rm", filename])
```

`shell=True` vůbec nepotřebuješ ve většině případů.

---

## 📤 Pipe — propojení procesů

```python
import subprocess

p1 = subprocess.Popen(["ls", "-la"], stdout=subprocess.PIPE)
p2 = subprocess.Popen(["grep", "py"], stdin=p1.stdout, stdout=subprocess.PIPE)
p1.stdout.close()
vystup = p2.communicate()[0].decode()
```

Modernější: `subprocess.run` s `input=`:

```python
ls = subprocess.run(["ls", "-la"], capture_output=True, text=True)
grep = subprocess.run(["grep", "py"], input=ls.stdout, capture_output=True, text=True)
```

---

## ⏰ Timeout

```python
try:
    subprocess.run(["sleep", "100"], timeout=2)
except subprocess.TimeoutExpired:
    print("Vypršelo!")
```

---

## 🔄 Async verze

```python
import asyncio

async def main():
    proc = await asyncio.create_subprocess_exec(
        "ls", "-la",
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    print(stdout.decode())
```

---

## 🎯 Best practice

✅ `subprocess.run` (ne `Popen`, pokud nepotřebuješ stream)
✅ `text=True` pro text výstup
✅ `check=True` pro vyhození chyby při fail
✅ List argumentů, **NE** `shell=True`
✅ `timeout` pro nedůvěryhodné procesy

---

## ✏️ Cvičení

1. **Ls:** Spusť `ls -la` a získej výstup do proměnné.
2. **Git:** Spusť `git --version`, vypiš verzi.
3. **Timeout:** Spusť `sleep 5` s timeoutem 1s, ošetři výjimku.
4. **Pipe:** `ls | grep .py` — implementuj v Pythonu.
5. **Bezpečně:** Funkce co dostane jméno souboru a smaže ho — bez shell injection.
