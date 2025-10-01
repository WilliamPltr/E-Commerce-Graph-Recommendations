#!/usr/bin/env bash
set -euo pipefail

MODE=${1:-host}

if [[ "$MODE" == "--container" ]]; then
  APP_HOST="http://app:8000"
  PGHOST=postgres
  PGUSER=app
  PGPASSWORD=app
  PGDATABASE=shop
else
  APP_HOST="http://127.0.0.1:8000"
fi

echo "› Health: $APP_HOST/health"
curl -sS "$APP_HOST/health"
echo

if [[ "$MODE" == "--container" ]]; then
  echo
  echo "› Postgres: SELECT * FROM orders LIMIT 5;"
  PGPASSWORD=${PGPASSWORD:-app} psql -h ${PGHOST:-127.0.0.1} -U ${PGUSER:-app} -d ${PGDATABASE:-shop} -c "SELECT * FROM orders LIMIT 5;"
  echo "✔ Orders query OK"

  echo
  echo "› Postgres: SELECT now();"
  PGPASSWORD=${PGPASSWORD:-app} psql -h ${PGHOST:-127.0.0.1} -U ${PGUSER:-app} -d ${PGDATABASE:-shop} -c "SELECT now();"
  echo "✔ now() query OK"

  echo
  echo "› ETL: python /work/app/elt.py"
  OUT=$(python /work/app/etl.py | tail -n 1)
  echo "$OUT"
  if [[ "$OUT" == "ETL done." ]]; then
    echo "✔ ETL output OK (ETL done.)"
  else
    echo "✖ ETL output not as expected" >&2
    exit 1
  fi
fi


