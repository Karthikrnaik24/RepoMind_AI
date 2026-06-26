"""User persistence repository."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.infrastructure.database.models import User, UserProfile
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Encapsulate persistence operations for users and user profiles."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, User)

    def get_by_provider_subject(
        self,
        provider_subject: str,
        provider: str = "supabase",
    ) -> User | None:
        """Return an active user by identity-provider subject."""

        statement = (
            select(User)
            .options(selectinload(User.profile))
            .where(
                User.auth_provider == provider,
                User.auth_provider_user_id == provider_subject,
                User.deleted_at.is_(None),
            )
        )
        return self.session.execute(statement).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        """Return an active user by normalized email address."""

        statement = (
            select(User)
            .options(selectinload(User.profile))
            .where(User.email == email, User.deleted_at.is_(None))
        )
        return self.session.execute(statement).scalar_one_or_none()

    def create_user(
        self,
        *,
        email: str,
        provider_subject: str,
        provider: str = "supabase",
        logged_in_at: datetime | None = None,
    ) -> User:
        """Stage a new local user linked to an external identity provider."""

        user = User(
            email=email,
            auth_provider=provider,
            auth_provider_user_id=provider_subject,
            status="active",
            last_login_at=logged_in_at or datetime.now(UTC),
        )
        return self.add(user)

    def update_last_login(
        self,
        user: User,
        *,
        email: str | None = None,
        logged_in_at: datetime | None = None,
    ) -> User:
        """Update login metadata and optionally refresh the user's email address."""

        if email is not None and user.email != email:
            user.email = email
        user.last_login_at = logged_in_at or datetime.now(UTC)
        return user

    def create_or_update_profile(
        self,
        user: User,
        *,
        display_name: str | None = None,
        avatar_url: str | None = None,
    ) -> UserProfile:
        """Create or update the user's profile metadata."""

        profile = user.profile
        if profile is None:
            profile = UserProfile(user=user)
            self.session.add(profile)

        if display_name is not None and profile.display_name != display_name:
            profile.display_name = display_name
        if avatar_url is not None and profile.avatar_url != avatar_url:
            profile.avatar_url = avatar_url

        return profile
