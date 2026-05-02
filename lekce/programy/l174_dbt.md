# Program — Lekce 174: Lekce 174: dbt — data transformation

Patří k lekci [Lekce 174: dbt — data transformation](../174_dbt.md).

## Jak spustit

```bash
python3 programy/l174_dbt.py
```

## Zdrojový kód

### `l174_dbt.py`

```py
"""Lekce 174 — dbt: data transformation.
Spuštění: uv run l174_dbt.py
Pro skutečný dbt: uv add dbt-core dbt-postgres
"""

import json


def demo_dbt_koncepty():
    print("=" * 50)
    print("  🔧 dbt — data build tool")
    print("=" * 50)
    print("""
dbt workflow:
  raw data (DB) → staging models → intermediate → marts
                                                    ↓
                                              analytici, BI tools

Klíčové koncepty:
  model     = SQL soubor → tabulka nebo view v DWH
  ref()     = závislost na jiném modelu (lineage)
  source()  = odkaz na raw data
  test      = SQL assertion (unique, not_null, accepted_values)
  macro     = Jinja2 funkce pro DRY SQL
  seed      = CSV soubor jako tabulka
  snapshot  = SCD Type 2 historické záznamy
""")


def demo_sql_simulace():
    """Simulace dbt transformací bez skutečné DB."""
    print("=== Simulace dbt transformací ===")

    # Simulace raw data
    raw_orders = [
        {"id": 1, "customer_id": 101, "amount": 1500, "status": "delivered", "deleted": False},
        {"id": 2, "customer_id": 102, "amount": 500, "status": "pending", "deleted": False},
        {"id": 3, "customer_id": 101, "amount": 2000, "status": "cancelled", "deleted": False},
        {"id": 4, "customer_id": 103, "amount": 750, "status": "delivered", "deleted": True},
    ]
    raw_customers = [
        {"id": 101, "name": "Anna", "segment": "premium"},
        {"id": 102, "name": "Bob", "segment": "standard"},
        {"id": 103, "name": "Carol", "segment": "premium"},
    ]

    # stg_orders (staging — rename + clean)
    def stg_orders(raw):
        return [
            {"order_id": r["id"], "customer_id": r["customer_id"],
             "total_czk": r["amount"], "status": r["status"]}
            for r in raw if not r["deleted"]
        ]

    # stg_customers
    def stg_customers(raw):
        return [{"customer_id": r["id"], "name": r["name"], "segment": r["segment"]} for r in raw]

    # marts/orders (finální — join + metriky)
    def mart_orders(orders, customers):
        cust_map = {c["customer_id"]: c for c in customers}
        return [
            {**o, "customer_name": cust_map.get(o["customer_id"], {}).get("name", "?"),
             "tier": "high" if o["total_czk"] >= 1000 else "low"}
            for o in orders
        ]

    stg_o = stg_orders(raw_orders)
    stg_c = stg_customers(raw_customers)
    final = mart_orders(stg_o, stg_c)

    print("\n  staging/stg_orders (3 řádky po filtraci deleted):")
    for r in stg_o: print(f"    {r}")
    print("\n  marts/orders (s joinem na customers):")
    for r in final: print(f"    {r}")


def demo_dbt_test():
    print("\n=== dbt testy (schema.yml) ===")
    schema = {
        "models": [{
            "name": "orders",
            "columns": [
                {"name": "order_id", "tests": ["unique", "not_null"]},
                {"name": "status", "tests": [{"accepted_values": {"values": ["pending","delivered","cancelled"]}}]},
                {"name": "total_czk", "tests": ["not_null"]},
            ]
        }]
    }
    print("  schema.yml:")
    print(json.dumps(schema, indent=4, ensure_ascii=False)[:400])

    # Simulace testů
    data = [
        {"order_id": 1, "status": "delivered", "total_czk": 1500},
        {"order_id": 2, "status": "pending", "total_czk": 500},
    ]
    ids = [r["order_id"] for r in data]
    print("\n  Výsledky testů:")
    print(f"    unique(order_id): {'✅ PASS' if len(ids) == len(set(ids)) else '❌ FAIL'}")
    print(f"    not_null(order_id): {'✅ PASS' if all(r['order_id'] for r in data) else '❌ FAIL'}")
    statuses = {r["status"] for r in data}
    ok_vals = {"pending","delivered","cancelled","processing"}
    print(f"    accepted_values(status): {'✅ PASS' if statuses <= ok_vals else '❌ FAIL'}")


def main():
    demo_dbt_koncepty()
    demo_sql_simulace()
    demo_dbt_test()
    print("\n✅ Demo dokončeno!")
    print("\ndbt příkazy:")
    print("  dbt run           → spusť všechny modely")
    print("  dbt test          → spusť všechny testy")
    print("  dbt docs serve    → vizualizace lineage")
    print("  dbt build         → run + test + seed")


if __name__ == "__main__":
    main()

```
