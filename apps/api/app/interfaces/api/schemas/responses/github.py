"""GitHub response DTOs."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.domain.github import RepositorySummary


class GitHubTokenDebugResponse(BaseModel):
    """Safe GitHub token availability debug payload."""

    github_linked: bool
    token_available: bool
    provider: Literal["github"] = "github"


class GitHubRepositoryOwnerResponse(BaseModel):
    """Repository owner response payload."""

    id: int
    login: str
    type: str
    avatar_url: str | None = None
    html_url: str | None = None


class GitHubRepositoryPermissionsResponse(BaseModel):
    """Repository permissions response payload."""

    admin: bool
    maintain: bool
    push: bool
    triage: bool
    pull: bool


class GitHubRepositorySummaryResponse(BaseModel):
    """Safe GitHub repository summary response payload."""

    id: int
    name: str
    full_name: str
    owner: GitHubRepositoryOwnerResponse
    private: bool
    visibility: str | None
    language: str | None
    default_branch: str
    updated_at: datetime | None
    description: str | None
    html_url: str
    permissions: GitHubRepositoryPermissionsResponse

    @classmethod
    def from_domain(cls, repository: RepositorySummary) -> "GitHubRepositorySummaryResponse":
        """Create a response DTO from a normalized domain repository summary."""

        return cls(
            id=repository.github_id,
            name=repository.name,
            full_name=repository.full_name,
            owner=GitHubRepositoryOwnerResponse(
                id=repository.owner.github_id,
                login=repository.owner.login,
                type=repository.owner.owner_type,
                avatar_url=repository.owner.avatar_url,
                html_url=repository.owner.html_url,
            ),
            private=repository.private,
            visibility=repository.visibility,
            language=repository.primary_language.name if repository.primary_language else None,
            default_branch=repository.default_branch,
            updated_at=repository.updated_at,
            description=repository.description,
            html_url=repository.html_url,
            permissions=GitHubRepositoryPermissionsResponse(
                admin=repository.permissions.admin,
                maintain=repository.permissions.maintain,
                push=repository.permissions.push,
                triage=repository.permissions.triage,
                pull=repository.permissions.pull,
            ),
        )