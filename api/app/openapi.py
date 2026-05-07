"""OpenAPI customization (API key scheme when auth is enforced)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.config import settings


def attach_openapi(app: FastAPI) -> None:
    def _openapi() -> dict:
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        schema.setdefault("components", {}).setdefault("securitySchemes", {})[
            "ApiKeyAuth"
        ] = {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "Issue keys with `python3 scripts/issue_api_key.py \"label\"` after migrations.",
        }
        if settings.api_auth_required:
            for path_key, item in schema.get("paths", {}).items():
                if not path_key.startswith("/datasets"):
                    continue
                for method in ("get", "head"):
                    op = item.get(method)
                    if op is None:
                        continue
                    op["security"] = [{"ApiKeyAuth": []}]
        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = _openapi  # type: ignore[method-assign]
