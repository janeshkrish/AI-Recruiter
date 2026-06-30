from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.api.router import api_router
from backend.app.core.config import get_settings
from backend.app.core.errors import register_exception_handlers
from backend.app.core.logging import configure_logging
from backend.app.core.middleware import register_middleware
from backend.app.dependencies import get_candidate_repository


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the dataset at startup so UI requests fail fast if data is missing.
    get_candidate_repository().ensure_loaded()
    yield


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Production API wrapper for the deterministic offline Redrob ranking pipeline. "
            "The ranking service performs no network calls during candidate scoring."
        ),
        lifespan=lifespan,
    )
    register_middleware(app, settings)
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/")
    async def root() -> dict:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "frontend": "http://127.0.0.1:5173",
            "docs": "http://127.0.0.1:8000/docs",
            "health": "http://127.0.0.1:8000/api/health",
            "message": "This is the backend API. Open the frontend URL for the app UI.",
        }

    return app


app = create_app()
