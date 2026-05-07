"""SQLAlchemy ORM models for the warehouse.

Three tables:

- `locations` — one row per location (FIPS-keyed dimension).
- `datasets`  — one row per metric present in Postgres (configured in
  `catalog.py`; CSV-backed metrics load when `{dataset_id}.csv` exists).
- `observations` — tall fact table; one row per (dataset, location, period).

`observations.value` may be **NULL** when the source CSV uses `NA`/empty markers.

Each monthly refresh wipes all three tables and reloads from the source CSVs.
There is no point-in-time history.

`api_keys` and `api_usage_log` are **not** truncated by ingest.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Location(Base):
    __tablename__ = "locations"

    fips_code: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    location_type: Mapped[str] = mapped_column(String, nullable=False)
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    state: Mapped[str | None] = mapped_column(String, nullable=True)
    county: Mapped[str | None] = mapped_column(String, nullable=True)
    metro: Mapped[str | None] = mapped_column(String, nullable=True)

    __table_args__ = (Index("ix_locations_type", "location_type"),)


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    current_release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    earliest_period: Mapped[date | None] = mapped_column(Date, nullable=True)
    latest_period: Mapped[date | None] = mapped_column(Date, nullable=True)


class Observation(Base):
    __tablename__ = "observations"

    dataset_id: Mapped[str] = mapped_column(
        String, ForeignKey("datasets.id"), primary_key=True
    )
    fips_code: Mapped[str] = mapped_column(
        String, ForeignKey("locations.fips_code"), primary_key=True
    )
    period: Mapped[date] = mapped_column(Date, primary_key=True)
    value: Mapped[Decimal | None] = mapped_column(Numeric(20, 8), nullable=True)

    __table_args__ = (
        Index("ix_observations_dataset_period", "dataset_id", "period"),
        Index("ix_observations_fips_period", "fips_code", "period"),
    )


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    label: Mapped[str] = mapped_column(String, nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class ApiUsageLog(Base):
    __tablename__ = "api_usage_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    api_key_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("api_keys.id", ondelete="SET NULL"),
        nullable=True,
    )
    method: Mapped[str] = mapped_column(String(8), nullable=False)
    path: Mapped[str] = mapped_column(String(512), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_api_usage_log_api_key_created", "api_key_id", "created_at"),
    )
