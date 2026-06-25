"""Current user route."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.domain.identity import AuthenticatedUser
from app.infrastructure.auth.dependencies import get_current_user
from app.interfaces.api.schemas.responses import ApiSuccessResponse, MeData, success_response

router = APIRouter(tags=["identity"])


@router.get("/me", response_model=ApiSuccessResponse[MeData])
def read_current_user(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict:
    """Return the authenticated user's external identity."""

    return success_response(
        MeData(
            id=current_user.provider_subject,
            email=current_user.email,
            provider="supabase",
            role=current_user.role,
            metadata=current_user.metadata,
        ),
    )
