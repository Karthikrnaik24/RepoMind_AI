"""Indexing application service placeholder."""

from app.repositories.indexing_repository import IndexingRepository


class IndexingService:
    """Coordinates future indexing use cases through repository dependencies."""

    def __init__(self, indexing_repository: IndexingRepository) -> None:
        self.indexing_repository = indexing_repository
