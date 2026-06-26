"""Repository registration application service."""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.application.services.github_service import GitHubService
from app.core.exceptions import AuthorizationException, ConflictException, ResourceNotFoundException
from app.domain.github import RepositorySummary
from app.domain.identity import AuthenticatedUser
from app.infrastructure.database.models import Repository
from app.repositories.repository_repository import RepositoryRepository


@dataclass(frozen=True)
class RepositoryRegistrationInput:
    """Validated input for registering a discovered GitHub repository."""

    github_repository_id: str
    full_name: str
    default_branch: str


class RepositoryRegistrationService:
    """Register discovered GitHub repositories as managed RepoMind resources."""

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

    def list_registered_repositories(self, owner_user_id: UUID) -> list[Repository]:
        """Return repositories registered by a local user."""

        return self.repository_repository.list_by_owner(owner_user_id)

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