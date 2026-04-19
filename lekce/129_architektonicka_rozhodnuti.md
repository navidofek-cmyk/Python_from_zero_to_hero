# Lekce 129 — Architektonická Rozhodnutí a Komunikace

Technická rozhodnutí mají dlouhodobé dopady. Tato lekce se věnuje strukturované dokumentaci
a komunikaci architektonických voleb — ADR, RFC, trade-off analýza a technické due diligence.

---

## 1. Proč dokumentovat architektonická rozhodnutí?

Bez dokumentace:
- Nový vývojář neví, proč byl použit Redis místo PostgreSQL
- Tým opakuje debaty o již rozhodnutých věcech
- Refaktoring ignoruje původní kontext a omezení
- Technický dluh se hromadí bez viditelnosti

S ADR (Architecture Decision Records):
- Historie rozhodnutí je přístupná všem
- Kontext a alternativy jsou zdokumentovány
- Nástupci mohou revidovat zastaralá rozhodnutí

---

## 2. ADR — Architecture Decision Record

ADR je krátký dokument zachycující jedno architektonické rozhodnutí.
Formát Michaela Nygarda (nejrozšířenější):

```
# ADR-001: Použití PostgreSQL jako primární databáze

## Status
Accepted

## Kontext
Potřebujeme persistentní úložiště pro uživatelská data a transakce.
Tým má zkušenosti s relačními databázemi. Očekávané množství: ~1M záznamů.

## Rozhodnutí
Použijeme PostgreSQL 15.

## Důsledky
### Pozitivní
- ACID transakce
- Podpora JSON a full-text search
- Dobrá podpora v ekosystému Python

### Negativní
- Horizontální škálování je složitější než u NoSQL
- Potřeba správy schématu (migrace)
```

---

## 3. Python generátor ADR šablon

```python
from dataclasses import dataclass, field
from enum import Enum
import datetime

class ADRStatus(str, Enum):
    PROPOSED   = "Proposed"
    ACCEPTED   = "Accepted"
    DEPRECATED = "Deprecated"
    SUPERSEDED = "Superseded"

@dataclass
class ADR:
    number: int
    title: str
    status: ADRStatus
    context: str
    decision: str
    consequences_positive: list[str] = field(default_factory=list)
    consequences_negative: list[str] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)
    superseded_by: int | None = None
    date: str = field(
        default_factory=lambda: datetime.date.today().isoformat()
    )
    authors: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [
            f"# ADR-{self.number:03d}: {self.title}",
            "",
            f"**Datum:** {self.date}  ",
            f"**Status:** {self.status.value}  ",
            f"**Autoři:** {', '.join(self.authors) or 'neznámí'}",
            "",
            "## Kontext",
            "",
            self.context,
            "",
            "## Rozhodnutí",
            "",
            self.decision,
            "",
        ]

        if self.alternatives:
            lines += ["## Zvažované alternativy", ""]
            for alt in self.alternatives:
                lines.append(f"- {alt}")
            lines.append("")

        lines += ["## Důsledky", ""]
        if self.consequences_positive:
            lines.append("### Pozitivní")
            for c in self.consequences_positive:
                lines.append(f"- {c}")
            lines.append("")

        if self.consequences_negative:
            lines.append("### Negativní")
            for c in self.consequences_negative:
                lines.append(f"- {c}")
            lines.append("")

        if self.superseded_by:
            lines.append(f"> Nahrazeno ADR-{self.superseded_by:03d}")

        return "\n".join(lines)
```

---

## 4. Trade-off Analýza Framework

Architektonická rozhodnutí jsou vždy kompromisem. Framework pro strukturovanou analýzu:

```python
@dataclass
class TradeoffCriterion:
    name: str
    weight: float          # 0.0 – 1.0, součet všech = 1.0
    description: str = ""

@dataclass
class TradeoffOption:
    name: str
    scores: dict[str, float]  # criterion_name → score (0–10)
    notes: str = ""

class TradeoffMatrix:
    def __init__(self, criteria: list[TradeoffCriterion]) -> None:
        self.criteria = criteria
        self.options: list[TradeoffOption] = []

    def add_option(self, option: TradeoffOption) -> None:
        self.options.append(option)

    def weighted_score(self, option: TradeoffOption) -> float:
        total = 0.0
        for criterion in self.criteria:
            score = option.scores.get(criterion.name, 0.0)
            total += score * criterion.weight
        return round(total, 2)

    def rank(self) -> list[tuple[str, float]]:
        ranked = [
            (opt.name, self.weighted_score(opt))
            for opt in self.options
        ]
        return sorted(ranked, key=lambda x: x[1], reverse=True)

    def to_table(self) -> str:
        header = ["Možnost"] + [c.name for c in self.criteria] + ["Celkem"]
        rows = []
        for opt in self.options:
            row = [opt.name]
            for c in self.criteria:
                row.append(str(opt.scores.get(c.name, 0)))
            row.append(str(self.weighted_score(opt)))
            rows.append(row)
        # Formátování tabulky
        widths = [max(len(str(r[i])) for r in [header] + rows) for i in range(len(header))]
        fmt = " | ".join(f"{{:<{w}}}" for w in widths)
        sep = "-+-".join("-" * w for w in widths)
        lines = [fmt.format(*header), sep]
        lines += [fmt.format(*row) for row in rows]
        return "\n".join(lines)
```

---

## 5. RFC Proces (Request for Comments)

RFC je formálnější než ADR — navrhuje změny před implementací a sbírá zpětnou vazbu.

```python
@dataclass
class RFC:
    number: int
    title: str
    author: str
    status: str          # "Draft" | "Open" | "Accepted" | "Rejected" | "Withdrawn"
    problem_statement: str
    proposed_solution: str
    alternatives: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    deadline: str = ""
    comments: list[dict] = field(default_factory=list)

    def add_comment(self, author: str, text: str) -> None:
        self.comments.append({
            "author": author,
            "text": text,
            "date": datetime.date.today().isoformat(),
        })

    def to_markdown(self) -> str:
        lines = [
            f"# RFC-{self.number:03d}: {self.title}",
            "",
            f"- **Autor:** {self.author}",
            f"- **Status:** {self.status}",
            f"- **Deadline:** {self.deadline or 'není'}",
            "",
            "## Problém",
            "",
            self.problem_statement,
            "",
            "## Navrhované řešení",
            "",
            self.proposed_solution,
            "",
        ]
        if self.alternatives:
            lines += ["## Alternativy", ""]
            for alt in self.alternatives:
                lines.append(f"- {alt}")
            lines.append("")
        if self.open_questions:
            lines += ["## Otevřené otázky", ""]
            for q in self.open_questions:
                lines.append(f"- [ ] {q}")
            lines.append("")
        if self.comments:
            lines += ["## Komentáře", ""]
            for c in self.comments:
                lines.append(f"**{c['author']}** ({c['date']}): {c['text']}")
                lines.append("")
        return "\n".join(lines)
```

---

## 6. Technické Due Diligence Checklisty

Při hodnocení nové technologie nebo akvizice:

```python
@dataclass
class ChecklistItem:
    category: str
    question: str
    critical: bool = False  # Kritická položka → blokuje schválení
    answer: str = ""
    passed: bool | None = None

class TechnicalDueDiligence:
    STANDARD_CHECKLIST = [
        # Bezpečnost
        ChecklistItem("Bezpečnost", "Jsou závislosti pravidelně aktualizovány?", critical=True),
        ChecklistItem("Bezpečnost", "Existuje proces pro security patching?", critical=True),
        ChecklistItem("Bezpečnost", "Jsou secrets správně spravovány (ne v kódu)?", critical=True),
        # Spolehlivost
        ChecklistItem("Spolehlivost", "Jaká je pokrytost testy (unit + integrační)?"),
        ChecklistItem("Spolehlivost", "Existuje monitoring a alerting?"),
        ChecklistItem("Spolehlivost", "Jak je řešena disaster recovery?", critical=True),
        # Škálování
        ChecklistItem("Škálování", "Jaký je maximální testovaný throughput?"),
        ChecklistItem("Škálování", "Kde jsou bottlenecky?"),
        # Udržovatelnost
        ChecklistItem("Udržovatelnost", "Existuje dokumentace architektury?"),
        ChecklistItem("Udržovatelnost", "Je kód reviewován?"),
        ChecklistItem("Udržovatelnost", "Jaká je úroveň technického dluhu?"),
    ]
    ...
```

---

## 7. DACI Framework pro rozhodování

| Role | Popis | Příklad |
|---|---|---|
| **D**river | Řídí proces rozhodování | Tech Lead |
| **A**pprover | Finální schválení | CTO, Architect |
| **C**ontributor | Přispívá znalostmi | Vývojáři, DevOps |
| **I**nformed | Je informován o výsledku | Product, Marketing |

```python
@dataclass
class DACIDecision:
    title: str
    driver: str
    approvers: list[str]
    contributors: list[str]
    informed: list[str]
    options: list[str]
    recommendation: str
    rationale: str
    deadline: str = ""
```

---

## 8. Kdy použít jaký nástroj

| Situace | Nástroj |
|---|---|
| Retroaktivní záznam rozhodnutí | ADR |
| Navrhovaná změna vyžadující souhlas | RFC |
| Výběr mezi technologiemi | Trade-off Matrix |
| Hodnocení projektu/akvizice | Due Diligence |
| Komplexní rozhodnutí s více stakeholders | DACI |

---

## Shrnutí

- **ADR** dokumentuje jedno rozhodnutí s kontextem, alternativami a důsledky.
- **Trade-off Matrix** kvantifikuje srovnání možností dle vážených kritérií.
- **RFC** sbírá zpětnou vazbu před implementací velké změny.
- **Due Diligence** strukturuje hodnocení technické kvality systému.
- **DACI** jasně definuje role v rozhodovacím procesu.
- Dokumentace rozhodnutí šetří čas budoucím vývojářům i vašemu budoucímu já.

## Cvičení

1. Napište ADR pro rozhodnutí, které jste v poslední době přijali (např. výběr frameworku).
2. Vytvořte Trade-off Matrix pro výběr message brokeru (Redis Streams vs. Kafka vs. RabbitMQ).
3. Implementuj `ADRRegistry` — centrální index všech ADR s vyhledáváním a exportem do HTML.
4. Přidej do `TradeoffMatrix` vizualizaci jako radar chart (ASCII art).
5. Navrhněte RFC pro zavedení nového API v existující službě.
