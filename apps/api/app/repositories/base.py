"""Base SQLAlchemy repository primitives."""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.base import Base


class BaseRepository[ModelT: Base]:
    """Encapsulate common SQLAlchemy operations for one ORM model."""

    model: type[ModelT]

    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    def get_by_id(self, entity_id: UUID) -> ModelT | None:
        """Return one entity by primary key."""

        return self.session.get(self.model, entity_id)

    def list(self, *, limit: int = 100, offset: int = 0) -> Sequence[ModelT]:
        """Return a bounded list of entities."""

        statement = select(self.model).limit(limit).offset(offset)
        return self.session.execute(statement).scalars().all()

    def add(self, entity: ModelT) -> ModelT:
        """Stage an entity for insertion."""

        self.session.add(entity)
        return entity

    def delete(self, entity: ModelT) -> None:
        """Stage an entity for deletion."""

        self.session.delete(entity)
