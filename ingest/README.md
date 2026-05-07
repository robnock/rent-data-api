# Ingest

Loads source CSVs from `data/` into the Postgres warehouse (full rebuild each run).

Metric definitions (`dataset_id`, titles, semantics) live in
**`api/app/catalog.py`** (five curated metrics — add rows there when new products
join the warehouse). Each publishes a **`{dataset_id}.csv`** with columns:

```text
location_fips_code, period, value, date_updated_at
```

Only CSVs matching the catalog whitelist (plus **`locations.csv`**) may live under
`data/` — `scripts/validate_data.py` enforces this.

## Run

Prerequisites: Postgres is running, `DATABASE_URL` is set (see repo root `.env`),
and migrations are current:

```bash
source api/.venv/bin/activate
PYTHONPATH=api alembic upgrade head
```

From the **repo root**, with `PYTHONPATH` including `api/`:

```bash
PYTHONPATH=api python3.12 -m ingest
```

Skip messages on stderr indicate configured metrics whose CSVs are absent; at
least **one** metric CSV must exist or ingest aborts.

## Validation

Structural checks:

```bash
python3 scripts/validate_data.py
```
