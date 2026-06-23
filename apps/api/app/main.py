from fastapi import FastAPI

from app.config.settings import get_settings
from app.interfaces.http.health import router as health_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
    )
    app.include_router(health_router)
    return app


app = create_app()
