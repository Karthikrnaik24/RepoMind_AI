"""Repository application service placeholder."""

from app.repositories.repository_repository import RepositoryRepository


class RepositoryService:
    """Coordinates future repository use cases through repository dependencies."""

    def __init__(self, repository_repository: RepositoryRepository) -> None:
        self.repository_repository = repository_repository
