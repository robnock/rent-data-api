"""Database engine + session factory.

The engine is created once at import time using the `DATABASE_URL` from
`app.config.settings`. Both the API and the ingest scripts share this engine.
"""

from __future__ import annotations

import socket

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings


def _resolve_ipv4(database_url: str) -> str | None:
    """Return an IPv4 address for a hostname, if available.

    Some hosts (notably managed Postgres endpoints) return an IPv6 AAAA record.
    Railway's networking may not have IPv6 egress, causing connection attempts to
    fail with "Network is unreachable". If an IPv4 A record exists, we can use it
    directly as the connection host (works with `sslmode=require`).
    """

    host = make_url(database_url).host
    if not host:
        return None

    try:
        infos = socket.getaddrinfo(
            host,
            None,
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        )
    except OSError:
        return None

    if not infos:
        return None
    return infos[0][4][0]


_ipv4 = _resolve_ipv4(settings.database_url)
_url = make_url(settings.database_url)
if _ipv4:
    # Prefer hard-forcing IPv4 as the host to avoid any IPv6 attempts.
    # With `sslmode=require` (Supabase default), connecting via IP is OK.
    _url = _url.set(host=_ipv4)

engine = create_engine(
    _url,
    future=True,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)
