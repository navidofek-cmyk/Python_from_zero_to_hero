"""Lekce 128 — Embeddable Python a Plugin Systémy."""

from __future__ import annotations

import ast
import importlib
import importlib.util
import sys
import tempfile
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

# ── Bezpečný exec() ───────────────────────────────────────────────────────────

SAFE_BUILTINS_LIST: list[str] = [
    "print", "len", "range", "int", "float", "str", "bool",
    "list", "dict", "set", "tuple", "sum", "min", "max", "abs",
    "sorted", "reversed", "enumerate", "zip", "map", "filter",
    "round", "isinstance", "type", "repr", "any", "all",
]


def safe_exec(
    code: str,
    context: dict[str, Any] | None = None,
    allowed_builtins: list[str] | None = None,
) -> dict[str, Any]:
    """
    Spustí kód s omezeným přístupem k builtins.
    Vrátí výsledný namespace (bez dunder klíčů).
    """
    builtins_list = allowed_builtins or SAFE_BUILTINS_LIST
    import builtins as _builtins
    all_builtins = vars(_builtins)
    safe_builtins = {name: all_builtins[name] for name in builtins_list if name in all_builtins}

    namespace: dict[str, Any] = {"__builtins__": safe_builtins}
    if context:
        namespace.update(context)

    exec(compile(code, "<sandbox>", "exec"), namespace)
    return {k: v for k, v in namespace.items() if not k.startswith("__")}


# ── AST Security Visitor ──────────────────────────────────────────────────────

BANNED_NAMES: frozenset[str] = frozenset({
    "__import__", "eval", "exec", "open", "compile",
    "__builtins__", "globals", "locals", "vars", "dir",
    "breakpoint", "input",
})

BANNED_MODULES: frozenset[str] = frozenset({
    "os", "sys", "subprocess", "socket", "shutil", "pathlib",
    "importlib", "ctypes", "pickle", "shelve",
})


class SecurityVisitor(ast.NodeVisitor):
    """Detekuje nebezpečné AST uzly v kódu."""

    def __init__(self) -> None:
        self.violations: list[str] = []

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in BANNED_NAMES:
            self.violations.append(
                f"Zakázané jméno '{node.id}' (řádek {node.lineno})"
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr.startswith("__") and node.attr.endswith("__"):
            self.violations.append(
                f"Zakázaný dunder atribut '{node.attr}' (řádek {node.lineno})"
            )
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root in BANNED_MODULES:
                self.violations.append(
                    f"Zakázaný import '{alias.name}' (řádek {node.lineno})"
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            root = node.module.split(".")[0]
            if root in BANNED_MODULES:
                self.violations.append(
                    f"Zakázaný import z '{node.module}' (řádek {node.lineno})"
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


def safe_eval_expr(expression: str, context: dict[str, Any] | None = None) -> Any:
    """Bezpečně vyhodnotí výraz (ne příkaz)."""
    violations = validate_code(expression)
    if violations:
        raise ValueError(f"Bezpečnostní porušení: {violations}")
    import builtins as _builtins
    all_builtins = vars(_builtins)
    safe_builtins = {n: all_builtins[n] for n in SAFE_BUILTINS_LIST if n in all_builtins}
    env: dict[str, Any] = {"__builtins__": safe_builtins}
    if context:
        env.update(context)
    return eval(compile(expression, "<expr>", "eval"), env)


# ── Dynamické načítání modulů ─────────────────────────────────────────────────

def load_module_from_file(name: str, path: Path) -> Any:
    """Načte Python modul ze souboru."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Nelze načíst modul z: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def load_module_from_string(name: str, source: str) -> Any:
    """Načte modul z řetězce zdrojového kódu (přes dočasný soubor)."""
    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w", delete=False, encoding="utf-8"
    ) as f:
        f.write(source)
        tmp_path = Path(f.name)
    try:
        module = load_module_from_file(name, tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)
    return module


# ── Plugin Protocol a Registry ────────────────────────────────────────────────

@runtime_checkable
class Plugin(Protocol):
    """Rozhraní, které musí každý plugin implementovat."""

    name: str
    version: str
    description: str

    def validate(self, data: dict[str, Any]) -> bool: ...
    def execute(self, data: dict[str, Any]) -> dict[str, Any]: ...


@dataclass
class PluginMetadata:
    name: str
    version: str
    description: str
    author: str = ""
    tags: list[str] = field(default_factory=list)


class PluginRegistry:
    """Registr pluginů s dekorátorovou registrací."""

    def __init__(self) -> None:
        self._plugins: dict[str, tuple[PluginMetadata, type]] = {}

    def register(self, plugin_cls: type) -> type:
        """Dekorátor pro registraci pluginu."""
        meta = PluginMetadata(
            name=getattr(plugin_cls, "name", plugin_cls.__name__),
            version=getattr(plugin_cls, "version", "0.1.0"),
            description=getattr(plugin_cls, "description", ""),
            author=getattr(plugin_cls, "author", "neznámý"),
            tags=getattr(plugin_cls, "tags", []),
        )
        self._plugins[meta.name] = (meta, plugin_cls)
        return plugin_cls

    def get(self, name: str) -> type | None:
        entry = self._plugins.get(name)
        return entry[1] if entry else None

    def list_plugins(self) -> list[PluginMetadata]:
        return [meta for meta, _ in self._plugins.values()]

    def execute(self, name: str, data: dict[str, Any]) -> dict[str, Any]:
        plugin_cls = self.get(name)
        if not plugin_cls:
            raise KeyError(f"Plugin '{name}' nenalezen. Dostupné: {list(self._plugins)}")
        plugin = plugin_cls()
        if not plugin.validate(data):
            raise ValueError(f"Plugin '{name}': neplatná vstupní data: {data}")
        return plugin.execute(data)

    def pipeline(self, plugin_names: list[str], data: dict[str, Any]) -> dict[str, Any]:
        """Spustí pluginy za sebou — výstup jednoho je vstup dalšího."""
        result = data
        for name in plugin_names:
            result = self.execute(name, result)
        return result


# ── Konkrétní pluginy ─────────────────────────────────────────────────────────

registry = PluginRegistry()


@registry.register
class UppercasePlugin:
    name = "uppercase"
    version = "1.0.0"
    description = "Převede text na velká písmena"
    author = "demo"
    tags = ["text", "transform"]

    def validate(self, data: dict[str, Any]) -> bool:
        return "text" in data and isinstance(data["text"], str)

    def execute(self, data: dict[str, Any]) -> dict[str, Any]:
        return {**data, "text": data["text"].upper()}


@registry.register
class WordCountPlugin:
    name = "word_count"
    version = "1.2.0"
    description = "Spočítá slova a přidá statistiky"
    author = "demo"
    tags = ["text", "analysis"]

    def validate(self, data: dict[str, Any]) -> bool:
        return "text" in data and isinstance(data["text"], str)

    def execute(self, data: dict[str, Any]) -> dict[str, Any]:
        words = data["text"].split()
        freq: dict[str, int] = {}
        for w in words:
            freq[w.lower()] = freq.get(w.lower(), 0) + 1
        top3 = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:3]
        return {
            **data,
            "word_count": len(words),
            "unique_words": len(freq),
            "top_words": [w for w, _ in top3],
        }


@registry.register
class TrimPlugin:
    name = "trim"
    version = "1.0.0"
    description = "Ořízne bílé znaky a normalizuje mezery"
    author = "demo"
    tags = ["text", "clean"]

    def validate(self, data: dict[str, Any]) -> bool:
        return "text" in data

    def execute(self, data: dict[str, Any]) -> dict[str, Any]:
        import re
        cleaned = re.sub(r"\s+", " ", data["text"].strip())
        return {**data, "text": cleaned}


@registry.register
class MathPlugin:
    name = "math_eval"
    version = "1.0.0"
    description = "Bezpečně vyhodnotí matematický výraz"
    author = "demo"
    tags = ["math", "eval"]

    def validate(self, data: dict[str, Any]) -> bool:
        return "expression" in data and isinstance(data["expression"], str)

    def execute(self, data: dict[str, Any]) -> dict[str, Any]:
        expr = data["expression"]
        try:
            result = safe_eval_expr(expr, context=data.get("variables", {}))
            return {**data, "result": result, "error": None}
        except Exception as e:
            return {**data, "result": None, "error": str(e)}


# ── Demo funkce ───────────────────────────────────────────────────────────────

def demo_safe_exec() -> None:
    print("=== DEMO 1: Bezpečný exec() ===")

    scripts = [
        ("Fibonacci", textwrap.dedent("""
            def fib(n):
                a, b = 0, 1
                result = []
                for _ in range(n):
                    result.append(a)
                    a, b = b, a + b
                return result
            output = fib(8)
        """)),
        ("Součet čísel", "total = sum(range(1, 101))"),
        ("Filtrace", "evens = list(filter(lambda x: x % 2 == 0, range(20)))"),
    ]

    for name, code in scripts:
        ns = safe_exec(code.strip())
        keys = [k for k in ns if not k.startswith("_") and k != "output"]
        result_key = "output" if "output" in ns else (keys[0] if keys else None)
        val = ns.get(result_key) if result_key else "—"
        print(f"  {name}: {repr(val)[:60]}")
    print()


def demo_ast_security() -> None:
    print("=== DEMO 2: AST Security Visitor ===")

    snippets = [
        ("Bezpečný kód", "result = sum(range(10))"),
        ("Pokus o import os", "import os; os.system('ls')"),
        ("Pokus o __import__", "m = __import__('subprocess')"),
        ("Dunder atribut", "x = obj.__class__.__bases__"),
        ("Import z sys", "from sys import argv"),
        ("Více chyb", "import os\nimport socket\nx = __builtins__"),
    ]

    for name, code in snippets:
        violations = validate_code(code)
        status = "BEZPEČNÝ" if not violations else f"PORUŠENÍ ({len(violations)}x)"
        print(f"  [{status}] {name}:")
        for v in violations:
            print(f"    → {v}")
    print()


def demo_dynamic_loading() -> None:
    print("=== DEMO 3: Dynamické načítání modulu ===")

    plugin_source = textwrap.dedent("""
        \"\"\"Dynamicky načtený plugin.\"\"\"

        def greet(name: str) -> str:
            return f"Ahoj, {name}! Jsem dynamicky načtený modul."

        def add(a: int, b: int) -> int:
            return a + b

        VERSION = "2.0.0"
    """)

    module = load_module_from_string("dynamic_plugin", plugin_source)
    print(f"  Verze: {module.VERSION}")
    print(f"  greet: {module.greet('světe')}")
    print(f"  add(7, 8) = {module.add(7, 8)}")

    # Cleanup
    if "dynamic_plugin" in sys.modules:
        del sys.modules["dynamic_plugin"]
    print()


def demo_plugin_registry() -> None:
    print("=== DEMO 4: Plugin Registry ===")

    print("  Registrované pluginy:")
    for meta in registry.list_plugins():
        print(f"    - {meta.name} v{meta.version}: {meta.description}")
    print()

    text_data = {"text": "  hello   world   hello   python   is   great  "}

    result1 = registry.execute("trim", text_data)
    print(f"  Po trim:       '{result1['text']}'")

    result2 = registry.execute("uppercase", result1)
    print(f"  Po uppercase:  '{result2['text']}'")

    result3 = registry.execute("word_count", {"text": result1["text"]})
    print(f"  Počet slov: {result3['word_count']}, unikátní: {result3['unique_words']}")
    print(f"  Top slova: {result3['top_words']}")
    print()


def demo_plugin_pipeline() -> None:
    print("=== DEMO 5: Plugin Pipeline ===")

    data = {"text": "  Python  is   amazing   and   Python   is   fun  "}
    result = registry.pipeline(["trim", "word_count"], data)
    print(f"  Vstup:       '{data['text'][:40]}...'")
    print(f"  Po pipeline: {result['word_count']} slov, top: {result['top_words']}\n")


def demo_math_plugin() -> None:
    print("=== DEMO 6: Bezpečný Math Plugin ===")

    expressions = [
        ("Základní výpočet", "2 ** 10 + sum(range(5))", {}),
        ("S proměnnými", "price * (1 - discount)", {"price": 1000, "discount": 0.2}),
        ("Pokus o nebezpečný kód", "open('/etc/passwd').read()", {}),
        ("Syntaktická chyba", "1 +* 2", {}),
    ]

    for name, expr, variables in expressions:
        data = {"expression": expr}
        if variables:
            data["variables"] = variables  # type: ignore[assignment]
        result = registry.execute("math_eval", data)
        if result["error"]:
            print(f"  {name}: CHYBA — {result['error'][:60]}")
        else:
            print(f"  {name}: {expr} = {result['result']}")
    print()


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    demo_safe_exec()
    demo_ast_security()
    demo_dynamic_loading()
    demo_plugin_registry()
    demo_plugin_pipeline()
    demo_math_plugin()
    print("Hotovo! Všechny demo sekce lekce 128 proběhly úspěšně.")


if __name__ == "__main__":
    main()
