"""GitHub integration diagnostic routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.services import GitHubService
from app.domain.identity import AuthenticatedUser
from app.infrastructure.auth.dependencies import get_current_user
from app.interfaces.api.dependencies import get_github_service
from app.interfaces.api.schemas.responses import (
    ApiSuccessResponse,
    GitHubTokenDebugResponse,
    success_response,
)

router = APIRouter(prefix="/github", tags=["github"])


@router.get("/debug-token", response_model=ApiSuccessResponse[GitHubTokenDebugResponse])
def debug_github_token(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    github_service: Annotated[GitHubService, Depends(get_github_service)],
) -> dict:
    """Return safe linked GitHub token availability for developer diagnostics."""

    token_status = github_service.get_token_status(current_user)
    return success_response(
        GitHubTokenDebugResponse(
            github_linked=token_status.linked,
            token_available=token_status.token_available,
            provider=token_status.provider,
        )
    )