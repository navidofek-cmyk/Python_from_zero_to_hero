"""Lekce 142 — Neo4j: grafová databáze.

Spuštění:
    docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
      -e NEO4J_AUTH=neo4j/heslo1234 neo4j:5

    uv run --with neo4j l142_neo4j_graph.py

Web UI: http://localhost:7474
"""

try:
    from neo4j import GraphDatabase
except ImportError:
    print("Nainstaluj: uv add neo4j")
    raise

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "heslo1234")


def pripoj():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    driver.verify_connectivity()
    return driver


def vycisti(driver):
    with driver.session() as s:
        s.run("MATCH (n) DETACH DELETE n")


def vytvor_data(driver):
    print("\n=== Vytváření grafu ===")
    with driver.session() as s:
        # Uživatelé
        s.run("""
            CREATE (anna:Uzivatel {jmeno:'Anna', vek:30, mesto:'Praha'})
            CREATE (bob:Uzivatel {jmeno:'Bob', vek:25, mesto:'Brno'})
            CREATE (carol:Uzivatel {jmeno:'Carol', vek:35, mesto:'Praha'})
            CREATE (dan:Uzivatel {jmeno:'Dan', vek:28, mesto:'Ostrava'})
            CREATE (eva:Uzivatel {jmeno:'Eva', vek:32, mesto:'Brno'})

            CREATE (py:Technologie {nazev:'Python', kategorie:'jazyk'})
            CREATE (fa:Technologie {nazev:'FastAPI', kategorie:'framework'})
            CREATE (dk:Technologie {nazev:'Docker', kategorie:'devops'})
            CREATE (pg:Technologie {nazev:'PostgreSQL', kategorie:'databaze'})
            CREATE (re:Technologie {nazev:'Redis', kategorie:'databaze'})

            CREATE (anna)-[:PRATEL_S {od:2020}]->(bob)
            CREATE (anna)-[:PRATEL_S {od:2019}]->(carol)
            CREATE (bob)-[:PRATEL_S {od:2021}]->(carol)
            CREATE (bob)-[:PRATEL_S {od:2022}]->(dan)
            CREATE (carol)-[:PRATEL_S {od:2020}]->(eva)
            CREATE (dan)-[:PRATEL_S {od:2023}]->(eva)

            CREATE (anna)-[:ZNA {uroven:'expert'}]->(py)
            CREATE (anna)-[:ZNA {uroven:'pokrocily'}]->(fa)
            CREATE (anna)-[:ZNA {uroven:'zacatecnik'}]->(dk)
            CREATE (bob)-[:ZNA {uroven:'pokrocily'}]->(py)
            CREATE (bob)-[:ZNA {uroven:'expert'}]->(dk)
            CREATE (carol)-[:ZNA {uroven:'expert'}]->(py)
            CREATE (carol)-[:ZNA {uroven:'pokrocily'}]->(pg)
            CREATE (dan)-[:ZNA {uroven:'expert'}]->(dk)
            CREATE (dan)-[:ZNA {uroven:'pokrocily'}]->(re)
            CREATE (eva)-[:ZNA {uroven:'zacatecnik'}]->(py)
            CREATE (eva)-[:ZNA {uroven:'expert'}]->(pg)
        """)
    print("  Graf vytvořen: 5 uživatelů, 5 technologií, 11 vztahů PRATEL_S+ZNA")


def demo_zakladni_dotazy(driver):
    print("\n=== Základní dotazy ===")
    with driver.session() as s:
        # Všichni uživatelé
        uziv = s.run("MATCH (u:Uzivatel) RETURN u.jmeno, u.vek ORDER BY u.vek").data()
        print("  Uživatelé:")
        for u in uziv:
            print(f"    {u['u.jmeno']} ({u['u.vek']} let)")

        # Přátelé Anny
        pratele = s.run("""
            MATCH (a:Uzivatel {jmeno:'Anna'})-[:PRATEL_S]-(p:Uzivatel)
            RETURN p.jmeno
        """).data()
        print(f"\n  Přátelé Anny: {[p['p.jmeno'] for p in pratele]}")

        # Co zná Anna
        zna = s.run("""
            MATCH (a:Uzivatel {jmeno:'Anna'})-[z:ZNA]->(t:Technologie)
            RETURN t.nazev, z.uroven ORDER BY z.uroven
        """).data()
        print("  Anna zná:")
        for z in zna:
            print(f"    {z['t.nazev']}: {z['z.uroven']}")


def demo_slozitejsi_dotazy(driver):
    print("\n=== Složitější dotazy ===")
    with driver.session() as s:
        # Přátelé přátel (noví potenciální přátelé)
        pp = s.run("""
            MATCH (anna:Uzivatel {jmeno:'Anna'})-[:PRATEL_S*2]-(mozny:Uzivatel)
            WHERE mozny.jmeno <> 'Anna'
            AND NOT (anna)-[:PRATEL_S]-(mozny)
            RETURN DISTINCT mozny.jmeno AS doporuceni
        """).data()
        print(f"  Doporučení nových přátel pro Annu: {[p['doporuceni'] for p in pp]}")

        # Nejkratší cesta
        cesta = s.run("""
            MATCH path = shortestPath(
                (a:Uzivatel {jmeno:'Anna'})-[:PRATEL_S*]-(b:Uzivatel {jmeno:'Eva'})
            )
            RETURN [n IN nodes(path) | n.jmeno] AS cesta, length(path) AS delka
        """).single()
        if cesta:
            print(f"  Cesta Anna → Eva: {' → '.join(cesta['cesta'])} ({cesta['delka']} kroků)")

        # Kdo zná Python na expert úrovni?
        experti = s.run("""
            MATCH (u:Uzivatel)-[z:ZNA {uroven:'expert'}]->(t:Technologie {nazev:'Python'})
            RETURN u.jmeno
        """).data()
        print(f"  Python experti: {[e['u.jmeno'] for e in experti]}")

        # Nejpropojitelnější uzel (degree centrality)
        centrality = s.run("""
            MATCH (u:Uzivatel)
            RETURN u.jmeno,
                   SIZE([(u)-[:PRATEL_S]-() | 1]) as stupen
            ORDER BY stupen DESC
            LIMIT 3
        """).data()
        print("\n  Top 3 nejpropojitelnější:")
        for c in centrality:
            print(f"    {c['u.jmeno']}: {c['stupen']} přátel")


def demo_doporucovaci_system(driver):
    print("\n=== Doporučovací systém technologií ===")
    with driver.session() as s:
        # Doporuč technologie na základě přátel
        doporuceni = s.run("""
            MATCH (anna:Uzivatel {jmeno:'Anna'})-[:PRATEL_S]-(pritel:Uzivatel)
            MATCH (pritel)-[:ZNA]->(tech:Technologie)
            WHERE NOT (anna)-[:ZNA]->(tech)
            WITH tech, COUNT(pritel) AS skore, COLLECT(pritel.jmeno) AS zdroje
            ORDER BY skore DESC
            RETURN tech.nazev AS technologie, skore, zdroje
        """).data()

        print("  Anna by mohla znát (přátelé to umí):")
        for d in doporuceni:
            print(f"    {d['technologie']}: doporučují {d['zdroje']} (skóre: {d['skore']})")


def demo_grafove_metriky(driver):
    print("\n=== Grafové metriky ===")
    with driver.session() as s:
        # Hustota grafu
        uzly = s.run("MATCH (u:Uzivatel) RETURN COUNT(u) AS n").single()["n"]
        hrany = s.run("MATCH ()-[r:PRATEL_S]-() RETURN COUNT(r)/2 AS e").single()["e"]
        max_hrany = uzly * (uzly - 1) / 2
        hustota = hrany / max_hrany if max_hrany > 0 else 0
        print(f"  Uzly: {uzly}, Hrany: {hrany}, Hustota: {hustota:.2f}")

        # Triangles (kliky přátel)
        trojuhelniki = s.run("""
            MATCH (a:Uzivatel)-[:PRATEL_S]-(b:Uzivatel)-[:PRATEL_S]-(c:Uzivatel)-[:PRATEL_S]-(a)
            RETURN COUNT(DISTINCT [a.jmeno, b.jmeno, c.jmeno]) / 6 AS trojuhelniki
        """).single()
        print(f"  Trojúhelníky (skupiny 3 přátel): {trojuhelniki['trojuhelniki']}")


def main():
    print("=" * 50)
    print("  🕸️  Neo4j Grafová DB Demo")
    print("=" * 50)

    try:
        driver = pripoj()
        print("✅ Neo4j připojeno")
    except Exception as e:
        print(f"❌ Neo4j nedostupné: {e}")
        print("   Spusť: docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \\")
        print("     -e NEO4J_AUTH=neo4j/heslo1234 neo4j:5")
        print("   Web UI: http://localhost:7474")
        return

    vycisti(driver)
    vytvor_data(driver)
    demo_zakladni_dotazy(driver)
    demo_slozitejsi_dotazy(driver)
    demo_doporucovaci_system(driver)
    demo_grafove_metriky(driver)

    driver.close()
    print("\n✅ Demo dokončeno!")
    print("   Vizualizuj v Neo4j Browser: http://localhost:7474")
    print("   Dotaz pro zobrazení: MATCH (n)-[r]-(m) RETURN n,r,m LIMIT 50")


if __name__ == "__main__":
    main()
