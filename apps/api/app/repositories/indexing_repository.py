"""Indexing persistence repository."""

from sqlalchemy.orm import Session

from app.infrastructure.database.models import CodeChunk, Embedding, IndexingJob, RepositoryFile
from app.repositories.base import BaseRepository


class IndexingRepository(BaseRepository[IndexingJob]):
    """Encapsulate persistence operations for indexing records."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, IndexingJob)

    def add_repository_file(self, repository_file: RepositoryFile) -> RepositoryFile:
        """Stage a repository file for insertion."""

        self.session.add(repository_file)
        return repository_file

    def add_code_chunk(self, code_chunk: CodeChunk) -> CodeChunk:
        """Stage a code chunk for insertion."""

        self.session.add(code_chunk)
        return code_chunk

    def add_embedding(self, embedding: Embedding) -> Embedding:
        """Stage an embedding for insertion."""

        self.session.add(embedding)
        return embedding
