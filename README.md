## Graph DB TP2 – E‑commerce Graph Recommendations

### Lancer la stack

```bash
docker compose up -d
docker compose logs -f
```

Attendus dans les logs:
- Postgres: "database system is ready to accept connections"
- Neo4j: interface à `http://localhost:7474/` (auth: `neo4j/password`)
- App: "Uvicorn running on http://0.0.0.0:8000"

### Vérifier rapidement

```bash
curl http://localhost:8000/health
```

### Exécuter l’ETL

Depuis l’hôte:

```bash
docker compose exec -T app python /work/app/elt.py
```

Sortie attendue (dernière ligne):

```
ETL done.
```

### Tests end‑to‑end

Script hôte:

```bash
bash scripts/check_containers.sh
```

Ou service Docker (tout en conteneur):

```bash
docker compose run --rm checks
```


### How to run

1) Prérequis

```bash
Docker Desktop démarré (allumé)
```

2) Démarrer

```bash
docker compose up -d
```

3) Vérifier que l’API répond

```bash
curl http://localhost:8000/health
# attendu: {"ok":true}
```

4) Lancer l’ETL (chargement Postgres → Neo4j)

```bash
docker compose exec -T app python /work/app/etl.py
# attendu (dernière ligne): ETL done.
```

5) Tester les endpoints de recommandations

```bash
# Recos par produit (co-achat)
curl "http://localhost:8000/recs/by-product/P1?limit=5"
curl "http://localhost:8000/recs/by-product/P2?limit=5"

# Recos pour un client
curl "http://localhost:8000/recs/by-customer/C2?strategy=events&limit=5"
```

6) Ouvrir Neo4j Browser

```text
URL: http://localhost:7474/
Login: neo4j
Password: password
```

Exemples Cypher rapides:

```cypher
MATCH (c:Customer) RETURN count(c) AS customers;
MATCH (p:Product) RETURN count(p) AS products;
MATCH (:Customer)-[:PLACED]->(:Order) RETURN count(*) AS orders;
```

7) Vérif Postgres (optionnel)

```bash
docker compose exec -T postgres psql -U app -d shop -c "\\dt"
docker compose exec -T postgres psql -U app -d shop -c "SELECT count(*) FROM customers;"
```

8) Arrêter

```bash
docker compose down
```


