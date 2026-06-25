"""User persistence repository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Encapsulate persistence operations for users."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, User)

    def get_by_email(self, email: str) -> User | None:
        """Return a user by normalized email address."""

        statement = select(User).where(User.email == email)
        return self.session.execute(statement).scalar_one_or_none()
