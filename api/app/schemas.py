"""Pydantic response models for the public HTTP API."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ObservationColumn(BaseModel):
    """Describes one logical column in a dataset's observation exports."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(description="CSV / JSON field name.")
    logical_type: str = Field(description="Semantic type hint (string, date, number, …).")
    nullable: bool = Field(default=False)
    description: str


class DatasetSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    display_name: str
    unit: str
    row_count: int | None = None
    earliest_period: date | None = None
    latest_period: date | None = None
    current_release_date: date | None = None


class DatasetDetail(DatasetSummary):
    description: str
    observation_columns: list[ObservationColumn] = Field(
        description="Column meanings for `/observations` JSON and CSV exports.",
    )


class ObservationItem(BaseModel):
    """One observation row aligned with catalog CSV headers."""

    location_fips_code: str
    period: date
    value: str | None = Field(
        default=None,
        description="Observation as a decimal string; null when absent in source.",
    )


class ObservationPage(BaseModel):
    items: list[ObservationItem]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)


def serialize_observation_value(value: Decimal | float | None) -> str | None:
    """Serialize ORM Numeric to a concise decimal string."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return format(value.normalize(), "f").rstrip("0").rstrip(".")
    return str(value)
