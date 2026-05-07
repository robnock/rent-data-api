# Deploy: Vercel (web) + Railway (API) + Supabase (Postgres)

Recommended production layout: **Next.js on Vercel**, **FastAPI on Railway** (long-lived
process, better for streaming CSV than serverless-only API hosts), **Postgres on Supabase**.

This repo does **not** use Supabase Auth or Edge Functions — only Supabase **Database**.

```mermaid
flowchart LR
  users[Users]
  vercel[Vercel_Next]
  railway[Railway_API]
  supa[(Supabase_DB)]

  users --> vercel
  vercel --> railway
  railway --> supa
```

---

## Phase A — Supabase (Postgres)

1. Create a project at [supabase.com](https://supabase.com).
2. Open **Project Settings → Database**.
3. Copy the **connection string** (URI). Two common modes:
   - **Direct** (often port **5432**) — reliable for **Alembic** migrations and DDL.
   - **Transaction pooler** (often port **6543**) — fine for many app workloads; if migrations fail, switch to the **direct** URI for `alembic upgrade` only.

4. Adapt the URI for **SQLAlchemy + psycopg3** (`DATABASE_URL` everywhere):

   - Dashboard strings usually look like  
     `postgresql://postgres.[ref]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres`
   - Use the **`postgresql+psycopg`** scheme for this codebase:

     `postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE?sslmode=require`

   - Replace `USER`, `PASSWORD`, `HOST`, `PORT`, `DATABASE` from the Supabase UI. URL-encode special characters in the password.

5. Store **`DATABASE_URL`** in your password manager — never commit it.

---

## Phase B — Migrations + ingest (Supabase must exist)

Point **`DATABASE_URL`** at Supabase, then load schema and data **before** expecting a
working public API.

**From your laptop** (requires `api/.venv` + `pip install -r api/requirements.txt`):

```bash
export DATABASE_URL='postgresql+psycopg://...'
./scripts/sync_prod_database.sh
```

Migrations only: `SKIP_INGEST=1 ./scripts/sync_prod_database.sh`

**From GitHub Actions:** add repository secret **`DATABASE_URL`**, then run manually:

- **Prod database migrate**
- **Prod database ingest**

Workflows live under [`.github/workflows/`](../.github/workflows/).

---

## Phase C — Railway (FastAPI)

1. [Railway](https://railway.app) → **New Project** → **Deploy from GitHub repo**.
2. Select this repository.
3. **Service settings → Root Directory** → **`api`** (critical: `requirements.txt`, `Dockerfile`, and package `app` must sit at the build root — without this step, Docker/Nixpacks often fails in ~15s).
4. Railway reads **[`api/railway.toml`](../api/railway.toml)** — build uses **[`api/Dockerfile`](../api/Dockerfile)** (`pip install`, then `uvicorn` on **`$PORT`**).
5. **Variables** (same semantics as [`.env.example`](../.env.example)):

   | Name | Notes |
   | --- | --- |
   | `DATABASE_URL` | Same Supabase URI as Phase A. |
   | `CORS_ALLOW_ORIGINS` | Your **Vercel** production URL(s), comma-separated, e.g. `https://your-app.vercel.app`. Add preview origins if needed. |
   | `API_AUTH_REQUIRED` | `false` for fully public `/datasets`; `true` to require `X-API-Key`. |

6. Deploy → copy the **public HTTPS URL** (e.g. `*.up.railway.app`).
7. Smoke test: `curl https://<railway-host>/healthz` and `/docs`.

**Build failed (“Failed to build an image”)** — open **Deployments → View logs** and confirm: (a) Root Directory is exactly **`api`**, not the repo root; (b) the log shows Docker building from `requirements.txt`. If Root Directory were wrong you would typically see no `requirements.txt` or wrong working directory.

Optional: generate an API key against Supabase (same **`DATABASE_URL`**):

```bash
export DATABASE_URL='postgresql+psycopg://...'
source api/.venv/bin/activate
python3 scripts/issue_api_key.py "production"
```

---

## Phase D — Vercel (Next.js only)

1. **New Project** → same repo → **Root Directory `web`**.
2. **Environment variables**:

   | Name | Value |
   | --- | --- |
   | `NEXT_PUBLIC_API_BASE_URL` | **Railway** API base URL from Phase C (no trailing slash required). |
   | `ECON_API_KEY` | Required only when **`API_AUTH_REQUIRED=true`** on Railway — same plaintext key issued above; **never** `NEXT_PUBLIC_*`. |

3. Deploy. Public users hit the **Vercel URL**; Next.js server components call Railway using
   [`withBackendApiHeaders`](../web/src/lib/backend-fetch.ts); browser download links use
   [`/api/datasets/...`](../web/src/app/api/datasets/) proxies.

Mirror prod vars locally in **`web/.env.local`** for `npm run dev` against production-like
settings.

---

## Phase E — Verification

- Browser: Vercel URL → **Datasets** → dataset detail → **Download CSV** / sample JSON.
- API: `curl https://<railway-host>/datasets` (add `-H "X-API-Key: …"` if auth enabled).

---

## Alternative: API on Vercel only

If you prefer both Next and FastAPI on Vercel (two projects), see
[`deploy-vercel.md`](deploy-vercel.md). Railway avoids serverless limits on large CSV streams.

---

## Risks

- Very large **CSV** exports may still hit timeouts — monitor Railway logs.
- Rotate **`DATABASE_URL`** if exposed; rotate API keys via DB if **`ECON_API_KEY`** leaks.
