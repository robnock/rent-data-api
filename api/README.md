# API

FastAPI service for the Econ Data API.

## Local setup

From the repo root:

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Prefer the interpreter that actually received the installs (often `python3.12`; see repo root README if Xcode’s `/usr/bin/python3` steals `python`).

## Run

From the `api/` directory with the venv active:

```bash
uvicorn app.main:app --reload --port 8000
```

Endpoints (see `/docs` for OpenAPI):

- `GET /healthz` — liveness
- `GET /datasets` — catalog summaries
- `GET /datasets/{dataset_id}` — metadata + exported column meanings
- `GET /datasets/{dataset_id}/observations` — paginated JSON observations
  (`limit` ≤ 1000; optional `fips_code`, `period_from`, `period_to`)
- `GET /datasets/{dataset_id}/observations.csv` — streamed CSV aligned with catalog layout

Uses `DATABASE_URL` from `.env` (warehouse must be migrated + ingested).

### API keys (Stage 6)

- `API_AUTH_REQUIRED` — when `true`, all `/datasets*` routes require header **`X-API-Key`**.
- `python3 scripts/issue_api_key.py "label"` — inserts `api_keys` row; prints plaintext once.
- Successful authenticated dataset responses append a row to **`api_usage_log`**.

`/healthz`, `/`, `/docs` stay unauthenticated for probes and OpenAPI UI.

### Railway (production API host)

When **Root Directory** for the Railway service is **`api`**, Railway uses
[`railway.toml`](railway.toml) to run:

`uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Set **`DATABASE_URL`**, **`CORS_ALLOW_ORIGINS`**, **`API_AUTH_REQUIRED`** in Railway → Variables.
Full checklist: [`docs/deploy-managed-stack.md`](../docs/deploy-managed-stack.md).

### Vercel (alternative API host)

[`pyproject.toml`](pyproject.toml) wires **FastAPI on Vercel** if you deploy this directory as its own Vercel project — see [`docs/deploy-vercel.md`](../docs/deploy-vercel.md).

## Layout

```
api/
  app/
    __init__.py
    main.py           # FastAPI app + routers
    config.py         # settings / env loading
    db.py             # engine + SessionLocal
    deps.py           # shared dependencies (`get_db`, …)
    models.py         # SQLAlchemy ORM
    catalog.py        # curated metric manifests (CSV↔dataset_id)
    schemas.py        # Pydantic response models
    routers/
      datasets.py     # `/datasets*` routes
  requirements.txt
  railway.toml      # Railway start command (Root Directory = api)
  pyproject.toml    # optional Vercel FastAPI entrypoint
  README.md
```
