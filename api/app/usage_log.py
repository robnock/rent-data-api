"""Persist per-key request counts for `/datasets*` (best-effort; never raises)."""

from __future__ import annotations

import logging
from uuid import UUID

from app.db import SessionLocal
from app.models import ApiUsageLog

logger = logging.getLogger(__name__)


def record_usage(*, api_key_id: UUID, method: str, path: str, status_code: int) -> None:
    path_stored = path[:512]
    try:
        with SessionLocal() as session, session.begin():
            session.add(
                ApiUsageLog(
                    api_key_id=api_key_id,
                    method=method.upper()[:8],
                    path=path_stored,
                    status_code=status_code,
                ),
            )
    except Exception:
        logger.exception("api usage log insert failed")
