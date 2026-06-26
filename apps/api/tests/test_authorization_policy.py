from app.domain.authorization import AuthorizationPolicy, Permission, Role


def test_permission_map_allows_user_profile_permissions() -> None:
    policy = AuthorizationPolicy()

    assert policy.has_permission(Role.USER, Permission.VIEW_PROFILE)
    assert policy.has_permission(Role.USER, Permission.EDIT_PROFILE)
    assert policy.has_permission(Role.USER, Permission.CONNECT_REPOSITORY)
    assert not policy.has_permission(Role.USER, Permission.VIEW_ADMIN_PANEL)


def test_permission_map_allows_admin_permissions() -> None:
    policy = AuthorizationPolicy()

    assert policy.has_permission(Role.ADMIN, Permission.VIEW_PROFILE)
    assert policy.has_permission(Role.ADMIN, Permission.VIEW_ADMIN_PANEL)


def test_role_enum_serialization() -> None:
    assert Role.USER.value == "user"
    assert Role.ADMIN.value == "admin"
    assert str(Role.USER) == "user"
