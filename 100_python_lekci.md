# 130 lekcí pro kompletní zvládnutí Pythonu (od juniora po senior architecta)

Postupný kurz od úplných základů (lekce 1) přes expertní jazykové znalosti (do 100) až po senior/architect úroveň (101–130). Každá lekce = jedno téma, jeden soubor s příklady a cvičeními.

---

## I. Základy jazyka (1–10)

1. **Instalace Pythonu, venv, pip** — interpret, virtuální prostředí, instalace balíčků
2. **REPL, skripty, `if __name__ == "__main__"`** — způsoby spouštění kódu
3. **Proměnné, jména, dynamické typování** — co je objekt, reference, `id()`, `is` vs `==`
4. **Základní typy: int, float, bool, complex** — celá čísla bez limitu, přesnost floatů
5. **Řetězce a f-stringy** — slicing, metody, escape, raw, formátování
6. **Operátory** — aritmetické, logické, bitové, walrus `:=`, ternární výraz
7. **Vstup/výstup: `input()`, `print()`** — argumenty `sep`, `end`, `file`, `flush`
8. **Podmínky: `if`/`elif`/`else`, pravdivostní hodnoty** — truthy/falsy, `and`/`or` short-circuit
9. **Smyčky `for` a `while`** — `range`, `break`, `continue`, `else` u smyček
10. **Komentáře, docstringy, PEP 8, typové hinty základ**

## II. Datové struktury (11–20)

11. **Seznamy (list)** — metody, list comprehension, kopírování
12. **N-tice (tuple)** — neměnnost, packing/unpacking, namedtuple
13. **Slovníky (dict)** — metody, dict comprehension, `setdefault`, `|` merge
14. **Množiny (set, frozenset)** — operace, set comprehension
15. **Řetězce do hloubky** — `str.translate`, `maketrans`, `format_map`, šablony
16. **`bytes`, `bytearray`, `memoryview`** — binární data, kódování
17. **`collections`** — `deque`, `Counter`, `defaultdict`, `OrderedDict`, `ChainMap`
18. **`array`, `heapq`, `bisect`** — efektivní speciální struktury
19. **Slicing pokročile** — kroky, přiřazení do slice, `slice` objekt
20. **Iterace, `enumerate`, `zip`, `reversed`, `sorted` s `key`**

## III. Funkce (21–30)

21. **Definice funkcí, návratové hodnoty, `None`**
22. **Argumenty: poziční, klíčové, defaulty, `*args`, `**kwargs`**
23. **Positional-only `/` a keyword-only `*`** — moderní signatury
24. **Lambda funkce** — kdy ano, kdy ne
25. **Closure a `nonlocal`** — zachycené proměnné
26. **Dekorátory funkcí** — `@wraps`, parametrizované dekorátory
27. **`functools`** — `lru_cache`, `partial`, `reduce`, `singledispatch`
28. **Rekurze a její limity** — `sys.setrecursionlimit`, ocasní rekurze
29. **Funkcionální nástroje** — `map`, `filter`, generátorové výrazy
30. **Anotace typů u funkcí** — `Callable`, `ParamSpec`, `Concatenate`

## IV. OOP (31–42)

31. **Třídy, instance, `__init__`, `self`**
32. **Atributy instance vs třídy** — sdílení, mutable defaults past
33. **Metody: instance, `@classmethod`, `@staticmethod`**
34. **Vlastnosti `@property`, settery, deletery**
35. **Dědičnost, `super()`, MRO, C3 linearizace**
36. **Vícenásobná dědičnost, mixiny**
37. **Dunder metody** — `__repr__`, `__str__`, `__eq__`, `__hash__`, `__lt__`, ...
38. **Operátorové přetížení** — `__add__`, `__getitem__`, `__call__`, `__contains__`
39. **`__slots__`** — paměť a rychlost
40. **Abstraktní třídy `abc`** — `ABC`, `@abstractmethod`
41. **`dataclasses`** — `field`, `frozen`, `slots`, `kw_only`
42. **Enum, IntEnum, StrEnum, Flag**

## V. Pokročilé OOP a metaprogramování (43–50)

43. **Deskriptory** — `__get__`, `__set__`, `__delete__`, jak fungují property
44. **Metatřídy** — `type`, custom metaclass, `__init_subclass__`
45. **`__new__` vs `__init__`** — singletony, immutable třídy
46. **Context managery** — `__enter__`/`__exit__`, `contextlib`, `@contextmanager`
47. **Monkey patching, introspekce** — `getattr`, `setattr`, `dir`, `vars`
48. **`inspect` modul** — signatury, zdrojový kód, frame objekty
49. **Dynamické vytváření tříd** — `type(name, bases, dict)`
50. **Protokoly a `typing.Protocol`** — strukturální typování (duck typing s typy)

## VI. Iterátory, generátory, async (51–60)

51. **Protokol iterátoru** — `__iter__`, `__next__`, `StopIteration`
52. **Generátory s `yield`** — líné vyhodnocení
53. **`yield from`, delegování** — skládání generátorů
54. **Korutiny založené na generátorech** — `send`, `throw`, `close`
55. **`itertools`** — `chain`, `groupby`, `product`, `permutations`, `tee`, `islice`
56. **`async`/`await` základ** — event loop, korutiny
57. **`asyncio`** — `gather`, `create_task`, `wait_for`, `TaskGroup`
58. **Async iterátory a generátory** — `async for`, `async with`
59. **Async knihovny** — `aiohttp`, `httpx`, `aiofiles`
60. **Streamy a fronty v asyncio** — `Queue`, `StreamReader`/`StreamWriter`

## VII. Výjimky a robustnost (61–66)

61. **`try`/`except`/`else`/`finally`** — pravidla pořadí
62. **Hierarchie výjimek, vlastní výjimky**
63. **`raise from`, řetězení výjimek, `__cause__`**
64. **`ExceptionGroup` a `except*`** — Python 3.11+
65. **Kontextové výjimky a logování stack trace**
66. **Defensive programming vs EAFP vs LBYL** — pythonic přístup

## VIII. Moduly, balíčky, distribuce (67–72)

67. **Moduly a `import` systém** — `sys.path`, `__init__.py`, namespace packages
68. **Relativní vs absolutní importy** — kruhové importy a jejich řešení
69. **`importlib`, dynamické importy, lazy import**
70. **Struktura projektu, `pyproject.toml`** — moderní packaging
71. **Build a publikace na PyPI** — `build`, `twine`, `hatch`/`poetry`/`uv`
72. **Entry points, CLI skripty**

## IX. Standardní knihovna — denní chleba (73–82)

73. **`pathlib`** — moderní práce se soubory
74. **Práce se soubory: text, binary, `with open`, kódování**
75. **`os`, `shutil`, `tempfile`, `glob`** — souborový systém a procesy
76. **`subprocess`** — spouštění procesů, pipy, timeout
77. **`datetime`, `zoneinfo`, `time`, `calendar`** — čas a časové zóny
78. **`json`, `csv`, `tomllib`, `configparser`, `pickle`, `shelve`**
79. **`re` — regulární výrazy** — skupiny, lookahead, `re.VERBOSE`
80. **`logging`** — handlery, formátery, konfigurace, vs `print`
81. **`argparse` (a `click`/`typer` jako alternativy)** — CLI
82. **`socket`, `urllib`, `http.client`** — síť na nízké úrovni

## X. Souběžnost a paralelismus (83–87)

83. **Vlákna `threading`** — GIL, kdy mají smysl
84. **Procesy `multiprocessing`** — IPC, pooly, sdílená paměť
85. **`concurrent.futures`** — `ThreadPoolExecutor`, `ProcessPoolExecutor`
86. **Synchronizace** — `Lock`, `Semaphore`, `Event`, `Condition`, `Queue`
87. **Free-threaded Python (3.13+ no-GIL) a `subinterpreters`**

## XI. Testování a kvalita (88–92)

88. **`unittest` a `pytest`** — fixtures, parametrize, marks
89. **Mockování — `unittest.mock`, `monkeypatch`**
90. **Coverage, property-based testing (`hypothesis`)**
91. **Statická analýza** — `mypy`/`pyright`, `ruff`, `black`, `isort`
92. **Debugging** — `pdb`/`breakpoint()`, `traceback`, `faulthandler`

## XII. Výkon, paměť, interní fungování (93–96)

93. **Profilování** — `cProfile`, `timeit`, `tracemalloc`, `py-spy`
94. **Optimalizace** — `__slots__`, lokální proměnné, vektorizace v NumPy
95. **C rozšíření a FFI** — `ctypes`, `cffi`, `Cython`, `pybind11`, PyO3
96. **CPython internals** — bytecode (`dis`), GC, reference counting

## XIII. Specializované oblasti (97–100)

97. **Web** — Flask/FastAPI základy, ASGI/WSGI, šablony, REST
98. **Datové analýzy** — NumPy, pandas, matplotlib základ
99. **Databáze** — `sqlite3`, SQLAlchemy ORM, asyncpg
100. **AI/ML a LLM** — práce s API (Anthropic SDK), embeddings, jednoduchý RAG

---

## XIV. Senior / Architect úroveň (101–130)

### Návrh kódu a architektury (101–110)

101. **SOLID v Pythonu** — jak principy vypadají dynamickém jazyce; kdy ANO a kdy „pythonic“ vyhrává
102. **Návrhové vzory pythonicky** — Strategy přes funkce, Singleton přes modul, Factory přes `__init_subclass__`, Observer, State, Visitor (přes `singledispatch`)
103. **Hexagonal / Ports & Adapters / Clean Architecture** — oddělení doménové logiky od I/O, závislost na rozhraních
104. **Domain-Driven Design** — entity, value objects, agregáty, repository, doménové eventy v Pythonu
105. **CQRS a Event Sourcing** — modelování stavu jako sled událostí, projekce, idempotence
106. **API design** — REST zralostní úrovně, GraphQL (`strawberry`), gRPC (`grpcio`), versioning, BFF pattern
107. **Idempotence, retry, timeouty, circuit breaker** — `tenacity`, vlastní decorátory, deadlines napříč voláními
108. **Konzistence dat** — Saga, outbox pattern, two-phase commit, transactional messaging
109. **Validace a kontrakty** — `pydantic` v2, JSON Schema, Protobuf/Avro, schema evolution
110. **Refactoring legacy Pythonu** — strangler fig, charakterizační testy, postupná typizace

### Produkční systémy (111–118)

111. **12-factor app v Pythonu** — config přes env, stateless procesy, log streamy, build/release/run
112. **Observabilita** — strukturované logy (`structlog`), metriky (Prometheus client), tracing (OpenTelemetry), correlation IDs
113. **Konfigurace v produkci** — `pydantic-settings`, secrety (Vault, AWS SM), feature flags
114. **Containerizace** — efektivní Dockerfile (multi-stage, distroless, `uv`/`pip` cache), reprodukovatelné buildy
115. **Orchestrace** — Kubernetes základ pro Pythonistu, health/readiness probes, graceful shutdown, signál SIGTERM
116. **CI/CD pipeline** — GitHub Actions / GitLab CI, matrix builds, caching, supply chain (`pip-audit`, SBOM, sigstore)
117. **Bezpečnost** — OWASP Top 10 v Pythonu, deserializace (pickle!), SSRF, secret scanning, dependency confusion
118. **Releasing & rollback** — semver, changelog, blue/green a canary, schema migrace bez downtime (Alembic patterns)

### Škálovatelnost a výkon (119–124)

119. **Performance engineering** — flame graphs (`py-spy`, `austin`), latence vs throughput, p50/p95/p99
120. **Memory engineering** — `memray`, fragmentace, leaky reference, weakrefs, object graph analýza
121. **GIL strategie v praxi** — kdy threading, kdy multiprocessing, kdy asyncio, kdy free-threaded build, kdy přejít do Rustu/C
122. **Async architektura ve velkém** — backpressure, bounded concurrency, structured concurrency (`anyio`, `TaskGroup`), cancellation correctness
123. **Distribuované systémy** — message brokers (Kafka, RabbitMQ, NATS), Celery/Dramatiq/Arq, exactly-once iluze
124. **Caching vrstvy** — Redis patterns (cache-aside, write-through), invalidation, request coalescing, lokální LRU

### Data, ML a platformové inženýrství (125–128)

125. **Data engineering pipelines** — Airflow/Prefect/Dagster, idempotentní tasky, backfilly, data lineage
126. **Stream processing** — Faust/Bytewax, windowing, late events, watermarky
127. **MLOps a LLMOps** — model registry, experiment tracking (MLflow), feature store, A/B testy, evaluace LLM, guardrails, cost & latency budgety
128. **Embeddable Python a platformy** — Python jako plugin/scripting layer (Blender, QGIS), sandboxing, omezení uživatelského kódu

### Týmová a technická vedoucí role (129–130)

129. **Architektonická rozhodnutí a komunikace** — ADR (Architecture Decision Records), trade-off analýza, RFC proces, technické due diligence balíčků
130. **Velký monorepo / multi-repo Python** — interní knihovny, semver politika, sdílené typy přes stuby, workspace nástroje (`uv`, `pants`, `bazel`), platform team mindset

---

## Jak postupovat

- **Tempo:** 1 lekce = 30–60 minut. Při denním tempu ~3 měsíce na celý kurz.
- **Forma každé lekce:** krátký výklad → příklady → 3–5 cvičení → mini projekt na konci sekce.
- **Mini projekty po sekcích:** CLI nástroj (po IX), web scraper async (po VI), TODO API (po IX), data dashboard (po XIII).
- Můžeme začít kteroukoliv lekcí — řekni číslo a vygeneruji výklad + cvičení.
