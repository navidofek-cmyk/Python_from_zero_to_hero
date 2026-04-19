# Lekce 62: Vlastní výjimky

## 🎨 Proč vlastní?

Aby tvůj kód mohl rozlišit **své vlastní chyby** od chyb knihoven.

```python
class NedostatekProstredku(Exception):
    pass

class Ucet:
    def vyber(self, castka):
        if castka > self.zustatek:
            raise NedostatekProstredku(f"Chybí {castka - self.zustatek} Kč")


try:
    ucet.vyber(1000)
except NedostatekProstredku as e:
    print(f"❌ {e}")
```

---

## 🌳 Vlastní hierarchie

Většinou si vyrobíš **bázovou** výjimku pro svou knihovnu a od ní odvodíš ostatní:

```python
class MujError(Exception):
    """Bázová výjimka mé knihovny."""

class ChybaVstupu(MujError):
    """Špatný vstup od uživatele."""

class ChybaSite(MujError):
    """Něco se síťí."""


# Uživatel může chytit cokoli z mé knihovny:
try:
    moje_funkce()
except MujError:
    ...
```

---

## 📦 Předání víc dat

```python
class HttpError(Exception):
    def __init__(self, status, body):
        super().__init__(f"HTTP {status}: {body[:100]}")
        self.status = status
        self.body = body


try:
    odeslat()
except HttpError as e:
    if e.status == 404:
        ...
```

---

## 🎯 Best practice — naming

- Končit `Error` (`ValidationError`, `TimeoutError`)
- Velbloudí (PascalCase)
- Specifické (ne `MujError`, ale `UserNotFoundError`)

---

## ✏️ Cvičení

1. **Nedostatek:** Vyrob `NedostatekProstredku` a používej v `Ucet`.
2. **Hierarchie:** Vyrob bázovou `OrderError` a podtřídy `OrderNotFound`, `OrderAlreadyPaid`.
3. **HTTP:** `HttpError` co nese status a body. Při 404 vrať None, jinak vyhoď.
4. **Validace:** `ValidationError(field, message)` co ví, které pole selhalo.
