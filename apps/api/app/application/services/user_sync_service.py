"""Synchronize verified external identities into local user records."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.domain.identity import AuthenticatedUser
from app.infrastructure.database.models import User, UserProfile
from app.repositories.user_repository import UserRepository


@dataclass(frozen=True)
class SyncedUserIdentity:
    """Local user identity data returned by the synchronization use case."""

    user: User
    profile: UserProfile


class UserSyncService:
    """Persist authenticated Supabase users in the local application database."""

    provider = "supabase"

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def sync_authenticated_user(self, authenticated_user: AuthenticatedUser) -> SyncedUserIdentity:
        """Create or update the local user and profile for a verified identity."""

        session = self.user_repository.session
        logged_in_at = datetime.now(UTC)
        normalized_email = authenticated_user.email.strip().lower()
        display_name = self._metadata_string(authenticated_user.metadata, "display_name")
        avatar_url = self._metadata_string(authenticated_user.metadata, "avatar_url")

        try:
            user = self.user_repository.get_by_provider_subject(
                authenticated_user.provider_subject,
                self.provider,
            )
            if user is None:
                user = self.user_repository.create_user(
                    email=normalized_email,
                    provider_subject=authenticated_user.provider_subject,
                    provider=self.provider,
                    logged_in_at=logged_in_at,
                )
            else:
                self.user_repository.update_last_login(
                    user,
                    email=normalized_email,
                    logged_in_at=logged_in_at,
                )

            profile = self.user_repository.create_or_update_profile(
                user,
                display_name=display_name,
                avatar_url=avatar_url,
            )
            session.flush()
            session.refresh(user)
            session.refresh(profile)
        except Exception:
            session.rollback()
            raise

        return SyncedUserIdentity(user=user, profile=profile)

    @classmethod
    def _metadata_string(cls, metadata: dict[str, Any], key: str) -> str | None:
        """Extract supported string profile metadata from Supabase claims."""

        user_metadata = metadata.get("user_metadata")
        if isinstance(user_metadata, dict):
            value = cls._first_non_empty_string(user_metadata, cls._metadata_keys(key))
            if value is not None:
                return value

        return cls._first_non_empty_string(metadata, cls._metadata_keys(key))

    @staticmethod
    def _metadata_keys(key: str) -> tuple[str, ...]:
        if key == "display_name":
            return ("display_name", "full_name", "name")
        return (key,)

    @staticmethod
    def _first_non_empty_string(source: dict[str, Any], keys: tuple[str, ...]) -> str | None:
        for key in keys:
            value = source.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None
