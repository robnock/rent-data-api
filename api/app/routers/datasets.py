"""Dataset catalog + observations HTTP API."""

from __future__ import annotations

import csv
import io
from collections.abc import Iterator
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth_api_key import require_api_key_for_datasets
from app.catalog import METRICS_BY_ID
from app.db import SessionLocal
from app.deps import get_db
from app.models import Dataset, Observation
from app.schemas import (
    DatasetDetail,
    DatasetSummary,
    ObservationColumn,
    ObservationItem,
    ObservationPage,
    serialize_observation_value,
)

router = APIRouter(
    prefix="/datasets",
    tags=["datasets"],
    dependencies=[Depends(require_api_key_for_datasets)],
)

DEFAULT_LIMIT = 100
MAX_LIMIT = 1000

_FIPS_DESCRIPTION = (
    "Location FIPS code as a string; leading zeros preserved (matches `data/` CSVs)."
)

_PERIOD_DESCRIPTION = (
    "Month anchor for the observation (calendar month, ISO week-year safe as YYYY-MM-01)."
)

_DATE_META_DESCRIPTION = (
    "Publication / extract date for this catalog revision (`date_updated_at` column "
    "in source CSVs; repeated on every export row)."
)


def _fallback_value_description() -> str:
    """When a warehouse dataset id is unknown to `app.catalog`."""
    return (
        "Numeric observation from the warehouse; see dataset `description` and `unit` "
        "for semantics."
    )


def _observation_columns(dataset_id: str) -> list[ObservationColumn]:
    meta = METRICS_BY_ID.get(dataset_id)
    value_desc = (
        meta.value_description if meta is not None else _fallback_value_description()
    )

    return [
        ObservationColumn(
            name="location_fips_code",
            logical_type="string",
            description=_FIPS_DESCRIPTION,
        ),
        ObservationColumn(
            name="period",
            logical_type="date",
            description=_PERIOD_DESCRIPTION,
        ),
        ObservationColumn(
            name="value",
            logical_type="number",
            nullable=True,
            description=value_desc,
        ),
        ObservationColumn(
            name="date_updated_at",
            logical_type="date",
            nullable=True,
            description=_DATE_META_DESCRIPTION,
        ),
    ]


def _dataset_or_404(session: Session, dataset_id: str) -> Dataset:
    row = session.get(Dataset, dataset_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return row


def _observation_filter_clauses(
    dataset_id: str,
    fips_code: str | None,
    period_from: date | None,
    period_to: date | None,
) -> list[object]:
    clauses: list[object] = [Observation.dataset_id == dataset_id]
    if fips_code is not None:
        clauses.append(Observation.fips_code == fips_code.strip())
    if period_from is not None:
        clauses.append(Observation.period >= period_from)
    if period_to is not None:
        clauses.append(Observation.period <= period_to)
    return clauses


@router.get("", response_model=list[DatasetSummary])
def list_datasets(db: Annotated[Session, Depends(get_db)]) -> list[Dataset]:
    return list(db.scalars(select(Dataset).order_by(Dataset.id)))


@router.get("/{dataset_id}", response_model=DatasetDetail)
def get_dataset(dataset_id: str, db: Annotated[Session, Depends(get_db)]) -> DatasetDetail:
    ds = _dataset_or_404(db, dataset_id)
    summary = DatasetSummary.model_validate(ds)
    return DatasetDetail(
        **summary.model_dump(),
        description=ds.description,
        observation_columns=_observation_columns(dataset_id),
    )


@router.get("/{dataset_id}/observations", response_model=ObservationPage)
def list_observations(
    dataset_id: str,
    db: Annotated[Session, Depends(get_db)],
    fips_code: Annotated[
        str | None,
        Query(description="Restrict to one `location_fips_code`."),
    ] = None,
    period_from: Annotated[
        date | None,
        Query(description="Inclusive lower bound on `period`."),
    ] = None,
    period_to: Annotated[
        date | None,
        Query(description="Inclusive upper bound on `period`."),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ObservationPage:
    _dataset_or_404(db, dataset_id)
    if (
        period_from is not None
        and period_to is not None
        and period_from > period_to
    ):
        raise HTTPException(status_code=400, detail="period_from must be ≤ period_to.")

    clauses = _observation_filter_clauses(
        dataset_id, fips_code, period_from, period_to
    )
    total_stmt = select(func.count()).select_from(Observation).where(*clauses)
    total = db.scalar(total_stmt) or 0

    page_stmt = (
        select(Observation)
        .where(*clauses)
        .order_by(Observation.fips_code, Observation.period)
        .limit(limit)
        .offset(offset)
    )
    rows = db.scalars(page_stmt).all()
    items = [
        ObservationItem(
            location_fips_code=o.fips_code,
            period=o.period,
            value=serialize_observation_value(o.value),
        )
        for o in rows
    ]
    return ObservationPage(
        items=items,
        total=int(total),
        limit=limit,
        offset=offset,
    )


@router.get("/{dataset_id}/observations.csv")
def download_observations_csv(
    dataset_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> StreamingResponse:
    """Streaming export matching catalog CSV layout (RFC 4180-safe via `csv`)."""
    ds = _dataset_or_404(db, dataset_id)
    release = (
        ds.current_release_date.isoformat() if ds.current_release_date else ""
    )

    def byte_chunks() -> Iterator[bytes]:
        with SessionLocal() as session:
            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerow(
                ["location_fips_code", "period", "value", "date_updated_at"]
            )
            yield buf.getvalue().encode("utf-8")

            stmt = (
                select(Observation)
                .where(Observation.dataset_id == dataset_id)
                .order_by(Observation.fips_code, Observation.period)
            )
            batch_size = 2_048
            for obs in session.scalars(stmt).yield_per(batch_size):
                buf.seek(0)
                buf.truncate(0)
                serialized = serialize_observation_value(obs.value)
                writer.writerow(
                    [
                        obs.fips_code,
                        obs.period.isoformat(),
                        "" if serialized is None else serialized,
                        release,
                    ]
                )
                yield buf.getvalue().encode("utf-8")

    disposition = f'attachment; filename="{dataset_id}.csv"'
    return StreamingResponse(
        byte_chunks(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": disposition},
    )
