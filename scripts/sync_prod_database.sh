#!/usr/bin/env bash
# Apply Alembic migrations and full ingest to DATABASE_URL (hosted Postgres).
# Run from your laptop after Neon/etc. is provisioned — not from Vercel.
#
# Usage:
#   export DATABASE_URL='postgresql+psycopg://user:pass@host/db?sslmode=require'
#   ./scripts/sync_prod_database.sh
#
# Optional: SKIP_INGEST=1 to only run migrations.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "error: set DATABASE_URL to your hosted Postgres connection string." >&2
  exit 1
fi

PY="${ROOT}/api/.venv/bin/python3.12"
if [[ ! -x "$PY" ]]; then
  PY="${ROOT}/api/.venv/bin/python3"
fi
if [[ ! -x "$PY" ]]; then
  echo "error: create api/.venv and pip install -r api/requirements.txt first." >&2
  exit 1
fi

export PYTHONPATH="${ROOT}/api"

echo "Running alembic upgrade head..."
"$PY" -m alembic upgrade head

if [[ "${SKIP_INGEST:-}" == "1" ]]; then
  echo "SKIP_INGEST=1 — skipping ingest."
  exit 0
fi

echo "Running ingest (full rebuild)..."
"$PY" -m ingest

echo "Done."
