"""Repository registration and management application service."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.application.services.github_service import GitHubService
from app.core.exceptions import AuthorizationException, ConflictException, ResourceNotFoundException
from app.domain.github import RepositorySummary
from app.domain.identity import AuthenticatedUser
from app.infrastructure.database.models import Repository
from app.repositories.repository_repository import RepositoryRepository

UNSET = object()


@dataclass(frozen=True)
class RepositoryRegistrationInput:
    """Validated input for registering a discovered GitHub repository."""

    github_repository_id: str
    full_name: str
    default_branch: str


@dataclass(frozen=True)
class RepositorySettingsUpdate:
    """Mutable user-owned settings for a registered repository."""

    display_name: str | None | object = UNSET
    favorite: bool | None | object = UNSET
    notes: str | None | object = UNSET


class RepositoryRegistrationService:
    """Register and manage discovered GitHub repositories as RepoMind resources."""

    def __init__(
        self,
        repository_repository: RepositoryRepository,
        github_service: GitHubService,
    ) -> None:
        self.repository_repository = repository_repository
        self.github_service = github_service

    def register_repository(
        self,
        *,
        owner_user_id: UUID,
        authenticated_user: AuthenticatedUser,
        registration_input: RepositoryRegistrationInput,
    ) -> Repository:
        """Validate and persist a GitHub repository registration."""

        session = self.repository_repository.session
        existing = self.repository_repository.get_by_owner_and_provider_repository_id(
            owner_user_id=owner_user_id,
            provider="github",
            provider_repository_id=registration_input.github_repository_id,
        )
        if existing is not None:
            raise ConflictException(
                "Repository is already registered.",
                code="repository_registered",
            )

        github_repository = self.github_service.get_repository_by_full_name(
            authenticated_user,
            full_name=registration_input.full_name,
        )
        self._validate_repository(registration_input, github_repository)

        try:
            repository = self.repository_repository.create_registered_repository(
                owner_user_id=owner_user_id,
                provider_repository_id=str(github_repository.github_id),
                owner_name=github_repository.owner.login,
                name=github_repository.name,
                full_name=github_repository.full_name,
                default_branch=github_repository.default_branch,
                visibility=github_repository.visibility or "private",
                language=github_repository.primary_language.name
                if github_repository.primary_language
                else None,
                description=github_repository.description,
                web_url=github_repository.html_url,
                github_updated_at=github_repository.updated_at,
            )
            session.flush()
            session.refresh(repository)
            return repository
        except IntegrityError as exc:
            session.rollback()
            raise ConflictException(
                "Repository is already registered.",
                code="repository_registered",
            ) from exc
        except Exception:
            session.rollback()
            raise

    def get_registered_repository(
        self,
        *,
        owner_user_id: UUID,
        repository_id: UUID,
    ) -> Repository:
        """Return an owner-scoped registered repository or raise a safe 404."""

        repository = self.repository_repository.get_by_owner_and_id(
            owner_user_id=owner_user_id,
            repository_id=repository_id,
        )
        if repository is None:
            raise ResourceNotFoundException(
                "Repository was not found.",
                code="repository_not_found",
            )
        return repository

    def list_registered_repositories(self, owner_user_id: UUID) -> list[Repository]:
        """Return repositories registered by a local user."""

        return self.repository_repository.list_by_owner(owner_user_id)

    def update_repository_settings(
        self,
        *,
        owner_user_id: UUID,
        repository_id: UUID,
        settings_update: RepositorySettingsUpdate,
    ) -> Repository:
        """Update mutable repository settings without changing GitHub identity."""

        repository = self.get_registered_repository(
            owner_user_id=owner_user_id,
            repository_id=repository_id,
        )
        updated_repository = self.repository_repository.update_management_settings(
            repository,
            display_name=settings_update.display_name,
            favorite=settings_update.favorite,
            notes=settings_update.notes,
            unset=UNSET,
        )
        self.repository_repository.session.flush()
        self.repository_repository.session.refresh(updated_repository)
        return updated_repository

    def refresh_repository_metadata(
        self,
        *,
        owner_user_id: UUID,
        repository_id: UUID,
        authenticated_user: AuthenticatedUser,
    ) -> Repository:
        """Refresh GitHub metadata without cloning or reading repository contents."""

        repository = self.get_registered_repository(
            owner_user_id=owner_user_id,
            repository_id=repository_id,
        )
        try:
            github_repository = self.github_service.get_repository_by_full_name(
                authenticated_user,
                full_name=repository.full_name,
            )
            self._validate_registered_repository_identity(repository, github_repository)
            refreshed_repository = self.repository_repository.update_refreshed_metadata(
                repository,
                description=github_repository.description,
                language=github_repository.primary_language.name
                if github_repository.primary_language
                else None,
                default_branch=github_repository.default_branch,
                visibility=github_repository.visibility or repository.visibility,
                github_updated_at=github_repository.updated_at,
                refreshed_at=datetime.now(UTC),
            )
            self.repository_repository.session.flush()
            self.repository_repository.session.refresh(refreshed_repository)
            return refreshed_repository
        except Exception:
            self.repository_repository.mark_sync_error(repository)
            raise

    def unregister_repository(
        self,
        *,
        owner_user_id: UUID,
        repository_id: UUID,
    ) -> UUID:
        """Remove a registered repository from RepoMind AI without touching GitHub."""

        repository = self.get_registered_repository(
            owner_user_id=owner_user_id,
            repository_id=repository_id,
        )
        removed_id = repository.id
        self.repository_repository.delete_registered_repository(repository)
        self.repository_repository.session.flush()
        return removed_id

    @staticmethod
    def _validate_repository(
        registration_input: RepositoryRegistrationInput,
        github_repository: RepositorySummary,
    ) -> None:
        if str(github_repository.github_id) != registration_input.github_repository_id:
            raise ResourceNotFoundException(
                "GitHub repository could not be validated.",
                code="github_repository_not_found",
            )
        if github_repository.full_name.lower() != registration_input.full_name.strip().lower():
            raise ResourceNotFoundException(
                "GitHub repository could not be validated.",
                code="github_repository_not_found",
            )
        if github_repository.default_branch != registration_input.default_branch:
            raise AuthorizationException(
                "Repository default branch did not match GitHub.",
                code="repository_validation_failed",
            )

    @staticmethod
    def _validate_registered_repository_identity(
        repository: Repository,
        github_repository: RepositorySummary,
    ) -> None:
        if str(github_repository.github_id) != repository.provider_repository_id:
            raise ResourceNotFoundException(
                "GitHub repository could not be validated.",
                code="github_repository_not_found",
            )
        if github_repository.full_name.lower() != repository.full_name.lower():
            raise ResourceNotFoundException(
                "GitHub repository could not be validated.",
                code="github_repository_not_found",
            )


def repository_settings_from_values(values: dict[str, Any]) -> RepositorySettingsUpdate:
    """Build a settings update value object from provided request fields."""

    return RepositorySettingsUpdate(
        display_name=values.get("display_name", UNSET),
        favorite=values.get("favorite", UNSET),
        notes=values.get("notes", UNSET),
    )