"""Registered repository routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.application.services import (
    RepositoryRegistrationInput,
    RepositoryRegistrationService,
    SyncedUserIdentity,
    repository_settings_from_values,
)
from app.domain.identity import AuthenticatedUser
from app.infrastructure.auth.dependencies import get_current_user
from app.interfaces.api.authorization import get_current_synced_user
from app.interfaces.api.dependencies import get_repository_registration_service
from app.interfaces.api.schemas.requests import (
    RegisterRepositoryRequest,
    UpdateRepositorySettingsRequest,
)
from app.interfaces.api.schemas.responses import (
    ApiSuccessResponse,
    RegisteredRepositoryResponse,
    RepositoryUnregisterResponse,
    success_response,
)

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.post(
    "/register",
    response_model=ApiSuccessResponse[RegisteredRepositoryResponse],
    status_code=status.HTTP_201_CREATED,
)
def register_repository(
    payload: RegisterRepositoryRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    synced_identity: Annotated[SyncedUserIdentity, Depends(get_current_synced_user)],
    registration_service: Annotated[
        RepositoryRegistrationService,
        Depends(get_repository_registration_service),
    ],
) -> dict:
    """Register a discovered GitHub repository as a managed resource."""

    repository = registration_service.register_repository(
        owner_user_id=synced_identity.user.id,
        authenticated_user=current_user,
        registration_input=RepositoryRegistrationInput(
            github_repository_id=payload.github_repository_id,
            full_name=payload.full_name,
            default_branch=payload.default_branch,
        ),
    )
    return success_response(RegisteredRepositoryResponse.from_orm(repository))


@router.get("", response_model=ApiSuccessResponse[list[RegisteredRepositoryResponse]])
def list_registered_repositories(
    synced_identity: Annotated[SyncedUserIdentity, Depends(get_current_synced_user)],
    registration_service: Annotated[
        RepositoryRegistrationService,
        Depends(get_repository_registration_service),
    ],
) -> dict:
    """Return repositories registered by the authenticated user."""

    repositories = registration_service.list_registered_repositories(synced_identity.user.id)
    return success_response(
        [RegisteredRepositoryResponse.from_orm(repository) for repository in repositories],
        meta={"count": len(repositories)},
    )


@router.get("/{repository_id}", response_model=ApiSuccessResponse[RegisteredRepositoryResponse])
def get_registered_repository(
    repository_id: UUID,
    synced_identity: Annotated[SyncedUserIdentity, Depends(get_current_synced_user)],
    registration_service: Annotated[
        RepositoryRegistrationService,
        Depends(get_repository_registration_service),
    ],
) -> dict:
    """Return one owner-scoped registered repository dashboard payload."""

    repository = registration_service.get_registered_repository(
        owner_user_id=synced_identity.user.id,
        repository_id=repository_id,
    )
    return success_response(RegisteredRepositoryResponse.from_orm(repository))


@router.patch("/{repository_id}", response_model=ApiSuccessResponse[RegisteredRepositoryResponse])
def update_registered_repository_settings(
    repository_id: UUID,
    payload: UpdateRepositorySettingsRequest,
    synced_identity: Annotated[SyncedUserIdentity, Depends(get_current_synced_user)],
    registration_service: Annotated[
        RepositoryRegistrationService,
        Depends(get_repository_registration_service),
    ],
) -> dict:
    """Update mutable repository settings without changing GitHub identity."""

    repository = registration_service.update_repository_settings(
        owner_user_id=synced_identity.user.id,
        repository_id=repository_id,
        settings_update=repository_settings_from_values(payload.model_dump(exclude_unset=True)),
    )
    return success_response(RegisteredRepositoryResponse.from_orm(repository))


@router.delete("/{repository_id}", response_model=ApiSuccessResponse[RepositoryUnregisterResponse])
def unregister_repository(
    repository_id: UUID,
    synced_identity: Annotated[SyncedUserIdentity, Depends(get_current_synced_user)],
    registration_service: Annotated[
        RepositoryRegistrationService,
        Depends(get_repository_registration_service),
    ],
) -> dict:
    """Remove a repository from RepoMind AI without deleting it from GitHub."""

    removed_id = registration_service.unregister_repository(
        owner_user_id=synced_identity.user.id,
        repository_id=repository_id,
    )
    return success_response(RepositoryUnregisterResponse(id=removed_id, removed=True))


@router.post(
    "/{repository_id}/refresh",
    response_model=ApiSuccessResponse[RegisteredRepositoryResponse],
)
def refresh_registered_repository(
    repository_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    synced_identity: Annotated[SyncedUserIdentity, Depends(get_current_synced_user)],
    registration_service: Annotated[
        RepositoryRegistrationService,
        Depends(get_repository_registration_service),
    ],
) -> dict:
    """Refresh GitHub metadata without cloning or parsing repository contents."""

    repository = registration_service.refresh_repository_metadata(
        owner_user_id=synced_identity.user.id,
        repository_id=repository_id,
        authenticated_user=current_user,
    )
    return success_response(RegisteredRepositoryResponse.from_orm(repository))