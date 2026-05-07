"""API key verification for `/datasets*` routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api_key_hash import hash_api_key
from app.config import settings
from app.deps import get_db
from app.models import ApiKey

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key_for_datasets(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    x_api_key: Annotated[str | None, Security(api_key_header)],
) -> None:
    token = (x_api_key or "").strip() or None

    def active_key_row() -> ApiKey | None:
        if token is None:
            return None
        digest = hash_api_key(token)
        return db.scalar(
            select(ApiKey).where(
                ApiKey.key_hash == digest,
                ApiKey.revoked_at.is_(None),
            ),
        )

    if not settings.api_auth_required:
        if token is None:
            return
        row = active_key_row()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid X-API-Key.",
            )
        request.state.api_key_id = row.id
        return

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key.",
        )
    row = active_key_row()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid X-API-Key.",
        )
    request.state.api_key_id = row.id
