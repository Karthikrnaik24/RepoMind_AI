"""Response DTOs."""

from app.interfaces.api.schemas.responses.admin import AdminPingResponse
from app.interfaces.api.schemas.responses.base import (
    ApiError,
    ApiFailureResponse,
    ApiSuccessResponse,
    failure_response,
    success_response,
)
from app.interfaces.api.schemas.responses.health import HealthData, StatusData
from app.interfaces.api.schemas.responses.identity import MeData, MeResponse

__all__ = [
    "AdminPingResponse",
    "ApiError",
    "ApiFailureResponse",
    "ApiSuccessResponse",
    "HealthData",
    "MeData",
    "MeResponse",
    "StatusData",
    "failure_response",
    "success_response",
]
