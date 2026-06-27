"""Response DTOs."""

from app.interfaces.api.schemas.responses.admin import AdminPingResponse
from app.interfaces.api.schemas.responses.base import (
    ApiError,
    ApiFailureResponse,
    ApiSuccessResponse,
    failure_response,
    success_response,
)
from app.interfaces.api.schemas.responses.github import (
    GitHubRepositoryOwnerResponse,
    GitHubRepositoryPermissionsResponse,
    GitHubRepositorySummaryResponse,
)
from app.interfaces.api.schemas.responses.health import HealthData, StatusData
from app.interfaces.api.schemas.responses.identity import MeData, MeResponse
from app.interfaces.api.schemas.responses.repository import (
    RegisteredRepositoryResponse,
    RepositoryUnregisterResponse,
)

__all__ = [
    "AdminPingResponse",
    "ApiError",
    "ApiFailureResponse",
    "ApiSuccessResponse",
    "GitHubRepositoryOwnerResponse",
    "GitHubRepositoryPermissionsResponse",
    "GitHubRepositorySummaryResponse",
    "HealthData",
    "MeData",
    "MeResponse",
    "RegisteredRepositoryResponse",
    "RepositoryUnregisterResponse",
    "StatusData",
    "failure_response",
    "success_response",
]