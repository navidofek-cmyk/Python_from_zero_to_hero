# Lekce 118 — Releasing, Rollback a Databázové migrace

Releasing je proces vydávání nových verzí aplikace do produkce. Správná strategie vydávání minimalizuje riziko výpadků a usnadňuje rollback.

---

## 1. Sémantické verzování (SemVer)

```
MAJOR.MINOR.PATCH[-pre-release][+build]

1.0.0         — Stabilní vydání
1.0.0-alpha.1 — Alpha verze
1.0.0-beta.2  — Beta verze
1.0.0-rc.1    — Release candidate
2.0.0         — Breaking change (nekompatibilní API)
1.1.0         — Nová zpětně kompatibilní funkcionalita
1.0.1         — Bugfix
```

### Použití packaging.version

```python
from packaging.version import Version, InvalidVersion

def compare_versions(v1: str, v2: str) -> int:
    """Porovná dvě verze. Vrátí -1, 0, nebo 1."""
    a, b = Version(v1), Version(v2)
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


def is_upgrade_safe(current: str, target: str) -> tuple[bool, str]:
    """
    Zkontroluje, zda je upgrade bezpečný.
    Vrátí (je_bezpečné, důvod).
    """
    try:
        c = Version(current)
        t = Version(target)
    except InvalidVersion as e:
        return False, f"Neplatná verze: {e}"

    if t <= c:
        return False, f"Cílová verze {target} není novější než {current}"

    if t.major > c.major:
        return True, f"MAJOR upgrade {c.major} → {t.major}: zkontrolujte breaking changes!"

    if t.minor > c.minor:
        return True, f"MINOR upgrade (nové funkce, zpětně kompatibilní)"

    return True, f"PATCH upgrade (bugfixes)"


def get_version_from_git() -> str:
    """Načte verzi z git tagu."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--exact-match"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip().lstrip("v")
    except subprocess.CalledProcessError:
        # Nejsme přesně na tagu — dev verze
        result = subprocess.run(
            ["git", "describe", "--tags"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            # Formát: v1.2.3-5-gabcdef → 1.2.3.dev5+gabcdef
            raw = result.stdout.strip().lstrip("v")
            parts = raw.rsplit("-", 2)
            if len(parts) == 3:
                return f"{parts[0]}.dev{parts[1]}+{parts[2]}"
        return "0.0.0.dev0"
```

---

## 2. Changelog generování

```python
from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class ChangeType(Enum):
    ADDED = "Added"
    CHANGED = "Changed"
    DEPRECATED = "Deprecated"
    REMOVED = "Removed"
    FIXED = "Fixed"
    SECURITY = "Security"


@dataclass
class ChangeEntry:
    type: ChangeType
    description: str
    issue: str | None = None


@dataclass
class Release:
    version: str
    date: date
    entries: list[ChangeEntry] = field(default_factory=list)
    yanked: bool = False

    def add(self, change_type: ChangeType, description: str, issue: str | None = None) -> None:
        self.entries.append(ChangeEntry(change_type, description, issue))


class Changelog:
    """Generátor CHANGELOG.md v Keep a Changelog formátu."""

    def __init__(self) -> None:
        self.releases: list[Release] = []

    def add_release(self, release: Release) -> None:
        self.releases.append(release)

    def to_markdown(self) -> str:
        lines = [
            "# Changelog",
            "",
            "Všechny podstatné změny tohoto projektu jsou dokumentovány v tomto souboru.",
            "",
            "Formát vychází z [Keep a Changelog](https://keepachangelog.com/cs/1.0.0/),",
            "projekt dodržuje [Sémantické verzování](https://semver.org/lang/cs/).",
            "",
        ]

        for release in self.releases:
            date_str = release.date.isoformat()
            yanked = " [YANKED]" if release.yanked else ""
            lines.append(f"## [{release.version}] — {date_str}{yanked}")
            lines.append("")

            # Seskup podle typu
            for change_type in ChangeType:
                type_entries = [e for e in release.entries if e.type == change_type]
                if type_entries:
                    lines.append(f"### {change_type.value}")
                    for entry in type_entries:
                        issue_ref = f" ([#{entry.issue}](issues/{entry.issue}))" if entry.issue else ""
                        lines.append(f"- {entry.description}{issue_ref}")
                    lines.append("")

        return "\n".join(lines)
```

---

## 3. Strategie nasazení

### Blue/Green deployment

```
Před deploymentem:
  Load Balancer → [Blue (v1.5.3)] ← 100% provozu
  [Green (v1.5.4)] ← připravuje se

Po deploymentu:
  Load Balancer → [Green (v1.5.4)] ← 100% provozu
  [Blue (v1.5.3)] ← standby (rychlý rollback!)

Rollback (okamžitý):
  Load Balancer → [Blue (v1.5.3)] ← přepnutí zpět
```

```python
from enum import Enum

class DeploymentColor(Enum):
    BLUE = "blue"
    GREEN = "green"


class BlueGreenRouter:
    """Jednoduchý blue/green router."""

    def __init__(self) -> None:
        self._active: DeploymentColor = DeploymentColor.BLUE
        self._deployments: dict[DeploymentColor, str] = {
            DeploymentColor.BLUE: "v1.5.3",
            DeploymentColor.GREEN: "v1.5.3",
        }

    def deploy(self, version: str) -> DeploymentColor:
        """Nasadí verzi na neaktivní slot."""
        inactive = self._inactive()
        self._deployments[inactive] = version
        return inactive

    def switch(self) -> None:
        """Přepne provoz na druhý slot."""
        self._active = self._inactive()

    def rollback(self) -> None:
        """Okamžitý rollback na předchozí slot."""
        self.switch()

    def _inactive(self) -> DeploymentColor:
        return (
            DeploymentColor.GREEN
            if self._active == DeploymentColor.BLUE
            else DeploymentColor.BLUE
        )

    @property
    def active_version(self) -> str:
        return self._deployments[self._active]
```

### Canary deployment

```python
import random

class CanaryRouter:
    """Postupný canary rollout."""

    def __init__(self, stable_version: str, canary_version: str) -> None:
        self.stable = stable_version
        self.canary = canary_version
        self._canary_percent: int = 0

    def set_canary_percent(self, percent: int) -> None:
        """Nastaví procento provozu pro canary verzi (0–100)."""
        self._canary_percent = max(0, min(100, percent))

    def route_request(self, request_id: str) -> str:
        """Vrátí verzi pro daný požadavek."""
        # Deterministické rozdělení — stejný request_id → stejná verze
        h = hash(request_id) % 100
        if h < self._canary_percent:
            return self.canary
        return self.stable

    @property
    def canary_percent(self) -> int:
        return self._canary_percent
```

---

## 4. Databázové migrace (Alembic vzory)

Alembic je de facto standard pro migraci databázových schémat s SQLAlchemy.

### Struktura projektu

```
myapp/
├── alembic.ini
├── alembic/
│   ├── env.py                  ← konfigurace
│   ├── script.py.mako          ← šablona pro nové migrace
│   └── versions/
│       ├── 001_initial.py
│       ├── 002_add_users.py
│       └── 003_add_orders.py
```

### Příklad migrace

```python
# alembic/versions/003_add_orders.py
"""Add orders table

Revision ID: a1b2c3d4e5f6
Revises: f5e4d3c2b1a0
Create Date: 2026-04-19 10:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f5e4d3c2b1a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"])
    op.create_index("ix_orders_status", "orders", ["status"])


def downgrade() -> None:
    op.drop_index("ix_orders_status")
    op.drop_index("ix_orders_user_id")
    op.drop_table("orders")
```

### Bezpečné migrace v produkci

```python
# alembic/versions/004_add_column_safe.py
"""Bezpečná migrace — přidání sloupce s výchozí hodnotou

Bezpečné změny (lze provést za provozu):
  + Přidat nullable sloupec
  + Přidat sloupec s DEFAULT
  + Přidat index CONCURRENTLY (PostgreSQL)
  + Přidat novou tabulku

Nebezpečné změny (vyžadují maintenance window nebo expand-contract vzor):
  - Přejmenovat sloupec
  - Změnit typ sloupce
  - Smazat sloupec (nejdřív odebrat z kódu!)
  - Přidat NOT NULL bez DEFAULT
"""

def upgrade() -> None:
    # BEZPEČNÉ: nullable sloupec s výchozí hodnotou
    op.add_column("users", sa.Column(
        "avatar_url",
        sa.String(500),
        nullable=True,  # ← nullable = bezpečné za provozu
    ))

    # POZOR: přidání NOT NULL vyžaduje existující data nebo DEFAULT
    # op.add_column("users", sa.Column(
    #     "email_verified",
    #     sa.Boolean,
    #     nullable=False,
    #     server_default="false",  # ← povinné pro NOT NULL bez dat
    # ))
```

### Spuštění migrací v CI/CD

```bash
# Kontrola čekajících migrací (fail pokud jsou)
alembic check

# Spuštění migrací
alembic upgrade head

# Rollback o jednu migraci
alembic downgrade -1

# Rollback na konkrétní revizi
alembic downgrade a1b2c3d4e5f6

# Historie migrací
alembic history --verbose

# Aktuální stav
alembic current
```

---

## 5. Release checklist

```python
RELEASE_CHECKLIST = """
Pre-release:
  [ ] Všechny testy prochází (CI zelené)
  [ ] Verze aktualizována v pyproject.toml
  [ ] CHANGELOG.md aktualizován
  [ ] Migrace databáze připraveny a otestovány
  [ ] Feature flags pro nové funkce vypnuty
  [ ] Rollback plán zdokumentován
  [ ] Staging testování dokončeno

Deploy:
  [ ] Záloha databáze (produkce)
  [ ] Deploy spuštěn (CI/CD nebo manuálně)
  [ ] Databázové migrace spuštěny
  [ ] Health check zelený
  [ ] Smoke testy prošly
  [ ] Metriky a logy monitorovány (15 minut)

Post-release:
  [ ] Feature flags postupně zapnuty (canary)
  [ ] Uživatelé informováni (release notes)
  [ ] Starý deployment slot připraven pro rollback
  [ ] Dokumentace aktualizována
"""
```

---

## Shrnutí

| Téma | Klíčový nástroj/vzor |
|------|---------------------|
| Verzování | `packaging.version`, SemVer |
| Changelog | Keep a Changelog, `git log --oneline` |
| Blue/green | Load balancer přepínání, okamžitý rollback |
| Canary | Postupné % provozu, monitoring metrik |
| DB migrace | Alembic, expand-contract vzor |
| Rollback | `alembic downgrade -1`, `kubectl rollout undo` |

---

## Cvičení

1. Implementujte `VersionBumper` třídu, která: přečte aktuální verzi z `pyproject.toml`, provede bump (major/minor/patch), aktualizuje soubor a vytvoří git tag.
2. Napište skript, který z `git log` vygeneruje CHANGELOG.md ve formátu Keep a Changelog — konvence: commit zprávy začínající `feat:`, `fix:`, `security:`, `breaking:`.
3. Vytvořte `MigrationSafety` třídu, která analyzuje Alembic migrace a varuje před nebezpečnými operacemi (DROP COLUMN, NOT NULL bez DEFAULT, přejmenování).
4. Implementujte `CanaryRouter` s perzistentním přiřazením uživatel → verze (stejný uživatel vždy dostane stejnou verzi) a metodou `promote()`, která zvyšuje canary procento o 10% každých N minut.
