"""GitHub domain transfer objects.

These objects normalize GitHub API payloads before they reach application
services or future API routes. GitHub JSON should not leak past the
infrastructure boundary.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal


def _parse_datetime(value: Any) -> datetime | None:
    """Parse GitHub ISO timestamps while tolerating missing fields."""

    if not isinstance(value, str) or not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@dataclass(frozen=True)
class GitHubTokenStatus:
    """Safe token availability status that never includes secret values."""

    linked: bool
    token_available: bool
    provider: Literal["github"] = "github"


@dataclass(frozen=True)
class RepositoryOwner:
    """Normalized GitHub repository owner."""

    github_id: int
    login: str
    owner_type: str
    avatar_url: str | None = None
    html_url: str | None = None

    @classmethod
    def from_github_api(cls, payload: dict[str, Any]) -> "RepositoryOwner":
        """Build a repository owner from a GitHub API owner payload."""

        return cls(
            github_id=int(payload["id"]),
            login=str(payload["login"]),
            owner_type=str(payload.get("type") or "User"),
            avatar_url=payload.get("avatar_url"),
            html_url=payload.get("html_url"),
        )


@dataclass(frozen=True)
class RepositoryPermissions:
    """Normalized GitHub repository permissions for the current token."""

    admin: bool = False
    maintain: bool = False
    push: bool = False
    triage: bool = False
    pull: bool = False

    @classmethod
    def from_github_api(cls, payload: dict[str, Any] | None) -> "RepositoryPermissions":
        """Build permissions from GitHub's permissions object."""

        if not payload:
            return cls()
        return cls(
            admin=bool(payload.get("admin")),
            maintain=bool(payload.get("maintain")),
            push=bool(payload.get("push")),
            triage=bool(payload.get("triage")),
            pull=bool(payload.get("pull")),
        )


@dataclass(frozen=True)
class RepositoryLicense:
    """Normalized GitHub repository license metadata."""

    key: str
    name: str
    spdx_id: str | None = None
    url: str | None = None

    @classmethod
    def from_github_api(cls, payload: dict[str, Any] | None) -> "RepositoryLicense | None":
        """Build license metadata from GitHub's nullable license payload."""

        if not payload:
            return None
        return cls(
            key=str(payload["key"]),
            name=str(payload["name"]),
            spdx_id=payload.get("spdx_id"),
            url=payload.get("url"),
        )


@dataclass(frozen=True)
class RepositoryLanguage:
    """Normalized GitHub repository language metadata."""

    name: str
    bytes: int | None = None


@dataclass(frozen=True)
class RepositorySummary:
    """Normalized summary of a GitHub repository."""

    github_id: int
    node_id: str | None
    name: str
    full_name: str
    private: bool
    fork: bool
    archived: bool
    visibility: str | None
    html_url: str
    description: str | None
    default_branch: str
    owner: RepositoryOwner
    permissions: RepositoryPermissions
    license: RepositoryLicense | None
    primary_language: RepositoryLanguage | None
    pushed_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def from_github_api(cls, payload: dict[str, Any]) -> "RepositorySummary":
        """Build a repository summary from a GitHub repository payload."""

        language = payload.get("language")
        return cls(
            github_id=int(payload["id"]),
            node_id=payload.get("node_id"),
            name=str(payload["name"]),
            full_name=str(payload["full_name"]),
            private=bool(payload.get("private")),
            fork=bool(payload.get("fork")),
            archived=bool(payload.get("archived")),
            visibility=payload.get("visibility"),
            html_url=str(payload["html_url"]),
            description=payload.get("description"),
            default_branch=str(payload.get("default_branch") or "main"),
            owner=RepositoryOwner.from_github_api(payload["owner"]),
            permissions=RepositoryPermissions.from_github_api(payload.get("permissions")),
            license=RepositoryLicense.from_github_api(payload.get("license")),
            primary_language=RepositoryLanguage(str(language)) if language else None,
            pushed_at=_parse_datetime(payload.get("pushed_at")),
            updated_at=_parse_datetime(payload.get("updated_at")),
        )