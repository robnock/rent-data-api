#!/usr/bin/env python3
"""Structural validation for source CSVs in `data/`.

Runs sanity checks without touching the database:

1. Only expected CSV filenames are present (whitelist from `api/app/catalog.py`).
2. `locations.csv` has unique `location_fips_code` values.
3. Each on-disk metric CSV (same canonical columns as `rent_growth_yoy.csv`):
   - every `location_fips_code` exists in `locations.csv`
   - `(location_fips_code, period)` is unique

Missing configured metric CSVs log an info line — they publish when extracts land.

Uses only Python stdlib for path setup; importing `api.app.catalog` requires the repo
structure (no pip deps beyond executing Python).
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"

LOCATIONS_CSV = DATA_DIR / "locations.csv"


def _catalog():
    sys.path.insert(0, str(REPO_ROOT / "api"))
    from app.catalog import METRICS, allowed_data_csv_filenames

    return METRICS, allowed_data_csv_filenames()


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def info(msg: str) -> None:
    print(f"  {msg}")


def load_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        fail(f"Missing file: {path.relative_to(REPO_ROOT)}")
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def check_known_csv_filenames(allowed_names: frozenset[str]) -> None:
    for path in DATA_DIR.glob("*.csv"):
        if path.name not in allowed_names:
            fail(f"Unexpected CSV in data/: {path.name} (whitelist={sorted(allowed_names)})")


def check_locations_unique(rows: list[dict[str, str]]) -> set[str]:
    fips = [r["location_fips_code"] for r in rows]
    counts = Counter(fips)
    dupes = [k for k, v in counts.items() if v > 1]
    if dupes:
        fail(
            f"locations.csv has duplicate location_fips_code values: {dupes[:5]}"
            + ("..." if len(dupes) > 5 else ""),
        )
    info(f"locations.csv: {len(fips)} unique locations")
    return set(fips)


def check_observations_for_file(
    path: Path,
    rows: list[dict[str, str]],
    known_fips: set[str],
) -> None:
    label = path.relative_to(REPO_ROOT).as_posix()

    observed_cols = set(rows[0].keys()) if rows else set()
    expected = {"location_fips_code", "period", "value", "date_updated_at"}
    if observed_cols != expected:
        fail(
            f"{label}: expected columns {sorted(expected)}, got {sorted(observed_cols)}",
        )

    seen: set[tuple[str, str]] = set()
    orphan_fips: set[str] = set()
    dupe_keys: list[tuple[str, str]] = []

    for r in rows:
        fips = r["location_fips_code"].strip()
        period = r["period"].strip()
        if fips not in known_fips:
            orphan_fips.add(fips)
        key = (fips, period)
        if key in seen:
            dupe_keys.append(key)
        seen.add(key)

    if orphan_fips:
        sample = sorted(orphan_fips)[:5]
        fail(
            f"{label}: {len(orphan_fips)} location_fips_code value(s) not in "
            f"locations.csv. Sample: {sample}",
        )
    if dupe_keys:
        sample = dupe_keys[:5]
        fail(f"{label}: {len(dupe_keys)} duplicate (location_fips_code, period). Sample: {sample}")

    info(
        f"{label}: {len(rows)} observations, schema OK, duplicates none, orphans none",
    )


def main() -> None:
    print("Validating source CSVs…")

    metrics, allowed = _catalog()

    if not DATA_DIR.exists():
        fail(f"Missing data directory {DATA_DIR.relative_to(REPO_ROOT)}")

    check_known_csv_filenames(allowed)

    _, loc_rows = load_rows(LOCATIONS_CSV)
    known_fips = check_locations_unique(loc_rows)

    for metric in metrics:
        path = DATA_DIR / metric.csv_filename()
        if not path.exists():
            info(f"[skip] {metric.csv_filename()}: not present yet")
            continue
        _, obs_rows = load_rows(path)
        check_observations_for_file(path, obs_rows, known_fips)

    print("OK")


if __name__ == "__main__":
    main()
