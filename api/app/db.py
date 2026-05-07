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


def _ipv4_hostaddr(database_url: str) -> str | None:
    """Return an IPv4 address for a hostname, if available.

    Some hosts (notably managed Postgres endpoints) return an IPv6 AAAA record.
    Railway's networking may not have IPv6 egress, causing connection attempts to
    fail with "Network is unreachable". If an IPv4 A record exists, pass it as
    libpq's `hostaddr` so psycopg connects over IPv4.
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


_hostaddr = _ipv4_hostaddr(settings.database_url)
_connect_args = {"hostaddr": _hostaddr} if _hostaddr else {}

engine = create_engine(
    settings.database_url,
    future=True,
    pool_pre_ping=True,
    connect_args=_connect_args,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)
