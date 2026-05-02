# Lekce 179: Pydantic AI — agentní framework

Pydantic AI je nový (2024) framework od tvůrců Pydantic. Type-safe agenti, dependency injection, strukturované výstupy.

---

## 🚀 Instalace

```bash
uv add pydantic-ai
```

---

## 🤖 Základní agent

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic import BaseModel


model = AnthropicModel("claude-haiku-4-5-20251001")

# Jednoduchý agent
agent = Agent(
    model,
    system_prompt="Jsi Python expert. Odpovídej stručně v češtině.",
)

result = agent.run_sync("Co je GIL?")
print(result.data)
print(f"Tokeny: {result.usage()}")
```

---

## 📦 Strukturované výstupy

```python
from pydantic import BaseModel, Field
from typing import Optional


class KodAnalyza(BaseModel):
    """Analýza Python kódu."""
    je_spravny: bool = Field(description="Je kód syntakticky správný?")
    slozitost: str = Field(description="O(1)/O(n)/O(n²)/O(n log n)")
    problemy: list[str] = Field(description="Nalezené problémy")
    vylepseni: list[str] = Field(description="Navrhovaná vylepšení")
    hodnoceni: int = Field(description="Hodnocení 1-10", ge=1, le=10)


analyzer = Agent(
    model,
    result_type=KodAnalyza,
    system_prompt="Analyzuj Python kód a vrať strukturovanou analýzu.",
)

kod = """
def najdi_max(seznam):
    max_val = seznam[0]
    for item in seznam:
        if item > max_val:
            max_val = item
    return max_val
"""

analyza = analyzer.run_sync(f"Analyzuj tento kód:\n{kod}")
print(f"Správný: {analyza.data.je_spravny}")
print(f"Složitost: {analyza.data.slozitost}")
print(f"Problémy: {analyza.data.problemy}")
print(f"Hodnocení: {analyza.data.hodnoceni}/10")
```

---

## 🔧 Nástroje (Tools)

```python
from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
import httpx


@dataclass
class AgentDependencies:
    """Závislosti injektované do agenta."""
    http_client: httpx.AsyncClient
    db_url: str
    max_vysledku: int = 5


agent_s_nastroji = Agent(
    model,
    deps_type=AgentDependencies,
    system_prompt="Jsi asistent pro vyhledávání Python dokumentace.",
)


@agent_s_nastroji.tool
async def vyhledej_v_docs(ctx: RunContext[AgentDependencies], dotaz: str) -> str:
    """Vyhledá v Python dokumentaci."""
    url = f"https://docs.python.org/3/search.html?q={dotaz}"
    response = await ctx.deps.http_client.get(url, timeout=10)
    # Zjednodušená parsování
    return f"Výsledky pro '{dotaz}': {url}"


@agent_s_nastroji.tool
def spust_kod(ctx: RunContext[AgentDependencies], kod: str) -> str:
    """Spustí bezpečný Python kód."""
    import subprocess, sys
    result = subprocess.run(
        [sys.executable, "-c", kod],
        capture_output=True, text=True, timeout=5,
        env={"PYTHONPATH": ""}
    )
    return result.stdout or result.stderr or "(žádný výstup)"


@agent_s_nastroji.tool
def najdi_lekci(ctx: RunContext[AgentDependencies], tema: str) -> list[str]:
    """Vyhledá relevantní lekce kurzu."""
    from pathlib import Path
    results = []
    for f in sorted(Path("lekce").glob("[0-9]*.md")):
        try:
            if tema.lower() in f.read_text(encoding="utf-8", errors="ignore").lower():
                results.append(f.name)
                if len(results) >= ctx.deps.max_vysledku:
                    break
        except Exception:
            continue
    return results


async def demo_agent():
    async with httpx.AsyncClient() as client:
        deps = AgentDependencies(
            http_client=client,
            db_url="postgresql://localhost/kurz",
        )
        result = await agent_s_nastroji.run(
            "Najdi lekce o asyncio a spusť ukázkový async kód",
            deps=deps,
        )
        print(result.data)
```

---

## 🔄 Multi-agent systémy

```python
from pydantic_ai import Agent


# Agent 1: Analyzátor
analyzator = Agent(
    model,
    result_type=KodAnalyza,
    system_prompt="Analyzuj kód a identifikuj problémy.",
)

# Agent 2: Opravovač
opravovac = Agent(
    model,
    result_type=str,
    system_prompt="Oprav problémy v Python kódu. Vrať jen opravený kód.",
)

# Agent 3: Dokumentátor
dokumentator = Agent(
    model,
    result_type=str,
    system_prompt="Přidej docstringy a komentáře do kódu.",
)


async def pipeline_kod(kod: str) -> str:
    """Orchestrace: analýza → oprava → dokumentace."""
    # Krok 1: Analýza
    analyza = await analyzator.run(f"Analyzuj:\n{kod}")
    if analyza.data.hodnoceni >= 8:
        print("Kód je dobrý, přeskakuji opravu")
        opraveny = kod
    else:
        # Krok 2: Oprava
        prompt_opravy = f"Oprav tyto problémy v kódu:\n{analyza.data.problemy}\n\nKód:\n{kod}"
        opraven = await opravovac.run(prompt_opravy)
        opraveny = opraven.data

    # Krok 3: Dokumentace
    zdokumentovany = await dokumentator.run(f"Zdokumentuj:\n{opraveny}")
    return zdokumentovany.data
```

---

## 🎯 Pydantic AI vs LangChain

| | Pydantic AI | LangChain |
|---|-------------|-----------|
| Type safety | ✅ plná | částečná |
| Dependency injection | ✅ nativní | ruční |
| Async | ✅ nativní | smíšené |
| Simplicita | ✅ přímočaré | komplexnější |
| Ekosystém | roste | ✅ velký |
| Testovatelnost | ✅ snazší | obtížnější |
| Structured outputs | ✅ Pydantic | schémata |

---

## ✏️ Cvičení

1. Postav **code review agenta** — přijme PR diff a vrátí strukturovanou zpětnou vazbu.
2. Implementuj **self-healing pipeline** — agent detekuje chybu a automaticky ji opraví.
3. Napiš **testovací agenty** — jeden generuje testy, druhý je spouští a opravuje.
4. Postav **RAG agenta** nad kurzem — závislosti obsahují vektorovou DB a embeddings.
5. Porovnej Pydantic AI s přímým Claude API (lekce 100) na stejné úloze.
