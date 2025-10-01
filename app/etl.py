import os
import time
from pathlib import Path
from typing import Iterable, List

import psycopg2
from neo4j import GraphDatabase


PG_DSN = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", "5432")),
    "dbname": os.getenv("PGDATABASE", "shop"),
    "user": os.getenv("PGUSER", "app"),
    "password": os.getenv("PGPASSWORD", "app"),
}

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


def wait_for_postgres(timeout_seconds: int = 120) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            conn = psycopg2.connect(**PG_DSN)
            conn.close()
            return
        except Exception:
            time.sleep(2)
    raise TimeoutError("Postgres non disponible après délai")


def wait_for_neo4j(timeout_seconds: int = 120) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
            ) as driver:
                with driver.session() as sess:
                    sess.run("RETURN 1")
            return
        except Exception:
            time.sleep(2)
    raise TimeoutError("Neo4j non disponible après délai")


def run_cypher(query: str, parameters: dict | None = None) -> None:
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        with driver.session() as session:
            session.run(query, parameters or {})


def run_cypher_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    # Séparer naïvement par ';' et ignorer les vides
    statements = [s.strip() for s in text.split(";") if s.strip()]
    for stmt in statements:
        run_cypher(stmt)


def chunk(iterable: List[tuple], size: int) -> Iterable[List[tuple]]:
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


def etl() -> None:
    """
    Main ETL function that migrates data from PostgreSQL to Neo4j.

    Étapes:
    1) Attendre Postgres et Neo4j
    2) Appliquer le schéma Neo4j via queries.cypher
    3) Extraire les tables de Postgres
    4) Charger les nœuds et relations dans Neo4j
    """

    wait_for_postgres()
    wait_for_neo4j()

    queries_path = Path(__file__).with_name("queries.cypher")
    run_cypher_file(queries_path)

    # Extraction
    conn = psycopg2.connect(**PG_DSN)
    cur = conn.cursor()

    def fetch(sql: str) -> list[tuple]:
        cur.execute(sql)
        return cur.fetchall()

    customers = fetch("SELECT id, name, join_date FROM customers")
    categories = fetch("SELECT id, name FROM categories")
    products = fetch("SELECT id, name, price, category_id FROM products")
    orders = fetch("SELECT id, customer_id, ts FROM orders")
    order_items = fetch("SELECT order_id, product_id, quantity FROM order_items")
    events = fetch("SELECT id, customer_id, product_id, event_type, ts FROM events")

    cur.close()
    conn.close()

    # Chargement — upserts simples
    run_cypher("MATCH (n) DETACH DELETE n")

    # Categories
    for batch in chunk(categories, 100):
        run_cypher(
            """
            UNWIND $rows AS row
            MERGE (c:Category {id: row.id})
            SET c.name = row.name
            """,
            {"rows": [{"id": r[0], "name": r[1]} for r in batch]},
        )

    # Products
    for batch in chunk(products, 100):
        run_cypher(
            """
            UNWIND $rows AS row
            MERGE (p:Product {id: row.id})
            SET p.name = row.name, p.price = row.price
            WITH p, row
            MATCH (c:Category {id: row.category_id})
            MERGE (p)-[:IN_CATEGORY]->(c)
            """,
            {
                "rows": [
                    {
                        "id": r[0],
                        "name": r[1],
                        "price": float(r[2]),
                        "category_id": r[3],
                    }
                    for r in batch
                ]
            },
        )

    # Customers
    for batch in chunk(customers, 100):
        run_cypher(
            """
            UNWIND $rows AS row
            MERGE (c:Customer {id: row.id})
            SET c.name = row.name, c.join_date = row.join_date
            """,
            {
                "rows": [
                    {"id": r[0], "name": r[1], "join_date": str(r[2])} for r in batch
                ]
            },
        )

    # Orders
    for batch in chunk(orders, 100):
        run_cypher(
            """
            UNWIND $rows AS row
            MERGE (o:Order {id: row.id})
            SET o.ts = row.ts
            WITH o, row
            MATCH (c:Customer {id: row.customer_id})
            MERGE (c)-[:PLACED]->(o)
            """,
            {
                "rows": [
                    {"id": r[0], "customer_id": r[1], "ts": str(r[2])} for r in batch
                ]
            },
        )

    # Order items
    for batch in chunk(order_items, 200):
        run_cypher(
            """
            UNWIND $rows AS row
            MATCH (o:Order {id: row.order_id})
            MATCH (p:Product {id: row.product_id})
            MERGE (o)-[r:CONTAINS]->(p)
            SET r.quantity = row.quantity
            """,
            {
                "rows": [
                    {"order_id": r[0], "product_id": r[1], "quantity": int(r[2])}
                    for r in batch
                ]
            },
        )

    # Events -> dynamic rels
    event_map = {
        "view": "VIEWED",
        "click": "CLICKED",
        "add_to_cart": "ADDED_TO_CART",
    }
    for e_id, c_id, p_id, e_type, ts in events:
        rel = event_map.get(e_type)
        if not rel:
            continue
        run_cypher(
            f"""
            MATCH (c:Customer {{id: $cid}})
            MATCH (p:Product {{id: $pid}})
            MERGE (c)-[r:{rel}]->(p)
            SET r.ts = $ts, r.event_id = $eid
            """,
            {"cid": c_id, "pid": p_id, "ts": str(ts), "eid": e_id},
        )

    print("ETL done.")


if __name__ == "__main__":
    etl()
