"""Repository response DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.infrastructure.database.models import Repository


class RegisteredRepositoryResponse(BaseModel):
    """Registered repository response payload."""

    id: UUID
    owner_user_id: UUID
    github_repository_id: str
    name: str
    full_name: str
    owner_login: str
    default_branch: str
    visibility: str
    display_name: str | None = None
    favorite: bool
    notes: str | None = None
    language: str | None = None
    description: str | None = None
    html_url: str | None = None
    registered_at: datetime
    sync_status: str
    last_synced_at: datetime | None = None
    github_updated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, repository: Repository) -> "RegisteredRepositoryResponse":
        """Create a response DTO from a registered repository ORM model."""

        return cls(
            id=repository.id,
            owner_user_id=repository.owner_user_id,
            github_repository_id=repository.provider_repository_id,
            name=repository.name,
            full_name=repository.full_name,
            owner_login=repository.owner_name,
            default_branch=repository.default_branch,
            visibility=repository.visibility,
            display_name=repository.display_name,
            favorite=repository.favorite,
            notes=repository.notes,
            language=repository.language,
            description=repository.description,
            html_url=repository.web_url,
            registered_at=repository.registered_at,
            sync_status=repository.sync_status,
            last_synced_at=repository.last_synced_at,
            github_updated_at=repository.github_updated_at,
            created_at=repository.created_at,
            updated_at=repository.updated_at,
        )


class RepositoryUnregisterResponse(BaseModel):
    """Repository unregister response payload."""

    id: UUID
    removed: bool