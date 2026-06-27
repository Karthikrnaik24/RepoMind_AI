"""GitHub integration routes."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Header, Query

from app.application.services import GitHubService
from app.domain.identity import AuthenticatedUser
from app.infrastructure.auth.dependencies import get_current_user
from app.interfaces.api.dependencies import get_github_service
from app.interfaces.api.schemas.responses import (
    ApiSuccessResponse,
    GitHubRepositorySummaryResponse,
    success_response,
)

router = APIRouter(prefix="/github", tags=["github"])


@router.get(
    "/repositories",
    response_model=ApiSuccessResponse[list[GitHubRepositorySummaryResponse]],
)
def list_github_repositories(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    github_service: Annotated[GitHubService, Depends(get_github_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 12,
    sort: Literal["created", "updated", "pushed", "full_name"] = "updated",
    direction: Literal["asc", "desc"] = "desc",
    visibility: Literal["all", "public", "private"] = "all",
    search: Annotated[str | None, Query(max_length=100)] = None,
    github_provider_token: Annotated[str | None, Header(alias="X-GitHub-Provider-Token")] = None,
) -> dict:
    """Return linked GitHub repositories as safe DTOs, using GitHub search when requested."""

    repositories = github_service.list_repositories(
        current_user,
        page=page,
        per_page=per_page,
        sort=sort,
        direction=direction,
        visibility=visibility,
        search=search,
        provider_token=github_provider_token,
    )
    data = [GitHubRepositorySummaryResponse.from_domain(repository) for repository in repositories]
    return success_response(
        data,
        meta={
            "page": page,
            "per_page": per_page,
            "count": len(data),
            "sort": sort,
            "direction": direction,
            "visibility": visibility,
            "search": search,
            "search_scope": "github" if search else "user_repositories",
        },
    )
