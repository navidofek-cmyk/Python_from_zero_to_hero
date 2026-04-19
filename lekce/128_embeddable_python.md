# Lekce 128 — Embeddable Python a Plugin Systémy

Python není jen samostatný jazyk — dá se vložit jako scripting vrstva do jiných aplikací,
nebo naopak Python aplikace mohou být rozšiřovány pluginy. V této lekci se naučíme
dynamicky načítat kód, bezpečně spouštět skripty a budovat plugin architektury.

---

## 1. Proč embeddable Python?

Mnoho aplikací potřebuje, aby uživatelé mohli přizpůsobit chování bez restartu nebo
recompilace. Python je ideální scripting jazyk díky čitelnosti a rozsáhlé stdlib.

Příklady použití:
- **Grafické editory** (Blender, GIMP) — Python makra
- **Hry** (Civilization, EVE Online) — herní logika v Pythonu
- **Business aplikace** — uživatelsky definované transformace dat
- **CI/CD nástroje** — pluginy a hooks
- **Datové platformy** — custom UDF (user-defined functions)

---

## 2. `exec()` a bezpečné spouštění kódu

### Základní exec()

```python
# NEBEZPEČNÉ — globální namespace
code = "print('hello')"
exec(code)

# Bezpečnější — oddělený namespace
namespace: dict = {}
exec("x = 42\nresult = x * 2", namespace)
print(namespace["result"])  # 84
```

### Omezení přístupu (sandbox myšlenka)

```python
def safe_exec(
    code: str,
    allowed_builtins: list[str] | None = None,
    context: dict | None = None,
) -> dict:
    """
    Spustí kód s omezenými builtins.
    Není 100% bezpečné (nenahrazuje RestrictedPython),
    ale výrazně omezuje přístup k nebezpečným funkcím.
    """
    if allowed_builtins is None:
        allowed_builtins = ["print", "len", "range", "int", "float", "str", "list",
                            "dict", "set", "tuple", "sum", "min", "max", "abs",
                            "sorted", "enumerate", "zip", "map", "filter"]

    safe_builtins = {name: __builtins__[name]
                     for name in allowed_builtins
                     if name in __builtins__}

    namespace = {"__builtins__": safe_builtins}
    if context:
        namespace.update(context)

    exec(compile(code, "<sandbox>", "exec"), namespace)
    return {k: v for k, v in namespace.items() if not k.startswith("__")}
```

### RestrictedPython myšlenka

Skutečný sandbox by potřeboval AST transformaci:

```python
import ast

class SecurityVisitor(ast.NodeVisitor):
    """Detekuje nebezpečné AST uzly."""
    BANNED_NAMES = {"__import__", "eval", "exec", "open", "compile",
                    "__builtins__", "globals", "locals", "vars", "dir"}

    def __init__(self) -> None:
        self.violations: list[str] = []

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in self.BANNED_NAMES:
            self.violations.append(f"Zakázané jméno: {node.id} (řádek {node.lineno})")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr.startswith("__"):
            self.violations.append(
                f"Zakázaný atribut: {node.attr} (řádek {node.lineno})"
            )
        self.generic_visit(node)

def validate_code(source: str) -> list[str]:
    """Vrátí seznam bezpečnostních porušení v kódu."""
    try:
        tree = ast.parse(source)
        visitor = SecurityVisitor()
        visitor.visit(tree)
        return visitor.violations
    except SyntaxError as e:
        return [f"Syntaktická chyba: {e}"]
```

---

## 3. `importlib` — dynamické načítání modulů

```python
import importlib
import importlib.util
import sys
from pathlib import Path

def load_module_from_file(name: str, path: Path):
    """Načte Python modul ze souboru bez manipulace sys.path."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Nelze načíst modul z: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def reload_module(name: str):
    """Hot-reload existujícího modulu."""
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    raise ImportError(f"Modul {name} není načten")
```

---

## 4. Plugin systém — kompletní implementace

### Rozhraní pluginu (Protocol)

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Plugin(Protocol):
    name: str
    version: str
    description: str

    def execute(self, data: dict) -> dict:
        ...

    def validate(self, data: dict) -> bool:
        ...
```

### Plugin Registry

```python
from dataclasses import dataclass, field
import inspect

@dataclass
class PluginMetadata:
    name: str
    version: str
    description: str
    author: str = ""
    tags: list[str] = field(default_factory=list)

class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, tuple[PluginMetadata, type]] = {}

    def register(self, plugin_cls: type) -> type:
        """Dekorátor pro registraci pluginu."""
        meta = PluginMetadata(
            name=getattr(plugin_cls, "name", plugin_cls.__name__),
            version=getattr(plugin_cls, "version", "0.1.0"),
            description=getattr(plugin_cls, "description", ""),
            author=getattr(plugin_cls, "author", ""),
            tags=getattr(plugin_cls, "tags", []),
        )
        self._plugins[meta.name] = (meta, plugin_cls)
        return plugin_cls

    def get(self, name: str) -> type | None:
        entry = self._plugins.get(name)
        return entry[1] if entry else None

    def list_plugins(self) -> list[PluginMetadata]:
        return [meta for meta, _ in self._plugins.values()]

    def execute(self, name: str, data: dict) -> dict:
        plugin_cls = self.get(name)
        if not plugin_cls:
            raise KeyError(f"Plugin '{name}' nenalezen")
        plugin = plugin_cls()
        if not plugin.validate(data):
            raise ValueError(f"Plugin '{name}': neplatná vstupní data")
        return plugin.execute(data)
```

### Příklad pluginů

```python
registry = PluginRegistry()

@registry.register
class UppercasePlugin:
    name = "uppercase"
    version = "1.0.0"
    description = "Převede text na velká písmena"
    tags = ["text", "transform"]

    def validate(self, data: dict) -> bool:
        return "text" in data

    def execute(self, data: dict) -> dict:
        return {"text": data["text"].upper(), "plugin": self.name}

@registry.register
class WordCountPlugin:
    name = "word_count"
    version = "1.0.0"
    description = "Spočítá slova v textu"
    tags = ["text", "analysis"]

    def validate(self, data: dict) -> bool:
        return "text" in data

    def execute(self, data: dict) -> dict:
        words = data["text"].split()
        return {"count": len(words), "unique": len(set(words)), "plugin": self.name}

# Použití
result = registry.execute("word_count", {"text": "hello world hello python"})
# {"count": 4, "unique": 3, "plugin": "word_count"}
```

---

## 5. Namespace packages (PEP 420)

Namespace packages umožňují rozložit balíček přes více adresářů bez `__init__.py`.

```
myapp/
    plugins/          ← namespace package (bez __init__.py)
        builtin/
            __init__.py
            text_plugin.py
        community/    ← přidáno třetí stranou
            __init__.py
            ml_plugin.py
```

```python
# Dynamické discovery pluginů dle namespace
import pkgutil
import importlib

def discover_plugins(namespace: str) -> list:
    """Najde všechny moduly v daném namespace."""
    plugins = []
    package = importlib.import_module(namespace)
    for _, name, _ in pkgutil.walk_packages(
        path=package.__path__,
        prefix=package.__name__ + ".",
    ):
        module = importlib.import_module(name)
        plugins.append(module)
    return plugins
```

---

## 6. Entry Points (setuptools)

Standardní Python mechanismus pro pluginy — plugin registruje sebe přes `pyproject.toml`:

```toml
[project.entry-points."myapp.plugins"]
my_plugin = "my_package.plugin:MyPlugin"
```

```python
from importlib.metadata import entry_points

def load_entry_point_plugins(group: str) -> list:
    """Načte pluginy registrované přes entry points."""
    plugins = []
    for ep in entry_points(group=group):
        plugin_cls = ep.load()
        plugins.append(plugin_cls)
    return plugins
```

---

## 7. Srovnání přístupů

| Přístup | Izolace | Výkon | Složitost | Použití |
|---|---|---|---|---|
| `exec()` + namespace | Nízká | Vysoký | Nízká | Jednoduché skripty |
| RestrictedPython | Střední | Střední | Vysoká | Untrusted code |
| importlib | Žádná | Vysoký | Nízká | Důvěryhodné pluginy |
| subprocess | Vysoká | Nízký | Střední | Izolované procesy |
| Entry points | Žádná | Vysoký | Střední | Distribuované pluginy |

---

## Shrnutí

- `exec()` s omezeným namespace omezuje přístup, ale není 100% bezpečný.
- AST analýza kódu před spuštěním přidá vrstvu ochrany.
- `importlib.util.spec_from_file_location()` umožňuje načíst plugin ze souboru.
- Plugin Pattern = Protocol + Registry + Discovery → flexibilní, rozšiřitelný systém.
- Entry Points jsou standardním mechanismem pro distribuované pluginy.

## Cvičení

1. Implementuj `PluginPipeline` — složení více pluginů za sebou (výstup jednoho je vstup dalšího).
2. Přidej do `PluginRegistry` podporu verzování — `get("myplugin", min_version="1.2.0")`.
3. Vytvoř `FileWatcher`, který sleduje adresář s pluginy a automaticky je načítá při změně.
4. Implementuj `SandboxedPlugin` — plugin běžící v izolovaném subprocess.
5. Přidej do `SecurityVisitor` detekci importu nebezpečných modulů (`os`, `subprocess`, `socket`).
