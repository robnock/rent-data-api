"""Observations.value may be null (source CSV uses NA sentinel).

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-06
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "observations",
        "value",
        existing_type=sa.Numeric(20, 8),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "observations",
        "value",
        existing_type=sa.Numeric(20, 8),
        nullable=False,
    )
