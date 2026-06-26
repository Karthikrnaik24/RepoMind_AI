"""Repository request DTOs."""

from pydantic import BaseModel, Field


class RegisterRepositoryRequest(BaseModel):
    """Request payload for registering a discovered GitHub repository."""

    github_repository_id: str = Field(min_length=1, max_length=255)
    full_name: str = Field(min_length=3, max_length=511, pattern=r"^[^/]+/[^/]+$")
    default_branch: str = Field(min_length=1, max_length=255)