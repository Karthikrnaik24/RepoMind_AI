"""Admin foundation routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.services import SyncedUserIdentity
from app.domain.authorization import Permission
from app.interfaces.api.authorization import require_permission
from app.interfaces.api.schemas.responses import ApiSuccessResponse, success_response
from app.interfaces.api.schemas.responses.admin import AdminPingResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ping", response_model=ApiSuccessResponse[AdminPingResponse])
def admin_ping(
    _: Annotated[
        SyncedUserIdentity,
        Depends(require_permission(Permission.VIEW_ADMIN_PANEL)),
    ],
) -> dict:
    """Return a minimal ADMIN-only authorization probe."""

    return success_response(AdminPingResponse(status="ok"))
