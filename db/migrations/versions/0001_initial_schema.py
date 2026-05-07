"""initial schema: locations, datasets, observations

Revision ID: 0001
Revises:
Create Date: 2026-04-30
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "locations",
        sa.Column("fips_code", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("location_type", sa.String(), nullable=False),
        sa.Column("population", sa.Integer(), nullable=True),
        sa.Column("state", sa.String(), nullable=True),
        sa.Column("county", sa.String(), nullable=True),
        sa.Column("metro", sa.String(), nullable=True),
    )
    op.create_index("ix_locations_type", "locations", ["location_type"])

    op.create_table(
        "datasets",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("current_release_date", sa.Date(), nullable=True),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("earliest_period", sa.Date(), nullable=True),
        sa.Column("latest_period", sa.Date(), nullable=True),
    )

    op.create_table(
        "observations",
        sa.Column("dataset_id", sa.String(), nullable=False),
        sa.Column("fips_code", sa.String(), nullable=False),
        sa.Column("period", sa.Date(), nullable=False),
        sa.Column("value", sa.Numeric(20, 8), nullable=False),
        sa.PrimaryKeyConstraint(
            "dataset_id", "fips_code", "period", name="pk_observations"
        ),
        sa.ForeignKeyConstraint(
            ["dataset_id"], ["datasets.id"], name="fk_observations_dataset"
        ),
        sa.ForeignKeyConstraint(
            ["fips_code"], ["locations.fips_code"], name="fk_observations_location"
        ),
    )
    op.create_index(
        "ix_observations_dataset_period",
        "observations",
        ["dataset_id", "period"],
    )
    op.create_index(
        "ix_observations_fips_period",
        "observations",
        ["fips_code", "period"],
    )


def downgrade() -> None:
    op.drop_index("ix_observations_fips_period", table_name="observations")
    op.drop_index("ix_observations_dataset_period", table_name="observations")
    op.drop_table("observations")
    op.drop_table("datasets")
    op.drop_index("ix_locations_type", table_name="locations")
    op.drop_table("locations")
