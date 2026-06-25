"""Repository metadata persistence repository."""

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

    def add_branch(self, branch: RepositoryBranch) -> RepositoryBranch:
        """Stage a repository branch for insertion."""

        self.session.add(branch)
        return branch
