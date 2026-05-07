"""Runtime configuration for the API.

Values are read from environment variables (typically loaded from a local
`.env` file at the repo root). See `.env.example` for the supported keys.
"""

from __future__ import annotations

import json
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_ORIGINS = ["http://localhost:3000"]


def _parse_cors_allow_origins(value: str) -> list[str]:
    """Comma-separated, JSON array, or empty → list of origins."""
    text = value.strip()
    if not text:
        return list(_DEFAULT_ORIGINS)
    if text.startswith("["):
        parsed = json.loads(text)
        if not isinstance(parsed, list):
            msg = "CORS_ALLOW_ORIGINS JSON must be an array of strings"
            raise ValueError(msg)
        return [str(item).strip() for item in parsed if str(item).strip()]
    return [part.strip() for part in text.split(",") if part.strip()]


class Settings(BaseSettings):
    """`CORS_ALLOW_ORIGINS` is read as a plain string so empty/comma values work.

    pydantic-settings applies JSON decoding to `list[...]` env values before
    validators run, which breaks `CORS_ALLOW_ORIGINS=` and comma-separated lists.
    """

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Econ Data API"
    app_version: str = "0.1.0"

    database_url: str = Field(
        default="postgresql+psycopg://localhost:5432/econ_data",
        description="SQLAlchemy URL for the Postgres database.",
    )

    api_auth_required: bool = Field(
        default=False,
        description="When true, `/datasets*` requires a valid `X-API-Key` (see `scripts/issue_api_key.py`).",
    )

    cors_allow_origins_env: str = Field(
        default="http://localhost:3000",
        validation_alias="cors_allow_origins",
        description="Comma-separated origins, JSON array, or empty → localhost:3000.",
    )

    @computed_field
    @property
    def cors_allow_origins(self) -> list[str]:
        return _parse_cors_allow_origins(self.cors_allow_origins_env)


settings = Settings()
