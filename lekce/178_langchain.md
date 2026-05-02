# Lekce 178: LangChain — LLM aplikační framework

LangChain spojuje LLM s nástroji, pamětí a datovými zdroji. Chains, agents, RAG pipelines.

---

## 🚀 Instalace

```bash
uv add langchain langchain-anthropic langchain-community chromadb
```

---

## 🔗 Základní chain

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


llm = ChatAnthropic(model="claude-haiku-4-5-20251001", max_tokens=500)

# Simple chain: prompt | llm | parser
prompt = ChatPromptTemplate.from_messages([
    ("system", "Jsi expert na Python. Odpovídej stručně v češtině."),
    ("human", "{otazka}"),
])

chain = prompt | llm | StrOutputParser()

odpoved = chain.invoke({"otazka": "Co je GIL v Pythonu?"})
print(odpoved)

# Streaming
for chunk in chain.stream({"otazka": "Vysvětli asyncio"}):
    print(chunk, end="", flush=True)
```

---

## 🗄️ RAG — Retrieval Augmented Generation

```python
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_anthropic import AnthropicEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough


# 1. Načti dokumenty
loader = DirectoryLoader("lekce/", glob="*.md", loader_cls=TextLoader)
dokumenty = loader.load()

# 2. Rozděl na chunky
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
chunky = splitter.split_documents(dokumenty)
print(f"Načteno {len(dokumenty)} dokumentů → {len(chunky)} chunků")

# 3. Vlož do vektorové databáze
vectorstore = Chroma.from_documents(
    chunky,
    embedding=AnthropicEmbeddings(),
    persist_directory="./chroma_db",
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 4. RAG chain
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """Odpovídej na základě kontextu z kurzu Python.
Kontext: {context}
Pokud odpověď není v kontextu, řekni to."""),
    ("human", "{dotaz}"),
])

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

rag_chain = (
    {"context": retriever | format_docs, "dotaz": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)

odpoved = rag_chain.invoke("Jak funguje asyncio v Pythonu?")
print(odpoved)
```

---

## 🤖 Agents — LLM s nástroji

```python
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
import subprocess


@tool
def spust_python(kod: str) -> str:
    """Spustí Python kód a vrátí výstup."""
    result = subprocess.run(
        ["python3", "-c", kod],
        capture_output=True, text=True, timeout=10
    )
    return result.stdout or result.stderr


@tool
def hledej_lekci(dotaz: str) -> str:
    """Vyhledá relevantní lekci v kurzu."""
    # Jednoduchý fulltext search
    from pathlib import Path
    results = []
    for f in Path("lekce").glob("*.md"):
        if dotaz.lower() in f.read_text(encoding="utf-8", errors="ignore").lower():
            results.append(f.name)
            if len(results) >= 3:
                break
    return "\n".join(results) if results else "Nic nenalezeno"


@tool
def vypocitej(vraz: str) -> str:
    """Vyhodnotí matematický výraz."""
    import math
    try:
        return str(eval(vraz, {"__builtins__": {}}, {"math": math}))
    except Exception as e:
        return f"Chyba: {e}"


# Vytvoř agenta
nastroje = [spust_python, hledej_lekci, vypocitej]

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", "Jsi Python lektor. Máš přístup k nástrojům pro spouštění kódu a vyhledávání lekcí."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, nastroje, agent_prompt)
executor = AgentExecutor(agent=agent, tools=nastroje, verbose=True)

vysledek = executor.invoke({"input": "Spusť Python kód, který vypíše prvních 10 Fibonacci čísel"})
print(vysledek["output"])
```

---

## 💾 Paměť (Memory)

```python
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

pamet = {}

def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in pamet:
        pamet[session_id] = ChatMessageHistory()
    return pamet[session_id]


chain_s_pameti = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# Konverzace si pamatuje kontext
chain_s_pameti.invoke(
    {"input": "Mé jméno je Anna."},
    config={"configurable": {"session_id": "session-1"}},
)

odpoved = chain_s_pameti.invoke(
    {"input": "Jak se jmenuji?"},
    config={"configurable": {"session_id": "session-1"}},
)
print(odpoved)  # "Jmenuješ se Anna."
```

---

## 🔄 LCEL — LangChain Expression Language

```python
from langchain_core.runnables import RunnableParallel, RunnableLambda

# Paralelní větve
parallel_chain = RunnableParallel(
    kratke=prompt | llm | StrOutputParser(),
    detailni=(
        ChatPromptTemplate.from_messages([
            ("system", "Odpovídej detailně."),
            ("human", "{otazka}"),
        ]) | llm | StrOutputParser()
    ),
)

vysledky = parallel_chain.invoke({"otazka": "Co je decorator v Pythonu?"})
print("Krátce:", vysledky["kratke"])
print("Detailně:", vysledky["detailni"])

# Podmíněné větvení
def router(input):
    if "kód" in input["otazka"].lower():
        return spust_python.invoke({"kod": "print('demo')"})
    return chain.invoke(input)

adaptivni_chain = RunnableLambda(router)
```

---

## ✏️ Cvičení

1. Postav RAG chatbot nad dokumentací Pythonu — zodpovídá otázky z docs.python.org.
2. Implementuj **multi-hop reasoning** — agent dělá víc kroků pro komplexní otázky.
3. Napiš **custom tool** pro čtení databáze — agent může dělat SQL dotazy.
4. Přidej **streaming** do RAG chainu — odpovědi se zobrazují postupně.
5. Porovnej LangChain vs přímé volání Anthropic API — overhead, flexibilita.
