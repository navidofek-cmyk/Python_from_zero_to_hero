"""Lekce 100 — Claude API demo.

Vyžaduje:
    pip install anthropic
    export ANTHROPIC_API_KEY=...
"""

import os
import sys


def main() -> None:
    try:
        from anthropic import Anthropic
    except ImportError:
        print("❌ Nainstaluj: pip install anthropic")
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Nastav ANTHROPIC_API_KEY")
        return

    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",   # nejlevnější
        max_tokens=300,
        messages=[
            {"role": "user", "content": "Vysvětli list comprehension v Pythonu jazykem 10letého dítěte."}
        ],
    )

    print("🤖 Claude říká:\n")
    print(response.content[0].text)
    print(f"\n📊 Použito tokenů: input={response.usage.input_tokens}, output={response.usage.output_tokens}")


if __name__ == "__main__":
    main()
