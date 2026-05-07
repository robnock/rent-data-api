# Database

PostgreSQL schema and migrations for the Econ Data API.

## Migrations

- [Alembic](https://alembic.sqlalchemy.org/) revisions live in `db/migrations/versions/`.
- SQLAlchemy `Base.metadata` lives in `api/app/models.py` (`prepend_sys_path = api`
  in root `alembic.ini`).
- **`0001`** — `locations`, `datasets`, `observations`
- **`0002`** — `observations.value` nullable (`NA` etc. in source CSV)
- **`0003`** — `api_keys`, `api_usage_log` (Stage 6)

Upgrade from the repo root (API settings load `DATABASE_URL` from `.env`):

```bash
source api/.venv/bin/activate
PYTHONPATH=api alembic upgrade head
```

Then run ingest (see `ingest/README.md`).

## Local Postgres setup (macOS)

Follow the root `README.md` “Local Postgres” section. Typical URL:

```
DATABASE_URL=postgresql+psycopg://localhost:5432/econ_data
```
