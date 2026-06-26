"""Typed application exceptions.

Routes and services should raise these exceptions instead of leaking framework
or persistence exceptions through the API boundary.
"""


class BaseAppException(Exception):  # noqa: N818 - name is part of the architecture contract.
    """Base exception for expected application failures."""

    status_code: int = 500
    code: str = "internal_error"
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message or self.message)
        self.message = message or self.message
        self.code = code or self.code
        self.details = details or {}


class ValidationException(BaseAppException):
    """Raised when input passes transport parsing but violates application rules."""

    status_code = 422
    code = "validation_error"
    message = "The request is invalid."


class AuthenticationException(BaseAppException):
    """Raised when a request cannot be authenticated."""

    status_code = 401
    code = "authentication_error"
    message = "Authentication is required."


class AuthorizationException(BaseAppException):
    """Raised when a principal is not allowed to perform an action."""

    status_code = 403
    code = "forbidden"
    message = "You do not have permission."


class ResourceNotFoundException(BaseAppException):
    """Raised when a requested resource does not exist or is inaccessible."""

    status_code = 404
    code = "resource_not_found"
    message = "The requested resource was not found."


class ConflictException(BaseAppException):
    """Raised when a request conflicts with the current resource state."""

    status_code = 409
    code = "conflict"
    message = "The request conflicts with the current resource state."


class ExternalServiceException(BaseAppException):
    """Raised when a dependency outside RepoMind AI fails."""

    status_code = 502
    code = "external_service_error"
    message = "An external service failed."
