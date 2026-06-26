"""Current user route."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.services import SyncedUserIdentity
from app.interfaces.api.authorization import get_current_synced_user
from app.interfaces.api.schemas.responses import ApiSuccessResponse, MeResponse, success_response

router = APIRouter(tags=["identity"])


@router.get("/me", response_model=ApiSuccessResponse[MeResponse])
def read_current_user(
    synced_identity: Annotated[SyncedUserIdentity, Depends(get_current_synced_user)],
) -> dict:
    """Return the authenticated user's synchronized local identity."""

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
            role=user.role,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
        ),
    )
