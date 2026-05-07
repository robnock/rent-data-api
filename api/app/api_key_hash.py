"""Deterministic hash for API key lookup (never store plaintext keys)."""

from __future__ import annotations

import hashlib


def hash_api_key(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()
