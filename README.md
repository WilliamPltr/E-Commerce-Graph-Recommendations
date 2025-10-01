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


