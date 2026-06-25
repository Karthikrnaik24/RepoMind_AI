"""Versioned system health routes."""

from fastapi import APIRouter

from app.config.settings import get_settings
from app.interfaces.api.schemas.responses import (
    ApiSuccessResponse,
    HealthData,
    StatusData,
    success_response,
)

router = APIRouter(tags=["system"])


@router.get("/health", response_model=ApiSuccessResponse[HealthData])
def read_health() -> dict:
    """Return the standard health response envelope."""

    return success_response(HealthData(status="ok"))


@router.get("/status", response_model=ApiSuccessResponse[StatusData])
def read_status() -> dict:
    """Return versioned service metadata."""

    settings = get_settings()
    return success_response(
        StatusData(
            status="ok",
            database="configured",
            supabase="configured" if settings.is_supabase_configured else "missing",
            service="repomind-api",
            version=settings.app_version,
        ),
    )
