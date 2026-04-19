"""Lekce 129 — Architektonická Rozhodnutí a Komunikace."""

from __future__ import annotations

import datetime
import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any

# ── ADR — Architecture Decision Record ───────────────────────────────────────

class ADRStatus(str, Enum):
    PROPOSED   = "Proposed"
    ACCEPTED   = "Accepted"
    DEPRECATED = "Deprecated"
    SUPERSEDED = "Superseded"


@dataclass
class ADR:
    """Architecture Decision Record — záznam jednoho architektonického rozhodnutí."""

    number: int
    title: str
    status: ADRStatus
    context: str
    decision: str
    consequences_positive: list[str] = field(default_factory=list)
    consequences_negative: list[str] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)
    superseded_by: int | None = None
    date: str = field(default_factory=lambda: datetime.date.today().isoformat())
    authors: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        return f"ADR-{self.number:03d}"

    def to_markdown(self) -> str:
        lines: list[str] = [
            f"# {self.id}: {self.title}",
            "",
            f"**Datum:** {self.date}  ",
            f"**Status:** {self.status.value}  ",
            f"**Autoři:** {', '.join(self.authors) or 'neznámí'}  ",
            f"**Tagy:** {', '.join(self.tags) or '—'}",
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
            lines += ["### Pozitivní", ""]
            for c in self.consequences_positive:
                lines.append(f"- {c}")
            lines.append("")

        if self.consequences_negative:
            lines += ["### Negativní", ""]
            for c in self.consequences_negative:
                lines.append(f"- {c}")
            lines.append("")

        if self.superseded_by:
            lines += [f"> Toto ADR bylo nahrazeno ADR-{self.superseded_by:03d}", ""]

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


class ADRRegistry:
    """Centrální index všech ADR v projektu."""

    def __init__(self) -> None:
        self._records: dict[int, ADR] = {}

    def add(self, adr: ADR) -> None:
        self._records[adr.number] = adr

    def get(self, number: int) -> ADR | None:
        return self._records.get(number)

    def list_by_status(self, status: ADRStatus) -> list[ADR]:
        return [a for a in self._records.values() if a.status == status]

    def search(self, keyword: str) -> list[ADR]:
        kw = keyword.lower()
        return [
            a for a in self._records.values()
            if kw in a.title.lower()
            or kw in a.context.lower()
            or kw in a.decision.lower()
            or any(kw in tag for tag in a.tags)
        ]

    def index(self) -> str:
        """Vrátí markdown index všech ADR."""
        lines = ["# ADR Index", ""]
        for adr in sorted(self._records.values(), key=lambda a: a.number):
            status_icon = {"Proposed": "🔵", "Accepted": "✅", "Deprecated": "⚠️", "Superseded": "🔄"}.get(
                adr.status.value, "❓"
            )
            lines.append(f"- {status_icon} **{adr.id}**: {adr.title} ({adr.date})")
        return "\n".join(lines)


# ── Trade-off Matrix ──────────────────────────────────────────────────────────

@dataclass
class TradeoffCriterion:
    """Kritérium pro hodnocení možností."""

    name: str
    weight: float       # 0.0–1.0; součet všech vah = 1.0
    description: str = ""
    higher_is_better: bool = True


@dataclass
class TradeoffOption:
    """Možnost k hodnocení."""

    name: str
    scores: dict[str, float]    # criterion.name → 0.0–10.0
    notes: str = ""


class TradeoffMatrix:
    """Framework pro strukturované srovnání možností."""

    def __init__(self, title: str, criteria: list[TradeoffCriterion]) -> None:
        self.title = title
        self.criteria = criteria
        self.options: list[TradeoffOption] = []

        total_weight = sum(c.weight for c in criteria)
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(
                f"Součet vah musí být 1.0, je {total_weight:.3f}"
            )

    def add_option(self, option: TradeoffOption) -> None:
        self.options.append(option)

    def weighted_score(self, option: TradeoffOption) -> float:
        total = 0.0
        for c in self.criteria:
            score = option.scores.get(c.name, 0.0)
            total += score * c.weight
        return round(total, 2)

    def rank(self) -> list[tuple[str, float]]:
        ranked = [(opt.name, self.weighted_score(opt)) for opt in self.options]
        return sorted(ranked, key=lambda x: x[1], reverse=True)

    def to_table(self) -> str:
        criterion_names = [c.name[:12] for c in self.criteria]
        header = ["Možnost"] + criterion_names + ["Celkem"]

        rows: list[list[str]] = []
        for opt in self.options:
            row = [opt.name]
            for c in self.criteria:
                row.append(f"{opt.scores.get(c.name, 0):.1f}")
            row.append(f"{self.weighted_score(opt):.2f}")
            rows.append(row)

        widths = [
            max(len(str(r[i])) for r in [header] + rows)
            for i in range(len(header))
        ]
        fmt = " | ".join(f"{{:<{w}}}" for w in widths)
        sep = "-+-".join("-" * w for w in widths)

        lines = [
            f"\n{self.title}",
            "Váhy: " + ", ".join(f"{c.name}={c.weight:.2f}" for c in self.criteria),
            fmt.format(*header),
            sep,
        ] + [fmt.format(*row) for row in rows]

        return "\n".join(lines)


# ── RFC ───────────────────────────────────────────────────────────────────────

@dataclass
class RFCComment:
    author: str
    text: str
    date: str = field(default_factory=lambda: datetime.date.today().isoformat())
    reaction: str = ""    # "+1" | "-1" | "?"


@dataclass
class RFC:
    """Request for Comments — návrh změny ke schválení komunitou."""

    number: int
    title: str
    author: str
    status: str    # Draft | Open | Accepted | Rejected | Withdrawn
    problem_statement: str
    proposed_solution: str
    alternatives: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    deadline: str = ""
    comments: list[RFCComment] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.date.today().isoformat())

    @property
    def id(self) -> str:
        return f"RFC-{self.number:03d}"

    def add_comment(self, author: str, text: str, reaction: str = "") -> None:
        self.comments.append(RFCComment(author=author, text=text, reaction=reaction))

    def sentiment(self) -> dict[str, int]:
        counts: dict[str, int] = {"+1": 0, "-1": 0, "?": 0, "": 0}
        for c in self.comments:
            counts[c.reaction] = counts.get(c.reaction, 0) + 1
        return counts

    def to_markdown(self) -> str:
        lines: list[str] = [
            f"# {self.id}: {self.title}",
            "",
            f"- **Autor:** {self.author}",
            f"- **Status:** {self.status}",
            f"- **Vytvořeno:** {self.created_at}",
            f"- **Deadline:** {self.deadline or 'není stanoven'}",
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
            sent = self.sentiment()
            lines += [
                "## Komentáře",
                f"(+1: {sent['+1']}, -1: {sent['-1']}, ?: {sent['?']})",
                "",
            ]
            for c in self.comments:
                reaction = f" [{c.reaction}]" if c.reaction else ""
                lines.append(f"**{c.author}** ({c.date}){reaction}: {c.text}")
                lines.append("")

        return "\n".join(lines)


# ── Due Diligence Checklist ───────────────────────────────────────────────────

@dataclass
class ChecklistItem:
    category: str
    question: str
    critical: bool = False
    answer: str = ""
    passed: bool | None = None

    def status_str(self) -> str:
        if self.passed is None:
            return "[ ] NEZODPOVĚZENO"
        return "[✓] SPLNĚNO" if self.passed else "[✗] NESPLNĚNO" + (" ⚠️ KRITICKÉ" if self.critical else "")


class TechnicalDueDiligence:
    """Checklist pro technické hodnocení projektu."""

    STANDARD_CHECKLIST: list[ChecklistItem] = [
        ChecklistItem("Bezpečnost", "Jsou závislosti pravidelně aktualizovány?", critical=True),
        ChecklistItem("Bezpečnost", "Jsou secrets spravovány mimo kód?", critical=True),
        ChecklistItem("Bezpečnost", "Existuje audit log?"),
        ChecklistItem("Bezpečnost", "Je provozováno HTTPS/TLS?", critical=True),
        ChecklistItem("Spolehlivost", "Pokrytí testy > 70%?"),
        ChecklistItem("Spolehlivost", "Existuje CI/CD pipeline?"),
        ChecklistItem("Spolehlivost", "Je definovaný SLA/SLO?"),
        ChecklistItem("Spolehlivost", "Existuje disaster recovery plán?", critical=True),
        ChecklistItem("Škálování", "Proběhl zátěžový test?"),
        ChecklistItem("Škálování", "Jsou identifikovány bottlenecky?"),
        ChecklistItem("Udržovatelnost", "Existuje dokumentace architektury?"),
        ChecklistItem("Udržovatelnost", "Je kód reviewován?"),
        ChecklistItem("Udržovatelnost", "Jsou zastaralé závislosti sledovány?"),
        ChecklistItem("Operace", "Existuje monitoring a alerting?", critical=True),
        ChecklistItem("Operace", "Jsou logy centralizovány?"),
        ChecklistItem("Operace", "Je definovaný on-call proces?"),
    ]

    def __init__(self) -> None:
        import copy
        self.items: list[ChecklistItem] = copy.deepcopy(self.STANDARD_CHECKLIST)

    def answer(self, question_substr: str, passed: bool, answer: str = "") -> None:
        for item in self.items:
            if question_substr.lower() in item.question.lower():
                item.passed = passed
                item.answer = answer
                return
        raise KeyError(f"Otázka obsahující '{question_substr}' nenalezena")

    def score(self) -> dict[str, Any]:
        answered = [i for i in self.items if i.passed is not None]
        passed = [i for i in answered if i.passed]
        critical_failed = [i for i in self.items if i.critical and i.passed is False]
        return {
            "total": len(self.items),
            "answered": len(answered),
            "passed": len(passed),
            "score_pct": round(len(passed) / len(self.items) * 100, 1),
            "critical_failed": len(critical_failed),
            "recommendation": (
                "BLOKUJÍCÍ PROBLÉMY" if critical_failed
                else "PODMÍNĚNĚ SCHVÁLENO" if len(passed) / len(self.items) < 0.75
                else "SCHVÁLENO"
            ),
        }

    def report(self) -> str:
        lines = ["=== TECHNICKÉ DUE DILIGENCE ===", ""]
        categories: dict[str, list[ChecklistItem]] = {}
        for item in self.items:
            categories.setdefault(item.category, []).append(item)

        for cat, items in categories.items():
            lines.append(f"## {cat}")
            for item in items:
                crit = " [KRITICKÉ]" if item.critical else ""
                lines.append(f"  {item.status_str()}{crit}")
                lines.append(f"  Q: {item.question}")
                if item.answer:
                    lines.append(f"  A: {item.answer}")
            lines.append("")

        s = self.score()
        lines += [
            "=== VÝSLEDEK ===",
            f"  Splněno: {s['passed']}/{s['total']} ({s['score_pct']}%)",
            f"  Kritické selhání: {s['critical_failed']}x",
            f"  Doporučení: {s['recommendation']}",
        ]
        return "\n".join(lines)


# ── Demo funkce ───────────────────────────────────────────────────────────────

def demo_adr() -> None:
    print("=== DEMO 1: ADR — Architecture Decision Records ===\n")

    adr1 = ADR(
        number=1,
        title="Použití PostgreSQL jako primární databáze",
        status=ADRStatus.ACCEPTED,
        context=(
            "Potřebujeme persistentní úložiště pro uživatelská data a transakce. "
            "Tým má silné zkušenosti s relačními databázemi."
        ),
        decision="Použijeme PostgreSQL 16 jako primární databázový systém.",
        consequences_positive=[
            "ACID transakce — garance konzistence",
            "JSON podpora pro semi-strukturovaná data",
            "Silný ekosystém Python driverů (asyncpg, psycopg3)",
        ],
        consequences_negative=[
            "Horizontální škálování složitější než u NoSQL",
            "Potřeba správy schémat a migrací",
        ],
        alternatives=[
            "MongoDB — flexibilnější schema, horší ACID",
            "MySQL — zralejší ale méně features",
            "SQLite — jen pro dev/test",
        ],
        authors=["Jana Nováková", "Petr Svoboda"],
        tags=["databáze", "infrastruktura"],
    )

    adr2 = ADR(
        number=2,
        title="Async API s FastAPI",
        status=ADRStatus.ACCEPTED,
        context="Potřebujeme REST API schopné obsluhovat 1000+ RPS s nízkými latencemi.",
        decision="Použijeme FastAPI s Uvicorn pro async HTTP server.",
        consequences_positive=[
            "Automatická OpenAPI dokumentace",
            "Native async/await podpora",
            "Rychlá iterace díky Pydantic validaci",
        ],
        consequences_negative=[
            "Strmější křivka učení než Flask",
            "Async kód přináší debugging složitost",
        ],
        alternatives=["Flask + Gunicorn", "Django REST Framework", "Litestar"],
        authors=["Martin Dvořák"],
        tags=["api", "backend", "async"],
    )

    registry = ADRRegistry()
    registry.add(adr1)
    registry.add(adr2)

    # Zobraz první ADR
    print(adr1.to_markdown()[:600] + "\n...[zkráceno]\n")

    # Index
    print(registry.index())
    print()

    # Vyhledávání
    results = registry.search("databáze")
    print(f"  Hledání 'databáze': {len(results)} nalezeno")
    for r in results:
        print(f"    - {r.id}: {r.title}")
    print()


def demo_tradeoff_matrix() -> None:
    print("=== DEMO 2: Trade-off Matrix — výběr message brokeru ===\n")

    criteria = [
        TradeoffCriterion("Výkon", weight=0.30, description="Throughput a latence"),
        TradeoffCriterion("Složitost", weight=0.20, description="Ops náročnost"),
        TradeoffCriterion("Ekosystém", weight=0.20, description="Python podpora, tooling"),
        TradeoffCriterion("Škálování", weight=0.20, description="Horizontální škálovatelnost"),
        TradeoffCriterion("Cena", weight=0.10, description="Licence a provozní náklady"),
    ]

    matrix = TradeoffMatrix("Výběr message brokeru", criteria)

    matrix.add_option(TradeoffOption(
        "Redis Streams",
        scores={"Výkon": 8.5, "Složitost": 8.0, "Ekosystém": 7.5, "Škálování": 6.5, "Cena": 9.0},
        notes="Nejjednodušší nasazení, dobré pro <10k msg/s",
    ))
    matrix.add_option(TradeoffOption(
        "Apache Kafka",
        scores={"Výkon": 9.5, "Složitost": 4.0, "Ekosystém": 9.0, "Škálování": 9.5, "Cena": 6.0},
        notes="Ideální pro high-throughput, ale těžká operace",
    ))
    matrix.add_option(TradeoffOption(
        "RabbitMQ",
        scores={"Výkon": 7.5, "Složitost": 6.5, "Ekosystém": 8.0, "Škálování": 7.0, "Cena": 8.5},
        notes="Vyvážený kompromis, AMQP standard",
    ))
    matrix.add_option(TradeoffOption(
        "NATS",
        scores={"Výkon": 9.0, "Složitost": 7.5, "Ekosystém": 6.5, "Škálování": 8.5, "Cena": 9.5},
        notes="Moderní, cloudnative, nižší adopce v Pythonu",
    ))

    print(matrix.to_table())
    print("\n  Ranking (nejlepší → nejhorší):")
    for i, (name, score) in enumerate(matrix.rank(), 1):
        print(f"  {i}. {name}: {score:.2f}/10")
    print()


def demo_rfc() -> None:
    print("=== DEMO 3: RFC — Request for Comments ===\n")

    rfc = RFC(
        number=7,
        title="Zavedení Rate Limiting do API",
        author="Ondřej Marek",
        status="Open",
        problem_statement=(
            "Naše API nemá žádný rate limiting. Jeden uživatel může odeslat "
            "neomezené množství požadavků a degradovat službu pro ostatní."
        ),
        proposed_solution=(
            "Implementujeme token bucket algoritmus v Redis. "
            "Limity: 100 req/min pro free tier, 1000 req/min pro pro tier."
        ),
        alternatives=[
            "Sliding window counter — přesnější, ale složitější",
            "Nginx rate limiting — infrastrukturní řešení bez Redis",
            "API Gateway (Kong) — komplexní řešení",
        ],
        open_questions=[
            "Jak komunikovat limity uživatelům (HTTP hlavičky)?",
            "Jak zacházet s burst traffic — měkký vs. tvrdý limit?",
            "Potřebujeme per-endpoint limity?",
        ],
        deadline="2024-03-01",
    )

    rfc.add_comment("Jana N.", "Souhlasím s Redis přístupem. Token bucket je standard.", "+1")
    rfc.add_comment("Petr S.", "Zvažte Nginx variantu — Redis přidává závislost.", "?")
    rfc.add_comment("Martin D.", "Burst traffic otázka je klíčová — navrhuju 20% burst.", "+1")

    print(rfc.to_markdown()[:800] + "\n...[zkráceno]")
    sent = rfc.sentiment()
    print(f"\n  Sentiment: +1={sent['+1']}, -1={sent['-1']}, ?={sent['?']}\n")


def demo_due_diligence() -> None:
    print("=== DEMO 4: Technické Due Diligence ===\n")

    dd = TechnicalDueDiligence()

    # Simulace odpovědí
    dd.answer("závislosti pravidelně", passed=True, answer="Dependabot + měsíční review")
    dd.answer("secrets spravovány", passed=True, answer="HashiCorp Vault + env vars")
    dd.answer("audit log", passed=False, answer="Neplánováno v Q1")
    dd.answer("HTTPS/TLS", passed=True, answer="Let's Encrypt, automaticky obnovováno")
    dd.answer("Pokrytí testy", passed=False, answer="Aktuálně 58%, cíl Q2 je 80%")
    dd.answer("CI/CD pipeline", passed=True, answer="GitHub Actions + ArgoCD")
    dd.answer("SLA/SLO", passed=True, answer="99.5% availability SLO definováno")
    dd.answer("disaster recovery", passed=True, answer="Nightly backup + RTO 4h definováno")
    dd.answer("monitoring a alerting", passed=True, answer="Grafana + PagerDuty")
    dd.answer("logy centralizovány", passed=True, answer="Elastic Stack")

    print(dd.report())
    print()


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    demo_adr()
    demo_tradeoff_matrix()
    demo_rfc()
    demo_due_diligence()
    print("Hotovo! Všechny demo sekce lekce 129 proběhly úspěšně.")


if __name__ == "__main__":
    main()
