"""Lekce 178 — LangChain: LLM aplikační framework.
Spuštění: uv run --with langchain,langchain-anthropic l178_langchain.py
"""

import os


def demo_koncepty():
    print("=" * 50)
    print("  🔗 LangChain Demo")
    print("=" * 50)
    print("""
LangChain základní stavební bloky:
  LLM/ChatModel  → volání AI modelu
  PromptTemplate → šablony zpráv
  OutputParser   → parsování výstupu
  Chain (|)      → propojení bloků (LCEL)
  Tool           → nástroj pro agenta
  Agent          → LLM + nástroje + smyčka
  Memory         → paměť konverzace
  VectorStore    → databáze embeddings (RAG)
  Retriever      → vyhledávání v VectorStore

LCEL (LangChain Expression Language):
  chain = prompt | llm | parser
  result = chain.invoke({"vstup": "..."})
  for chunk in chain.stream({"vstup": "..."}): ...
""")


def demo_bez_api():
    """Demo bez API klíče — ukáže strukturu kódu."""
    print("\n=== LangChain kód (bez API klíče) ===")

    # Simulace chain bez skutečného LLM
    class FakeLLM:
        def invoke(self, messages):
            posledni = messages[-1]["content"] if isinstance(messages[-1], dict) else str(messages[-1])
            return f"[Simulovaná odpověď na: {posledni[:50]}]"

        def stream(self, messages):
            text = self.invoke(messages)
            for word in text.split():
                yield word + " "

    class FakeParser:
        def invoke(self, text): return text.strip()

    class PromptTemplate:
        def __init__(self, messages):
            self.messages = messages
        def invoke(self, data):
            return [{"role": r, "content": c.format(**data)} for r, c in self.messages]

    # Chain simulace
    prompt = PromptTemplate([
        ("system", "Jsi Python expert. Odpovídej v češtině."),
        ("human", "{otazka}"),
    ])
    llm = FakeLLM()
    parser = FakeParser()

    def chain_invoke(vstup):
        messages = prompt.invoke(vstup)
        response = llm.invoke(messages)
        return parser.invoke(response)

    print("\n  Simulovaný chain:")
    for otazka in ["Co je GIL?", "Jak funguje asyncio?", "Vysvětli decorátory"]:
        odpoved = chain_invoke({"otazka": otazka})
        print(f"  Q: {otazka}")
        print(f"  A: {odpoved}\n")


def demo_s_api():
    """Demo se skutečným API (pokud je dostupný)."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n=== LangChain se skutečným API ===")
        print("  Nastav ANTHROPIC_API_KEY pro spuštění se skutečným LLM")
        print("""
  Kód:
    from langchain_anthropic import ChatAnthropic
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    llm = ChatAnthropic(model="claude-haiku-4-5-20251001")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Jsi Python expert."),
        ("human", "{otazka}"),
    ])
    chain = prompt | llm | StrOutputParser()
    print(chain.invoke({"otazka": "Co je GIL?"}))
""")
        return

    try:
        from langchain_anthropic import ChatAnthropic
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        llm = ChatAnthropic(model="claude-haiku-4-5-20251001", max_tokens=200)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Jsi Python expert. Odpovídej stručně v češtině."),
            ("human", "{otazka}"),
        ])
        chain = prompt | llm | StrOutputParser()
        odpoved = chain.invoke({"otazka": "Co je GIL v Pythonu? (1 věta)"})
        print(f"\n  Claude odpověděl: {odpoved}")
    except ImportError:
        print("  uv add langchain langchain-anthropic")


def demo_rag_architektura():
    print("\n=== RAG architektura ===")
    print("""
  Dokumenty → Chunky → Embeddings → VectorStore
                                         ↓
  Dotaz → Embedding → Similarity search → Top-K chunky
                                              ↓
  Prompt = "Kontext: {chunky}\\nOtázka: {dotaz}" → LLM → Odpověď

  Implementace:
    loader = DirectoryLoader("lekce/", glob="*.md")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
    vectorstore = Chroma.from_documents(chunky, embedding)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    rag_chain = (
        {"context": retriever | format_docs, "dotaz": RunnablePassthrough()}
        | rag_prompt | llm | StrOutputParser()
    )
    print(rag_chain.invoke("Jak funguje asyncio?"))
""")


def main():
    demo_koncepty()
    demo_bez_api()
    demo_s_api()
    demo_rag_architektura()
    print("\n✅ Demo dokončeno!")
    print("Instalace: uv add langchain langchain-anthropic langchain-community chromadb")


if __name__ == "__main__":
    main()
