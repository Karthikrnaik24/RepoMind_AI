"""Request DTOs."""

from app.interfaces.api.schemas.requests.repository import (
    RegisterRepositoryRequest,
    UpdateRepositorySettingsRequest,
)

__all__ = ["RegisterRepositoryRequest", "UpdateRepositorySettingsRequest"]