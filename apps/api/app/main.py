from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.infrastructure.database.session import (
    check_database_connection,
    close_database_connections,
)
from app.interfaces.http.health import router as health_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Validate database connectivity on startup and close pools on shutdown."""

    check_database_connection()
    try:
        yield
    finally:
        close_database_connections()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    return app


app = create_app()
