"""FastAPI entrypoint for the Econ Data API."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.openapi import attach_openapi
from app.routers import datasets
from app.usage_log import record_usage

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Public catalog and API for rental market data. "
        "v1 is experimental; endpoints may change without notice."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

attach_openapi(app)


@app.middleware("http")
async def log_dataset_api_usage(request: Request, call_next):
    response = await call_next(request)
    key_id = getattr(request.state, "api_key_id", None)
    if key_id is not None and request.url.path.startswith("/datasets"):
        record_usage(
            api_key_id=key_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        )
    return response


app.include_router(datasets.router)


@app.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    """Liveness probe. Returns 200 if the API process is running."""
    return {"status": "ok"}


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }
