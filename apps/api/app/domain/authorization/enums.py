"""Role and permission primitives for RepoMind AI authorization."""

from enum import StrEnum


class Role(StrEnum):
    """Application roles stored on local users."""

    USER = "user"
    ADMIN = "admin"


class Permission(StrEnum):
    """Application permissions checked by authorization policies."""

    VIEW_PROFILE = "view_profile"
    EDIT_PROFILE = "edit_profile"
    CONNECT_REPOSITORY = "connect_repository"
    VIEW_ADMIN_PANEL = "view_admin_panel"
