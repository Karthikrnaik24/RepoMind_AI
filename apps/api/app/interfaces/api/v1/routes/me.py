"""Current user route."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.services import UserSyncService
from app.domain.identity import AuthenticatedUser
from app.infrastructure.auth.dependencies import get_current_user
from app.interfaces.api.dependencies import get_user_sync_service
from app.interfaces.api.schemas.responses import ApiSuccessResponse, MeResponse, success_response

router = APIRouter(tags=["identity"])


@router.get("/me", response_model=ApiSuccessResponse[MeResponse])
def read_current_user(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    user_sync_service: Annotated[UserSyncService, Depends(get_user_sync_service)],
) -> dict:
    """Return the authenticated user's synchronized local identity."""

    synced_identity = user_sync_service.sync_authenticated_user(current_user)
    user = synced_identity.user
    profile = synced_identity.profile

    return success_response(
        MeResponse(
            id=user.id,
            email=user.email,
            display_name=profile.display_name,
            avatar_url=profile.avatar_url,
            provider=user.auth_provider,
            provider_subject=user.auth_provider_user_id,
            role=current_user.role,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
        ),
    )
