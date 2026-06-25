"""User application service placeholder."""

from app.repositories.user_repository import UserRepository


class UserService:
    """Coordinates future user use cases through repository dependencies."""

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository
