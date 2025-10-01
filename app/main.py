from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel
from neo4j import GraphDatabase
import os


NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


app = FastAPI(title="GDB TP2 API", version="0.2.0")


@app.get("/health")
def health() -> dict:
    """Healthcheck minimal pour vérifier que l'API tourne."""
    return {"ok": True}


class RecItem(BaseModel):
    product_id: str
    name: str
    score: int


def run_cypher(query: str, params: dict) -> list[dict]:
    """Exécute une requête Cypher et renvoie les records sous forme de dicts."""
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        with driver.session() as session:
            result = session.run(query, params)
            return [r.data() for r in result]


@app.get("/recs/by-product/{product_id}", response_model=list[RecItem])
def recs_by_product(product_id: str, limit: int = 5) -> list[RecItem]:
    """
    Recommandations par co-achat/co-occurrence d'articles au niveau des commandes.
    """
    rows = run_cypher(
        """
        MATCH (p:Product {id: $pid})<-[:CONTAINS]-(o:Order)-[:CONTAINS]->(other:Product)
        WHERE other.id <> $pid
        RETURN other.id AS product_id, other.name AS name, count(*) AS score
        ORDER BY score DESC
        LIMIT $limit
        """,
        {"pid": product_id, "limit": limit},
    )
    return [RecItem(**row) for row in rows]


@app.get("/recs/by-customer/{customer_id}", response_model=list[RecItem])
def recs_by_customer(
    customer_id: str,
    strategy: Literal["orders", "events"] = "orders",
    limit: int = 5,
) -> list[RecItem]:
    """
    Recommandations pour un client:
    - strategy=orders: basée sur ses achats et co-achats des autres clients
    - strategy=events: basée sur ses interactions (view/click/add_to_cart) et co-achats des autres
    """
    if strategy == "orders":
        query = """
            MATCH (c:Customer {id:$cid})-[:PLACED]->(:Order)-[:CONTAINS]->(p:Product)
            WITH collect(DISTINCT p) AS purchased
            UNWIND purchased AS p
            MATCH (p)<-[:CONTAINS]-(:Order)-[:CONTAINS]->(rec:Product)
            WHERE NOT rec IN purchased
            RETURN rec.id AS product_id, rec.name AS name, count(*) AS score
            ORDER BY score DESC
            LIMIT $limit
            """
    else:
        query = """
            MATCH (c:Customer {id:$cid})-[r:VIEWED|CLICKED|ADDED_TO_CART]->(p:Product)
            WITH collect(DISTINCT p) AS engaged
            UNWIND engaged AS p
            MATCH (p)<-[:CONTAINS]-(:Order)-[:CONTAINS]->(rec:Product)
            WHERE NOT rec IN engaged
            RETURN rec.id AS product_id, rec.name AS name, count(*) AS score
            ORDER BY score DESC
            LIMIT $limit
            """

    rows = run_cypher(query, {"cid": customer_id, "limit": limit})
    return [RecItem(**row) for row in rows]
