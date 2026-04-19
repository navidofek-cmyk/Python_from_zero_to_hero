# Lekce 22: `*args` a `**kwargs`

## 🌟 `*args` — neomezený počet argumentů

Co když nevíš, kolik argumentů ti dají?

```python
def soucet(*cisla):
    return sum(cisla)

soucet(1, 2, 3)            # 6
soucet(1, 2, 3, 4, 5, 6)   # 21
soucet()                    # 0
```

`*cisla` = „seber všechny pozice do tuple jménem `cisla`“. Jméno `args` je jen konvence — můžeš si pojmenovat jak chceš.

```python
def vypis_vse(*items):
    for x in items:
        print(x)
```

---

## 🌟🌟 `**kwargs` — neomezené pojmenované

```python
def info(**data):
    for klic, hodnota in data.items():
        print(f"{klic}: {hodnota}")

info(jmeno="Eliška", vek=10, mesto="Praha")
# jmeno: Eliška
# vek: 10
# mesto: Praha
```

`**data` = „seber všechny pojmenované do dict jménem `data`“.

---

## 🎰 Kombinace

```python
def vsechno(prvni, *args, default="nic", **kwargs):
    print(f"prvni:   {prvni}")
    print(f"args:    {args}")
    print(f"default: {default}")
    print(f"kwargs:  {kwargs}")

vsechno("A", 1, 2, 3, default="X", barva="modrá", vek=10)
# prvni:   A
# args:    (1, 2, 3)
# default: X
# kwargs:  {'barva': 'modrá', 'vek': 10}
```

**Pořadí** v definici:
1. Pozici (`a, b`)
2. `*args`
3. Pojmenované s defaultem (`x=10`)
4. `**kwargs`

---

## 📦 Rozbalení při volání

`*` a `**` fungují i **opačně** — rozbalíš seznam/slovník do argumentů:

```python
def secti(a, b, c):
    return a + b + c

cisla = [1, 2, 3]
secti(*cisla)              # 6   (jako secti(1, 2, 3))

data = {"a": 1, "b": 2, "c": 3}
secti(**data)              # 6   (jako secti(a=1, b=2, c=3))
```

Hodí se třeba k „přeposílání“ argumentů:

```python
def wrapper(*args, **kwargs):
    print("Volám:", args, kwargs)
    return puvodni_funkce(*args, **kwargs)
```

---

## 🎯 Časté použití

### Přijímání jakékoliv konfigurace

```python
def setup(host, port=80, **options):
    print(f"Host: {host}:{port}")
    for k, v in options.items():
        print(f"  {k} = {v}")

setup("localhost", debug=True, log_level="INFO")
```

### Spojení slovníků (alternativa k `|`)

```python
a = {"x": 1}
b = {"y": 2}
spojeno = {**a, **b}        # {"x": 1, "y": 2}
```

### Spojení seznamů

```python
spojeny = [*a, *b, 99]
```

---

## ✏️ Cvičení

1. **Maximum:** Napiš funkci `maximum(*cisla)` co vrátí největší (bez `max`!).
2. **Zpráva:** Funkce `zprava(do, *prijemci, **detaily)`. Vypíše komu posíláš a všechny detaily.
3. **Wrapper:** Vyrob funkci `loguj_volani(funkce, *args, **kwargs)`, která vypíše argumenty, zavolá funkci a vrátí výsledek.
4. **Rozbalení:** Máš `params = {"jmeno": "Bob", "vek": 11}`. Vyrob funkci `kdo(jmeno, vek)` a zavolej ji rozbalením `**params`.
5. **Spojení slovníků:** Spoj 3 slovníky do jednoho pomocí `**`.
