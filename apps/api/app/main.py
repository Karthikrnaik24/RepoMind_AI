from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.infrastructure.database.session import (
    check_database_connection,
    close_database_connections,
)
from app.interfaces.api.v1 import api_v1_router
from app.interfaces.http.health import router as health_router
from app.middleware import ErrorHandlingMiddleware, LoggingMiddleware, RequestIdMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Validate database connectivity on startup and close pools on shutdown."""

    if app.state.settings.database_check_on_startup:
        check_database_connection()
    try:
        yield
    finally:
        close_database_connections()


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )
    app.state.settings = settings
    register_exception_handlers(app)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(api_v1_router)
    return app


app = create_app()
