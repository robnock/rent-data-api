# Working conventions

These rules apply to humans and to any AI agents (Cursor, etc.) editing this
repo. Read this first before making changes.

## Stack

- **Web**: Next.js (App Router) + TypeScript + Tailwind. No `.js`/`.jsx`
  source files. Lives in `web/`.
- **API**: Python FastAPI. Lives in `api/`. Uses a project-local
  virtualenv at `api/.venv`. Dependencies in `api/requirements.txt`.
- **Database**: Local PostgreSQL via Homebrew. **No Docker.**
- **Ingest**: Plain Python in `ingest/`, runs against the same Postgres.

## Source data

- Authoritative CSVs live in `data/` and are **committed** to git so the
  monthly diff is the changelog. Do not gitignore them.
- Filenames are **stable** (`rent_growth_yoy.csv`, not
  `rent_growth_yoy_2026_04.csv`); the release date lives inside the file
  as the `date_updated_at` column.
- `fips_code`s are **strings with leading zeros preserved**
  (`"06"` for California, `"06037"` for LA County). Never coerce to int.

## Workflow

- One PR = one logical change. Keep diffs small and reviewable.
- Commit messages explain **why**, not just what.
- Do not commit secrets. `.env` is gitignored; `.env.example` is committed.
- Before merging, run:
  - `python3 scripts/validate_data.py` (passes)
  - `cd api && source .venv/bin/activate && python -c "from app.main import app"` (no import errors)
  - `cd web && npm run build` (passes)

## Style

- TypeScript: strict mode is on; prefer typed props and explicit return types
  on exported functions.
- Python: type hints on public functions; `from __future__ import annotations`
  at the top of new modules.
- Avoid comments that just narrate the code. Comments should explain intent,
  trade-offs, or non-obvious constraints.

## Out of scope (for now)

- Cloud deployment (local-only through Stage 4).
- Point-in-time queries / historical revisions.
- The `summary` dataset.

If a task requires changing any of the above, pause and confirm with the
maintainer before proceeding.
