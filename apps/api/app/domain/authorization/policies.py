"""Role-to-permission policy definitions."""

from collections.abc import Mapping

from app.domain.authorization.enums import Permission, Role

RolePermissionMap = Mapping[Role, frozenset[Permission]]

ROLE_PERMISSION_MAP: RolePermissionMap = {
    Role.USER: frozenset(
        {
            Permission.VIEW_PROFILE,
            Permission.EDIT_PROFILE,
            Permission.CONNECT_REPOSITORY,
        },
    ),
    Role.ADMIN: frozenset(
        {
            Permission.VIEW_PROFILE,
            Permission.EDIT_PROFILE,
            Permission.CONNECT_REPOSITORY,
            Permission.VIEW_ADMIN_PANEL,
        },
    ),
}


class AuthorizationPolicy:
    """Evaluate whether roles grant permissions."""

    def __init__(self, role_permission_map: RolePermissionMap = ROLE_PERMISSION_MAP) -> None:
        self.role_permission_map = role_permission_map

    def has_permission(self, role: Role | str, permission: Permission) -> bool:
        """Return whether a role grants the requested permission."""

        try:
            resolved_role = Role(role)
        except ValueError:
            return False
        return permission in self.role_permission_map.get(resolved_role, frozenset())
