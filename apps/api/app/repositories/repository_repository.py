"""Repository metadata persistence repository."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.models import Repository, RepositoryBranch
from app.repositories.base import BaseRepository


class RepositoryRepository(BaseRepository[Repository]):
    """Encapsulate persistence operations for repositories and branches."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Repository)

    def get_by_provider_repository_id(
        self,
        *,
        provider: str,
        provider_repository_id: str,
    ) -> Repository | None:
        """Return a repository by provider identity."""

        statement = select(Repository).where(
            Repository.provider == provider,
            Repository.provider_repository_id == provider_repository_id,
        )
        return self.session.execute(statement).scalar_one_or_none()

    def get_by_owner_and_id(
        self,
        *,
        owner_user_id: UUID,
        repository_id: UUID,
    ) -> Repository | None:
        """Return a registered repository by local owner and repository id."""

        statement = select(Repository).where(
            Repository.owner_user_id == owner_user_id,
            Repository.id == repository_id,
        )
        return self.session.execute(statement).scalar_one_or_none()

    def get_by_owner_and_provider_repository_id(
        self,
        *,
        owner_user_id: UUID,
        provider: str,
        provider_repository_id: str,
    ) -> Repository | None:
        """Return a user's registered repository by provider identity."""

        statement = select(Repository).where(
            Repository.owner_user_id == owner_user_id,
            Repository.provider == provider,
            Repository.provider_repository_id == provider_repository_id,
        )
        return self.session.execute(statement).scalar_one_or_none()

    def list_by_owner(self, owner_user_id: UUID) -> list[Repository]:
        """Return repositories registered by the given user."""

        statement = (
            select(Repository)
            .where(Repository.owner_user_id == owner_user_id)
            .order_by(
                Repository.favorite.desc(),
                Repository.registered_at.desc(),
                Repository.created_at.desc(),
            )
        )
        return list(self.session.execute(statement).scalars().all())

    def create_registered_repository(
        self,
        *,
        owner_user_id: UUID,
        provider_repository_id: str,
        owner_name: str,
        name: str,
        full_name: str,
        default_branch: str,
        visibility: str,
        language: str | None,
        description: str | None,
        web_url: str | None,
        github_updated_at: datetime | None = None,
    ) -> Repository:
        """Stage a newly registered GitHub repository for insertion."""

        repository = Repository(
            owner_user_id=owner_user_id,
            provider="github",
            provider_repository_id=provider_repository_id,
            owner_name=owner_name,
            name=name,
            full_name=full_name,
            default_branch=default_branch,
            visibility=visibility,
            language=language,
            description=description,
            web_url=web_url,
            sync_status="PENDING",
            github_updated_at=github_updated_at,
        )
        self.session.add(repository)
        return repository

    def update_management_settings(
        self,
        repository: Repository,
        *,
        display_name: str | None | object,
        favorite: bool | None | object,
        notes: str | None | object,
        unset: object,
    ) -> Repository:
        """Apply mutable user-owned settings without changing GitHub identity."""

        if display_name is not unset:
            repository.display_name = display_name  # type: ignore[assignment]
        if favorite is not unset:
            repository.favorite = bool(favorite)
        if notes is not unset:
            repository.notes = notes  # type: ignore[assignment]
        self.session.add(repository)
        return repository

    def update_refreshed_metadata(
        self,
        repository: Repository,
        *,
        description: str | None,
        language: str | None,
        default_branch: str,
        visibility: str,
        github_updated_at: datetime | None,
        refreshed_at: datetime,
    ) -> Repository:
        """Apply metadata refreshed from GitHub without touching repository contents."""

        repository.description = description
        repository.language = language
        repository.default_branch = default_branch
        repository.visibility = visibility
        repository.github_updated_at = github_updated_at
        repository.last_synced_at = refreshed_at
        repository.sync_status = "READY"
        self.session.add(repository)
        return repository

    def mark_sync_error(self, repository: Repository) -> Repository:
        """Mark a repository refresh attempt as failed."""

        repository.sync_status = "ERROR"
        self.session.add(repository)
        return repository

    def delete_registered_repository(self, repository: Repository) -> None:
        """Stage a registered repository for removal from RepoMind AI only."""

        self.session.delete(repository)

    def add_branch(self, branch: RepositoryBranch) -> RepositoryBranch:
        """Stage a repository branch for insertion."""

        self.session.add(branch)
        return branch