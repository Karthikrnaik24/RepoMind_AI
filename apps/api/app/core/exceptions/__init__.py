"""Application exception hierarchy and FastAPI handlers."""

from app.core.exceptions.handlers import register_exception_handlers
from app.core.exceptions.types import (
    AuthorizationException,
    BaseAppException,
    ConflictException,
    ExternalServiceException,
    ResourceNotFoundException,
    ValidationException,
)

__all__ = [
    "AuthorizationException",
    "BaseAppException",
    "ConflictException",
    "ExternalServiceException",
    "ResourceNotFoundException",
    "ValidationException",
    "register_exception_handlers",
]
