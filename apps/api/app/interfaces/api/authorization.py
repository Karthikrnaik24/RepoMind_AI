"""Authorization dependencies for protected API routes."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends

from app.application.services import SyncedUserIdentity, UserSyncService
from app.core.exceptions import AuthorizationException
from app.domain.authorization import AuthorizationPolicy, Permission
from app.domain.identity import AuthenticatedUser
from app.infrastructure.auth.dependencies import get_current_user
from app.interfaces.api.dependencies import get_user_sync_service


def get_authorization_policy() -> AuthorizationPolicy:
    """Return the default role-permission policy."""

    return AuthorizationPolicy()


def get_current_synced_user(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    user_sync_service: Annotated[UserSyncService, Depends(get_user_sync_service)],
) -> SyncedUserIdentity:
    """Authenticate and synchronize the current local user."""

    return user_sync_service.sync_authenticated_user(current_user)


def require_permission(permission: Permission) -> Callable[..., SyncedUserIdentity]:
    """Create a dependency that requires the current user to have a permission."""

    def dependency(
        synced_user: Annotated[SyncedUserIdentity, Depends(get_current_synced_user)],
        policy: Annotated[AuthorizationPolicy, Depends(get_authorization_policy)],
    ) -> SyncedUserIdentity:
        if not policy.has_permission(synced_user.user.role, permission):
            raise AuthorizationException()
        return synced_user

    return dependency
