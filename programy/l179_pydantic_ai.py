"""Lekce 179 — Pydantic AI: type-safe agentní framework.
Spuštění: uv run --with pydantic-ai l179_pydantic_ai.py
"""

import os
from pydantic import BaseModel, Field
from typing import Optional


class KodAnalyza(BaseModel):
    je_spravny: bool
    slozitost: str = Field(description="O(1)/O(n)/O(n²)/O(n log n)")
    problemy: list[str]
    vylepseni: list[str]
    hodnoceni: int = Field(ge=1, le=10)


def demo_koncepty():
    print("=" * 50)
    print("  🤖 Pydantic AI Demo")
    print("=" * 50)
    print("""
Pydantic AI vs LangChain:
  + Plná type safety (mypy kompatibilní)
  + Dependency injection (deps_type)
  + Nativní async
  + Jednoduší API
  - Menší ekosystém

Klíčové koncepty:
  Agent(model, result_type=T)   → agent s typovaným výstupem
  @agent.tool                   → nástroj (funkce k volání)
  RunContext[Deps]               → přístup k závislostem
  agent.run_sync("...")          → synchronní volání
  await agent.run("...")         → async volání
""")


def demo_strukturovany_vystup():
    print("=== Strukturovaný výstup (bez API) ===")

    # Simulace bez skutečného LLM
    def fake_analyze(kod: str) -> KodAnalyza:
        """Simulace AI analýzy kódu."""
        has_loop = "for" in kod or "while" in kod
        has_nested = kod.count("for") > 1
        problemy = []
        if "range(len(" in kod:
            problemy.append("Použij enumerate() místo range(len())")
        if "== None" in kod:
            problemy.append("Použij 'is None' místo '== None'")
        vylepseni = ["Přidej type hints", "Přidej docstring"] if len(problemy) < 2 else []
        return KodAnalyza(
            je_spravny=True,
            slozitost="O(n²)" if has_nested else "O(n)" if has_loop else "O(1)",
            problemy=problemy,
            vylepseni=vylepseni,
            hodnoceni=7 - len(problemy),
        )

    kody = [
        'def suma(lst):\n    total = 0\n    for i in range(len(lst)):\n        total += lst[i]\n    return total',
        'def max_val(lst):\n    return max(lst)',
        'def bubble_sort(arr):\n    for i in range(len(arr)):\n        for j in range(len(arr)-i-1):\n            if arr[j] > arr[j+1]: arr[j], arr[j+1] = arr[j+1], arr[j]',
    ]

    for kod in kody:
        analyza = fake_analyze(kod)
        print(f"\n  Kód: {kod[:50]}...")
        print(f"  Správný: {analyza.je_spravny}, Složitost: {analyza.slozitost}, "
              f"Hodnocení: {analyza.hodnoceni}/10")
        if analyza.problemy:
            print(f"  Problémy: {analyza.problemy}")
        if analyza.vylepseni:
            print(f"  Vylepšení: {analyza.vylepseni}")


def demo_s_api():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("""
=== Pydantic AI se skutečným API ===
  Nastav ANTHROPIC_API_KEY, pak:

    from pydantic_ai import Agent
    from pydantic_ai.models.anthropic import AnthropicModel

    agent = Agent(
        AnthropicModel("claude-haiku-4-5-20251001"),
        result_type=KodAnalyza,
        system_prompt="Analyzuj Python kód.",
    )
    result = agent.run_sync("Analyzuj: def f(x): return x*2")
    print(result.data.hodnoceni)  # → typovaný výsledek!
""")
        return

    try:
        from pydantic_ai import Agent
        from pydantic_ai.models.anthropic import AnthropicModel

        agent = Agent(
            AnthropicModel("claude-haiku-4-5-20251001"),
            result_type=KodAnalyza,
            system_prompt="Analyzuj Python kód a vrať strukturovanou analýzu.",
        )
        result = agent.run_sync("Analyzuj: def secti(a, b): return a + b")
        print(f"\n  Hodnocení: {result.data.hodnoceni}/10")
        print(f"  Složitost: {result.data.slozitost}")
    except ImportError:
        print("  uv add pydantic-ai")


def demo_tools():
    print("\n=== Agent s nástroji (simulace) ===")

    class FakeAgent:
        def __init__(self, tools):
            self.tools = tools

        def run(self, prompt: str) -> str:
            # Jednoduchá simulace: detekuj co agent potřebuje
            if "spusť" in prompt.lower() or "run" in prompt.lower():
                return self.tools["spust_python"]("print('Hello from tool!')")
            elif "najdi" in prompt.lower() or "lekci" in prompt.lower():
                return str(self.tools["najdi_lekci"]("asyncio"))
            return "Nevím jak odpovědět bez nástroje."

    def spust_python(kod: str) -> str:
        import subprocess, sys
        r = subprocess.run([sys.executable, "-c", kod], capture_output=True, text=True, timeout=5)
        return r.stdout or r.stderr

    def najdi_lekci(tema: str) -> list[str]:
        from pathlib import Path
        results = []
        for f in sorted(Path("lekce").glob("[0-9]*.md")):
            try:
                if tema.lower() in f.read_text(encoding="utf-8", errors="ignore").lower():
                    results.append(f.name)
                    if len(results) >= 3: break
            except: pass
        return results

    agent = FakeAgent({"spust_python": spust_python, "najdi_lekci": najdi_lekci})

    for prompt in ["Spusť print('Ahoj!')", "Najdi lekce o asyncio"]:
        result = agent.run(prompt)
        print(f"\n  Prompt: {prompt}")
        print(f"  Výsledek: {result}")


def main():
    demo_koncepty()
    demo_strukturovany_vystup()
    demo_s_api()
    demo_tools()
    print("\n✅ Demo dokončeno!")
    print("Instalace: uv add pydantic-ai")


if __name__ == "__main__":
    main()
