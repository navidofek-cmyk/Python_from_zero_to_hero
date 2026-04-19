"""Lekce 118 — Releasing & Rollback: semver, changelog, blue/green, migrace."""
from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, NamedTuple


# ── Sémantické verzování ──────────────────────────────────────────────────────

@dataclass(frozen=True, order=True)
class SemVer:
    """
    Sémantická verze dle SemVer 2.0.0.
    Implementováno bez packaging knihovny — čistá stdlib.
    """
    major: int
    minor: int
    patch: int
    pre_release: str = ""      # "alpha.1", "beta.2", "rc.1"
    build_meta: str = ""       # "+sha.abc1234" (ignorováno při porovnání)

    @classmethod
    def parse(cls, version_str: str) -> SemVer:
        """Parsuje verzi ze stringu. Akceptuje volitelný prefix 'v'."""
        s = version_str.lstrip("v").strip()
        # Odděl build metadata
        build = ""
        if "+" in s:
            s, build = s.split("+", 1)
        # Odděl pre-release
        pre = ""
        if "-" in s:
            s, pre = s.split("-", 1)
        parts = s.split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise ValueError(f"Neplatná SemVer: {version_str!r}")
        return cls(int(parts[0]), int(parts[1]), int(parts[2]), pre, build)

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_release:
            base += f"-{self.pre_release}"
        if self.build_meta:
            base += f"+{self.build_meta}"
        return base

    def is_stable(self) -> bool:
        return not self.pre_release

    def bump_major(self) -> SemVer:
        return SemVer(self.major + 1, 0, 0)

    def bump_minor(self) -> SemVer:
        return SemVer(self.major, self.minor + 1, 0)

    def bump_patch(self) -> SemVer:
        return SemVer(self.major, self.minor, self.patch + 1)

    def upgrade_type(self, other: SemVer) -> str:
        """Popis typu upgradu z self na other."""
        if other.major > self.major:
            return "MAJOR (breaking changes!)"
        if other.minor > self.minor:
            return "MINOR (nové funkce, zpětně kompatibilní)"
        if other.patch > self.patch:
            return "PATCH (bugfixes)"
        return "DOWNGRADE nebo stejná verze"


def demonstrate_semver() -> None:
    """Ukázka práce se sémantickými verzemi."""
    versions_raw = ["1.0.0", "2.1.3", "1.0.0-alpha.1", "1.0.0-rc.2", "2.0.0-beta.1", "v3.0.0"]
    versions = [SemVer.parse(v) for v in versions_raw]
    sorted_versions = sorted(versions)

    print("  Verzování:")
    print(f"  {'Původní':20s} {'Parsovaná':20s} {'Stabilní':8s}")
    for raw, v in zip(versions_raw, versions):
        print(f"  {raw:20s} {str(v):20s} {str(v.is_stable()):8s}")

    print(f"\n  Seřazené verze: {' < '.join(str(v) for v in sorted_versions)}")

    base = SemVer.parse("1.5.3")
    print(f"\n  Bumps z {base}:")
    print(f"    bump_patch() → {base.bump_patch()}")
    print(f"    bump_minor() → {base.bump_minor()}")
    print(f"    bump_major() → {base.bump_major()}")

    pairs = [("1.5.3", "1.5.4"), ("1.5.3", "1.6.0"), ("1.5.3", "2.0.0")]
    print("\n  Typy upgradů:")
    for from_v, to_v in pairs:
        a, b = SemVer.parse(from_v), SemVer.parse(to_v)
        print(f"  {from_v} → {to_v}: {a.upgrade_type(b)}")


# ── Changelog ─────────────────────────────────────────────────────────────────

class ChangeType(Enum):
    ADDED = "Added"
    CHANGED = "Changed"
    DEPRECATED = "Deprecated"
    REMOVED = "Removed"
    FIXED = "Fixed"
    SECURITY = "Security"


@dataclass
class ChangeEntry:
    change_type: ChangeType
    description: str
    issue: str | None = None
    pr: str | None = None


@dataclass
class Release:
    version: str
    release_date: date
    entries: list[ChangeEntry] = field(default_factory=list)
    yanked: bool = False

    def add(
        self,
        change_type: ChangeType,
        description: str,
        issue: str | None = None,
        pr: str | None = None,
    ) -> Release:
        self.entries.append(ChangeEntry(change_type, description, issue, pr))
        return self


def build_sample_changelog() -> list[Release]:
    """Sestaví ukázkový changelog."""
    r1 = Release("1.5.4", date(2026, 4, 19))
    r1.add(ChangeType.SECURITY, "Aktualizována verze cryptography na 41.0.2 (CVE-2023-38325)", pr="142")
    r1.add(ChangeType.FIXED, "Opraven race condition v cache wrapperu", issue="89", pr="140")
    r1.add(ChangeType.FIXED, "Health endpoint vrací správný HTTP kód při DB výpadku", issue="91")

    r2 = Release("1.5.3", date(2026, 4, 10))
    r2.add(ChangeType.ADDED, "Nový /ready endpoint pro Kubernetes readiness probe", pr="135")
    r2.add(ChangeType.ADDED, "Strukturované JSON logy (JsonFormatter)", issue="78", pr="133")
    r2.add(ChangeType.CHANGED, "Migrace konfigurace na pydantic-settings vzor")
    r2.add(ChangeType.FIXED, "Opraveno maskování hesel v URL v logách", issue="82")

    r3 = Release("1.5.2", date(2026, 3, 28))
    r3.add(ChangeType.SECURITY, "Opravena SQL injection zranitelnost v uživatelském filtru", issue="75")
    r3.add(ChangeType.DEPRECATED, "Funkce load_config_from_file() bude odstraněna ve 2.0.0")

    return [r1, r2, r3]


def render_changelog(releases: list[Release]) -> str:
    """Vygeneruje CHANGELOG.md v Keep a Changelog formátu."""
    lines = [
        "# Changelog",
        "",
        "Všechny podstatné změny tohoto projektu jsou v tomto souboru.",
        "Formát: [Keep a Changelog](https://keepachangelog.com/cs/1.0.0/)",
        "Verzování: [SemVer](https://semver.org/lang/cs/)",
        "",
    ]
    for release in releases:
        yanked = " [YANKED]" if release.yanked else ""
        lines.append(f"## [{release.version}] — {release.release_date}{yanked}")
        lines.append("")
        for ct in ChangeType:
            entries = [e for e in release.entries if e.change_type == ct]
            if entries:
                lines.append(f"### {ct.value}")
                for e in entries:
                    refs = []
                    if e.issue:
                        refs.append(f"#{e.issue}")
                    if e.pr:
                        refs.append(f"PR #{e.pr}")
                    ref_str = f" ({', '.join(refs)})" if refs else ""
                    lines.append(f"- {e.description}{ref_str}")
                lines.append("")
    return "\n".join(lines)


# ── Blue/Green deployment ─────────────────────────────────────────────────────

class Slot(Enum):
    BLUE = "blue"
    GREEN = "green"


@dataclass
class DeploymentSlot:
    slot: Slot
    version: str
    deployed_at: datetime | None = None
    healthy: bool = False


class BlueGreenDeployer:
    """
    Blue/Green deployment manager.
    Umožňuje zero-downtime deploy a okamžitý rollback.
    """

    def __init__(self, initial_version: str) -> None:
        self._slots: dict[Slot, DeploymentSlot] = {
            Slot.BLUE: DeploymentSlot(Slot.BLUE, initial_version, datetime.now(), True),
            Slot.GREEN: DeploymentSlot(Slot.GREEN, initial_version, None, False),
        }
        self._active: Slot = Slot.BLUE
        self._history: list[tuple[str, str, str]] = []  # (čas, akce, popis)

    def _log(self, action: str, detail: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self._history.append((ts, action, detail))
        print(f"  [{ts}] {action:15s} {detail}")

    @property
    def active_version(self) -> str:
        return self._slots[self._active].version

    @property
    def inactive_slot(self) -> Slot:
        return Slot.GREEN if self._active == Slot.BLUE else Slot.BLUE

    def deploy(self, new_version: str) -> Slot:
        """Nasadí novou verzi na neaktivní slot."""
        target = self.inactive_slot
        self._log("DEPLOY", f"Nasazuji {new_version} na slot {target.value}")
        self._slots[target] = DeploymentSlot(target, new_version, datetime.now(), False)
        time.sleep(0.05)  # Simulace deploymentu
        self._log("HEALTHCHECK", f"Kontrola zdraví slotu {target.value}...")
        self._slots[target].healthy = True
        self._log("READY", f"Slot {target.value} ({new_version}) připraven")
        return target

    def switch(self) -> None:
        """Přepne provoz na neaktivní slot."""
        old_slot = self._active
        old_version = self._slots[old_slot].version
        new_slot = self.inactive_slot
        new_version = self._slots[new_slot].version
        self._active = new_slot
        self._log("SWITCH", f"{old_version} ({old_slot.value}) → {new_version} ({new_slot.value})")

    def rollback(self) -> None:
        """Okamžitý rollback na předchozí slot."""
        prev_version = self._slots[self.inactive_slot].version
        self._log("ROLLBACK", f"Vracím se na {prev_version} ({self.inactive_slot.value})")
        self._active = self.inactive_slot
        self._log("ROLLBACK_DONE", f"Aktivní verze: {self.active_version}")

    def status(self) -> dict[str, Any]:
        return {
            "active_slot": self._active.value,
            "active_version": self.active_version,
            "slots": {
                s.value: {"version": slot.version, "healthy": slot.healthy}
                for s, slot in self._slots.items()
            },
        }


# ── Canary deployment ─────────────────────────────────────────────────────────

class CanaryDeployer:
    """
    Postupný canary rollout.
    Deterministické přiřazení user_id → verze.
    """

    def __init__(self, stable: str, canary: str) -> None:
        self.stable = stable
        self.canary = canary
        self._canary_pct: int = 0
        self._metrics: dict[str, int] = {stable: 0, canary: 0}

    def set_percent(self, pct: int) -> None:
        self._canary_pct = max(0, min(100, pct))

    def route(self, user_id: str) -> str:
        """Vrátí verzi pro daného uživatele — deterministické."""
        h = int(hashlib.sha256(f"{self.canary}:{user_id}".encode()).hexdigest(), 16) % 100
        version = self.canary if h < self._canary_pct else self.stable
        self._metrics[version] = self._metrics.get(version, 0) + 1
        return version

    def traffic_split(self, n_users: int = 1000) -> dict[str, float]:
        """Simuluje rozdělení provozu pro N uživatelů."""
        counts: dict[str, int] = {self.stable: 0, self.canary: 0}
        for i in range(n_users):
            v = self.route(f"user-{i:05d}")
            counts[v] = counts.get(v, 0) + 1
        return {v: round(c / n_users * 100, 1) for v, c in counts.items()}

    def promote(self, step: int = 10) -> int:
        """Zvýší canary procento o krok."""
        self._canary_pct = min(100, self._canary_pct + step)
        return self._canary_pct

    def rollback(self) -> None:
        self._canary_pct = 0


# ── Databázové migrace (simulace Alembic vzorů) ───────────────────────────────

@dataclass
class Migration:
    revision: str
    down_revision: str | None
    description: str
    operations: list[str]
    safe: bool = True  # Lze provést za provozu?
    warnings: list[str] = field(default_factory=list)


def build_migration_history() -> list[Migration]:
    """Vrátí ukázkovou historii migrací."""
    return [
        Migration(
            revision="001_initial",
            down_revision=None,
            description="Initial schema",
            operations=["CREATE TABLE users", "CREATE TABLE sessions"],
            safe=True,
        ),
        Migration(
            revision="002_add_email_index",
            down_revision="001_initial",
            description="Add index on users.email",
            operations=["CREATE INDEX CONCURRENTLY ix_users_email ON users(email)"],
            safe=True,
        ),
        Migration(
            revision="003_add_orders",
            down_revision="002_add_email_index",
            description="Add orders table",
            operations=["CREATE TABLE orders", "CREATE INDEX ix_orders_user_id ON orders(user_id)"],
            safe=True,
        ),
        Migration(
            revision="004_add_avatar_url",
            down_revision="003_add_orders",
            description="Add nullable avatar_url column",
            operations=["ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500)"],
            safe=True,
        ),
        Migration(
            revision="005_rename_column",
            down_revision="004_add_avatar_url",
            description="Rename users.name to users.full_name",
            operations=["ALTER TABLE users RENAME COLUMN name TO full_name"],
            safe=False,
            warnings=["Přejmenování sloupce vyžaduje expand-contract vzor nebo maintenance window"],
        ),
        Migration(
            revision="006_drop_sessions",
            down_revision="005_rename_column",
            description="Drop deprecated sessions table",
            operations=["DROP TABLE sessions"],
            safe=False,
            warnings=["Nejdřív odeberte sessions z kódu, pak teprve spusťte tuto migraci"],
        ),
    ]


def analyze_migration_safety(migrations: list[Migration]) -> None:
    """Analyzuje bezpečnost migrací pro produkci."""
    print("  Analýza bezpečnosti migrací:")
    print(f"  {'Revize':20s} {'Bezpečná':10s} {'Popis'}")
    print(f"  {'-'*65}")
    for m in migrations:
        safety = "ANO    " if m.safe else "VAROVÁNÍ"
        print(f"  {m.revision:20s} {safety:10s} {m.description}")
        for warning in m.warnings:
            print(f"  {'':20s}           ⚠ {warning}")


# ── Release checklist ─────────────────────────────────────────────────────────

@dataclass
class ChecklistItem:
    text: str
    phase: str
    done: bool = False


def build_release_checklist() -> list[ChecklistItem]:
    return [
        # Pre-release
        ChecklistItem("Všechny testy prochází (CI zelené)", "pre-release"),
        ChecklistItem("Verze bumped v pyproject.toml", "pre-release"),
        ChecklistItem("CHANGELOG.md aktualizován", "pre-release"),
        ChecklistItem("Databázové migrace připraveny a otestovány", "pre-release"),
        ChecklistItem("Feature flags pro nové funkce vypnuty", "pre-release"),
        ChecklistItem("Rollback plán zdokumentován", "pre-release"),
        # Deploy
        ChecklistItem("Záloha databáze provedena", "deploy"),
        ChecklistItem("Deploy spuštěn (CI/CD)", "deploy"),
        ChecklistItem("Databázové migrace spuštěny", "deploy"),
        ChecklistItem("Health check zelený", "deploy"),
        ChecklistItem("Smoke testy prošly", "deploy"),
        # Post-release
        ChecklistItem("Metriky a logy monitorovány (15 min)", "post-release"),
        ChecklistItem("Feature flags postupně zapnuty", "post-release"),
        ChecklistItem("Uživatelé informováni (release notes)", "post-release"),
        ChecklistItem("Dokumentace aktualizována", "post-release"),
    ]


# ── Hlavní funkce ─────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 65)
    print("RELEASING & ROLLBACK — DEMO")
    print("=" * 65)

    # --- 1. SemVer ---
    print("\n[1] Sémantické verzování (SemVer):")
    demonstrate_semver()

    # --- 2. Changelog ---
    print("\n[2] Generování CHANGELOG.md:")
    releases = build_sample_changelog()
    changelog = render_changelog(releases)
    lines = changelog.splitlines()
    print(f"  Vygenerováno {len(lines)} řádků pro {len(releases)} vydání")
    print(f"\n  {'='*50}")
    for line in lines[:35]:
        print(f"  {line}")
    if len(lines) > 35:
        print(f"  ... ({len(lines) - 35} dalších řádků)")

    # --- 3. Blue/Green deployment ---
    print("\n[3] Blue/Green deployment simulace:")
    bg = BlueGreenDeployer("1.5.3")
    print(f"  Počáteční stav: {json.dumps(bg.status())}")

    # Deploy nové verze
    print("\n  Deploy verze 1.5.4:")
    bg.deploy("1.5.4")
    bg.switch()
    print(f"  Aktivní verze: {bg.active_version}")

    # Simulace problému → rollback
    print("\n  Detekován problém → Rollback!")
    bg.rollback()
    print(f"  Aktivní verze po rollbacku: {bg.active_version}")
    print(f"\n  Stav slotů: {json.dumps(bg.status(), indent=2)}")

    # --- 4. Canary deployment ---
    print("\n[4] Canary deployment simulace:")
    canary = CanaryDeployer("1.5.3", "1.5.4")

    print(f"  {'Canary %':10s} {'v1.5.3':10s} {'v1.5.4':10s}")
    print(f"  {'-'*30}")
    for pct in [0, 10, 25, 50, 75, 100]:
        canary.set_percent(pct)
        split = canary.traffic_split(n_users=500)
        print(f"  {pct:3d}%       {split.get('1.5.3', 0):5.1f}%    {split.get('1.5.4', 0):5.1f}%")

    print("\n  Postupný rollout (promote o 25% kroky):")
    canary.set_percent(0)
    for step_n in range(5):
        pct = canary.promote(step=25)
        split = canary.traffic_split(200)
        print(f"  Krok {step_n+1}: {pct:3d}% canary | "
              f"v1.5.3: {split.get('1.5.3', 0):.1f}% | "
              f"v1.5.4: {split.get('1.5.4', 0):.1f}%")

    # --- 5. Databázové migrace ---
    print("\n[5] Analýza databázových migrací:")
    migrations = build_migration_history()
    analyze_migration_safety(migrations)

    safe_count = sum(1 for m in migrations if m.safe)
    unsafe_count = len(migrations) - safe_count
    print(f"\n  Celkem: {len(migrations)} migrací, {safe_count} bezpečných, {unsafe_count} s varováním")

    # --- 6. Release checklist ---
    print("\n[6] Release checklist:")
    checklist = build_release_checklist()
    current_phase = ""
    for item in checklist:
        if item.phase != current_phase:
            current_phase = item.phase
            print(f"\n  [{current_phase.upper()}]")
        status = "[x]" if item.done else "[ ]"
        print(f"  {status} {item.text}")

    # --- 7. Verzovací strategie shrnutí ---
    print("\n[7] Přehled deploy strategií:")
    strategies = [
        ("Rolling update", "K8s výchozí — postupně nahrazuje staré pody", "Žádný rollback slot"),
        ("Blue/Green", "Dva sloty — okamžitý rollback přepnutím", "2x infrastruktura"),
        ("Canary", "Postupný rollout — detekce problémů", "Složitější routing"),
        ("Feature flags", "Deploy bez aktivace — toggle za běhu", "Správa flag dluhu"),
        ("Recreate", "Výpadek → smazání starého → deploy nového", "Downtime nutný"),
    ]
    print(f"  {'Strategie':15s} {'Výhoda':45s} {'Nevýhoda'}")
    print(f"  {'-'*85}")
    for name, pro, con in strategies:
        print(f"  {name:15s} {pro:45s} {con}")

    # --- 8. SemVer summary ---
    print("\n[8] Kdy bumpit jakou verzi:")
    print("  MAJOR (2.0.0): Breaking changes — změna API, smazání funkcí")
    print("  MINOR (1.1.0): Nové funkce zpětně kompatibilní")
    print("  PATCH (1.0.1): Bugfixes, bezpečnostní opravy")
    print("  PRE  (1.1.0-rc.1): Alpha/Beta/RC — není pro produkci")


if __name__ == "__main__":
    main()
