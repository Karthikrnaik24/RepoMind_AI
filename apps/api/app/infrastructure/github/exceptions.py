"""Typed GitHub integration exceptions."""

from datetime import datetime

from app.core.exceptions import (
    AuthenticationException,
    ExternalServiceException,
    ResourceNotFoundException,
)


class GitHubUnauthorized(AuthenticationException):
    """Raised when GitHub rejects or lacks usable OAuth credentials."""

    code = "github_unauthorized"
    message = "GitHub authentication is required."


class GitHubProviderNotLinked(GitHubUnauthorized):
    """Raised when the authenticated user has no linked GitHub identity."""

    code = "github_provider_not_linked"
    message = "GitHub is not linked for this account."


class GitHubTokenUnavailable(GitHubUnauthorized):
    """Raised when a linked GitHub identity has no available provider token."""

    code = "github_reconnect_required"
    message = "Reconnect GitHub to refresh repository access."


class GitHubRateLimited(ExternalServiceException):
    """Raised when GitHub rate limits the current token or integration."""

    status_code = 429
    code = "github_rate_limited"
    message = "GitHub rate limit exceeded."

    def __init__(self, message: str | None = None, *, reset_at: datetime | None = None) -> None:
        details = {"reset_at": reset_at.isoformat()} if reset_at else None
        super().__init__(message, code=self.code, details=details)
        self.reset_at = reset_at


class GitHubNotFound(ResourceNotFoundException):
    """Raised when a GitHub resource cannot be found or accessed."""

    code = "github_not_found"
    message = "The requested GitHub resource was not found."


class GitHubUnavailable(ExternalServiceException):
    """Raised when GitHub is unavailable, slow, or returns an unexpected response."""

    code = "github_unavailable"
    message = "GitHub is temporarily unavailable."
