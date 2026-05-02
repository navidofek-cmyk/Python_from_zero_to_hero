# Program — Lekce 130: Lekce 130 — Velký Monorepo a Multi-repo Python

Patří k lekci [Lekce 130 — Velký Monorepo a Multi-repo Python](../130_monorepo.md).

## Jak spustit

```bash
python3 programy/l130_monorepo.py
```

## Zdrojový kód

### `l130_monorepo.py`

```py
"""Lekce 130 — Velký Monorepo a Multi-repo Python."""

from __future__ import annotations

import functools
import json
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, TypeVar

# ── Semver utilita ────────────────────────────────────────────────────────────

@dataclass(order=True, frozen=True)
class Version:
    """Semantic Version (MAJOR.MINOR.PATCH)."""

    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, s: str) -> "Version":
        parts = s.lstrip("v").split(".")
        if len(parts) != 3:
            raise ValueError(f"Neplatná verze: '{s}' (očekáváno MAJOR.MINOR.PATCH)")
        return cls(int(parts[0]), int(parts[1]), int(parts[2]))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def bump_major(self) -> "Version":
        return Version(self.major + 1, 0, 0)

    def bump_minor(self) -> "Version":
        return Version(self.major, self.minor + 1, 0)

    def bump_patch(self) -> "Version":
        return Version(self.major, self.minor, self.patch + 1)

    def is_compatible(self, other: "Version") -> bool:
        """Zpětně kompatibilní = stejné MAJOR, vyšší nebo stejné MINOR."""
        return self.major == other.major and self >= other

    def breaking_change(self, other: "Version") -> bool:
        """Vrátí True pokud je přechod na `other` breaking change."""
        return other.major > self.major


# ── Interní knihovna — simulace ───────────────────────────────────────────────

@dataclass
class InternalPackage:
    """Metadata interní Python knihovny."""

    name: str
    version: Version
    description: str
    owners: list[str] = field(default_factory=list)
    dependents: list[str] = field(default_factory=list)    # kdo na ni závisí
    dependencies: list[str] = field(default_factory=list)  # na čem závisí
    deprecated: bool = False
    deprecation_message: str = ""

    def __str__(self) -> str:
        dep = " [DEPRECATED]" if self.deprecated else ""
        return f"{self.name} v{self.version}{dep}"


class InternalRegistry:
    """Registr interních balíčků organizace."""

    def __init__(self) -> None:
        self._packages: dict[str, InternalPackage] = {}

    def register(self, pkg: InternalPackage) -> None:
        self._packages[pkg.name] = pkg

    def get(self, name: str) -> InternalPackage | None:
        return self._packages.get(name)

    def resolve_dependencies(self, name: str, visited: set[str] | None = None) -> list[str]:
        """Rekurzivně vyřeší tranzitivní závislosti."""
        if visited is None:
            visited = set()
        if name in visited:
            return []
        visited.add(name)
        pkg = self._packages.get(name)
        if not pkg:
            return [f"[MISSING: {name}]"]
        result: list[str] = list(pkg.dependencies)
        for dep in pkg.dependencies:
            result.extend(self.resolve_dependencies(dep, visited))
        return list(dict.fromkeys(result))  # dedup, zachovej pořadí

    def impact_analysis(self, name: str) -> list[str]:
        """Co by bylo ovlivněno breaking change v `name`?"""
        affected: list[str] = []
        for pkg_name, pkg in self._packages.items():
            if name in pkg.dependencies:
                affected.append(pkg_name)
        return affected

    def summary_table(self) -> str:
        lines = [
            f"{'Balíček':<30} {'Verze':<12} {'Závislosti':<25} {'Vlastníci'}",
            "-" * 85,
        ]
        for pkg in sorted(self._packages.values(), key=lambda p: p.name):
            deps = ", ".join(pkg.dependencies[:2]) or "—"
            owners = ", ".join(pkg.owners[:2]) or "—"
            dep_mark = " ⚠" if pkg.deprecated else ""
            lines.append(
                f"{pkg.name + dep_mark:<30} {str(pkg.version):<12} {deps:<25} {owners}"
            )
        return "\n".join(lines)


# ── Namespace Package simulace ────────────────────────────────────────────────

class NamespacePackageDemo:
    """Demonstruje princip namespace packages bez fyzického filesystemu."""

    def __init__(self) -> None:
        self._modules: dict[str, dict[str, Any]] = {}

    def register_module(self, dotted_path: str, exports: dict[str, Any]) -> None:
        """Simuluje importovatelný modul v namespace."""
        self._modules[dotted_path] = exports

    def import_from(self, dotted_path: str, name: str) -> Any:
        """Simuluje `from dotted_path import name`."""
        module = self._modules.get(dotted_path)
        if module is None:
            raise ImportError(f"Modul '{dotted_path}' neexistuje")
        if name not in module:
            raise ImportError(f"Nelze importovat '{name}' z '{dotted_path}'")
        return module[name]

    def show_tree(self) -> None:
        """Zobrazí strom namespace packages."""
        tree: dict[str, Any] = {}
        for path in self._modules:
            parts = path.split(".")
            node = tree
            for part in parts:
                node = node.setdefault(part, {})

        def print_tree(d: dict, indent: int = 0) -> None:
            for key, val in sorted(d.items()):
                prefix = "  " * indent + ("├── " if indent > 0 else "")
                has_exports = not isinstance(val, dict) or not val
                print(f"{prefix}{key}{'/' if not has_exports else ''}")
                if isinstance(val, dict) and val:
                    print_tree(val, indent + 1)

        print("mycompany/  (namespace package — bez __init__.py)")
        print_tree(tree.get("mycompany", {}), indent=1)


# ── Deprecation dekorátor ─────────────────────────────────────────────────────

F = TypeVar("F", bound=Callable[..., Any])

_deprecation_call_counts: dict[str, int] = {}


def deprecated(
    reason: str,
    since: str,
    replacement: str = "",
    removal: str | None = None,
) -> Callable[[F], F]:
    """Označí funkci jako deprecated s informativní zprávou."""

    def decorator(fn: F) -> F:
        msg = f"{fn.__qualname__}() je deprecated od verze {since}: {reason}."
        if replacement:
            msg += f" Použijte místo toho {replacement}()."
        if removal:
            msg += f" Bude odstraněno v {removal}."

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _deprecation_call_counts[fn.__qualname__] = (
                _deprecation_call_counts.get(fn.__qualname__, 0) + 1
            )
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return fn(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


# ── Compatibility Matrix ──────────────────────────────────────────────────────

class CompatibilityMatrix:
    """Sleduje kompatibilitu verzí mezi interními knihovnami."""

    def __init__(self) -> None:
        # (consumer, provider) -> (min_version, max_version, tested_with)
        self._matrix: dict[tuple[str, str], dict[str, str]] = {}

    def add_tested(
        self,
        consumer: str,
        provider: str,
        min_version: str,
        max_version: str,
        tested_with: str,
    ) -> None:
        self._matrix[(consumer, provider)] = {
            "min": min_version,
            "max": max_version,
            "tested_with": tested_with,
        }

    def check(self, consumer: str, provider: str, version: str) -> dict[str, Any]:
        key = (consumer, provider)
        entry = self._matrix.get(key)
        if not entry:
            return {"compatible": None, "reason": "Netestováno"}
        v = Version.parse(version)
        v_min = Version.parse(entry["min"])
        v_max = Version.parse(entry["max"])
        compatible = v_min <= v <= v_max
        return {
            "compatible": compatible,
            "tested_range": f"{entry['min']}–{entry['max']}",
            "last_tested_with": entry["tested_with"],
            "reason": "OK" if compatible else f"Mimo rozsah {entry['min']}–{entry['max']}",
        }

    def to_table(self) -> str:
        if not self._matrix:
            return "(prázdná matice)"
        lines = [f"{'Consumer':<20} {'Provider':<20} {'Rozsah':<20} {'Testováno s'}"]
        lines.append("-" * 75)
        for (consumer, provider), info in sorted(self._matrix.items()):
            lines.append(
                f"{consumer:<20} {provider:<20} "
                f"{info['min']}–{info['max']:<14} {info['tested_with']}"
            )
        return "\n".join(lines)


# ── Selective CI simulace ─────────────────────────────────────────────────────

COMPONENT_OWNERS: dict[str, str] = {
    "libs/common":    "platform-team",
    "libs/auth":      "security-team",
    "libs/types":     "platform-team",
    "services/api":   "api-team",
    "services/worker":"data-team",
    "tools":          "platform-team",
}

COMPONENT_DEPS: dict[str, list[str]] = {
    "services/api":    ["libs/common", "libs/auth", "libs/types"],
    "services/worker": ["libs/common", "libs/types"],
    "libs/auth":       ["libs/common"],
}


def find_affected_components(changed_files: list[str]) -> set[str]:
    """Zjistí, které komponenty jsou ovlivněny změněnými soubory."""
    directly_changed: set[str] = set()
    for f in changed_files:
        for component in COMPONENT_OWNERS:
            if f.startswith(component):
                directly_changed.add(component)

    # Tranzitivní závislosti — co závisí na změněné komponentě?
    all_affected = set(directly_changed)
    for changed in list(directly_changed):
        for consumer, deps in COMPONENT_DEPS.items():
            if changed in deps:
                all_affected.add(consumer)

    return all_affected


# ── Demo funkce ───────────────────────────────────────────────────────────────

def demo_semver() -> None:
    print("=== DEMO 1: Semantic Versioning ===\n")

    v1 = Version.parse("1.2.3")
    v2 = Version.parse("1.3.0")
    v3 = Version.parse("2.0.0")

    print(f"  Verze: {v1}, {v2}, {v3}")
    print(f"  {v1} → bump_minor → {v1.bump_minor()}")
    print(f"  {v1} → bump_major → {v1.bump_major()}")
    print(f"  {v1} kompatibilní s {v2}? {v2.is_compatible(v1)}")
    print(f"  {v1} → {v3} je breaking change? {v1.breaking_change(v3)}")
    print(f"  Řazení: {sorted([v3, v1, v2])}")
    print()


def demo_internal_registry() -> None:
    print("=== DEMO 2: Registr interních knihoven ===\n")

    registry = InternalRegistry()

    packages = [
        InternalPackage(
            "mycompany-common", Version.parse("3.1.0"),
            "Sdílené utility (retry, config, logging)",
            owners=["platform-team"],
        ),
        InternalPackage(
            "mycompany-auth", Version.parse("2.0.0"),
            "JWT autentizace a autorizace",
            owners=["security-team"],
            dependencies=["mycompany-common"],
        ),
        InternalPackage(
            "mycompany-types", Version.parse("1.5.2"),
            "Sdílené TypedDict a Protocol definice",
            owners=["platform-team"],
        ),
        InternalPackage(
            "mycompany-db", Version.parse("4.0.0"),
            "Databázové utility a connection pooling",
            owners=["platform-team"],
            dependencies=["mycompany-common"],
        ),
        InternalPackage(
            "mycompany-api-client", Version.parse("1.2.0"),
            "HTTP klient pro interní API",
            owners=["api-team"],
            dependencies=["mycompany-common", "mycompany-auth"],
        ),
        InternalPackage(
            "mycompany-old-utils", Version.parse("0.9.0"),
            "Zastaralé utility — DEPRECATED",
            owners=["platform-team"],
            deprecated=True,
            deprecation_message="Použijte mycompany-common v3.0+",
        ),
    ]

    for pkg in packages:
        registry.register(pkg)

    print(registry.summary_table())
    print()

    print("  Tranzitivní závislosti pro 'mycompany-api-client':")
    deps = registry.resolve_dependencies("mycompany-api-client")
    for d in deps:
        print(f"    ↳ {d}")

    print("\n  Impact analysis — co závisí na 'mycompany-common'?")
    affected = registry.impact_analysis("mycompany-common")
    for a in affected:
        print(f"    → {a}")
    print()


def demo_namespace_packages() -> None:
    print("=== DEMO 3: Namespace Packages ===\n")

    ns = NamespacePackageDemo()

    # Simulace struktury balíčků
    ns.register_module("mycompany.common.retry", {
        "retry": lambda fn, n=3: fn,
        "exponential_backoff": lambda base=1.0: base,
    })
    ns.register_module("mycompany.common.config", {
        "load_config": lambda path: {},
        "Settings": type("Settings", (), {}),
    })
    ns.register_module("mycompany.auth.jwt", {
        "encode_token": lambda payload: "jwt.token.here",
        "decode_token": lambda token: {},
    })
    ns.register_module("mycompany.api.main", {
        "create_app": lambda: "FastAPI app",
        "router": object(),
    })
    ns.register_module("mycompany.worker.tasks", {
        "process_order": lambda order_id: None,
        "send_notification": lambda user_id, msg: None,
    })

    print("  Struktura namespace packages:")
    ns.show_tree()

    retry_fn = ns.import_from("mycompany.common.retry", "retry")
    encode = ns.import_from("mycompany.auth.jwt", "encode_token")
    print(f"\n  Import retry: {retry_fn}")
    print(f"  encode_token('payload'): {encode('payload')}")
    print()


def demo_deprecation() -> None:
    print("=== DEMO 4: Deprecation Pattern ===\n")

    @deprecated(
        reason="Neefektivní implementace, O(n²) složitost",
        since="2.0.0",
        replacement="fast_search",
        removal="3.0.0",
    )
    def slow_search(items: list[str], query: str) -> list[str]:
        return [i for i in items if query in i]

    def fast_search(items: list[str], query: str) -> list[str]:
        return [i for i in items if query in i]

    # Zachytíme DeprecationWarning
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = slow_search(["alpha", "beta", "gamma", "alpha2"], "alpha")
        result2 = slow_search(["a", "b", "c"], "b")

    print(f"  slow_search vrátil: {result}")
    print(f"  Počet volání slow_search: {_deprecation_call_counts.get('slow_search', 0)}")
    if caught:
        print(f"  Varování: {caught[0].message}")
    print()


def demo_compatibility_matrix() -> None:
    print("=== DEMO 5: Compatibility Matrix ===\n")

    matrix = CompatibilityMatrix()
    matrix.add_tested("mycompany-api-client", "mycompany-auth", "1.5.0", "2.1.0", "2.0.0")
    matrix.add_tested("mycompany-api-client", "mycompany-common", "2.0.0", "3.2.0", "3.1.0")
    matrix.add_tested("mycompany-worker", "mycompany-common", "2.5.0", "3.2.0", "3.0.0")
    matrix.add_tested("mycompany-worker", "mycompany-db", "3.0.0", "4.1.0", "4.0.0")

    print(matrix.to_table())
    print()

    checks = [
        ("mycompany-api-client", "mycompany-auth", "1.8.0"),
        ("mycompany-api-client", "mycompany-auth", "2.5.0"),    # mimo rozsah
        ("mycompany-worker",     "mycompany-common", "3.1.0"),
        ("mycompany-worker",     "mycompany-db",     "5.0.0"),  # mimo rozsah
    ]

    print("  Kontroly kompatibility:")
    for consumer, provider, version in checks:
        result = matrix.check(consumer, provider, version)
        mark = "✓" if result["compatible"] else "✗" if result["compatible"] is False else "?"
        print(
            f"  {mark} {consumer} → {provider} v{version}: "
            f"{result['reason']}"
        )
    print()


def demo_selective_ci() -> None:
    print("=== DEMO 6: Selective CI/CD ===\n")

    changesets = [
        (
            "Oprava v common utility",
            ["libs/common/retry.py", "libs/common/tests/test_retry.py"],
        ),
        (
            "Nový endpoint v API",
            ["services/api/routes/orders.py", "services/api/tests/test_orders.py"],
        ),
        (
            "Bezpečnostní patch v auth",
            ["libs/auth/jwt.py"],
        ),
        (
            "Velká refaktorizace common + worker",
            ["libs/common/config.py", "services/worker/tasks.py"],
        ),
    ]

    for description, changed in changesets:
        affected = find_affected_components(changed)
        owners = {COMPONENT_OWNERS.get(c, "?") for c in affected}
        print(f"  Změna: {description}")
        print(f"    Soubory:       {', '.join(changed)}")
        print(f"    Ovlivněno:     {', '.join(sorted(affected)) or '—'}")
        print(f"    Notifikovat:   {', '.join(sorted(owners))}")
        print()


def demo_final_showcase() -> None:
    """Závěrečné shrnutí — ukázka celé pipeline."""
    print("=" * 60)
    print("  ZÁVĚREČNÁ UKÁZKA: Monorepo Lifecycle")
    print("=" * 60)

    # 1. Nová verze common
    old_v = Version.parse("3.1.0")
    new_v = old_v.bump_minor()
    print(f"\n  1. Release common: {old_v} → {new_v}")
    print(f"     Breaking change: {old_v.breaking_change(new_v)}")
    print(f"     Zpětně kompatibilní: {new_v.is_compatible(old_v)}")

    # 2. Impact analysis
    registry = InternalRegistry()
    registry.register(InternalPackage("mycompany-common", new_v, "", owners=["platform-team"]))
    registry.register(InternalPackage("mycompany-auth", Version.parse("2.0.0"), "",
                                       dependencies=["mycompany-common"]))
    registry.register(InternalPackage("mycompany-api-client", Version.parse("1.2.0"), "",
                                       dependencies=["mycompany-common", "mycompany-auth"]))

    affected = registry.impact_analysis("mycompany-common")
    print(f"\n  2. Ovlivněné komponenty: {affected}")

    # 3. Selective CI
    changed_files = [f"libs/common/v{new_v}/utils.py"]
    ci_affected = find_affected_components(changed_files)
    print(f"\n  3. CI/CD spustí testy pro: {sorted(ci_affected)}")

    print(f"\n  Release {new_v} proběhl úspěšně!\n")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    demo_semver()
    demo_internal_registry()
    demo_namespace_packages()
    demo_deprecation()
    demo_compatibility_matrix()
    demo_selective_ci()
    demo_final_showcase()

    print("=" * 60)
    print("  Lekce 130 dokončena.")
    print("  Kurz Python: Zero to Hero — KOMPLETNÍ!")
    print("  130 lekcí, stovky konceptů, jeden jazyk.")
    print("  Nyní jste připraveni budovat cokoliv.")
    print("=" * 60)


if __name__ == "__main__":
    main()

```
