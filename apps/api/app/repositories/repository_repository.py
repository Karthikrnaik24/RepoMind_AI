"""Repository metadata persistence repository."""

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
            .order_by(Repository.registered_at.desc(), Repository.created_at.desc())
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
        )
        self.session.add(repository)
        return repository

    def add_branch(self, branch: RepositoryBranch) -> RepositoryBranch:
        """Stage a repository branch for insertion."""

        self.session.add(branch)
        return branch