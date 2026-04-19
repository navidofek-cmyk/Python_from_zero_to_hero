# Lekce 130 — Velký Monorepo a Multi-repo Python

Organizace kódu na úrovni celé firmy nebo velkého projektu je zásadní strategické rozhodnutí.
V této lekci prozkoumáme monorepo vs. multi-repo pattern, interní knihovny, namespace packages,
sdílené typy a platform team mindset.

---

## 1. Monorepo vs. Multi-repo

### Monorepo
Veškerý kód organizace v jednom repozitáři.

```
my-company/
├── libs/
│   ├── common/           # sdílené utility
│   ├── auth/             # autentizační knihovna
│   └── data-models/      # sdílené Pydantic modely
├── services/
│   ├── api/              # REST API service
│   ├── worker/           # background worker
│   └── ml-pipeline/      # ML pipeline
├── tools/
│   └── dev-tools/        # interní nástroje
└── pyproject.toml        # uv workspace root
```

### Multi-repo
Každá služba/knihovna v samostatném repozitáři.

| Aspekt | Monorepo | Multi-repo |
|---|---|---|
| Sdílení kódu | Snadné (přímý import) | Přes package registry |
| Atomic commits | Ano (cross-service) | Ne |
| CI/CD složitost | Vyšší (selective builds) | Nižší (per repo) |
| Onboarding | Jeden checkout | Více repozitářů |
| Ownership | Méně jasné | Jasně definované |
| Tooling | Nutné specializované | Standardní |

---

## 2. uv Workspaces — moderní monorepo

`uv` od Astral je moderní Python package manager s nativní podporou workspace:

```toml
# pyproject.toml (root)
[tool.uv.workspace]
members = [
    "libs/common",
    "libs/auth",
    "services/api",
    "services/worker",
]
```

```toml
# libs/common/pyproject.toml
[project]
name = "mycompany-common"
version = "1.2.0"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

```toml
# services/api/pyproject.toml
[project]
name = "mycompany-api"
version = "0.5.0"
dependencies = [
    "mycompany-common",   # lokální workspace dependency!
    "mycompany-auth",
    "fastapi>=0.100",
]
```

Vývoj: `uv sync` nainstaluje vše, lokální balíčky jsou linked (editable).

---

## 3. Namespace Packages (PEP 420)

Namespace packages umožňují rozložit balíček `mycompany` přes více adresářů
bez `__init__.py` v root namespace:

```
libs/
    mycompany/
        common/          ← žádný __init__.py v mycompany/!
            __init__.py
            utils.py
        auth/
            __init__.py
            jwt.py
services/
    mycompany/
        api/
            __init__.py
            main.py
```

```python
# Funguje bez konfliktu, protože mycompany/ je namespace package
from mycompany.common.utils import retry
from mycompany.auth.jwt import decode_token
from mycompany.api.main import app
```

### Vytvoření namespace package

```python
# libs/mycompany/common/__init__.py — EXISTUJE
# libs/mycompany/__init__.py — NEEXISTUJE (namespace package!)

# setup.cfg nebo pyproject.toml
[options]
packages = find_namespace:
package_dir = =libs
```

---

## 4. Interní knihovny a Semver politika

### Semantic Versioning v monorepu

```
MAJOR.MINOR.PATCH
  │     │     └── Bugfix, zpětně kompatibilní
  │     └──────── Nová feature, zpětně kompatibilní
  └────────────── Breaking change
```

### Politika pro interní knihovny

```python
# libs/common/mycompany/common/__init__.py

# Explicitní public API — vše ostatní je interní
__all__ = ["retry", "RateLimiter", "CircuitBreaker"]
__version__ = "2.3.1"
```

### Verze v pyproject.toml

```toml
[project]
name = "mycompany-common"
version = "2.3.1"

[project.optional-dependencies]
dev = ["pytest", "mypy"]

# Omezení verzí — nikdy neblokovat na přesné verze (pin only v leaf services)
[tool.uv.sources]
mycompany-auth = { workspace = true }
```

---

## 5. Sdílené typy přes .pyi stubs

Type stubs umožňují sdílet typy bez runtime závislosti:

```python
# libs/types/mycompany_types/__init__.pyi

from typing import TypedDict, Literal

class UserDTO(TypedDict):
    id: str
    email: str
    role: Literal["admin", "user", "readonly"]
    created_at: str

class OrderDTO(TypedDict):
    id: str
    user_id: str
    amount_czk: float
    status: Literal["pending", "paid", "cancelled"]

class PaginatedResponse(TypedDict):
    items: list
    total: int
    page: int
    page_size: int
    has_next: bool
```

```python
# Použití v services/api/
from mycompany_types import UserDTO, OrderDTO

def get_user(user_id: str) -> UserDTO:
    ...  # mypy kontroluje return type
```

---

## 6. Platform Team Mindset

Platform team (nebo developer platform team) se stará o:
- Interní tooling a knihovny
- CI/CD a deployment infrastrukturu
- Developer experience (DX)
- Governance a standardy

### Zlatá pravidla platform teamu

```
1. Treat internal teams as customers
2. Docs-first development
3. Semantic versioning + changelog vždy
4. Breaking changes s deprecation period
5. Internal SLA (response time, uptime)
```

### Deprecation pattern

```python
import warnings
import functools
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable)

def deprecated(
    reason: str,
    since: str,
    removal: str | None = None,
) -> Callable[[F], F]:
    """Dekorátor označující funkci jako deprecated."""
    def decorator(fn: F) -> F:
        msg = f"{fn.__name__} je deprecated od {since}: {reason}."
        if removal:
            msg += f" Bude odstraněno v {removal}."

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return fn(*args, **kwargs)
        return wrapper  # type: ignore
    return decorator

# Použití
@deprecated(
    reason="Použijte místo toho authenticate_v2()",
    since="2.0.0",
    removal="3.0.0",
)
def authenticate(token: str) -> bool:
    ...
```

---

## 7. Selective CI/CD pro monorepo

```python
# tools/check_affected.py — zjistí, které služby jsou ovlivněny změnami

import subprocess
from pathlib import Path

OWNERS: dict[str, str] = {
    "libs/common": "platform-team",
    "libs/auth": "security-team",
    "services/api": "api-team",
    "services/worker": "data-team",
}

def get_changed_paths(base_branch: str = "main") -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_branch}...HEAD"],
        capture_output=True, text=True
    )
    return result.stdout.strip().splitlines()

def find_affected_services(changed: list[str]) -> set[str]:
    affected = set()
    for path in changed:
        for service_path in OWNERS:
            if path.startswith(service_path):
                affected.add(service_path)
    return affected
```

---

## 8. Doporučená struktura Python monorepa

```
company-mono/
├── .github/
│   └── workflows/
│       ├── ci.yml              # selective CI
│       └── release.yml
├── libs/
│   ├── common/
│   │   ├── pyproject.toml
│   │   ├── mycompany/common/
│   │   │   ├── __init__.py
│   │   │   ├── retry.py
│   │   │   └── config.py
│   │   └── tests/
│   ├── auth/
│   │   ├── pyproject.toml
│   │   └── mycompany/auth/
│   └── types/
│       ├── pyproject.toml
│       └── mycompany_types/
│           └── __init__.pyi
├── services/
│   ├── api/
│   │   ├── pyproject.toml
│   │   └── src/
│   └── worker/
│       ├── pyproject.toml
│       └── src/
├── tools/
│   ├── check_affected.py
│   └── release.py
├── pyproject.toml              # uv workspace root
├── uv.lock                     # lockfile pro reprodukovatelné buildy
└── CHANGELOG.md
```

---

## Shrnutí

- **Monorepo** usnadňuje sdílení kódu a atomic refaktoring, ale vyžaduje specializovaný tooling.
- **uv workspaces** jsou moderní řešení pro Python monorepo — lokální závislosti, lockfile.
- **Namespace packages** (PEP 420) umožňují distribuovat `mycompany.*` přes více adresářů.
- **Semver** je závazná smlouva se uživateli vaší knihovny — breaking changes v MAJOR.
- **.pyi stubs** sdílí typy bez runtime overhead — ideální pro cross-service kontrakty.
- **Platform team** je interní zákazník-orientovaný tým starající se o DX ostatních týmů.
- **Selective CI** spouští testy jen pro ovlivněné komponenty — klíčové pro výkon.

## Cvičení

1. Vytvořte lokální uv workspace se dvěma balíčky (`mylib` a `myapp`, která závisí na `mylib`).
2. Implementujte `check_affected.py` — skript, který z `git diff` zjistí, které služby jsou dotčeny.
3. Přidejte do `deprecated` dekorátoru logování s počtem volání (kolik kódu stále deprecated API používá).
4. Napište `release.py` — script, který z `CHANGELOG.md` přečte verzi a automaticky bumpe `pyproject.toml`.
5. Implementujte `CompatibilityMatrix` — tabulku kompatibility verzí interních knihoven.

---

---

# Závěr kurzu: Python od Nuly k Hrdinovi

Gratulujeme. Právě jste dokončili 130 lekcí Pythonu — od prvního `print("Hello, world!")` až
po monorepo architekturu velkých systémů.

## Co jste se naučili

### Základy (lekce 1–30)
Proměnné, datové typy, podmínky, cykly, funkce, třídy — stavební kameny každého Python programu.

### Středně pokročilé (lekce 31–70)
Dekorátory, generátory, kontextové manažery, deskriptory, metaklasy, iterátory —
Python jako expresivní a elegantní jazyk.

### Pokročilé (lekce 71–100)
Concurrency, networking, testování, profilování, C rozšíření, CPython internals —
Python jako výkonný nástroj pro produkční systémy.

### Expert (lekce 101–130)
AI/LLM integrace, SOLID principy, návrhové vzory, data engineering, stream processing,
MLOps, plugin architektury, architektonická rozhodnutí, monorepo —
Python jako páteř moderní softwarové organizace.

## Cesta vpřed

Znalosti jsou jen začátek. Skuteční hrdinové kódu:

1. **Tvoří** — každý projekt, i malý, buduje intuici
2. **Čtou kód** — CPython, populární open-source knihovny, PEP dokumenty
3. **Přispívají** — open-source je nejlepší portfolio
4. **Učí** — vysvětlovat je nejlepší způsob, jak hluboce pochopit
5. **Nespokojí se** — každá lekce otevírá deset dalších otázek

## Doporučené zdroje

| Téma | Zdroj |
|---|---|
| CPython internals | "CPython Internals" — Anthony Shaw |
| High Performance Python | "High Performance Python" — Micha Gorelick |
| Architektura | "Architecture Patterns with Python" — Percival & Gregory |
| Data Engineering | "Fundamentals of Data Engineering" — Reis & Housley |
| ML Systems | "Designing Machine Learning Systems" — Chip Huyen |
| Komunita | Python Discord, PyPI, PyCon přednášky |

## Závěrečné slovo

Python není jen programovací jazyk — je to způsob myšlení.
Čistý kód, explicitní záměry, "batteries included" filozofie —
tyto principy přesahují Python a platí pro každý software, který napíšete.

Svět potřebuje vývojáře, kteří nejen píší kód, ale rozumí proč.
Kteří se nebojí jít do CPython source a podívat se jak věci skutečně fungují.
Kteří dokumentují rozhodnutí, protože vědí, že kód čtou lidé.

Jste připraveni. Jste Python hero.

```python
import you
you.build_something_amazing()
```

*— Konec kurzu Python: Zero to Hero —*
