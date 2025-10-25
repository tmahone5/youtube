#!/usr/bin/env bash
set -euo pipefail

PG_SUPERUSER=postgres
PG_SUPERPASS=wWfKvYbyD3kRnE4u
CELERY_DB="${CELERY_BACKEND_NAME:-celery_results_db}"
CELERY_USER="${CELERY_BACKEND_USERNAME:-celery_user}"
CELERY_PASS="${CELERY_BACKEND_PASSWORD:-L4PYpRNq6mxSQfyj}"

echo "Starting postgres & redis…"
docker compose up -d postgres redis

echo "Creating/aligning role ${CELERY_USER}…"
docker compose exec -e PGPASSWORD="${PG_SUPERPASS}" postgres \
  psql -U "${PG_SUPERUSER}" -d postgres -c "DO \$\$ BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='${CELERY_USER}') THEN
      CREATE ROLE ${CELERY_USER} LOGIN PASSWORD '${CELERY_PASS}';
    ELSE
      ALTER ROLE ${CELERY_USER} WITH PASSWORD '${CELERY_PASS}' LOGIN;
    END IF;
  END \$\$;"

echo "Ensuring database ${CELERY_DB} exists…"
if ! docker compose exec -e PGPASSWORD="${PG_SUPERPASS}" postgres \
  psql -U "${PG_SUPERUSER}" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='${CELERY_DB}'" | grep -q 1; then
  docker compose exec -e PGPASSWORD="${PG_SUPERPASS}" postgres \
    psql -U "${PG_SUPERUSER}" -d postgres -c "CREATE DATABASE ${CELERY_DB} OWNER ${CELERY_USER};"
fi

echo "Smoke test as ${CELERY_USER}…"
docker compose exec -e PGPASSWORD="${CELERY_PASS}" postgres \
  psql -U "${CELERY_USER}" -d "${CELERY_DB}" -c "select 1;"

echo "Recreating Airflow services…"
docker compose up -d --force-recreate airflow-webserver airflow-scheduler airflow-worker

echo "Done. Result backend URL in worker:"
docker compose exec airflow-worker /bin/sh -lc 'echo "$AIRFLOW__CELERY__RESULT_BACKEND"'
