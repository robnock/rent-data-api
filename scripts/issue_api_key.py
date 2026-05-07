#!/usr/bin/env python3
"""Create an API key row and print the secret once (never committed).

Requires Postgres + migration `0003_api_keys_and_usage_log`. Run from repo root:

    source api/.venv/bin/activate
    python3 scripts/issue_api_key.py \"My laptop\"
"""

from __future__ import annotations

import secrets
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "api"))

from app.api_key_hash import hash_api_key  # noqa: E402
from app.db import SessionLocal  # noqa: E402
from app.models import ApiKey  # noqa: E402


def main() -> None:
    label = " ".join(sys.argv[1:]).strip() or "unnamed"
    plaintext = "econ_" + secrets.token_urlsafe(24)
    digest = hash_api_key(plaintext)
    key_id = uuid.uuid4()
    with SessionLocal() as session, session.begin():
        session.add(ApiKey(id=key_id, label=label, key_hash=digest))

    print(f"id: {key_id}")
    print(f"label: {label}")
    print(f"X-API-Key (copy to `.env`; shown once): {plaintext}")


if __name__ == "__main__":
    main()
