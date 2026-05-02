# Lekce 142: Neo4j — grafová databáze

Neo4j ukládá data jako **uzly (nodes) a hrany (relationships)**. Ideální pro silně propojená data — sociální sítě, doporučovací systémy, knowledge grafy, detekce podvodů.

---

## 🚀 Instalace

```bash
uv add neo4j

# Neo4j server (Docker)
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/heslo1234 \
  neo4j:5

# Web UI (Browser): http://localhost:7474
# Bolt protokol:    neo4j://localhost:7687
```

---

## 🔑 Koncepty

```
Uzel (Node):        (anna:Uzivatel {jmeno: "Anna", vek: 30})
Hrana (Relationship): (anna)-[:PRATEL_S {od: 2020}]->(bob)
Vlastnosti:         klíč-hodnota na uzlech i hranách
Label:              typ uzlu — Uzivatel, Produkt, Film...
```

---

## 🔌 Připojení

```python
from neo4j import GraphDatabase

# Připojení
driver = GraphDatabase.driver(
    "neo4j://localhost:7687",
    auth=("neo4j", "heslo1234")
)

# Ověření
driver.verify_connectivity()
print("Připojeno!")

# Session — základní jednotka pro dotazy
with driver.session(database="neo4j") as session:
    result = session.run("RETURN 'Ahoj Neo4j!' AS zprava")
    print(result.single()["zprava"])

driver.close()
```

---

## 📝 Cypher — dotazovací jazyk

### CREATE — vytváření uzlů a hran

```python
with driver.session() as session:
    # Vytvoř uzly
    session.run("""
        CREATE (anna:Uzivatel {jmeno: 'Anna', vek: 30, email: 'anna@example.com'})
        CREATE (bob:Uzivatel {jmeno: 'Bob', vek: 25, email: 'bob@example.com'})
        CREATE (carol:Uzivatel {jmeno: 'Carol', vek: 35, email: 'carol@example.com'})
        CREATE (python:Technologie {nazev: 'Python'})
        CREATE (fastapi:Technologie {nazev: 'FastAPI'})
        CREATE (docker:Technologie {nazev: 'Docker'})
    """)

    # Vytvoř vztahy
    session.run("""
        MATCH (anna:Uzivatel {jmeno: 'Anna'})
        MATCH (bob:Uzivatel {jmeno: 'Bob'})
        MATCH (carol:Uzivatel {jmeno: 'Carol'})
        MATCH (python:Technologie {nazev: 'Python'})
        MATCH (fastapi:Technologie {nazev: 'FastAPI'})
        MATCH (docker:Technologie {nazev: 'Docker'})
        CREATE (anna)-[:PRATEL_S {od: 2020}]->(bob)
        CREATE (anna)-[:PRATEL_S {od: 2019}]->(carol)
        CREATE (bob)-[:PRATEL_S {od: 2021}]->(carol)
        CREATE (anna)-[:ZNA {uroven: 'expert'}]->(python)
        CREATE (anna)-[:ZNA {uroven: 'pokrocily'}]->(fastapi)
        CREATE (bob)-[:ZNA {uroven: 'zacatecnik'}]->(python)
        CREATE (bob)-[:ZNA {uroven: 'expert'}]->(docker)
        CREATE (carol)-[:ZNA {uroven: 'pokrocily'}]->(python)
        CREATE (carol)-[:ZNA {uroven: 'pokrocily'}]->(docker)
    """)
    print("Uzly a vztahy vytvořeny")
```

### MATCH — dotazování

```python
with driver.session() as session:
    # Najdi všechny uzivatele
    vysledek = session.run("MATCH (u:Uzivatel) RETURN u.jmeno, u.vek ORDER BY u.vek")
    for zaznam in vysledek:
        print(f"{zaznam['u.jmeno']}, {zaznam['u.vek']} let")

    # Najdi přátele Anny
    vysledek = session.run("""
        MATCH (anna:Uzivatel {jmeno: 'Anna'})-[:PRATEL_S]-(pritel:Uzivatel)
        RETURN pritel.jmeno
    """)
    pratele = [z["pritel.jmeno"] for z in vysledek]
    print(f"Přátelé Anny: {pratele}")

    # Přátelé přátel (2 kroky)
    vysledek = session.run("""
        MATCH (anna:Uzivatel {jmeno: 'Anna'})-[:PRATEL_S*2]-(mozny:Uzivatel)
        WHERE mozny <> anna
        AND NOT (anna)-[:PRATEL_S]-(mozny)
        RETURN DISTINCT mozny.jmeno AS doporuceni
    """)
    print("Možní noví přátelé:")
    for z in vysledek:
        print(f"  {z['doporuceni']}")

    # Kdo zná Python na expert úrovni?
    vysledek = session.run("""
        MATCH (u:Uzivatel)-[z:ZNA]->(t:Technologie {nazev: 'Python'})
        WHERE z.uroven = 'expert'
        RETURN u.jmeno, z.uroven
    """)
    for z in vysledek:
        print(f"{z['u.jmeno']}: {z['z.uroven']} Python")
```

---

## 🔗 Parametrizované dotazy

```python
def vytvor_uzivatele(driver, jmeno: str, vek: int, email: str) -> dict:
    with driver.session() as session:
        result = session.run(
            """
            CREATE (u:Uzivatel {jmeno: $jmeno, vek: $vek, email: $email})
            RETURN u
            """,
            jmeno=jmeno, vek=vek, email=email
        )
        return result.single()["u"]


def pridej_vztah(driver, od: str, do: str, typ: str, vlastnosti: dict = None):
    with driver.session() as session:
        session.run(
            f"""
            MATCH (a:Uzivatel {{jmeno: $od}})
            MATCH (b:Uzivatel {{jmeno: $do}})
            CREATE (a)-[:{typ} $vlastnosti]->(b)
            """,
            od=od, do=do, vlastnosti=vlastnosti or {}
        )


def najdi_nejkratsi_cestu(driver, od: str, do: str) -> list:
    with driver.session() as session:
        result = session.run(
            """
            MATCH path = shortestPath(
                (a:Uzivatel {jmeno: $od})-[:PRATEL_S*]-(b:Uzivatel {jmeno: $do})
            )
            RETURN [n IN nodes(path) | n.jmeno] AS cesta,
                   length(path) AS delka
            """,
            od=od, do=do
        )
        zaznam = result.single()
        if zaznam:
            return zaznam["cesta"]
        return []
```

---

## 📊 Grafové algoritmy

```python
# Potřebuje Graph Data Science plugin (GDS)
# docker run -e NEO4J_PLUGINS='["graph-data-science"]' ...

with driver.session() as session:
    # PageRank — kdo je nejdůležitější uzel
    session.run("""
        CALL gds.graph.project('socialni_sit', 'Uzivatel', 'PRATEL_S')
    """)

    vysledek = session.run("""
        CALL gds.pageRank.stream('socialni_sit')
        YIELD nodeId, score
        RETURN gds.util.asNode(nodeId).jmeno AS jmeno, score
        ORDER BY score DESC
        LIMIT 10
    """)
    print("PageRank — nejdůležitější uživatelé:")
    for z in vysledek:
        print(f"  {z['jmeno']}: {z['score']:.4f}")

    # Detekce komunit (Louvain)
    vysledek = session.run("""
        CALL gds.louvain.stream('socialni_sit')
        YIELD nodeId, communityId
        RETURN gds.util.asNode(nodeId).jmeno AS jmeno, communityId
        ORDER BY communityId
    """)
    print("\nKomunity:")
    for z in vysledek:
        print(f"  Komunita {z['communityId']}: {z['jmeno']}")
```

---

## 🛒 Doporučovací systém

```python
def doporuc_produkty(driver, uzivatel_jmeno: str, n: int = 5) -> list:
    """
    Collaborative filtering — doporuč produkty, které koupili
    přátelé uživatele, ale on sám je nekoupil.
    """
    with driver.session() as session:
        vysledek = session.run(
            """
            MATCH (u:Uzivatel {jmeno: $jmeno})-[:PRATEL_S]-(pritel:Uzivatel)
            MATCH (pritel)-[:KOUPIL]->(p:Produkt)
            WHERE NOT (u)-[:KOUPIL]->(p)
            WITH p, COUNT(pritel) AS skore
            ORDER BY skore DESC
            LIMIT $n
            RETURN p.nazev AS produkt, skore
            """,
            jmeno=uzivatel_jmeno, n=n
        )
        return [(z["produkt"], z["skore"]) for z in vysledek]
```

---

## 🔐 Detekce podvodů

```python
def detekuj_podvod(driver, ucet_id: str) -> dict:
    """
    Najdi účty sdílející stejné zařízení/email/telefon
    v posledních 24 hodinách.
    """
    with driver.session() as session:
        vysledek = session.run(
            """
            MATCH (u:Ucet {id: $id})-[:POUZIL]->(z:Zarizeni)
            MATCH (jiny:Ucet)-[:POUZIL]->(z)
            WHERE jiny <> u
            AND jiny.vytvoreno > datetime() - duration({hours: 24})
            WITH jiny, COUNT(z) AS spolecna_zarizeni
            WHERE spolecna_zarizeni >= 2
            RETURN jiny.id AS podezrely_ucet,
                   spolecna_zarizeni,
                   'shared_device' AS duvod
            """,
            id=ucet_id
        )
        return [dict(z) for z in vysledek]
```

---

## 🎯 Kdy použít grafovou databázi

| Případ | Neo4j | PostgreSQL | MongoDB |
|--------|-------|-----------|---------|
| Sociální sítě | ✅ | složité JOINy | ❌ |
| Doporučení | ✅ | ❌ | ❌ |
| Detekce podvodů | ✅ | ❌ | ❌ |
| Knowledge graph | ✅ | ❌ | ❌ |
| Nejkratší cesta | ✅ nativní | rekurze | ❌ |
| ACID transakce | ✅ | ✅ | ✅ |
| Jednoduché CRUD | overkill | ✅ | ✅ |
| Relační data | ❌ | ✅ | ❌ |

---

## ✏️ Cvičení

1. Spusť Neo4j v Dockeru, vytvoř graf přátel (10 uživatelů, 15+ vztahů).
2. Implementuj **6 stupňů odloučení** — najdi nejkratší cestu mezi dvěma uživateli.
3. Postav doporučovací systém filmů — uživatelé, filmy, hodnocení (HODNOTIL vztah s `score`).
4. Implementuj knowledge graph technologií — které technologie na sebe navazují (`VYCHAZI_Z`).
5. Navrhni grafový model pro detekci podvodů — účty, zařízení, IP adresy, transakce.
