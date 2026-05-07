# Go live: Vercel (web + API) + hosted Postgres

> **Preferred stack for this repo is Vercel + Railway + Supabase** — see
> **[`deploy-managed-stack.md`](deploy-managed-stack.md)**. This page covers deploying **both**
> Next.js and FastAPI on **Vercel** (two projects) if you do not use Railway.

Do these steps **in order**. Vercel cannot see your laptop Postgres — you need a **cloud
database** first, then you point the API at it, load data, then ship the website.

## 0. Create hosted Postgres (Neon is the quickest)

1. Sign up at [Neon](https://neon.tech) (or use Supabase / Vercel Postgres / etc.).
2. Create a project and database; copy the **connection string** (Postgres URL).
3. For SQLAlchemy + psycopg3, the URL should look like:

   `postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require`

   If the host only gives `postgresql://...`, add `+psycopg` after `postgresql` and add
   `?sslmode=require` if the provider requires SSL.

4. **Save this as `DATABASE_URL`** — you will use it in Vercel (API), in the script below,
   and optionally in GitHub **Secrets** for CI.

## 1. One-time: schema + data in that database

From a clone of this repo on your machine (with `api/.venv` and `pip install -r api/requirements.txt`):

```bash
export DATABASE_URL='postgresql+psycopg://...'   # your Neon string
./scripts/sync_prod_database.sh
```

This runs **migrations** and **ingest** (full rebuild from `data/`).  
Migrations only: `SKIP_INGEST=1 ./scripts/sync_prod_database.sh`

**Or** use GitHub Actions (after you add **`DATABASE_URL`** in the repo’s **Settings →
Secrets and variables → Actions**):

- **Actions → “Prod database migrate” → Run workflow** (migrations only)
- **Actions → “Prod database ingest” → Run workflow** (load CSVs; run after migrate)

## 2. Deploy the API (Vercel, root = `api`)

1. [New Project](https://vercel.com/new) → import this GitHub repo.
2. **Root Directory** → **`api`**.
3. **Environment variables** (at least **Production**):

   | Name | Value |
   | --- | --- |
   | `DATABASE_URL` | Same as above (Neon). |
   | `CORS_ALLOW_ORIGINS` | Your **future** site origin(s), comma-separated. For the first deploy use the placeholder Vercel will give the web app, e.g. `https://your-web.vercel.app` — you can add your custom domain later and update this. |
   | `API_AUTH_REQUIRED` | `false` if anyone may call `/datasets` without a key; `true` if only clients with keys (browsers still use the Next.js site, which uses `ECON_API_KEY` — see below). |

4. Deploy. Open `https://<api-project>.vercel.app/healthz` and `/docs` — if 200, the API is public.

## 3. (Optional) API key in production

Only if **`API_AUTH_REQUIRED=true`**:

```bash
export DATABASE_URL='postgresql+psycopg://...'
source api/.venv/bin/activate
python3 scripts/issue_api_key.py "prod website"
```

Put the printed key in the **web** project as **`ECON_API_KEY`** (next step). Do **not**
put it in `NEXT_PUBLIC_*`.

## 4. Deploy the website (Vercel, root = `web`)

1. **Another** Vercel project → same repo.
2. **Root Directory** → **`web`**.
3. **Environment variables**:

   | Name | Value |
   | --- | --- |
   | `NEXT_PUBLIC_API_BASE_URL` | The **API** URL from step 2, e.g. `https://<api>.vercel.app` |
   | `ECON_API_KEY` | Only if `API_AUTH_REQUIRED=true` — the key from step 3. |

4. Deploy. Your **public URL** is the web project’s production domain — share that.

## 5. Verify end-to-end

- Browser: open the **web** URL → **Datasets** → open a dataset → **Download CSV**.
- API: `curl https://<api>.vercel.app/datasets` — use `-H "X-API-Key: …"` only if auth is required.

## Limits and notes

- **CSV streaming** on large tables may hit [Vercel function limits](https://vercel.com/docs/functions/limitations); if exports fail, revisit hosting or chunking later.
- **Related Projects** on Vercel can wire preview deployments together — see [Monorepos](https://vercel.com/docs/monorepos).
- More detail on env vars: `web/.env.production.example`.
