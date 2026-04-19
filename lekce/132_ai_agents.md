# Lekce 132: AI Agenti — LLM + nástroje + smyčka

## Co je AI agent?

AI agent je systém, kde LLM **nejen generuje text**, ale aktivně **rozhoduje, jaké nástroje zavolá** a na základě výsledků **pokračuje v řešení úkolu** — dokud problém nevyřeší.

```
Uživatelský dotaz
       │
       ▼
  ┌─────────┐
  │   LLM   │◀──── výsledek nástroje
  │ (mozek) │
  └────┬────┘
       │ rozhodne: zavolám nástroj X
       ▼
  ┌─────────┐
  │ Nástroj │  (kalkulačka, web, DB, API…)
  └─────────┘
       │
       └──────────► LLM dostane výsledek → další krok
```

Tři stavební kameny agenta:
| Složka | Role | Příklad |
|--------|------|---------|
| LLM | Mozek — plánuje a rozhoduje | Claude, GPT-4 |
| Nástroje (tools) | Ruce — provádí akce | kalkulačka, vyhledávač |
| Smyčka (loop) | Paměť kroků + řízení toku | ReAct, Plan-and-Execute |

---

## ReAct pattern — Reason + Act

ReAct (Yao et al., 2022) střídá dvě fáze:

1. **Thought** — LLM přemýšlí: "Potřebuji vědět X, zavolám nástroj Y."
2. **Action** → spustí nástroj, dostane **Observation**
3. Opakuje, dokud nemá konečnou odpověď.

```
Dotaz: "Kolik je 123 * 456 a jaké je počasí v Praze?"

Thought: Potřebuji vypočítat součin.
Action: kalkulator(123, 456)
Observation: 56088

Thought: Teď potřebuji počasí.
Action: pocasi("Praha")
Observation: 18 °C, oblačno

Thought: Mám vše. Odpovím.
Final Answer: Součin je 56088. V Praze je 18 °C a oblačno.
```

---

## Tool use s Anthropic SDK

Anthropic API umí nativně **tool use** — modelu řekneme, jaké nástroje má k dispozici (JSON schema), a on vrátí strukturovaný požadavek na zavolání.

### Definice nástroje

```python
import anthropic

klient = anthropic.Anthropic()

NASTROJE = [
    {
        "name": "kalkulator",
        "description": "Provede matematický výpočet. Zadej výraz jako string.",
        "input_schema": {
            "type": "object",
            "properties": {
                "vyraz": {
                    "type": "string",
                    "description": "Matematický výraz, např. '2 + 2' nebo '10 * 5'",
                }
            },
            "required": ["vyraz"],
        },
    }
]
```

### Smyčka agenta

```python
def spust_agenta(dotaz: str) -> str:
    zpravy = [{"role": "user", "content": dotaz}]

    while True:
        odpoved = klient.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            tools=NASTROJE,
            messages=zpravy,
        )

        # Přidáme odpověď asistenta do historie
        zpravy.append({"role": "assistant", "content": odpoved.content})

        if odpoved.stop_reason == "end_turn":
            # Hotovo — vrátíme text
            return next(b.text for b in odpoved.content if hasattr(b, "text"))

        if odpoved.stop_reason == "tool_use":
            # Zpracujeme všechna volání nástrojů
            vysledky = []
            for blok in odpoved.content:
                if blok.type == "tool_use":
                    vysledek = zavolej_nastroj(blok.name, blok.input)
                    vysledky.append({
                        "type": "tool_result",
                        "tool_use_id": blok.id,
                        "content": str(vysledek),
                    })

            zpravy.append({"role": "user", "content": vysledky})
```

### Implementace nástroje

```python
import math

def zavolej_nastroj(nazev: str, vstup: dict) -> str:
    if nazev == "kalkulator":
        try:
            # Bezpečnější než eval — použijeme ast.literal_eval nebo omezené eval
            vyraz = vstup["vyraz"]
            vysledek = eval(vyraz, {"__builtins__": {}}, {
                "abs": abs, "round": round, "sqrt": math.sqrt,
            })
            return str(vysledek)
        except Exception as e:
            return f"Chyba: {e}"
    raise ValueError(f"Neznámý nástroj: {nazev}")
```

---

## Více nástrojů najednou

Moderní modely umí volat **více nástrojů paralelně** v jednom kroku:

```python
# Model může vrátit:
# [ToolUseBlock(name="kalkulator", input={"vyraz": "2+2"}),
#  ToolUseBlock(name="pocasi",     input={"mesto": "Praha"})]

for blok in odpoved.content:
    if blok.type == "tool_use":
        vysledky.append(zpracuj(blok))
```

---

## Paměť agenta

Agenti mohou mít různé typy paměti:

| Typ | Popis | Implementace |
|-----|-------|--------------|
| In-context | Seznam zpráv v API volání | `messages` list |
| Krátkodobá | Shrnuto na konci smyčky | Summarization |
| Dlouhodobá | Uloženo mimo kontext | Databáze, RAG |
| Episodická | Záznamy minulých relací | Soubory, vector DB |

---

## Multi-step agent — celý příklad

```python
import anthropic, math, random

klient = anthropic.Anthropic()

NASTROJE = [
    {
        "name": "kalkulator",
        "description": "Spočítá matematický výraz.",
        "input_schema": {
            "type": "object",
            "properties": {"vyraz": {"type": "string"}},
            "required": ["vyraz"],
        },
    },
    {
        "name": "pocasi",
        "description": "Vrátí simulované počasí pro dané město.",
        "input_schema": {
            "type": "object",
            "properties": {"mesto": {"type": "string"}},
            "required": ["mesto"],
        },
    },
]

def zavolej_nastroj(nazev: str, vstup: dict) -> str:
    if nazev == "kalkulator":
        return str(eval(vstup["vyraz"], {"__builtins__": {}}, {"sqrt": math.sqrt}))
    if nazev == "pocasi":
        teploty = {"Praha": 18, "Brno": 16, "Ostrava": 14}
        t = teploty.get(vstup["mesto"], random.randint(10, 25))
        return f"{t} °C, {random.choice(['slunečno', 'oblačno', 'déšť'])}"
    return "Nástroj nenalezen."

def agent(dotaz: str) -> str:
    zpravy = [{"role": "user", "content": dotaz}]
    for _ in range(10):  # max 10 kroků
        r = klient.messages.create(
            model="claude-opus-4-5", max_tokens=1024,
            tools=NASTROJE, messages=zpravy,
        )
        zpravy.append({"role": "assistant", "content": r.content})
        if r.stop_reason == "end_turn":
            return next(b.text for b in r.content if hasattr(b, "text"))
        vysledky = [
            {"type": "tool_result", "tool_use_id": b.id,
             "content": zavolej_nastroj(b.name, b.input)}
            for b in r.content if b.type == "tool_use"
        ]
        zpravy.append({"role": "user", "content": vysledky})
    return "Překročen limit kroků."

print(agent("Kolik je 17 * 23? A jaké je počasí v Brně?"))
```

---

## Kdy použít agenty vs. jednorázové volání

| Situace | Doporučení |
|---------|-----------|
| Jednoduchá odpověď na fakta | Jednorázové volání |
| Potřeba dat z externího zdroje | Tool use (1–2 kroky) |
| Složitý vícekrokový úkol | Agent se smyčkou |
| Autonomní práce bez dozoru | Opatrně — vždy sandbox |

---

## Shrnutí

- **Agent = LLM + nástroje + smyčka** — model sám rozhoduje, kdy a jaký nástroj zavolá
- **ReAct** je nejpopulárnější pattern: Thought → Action → Observation → opakuj
- Anthropic SDK podporuje **nativní tool use** přes `tools` parametr a `stop_reason == "tool_use"`
- Smyčka běží, dokud model nevrátí `stop_reason == "end_turn"`
- Vždy omezte počet kroků (`for _ in range(N)`) a sandboxujte nástroje

---

## Cvičení

1. Přidej do agenta nástroj `preved_meny(castka, z_meny, na_menu)` s pevným kurzem (simulace).
2. Implementuj jednoduchý nástroj `vyhledej_v_textu(text, dotaz)` — agent v něm hledá informace.
3. Uprav smyčku tak, aby logovala každý krok (Thought/Action/Observation) do souboru.
4. Přidej paměť: po každé relaci ulož souhrn konverzace do JSON souboru a načti ho při dalším spuštění.
5. Zkus vytvořit agenta s **paralelním voláním nástrojů** — dej mu dotaz, kde musí zavolat kalkulačku i počasí současně.
