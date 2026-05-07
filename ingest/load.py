"""Load warehouse tables from CSVs under `data/` (full rebuild).

Configurable metrics live in ``api/app/catalog.py``. Each metric publishes a CSV
named ``{dataset_id}.csv`` with columns:

``location_fips_code``, ``period``, ``value``, ``date_updated_at``

Run from repo root:

    cd /path/to/repo
    source api/.venv/bin/activate
    PYTHONPATH=api python -m ingest
"""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]

_DATA_DIR = _REPO_ROOT / "data"
_LOCATIONS_CSV = _DATA_DIR / "locations.csv"

_OBS_COLUMNS = frozenset(
    {"location_fips_code", "period", "value", "date_updated_at"},
)


def _ensure_api_on_path() -> None:
    api = _REPO_ROOT / "api"
    ap = str(api)
    if ap not in sys.path:
        sys.path.insert(0, ap)


def _empty_string_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    s = value.strip()
    return None if s == "" else s


def _parse_int(cell: str) -> int | None:
    s = cell.strip()
    return int(s) if s else None


def _parse_date_iso(cell: str, field_name: str) -> date:
    s = cell.strip()
    try:
        return datetime.fromisoformat(s).date()
    except ValueError as e:
        raise ValueError(f"{field_name}: invalid date {cell!r}") from e


def _parse_observation_value(cell: str) -> Decimal | None:
    s = cell.strip()
    if not s:
        return None
    token = s.upper()
    if token in {"NA", "N/A", "NULL", "#N/A"}:
        return None
    try:
        return Decimal(s)
    except Exception as e:
        raise ValueError(f"Invalid observation value: {cell!r}") from e


def _validate_obs_header(fieldnames: list[str] | None, csv_label: str) -> None:
    fields = frozenset(fieldnames or ())
    if fields != _OBS_COLUMNS:
        msg = (
            f"{csv_label}: column mismatch (expected {_OBS_COLUMNS!r}); "
            f"got {sorted(fields)!r}"
        )
        raise ValueError(msg)


@dataclass
class MetricObsChunk:
    obs_maps: list[dict[str, object]]
    earliest_period: date
    latest_period: date
    current_release_date: date


def _load_locations() -> list[dict[str, object]]:
    location_maps: list[dict[str, object]] = []
    with _LOCATIONS_CSV.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        loc_fields = set(reader.fieldnames or ())
        needed_loc = {
            "location_fips_code",
            "location_name",
            "location_type",
            "population",
            "state",
            "county",
            "metro",
        }
        if loc_fields != needed_loc:
            msg = (
                "locations.csv column set changed: "
                f"missing={needed_loc - loc_fields} extra={loc_fields - needed_loc}"
            )
            raise ValueError(msg)
        for row in reader:
            location_maps.append(
                {
                    "fips_code": row["location_fips_code"].strip(),
                    "name": row["location_name"].strip(),
                    "location_type": row["location_type"].strip(),
                    "population": _parse_int(row["population"]),
                    "state": _empty_string_to_none(row.get("state")),
                    "county": _empty_string_to_none(row.get("county")),
                    "metro": _empty_string_to_none(row.get("metro")),
                },
            )
    return location_maps


def _parse_metric_csv(path: Path, dataset_id: str, csv_label: str) -> MetricObsChunk:
    periods: list[date] = []
    release_dates: list[date] = []
    obs_maps: list[dict[str, object]] = []

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        _validate_obs_header(list(reader.fieldnames or []), csv_label)
        for row in reader:
            period = _parse_date_iso(row["period"], "period")
            released = _parse_date_iso(row["date_updated_at"], "date_updated_at")
            periods.append(period)
            release_dates.append(released)
            obs_maps.append(
                {
                    "dataset_id": dataset_id,
                    "fips_code": row["location_fips_code"].strip(),
                    "period": period,
                    "value": _parse_observation_value(row["value"]),
                },
            )

    if not periods:
        raise ValueError(f"{csv_label} contains zero observations.")

    earliest = min(periods)
    latest = max(periods)
    release = max(release_dates)

    return MetricObsChunk(
        obs_maps=obs_maps,
        earliest_period=earliest,
        latest_period=latest,
        current_release_date=release,
    )


def load() -> None:
    _ensure_api_on_path()
    from sqlalchemy import text

    from app.catalog import METRICS
    from app.db import SessionLocal
    from app.models import Dataset, Location, Observation

    location_maps = _load_locations()

    datasets: list[Dataset] = []
    obs_aggregate: list[dict[str, object]] = []

    for metric in METRICS:
        csv_path = _DATA_DIR / metric.csv_filename()
        if not csv_path.exists():
            print(
                f"[ingest] skip {metric.dataset_id}: missing "
                f"{csv_path.relative_to(_REPO_ROOT)}",
                file=sys.stderr,
            )
            continue

        csv_label = csv_path.relative_to(_REPO_ROOT).as_posix()
        chunk = _parse_metric_csv(csv_path, metric.dataset_id, csv_label)

        datasets.append(
            Dataset(
                id=metric.dataset_id,
                display_name=metric.display_name,
                description=metric.description,
                unit=metric.unit,
                current_release_date=chunk.current_release_date,
                row_count=len(chunk.obs_maps),
                earliest_period=chunk.earliest_period,
                latest_period=chunk.latest_period,
            ),
        )
        obs_aggregate.extend(chunk.obs_maps)

    if not datasets:
        msg = (
            "No metric CSV files found under data/. Populate at least one catalog CSV "
            f"({', '.join(m.csv_filename() for m in METRICS)})."
        )
        raise ValueError(msg)

    with SessionLocal() as session, session.begin():
        session.execute(
            text("TRUNCATE TABLE observations, datasets, locations CASCADE"),
        )
        session.bulk_insert_mappings(Location, location_maps)
        session.add_all(datasets)
        session.flush()
        session.bulk_insert_mappings(Observation, obs_aggregate)


def main() -> None:
    print(f"Ingest from {_REPO_ROOT} …")
    load()
    print("Done.")


if __name__ == "__main__":
    main()
