from app.infrastructure.database.models import User, UserProfile


def test_user_model_creation_with_profile_relationship() -> None:
    user = User(
        email="engineer@example.com",
        auth_provider="github",
        auth_provider_user_id="12345",
        status="active",
    )
    profile = UserProfile(display_name="Engineering Lead", timezone="Asia/Calcutta", locale="en")

    user.profile = profile

    assert user.email == "engineer@example.com"
    assert user.profile is profile
    assert profile.user is user


def test_user_and_profile_table_names_match_database_spec() -> None:
    assert User.__tablename__ == "users"
    assert UserProfile.__tablename__ == "user_profiles"


def test_user_model_constraints_and_indexes_are_declared() -> None:
    index_names = {index.name for index in User.__table__.indexes}
    constraint_names = {constraint.name for constraint in User.__table__.constraints}

    assert User.__table__.primary_key.columns.keys() == ["id"]
    assert "uq_users_email_active" in index_names
    assert "uq_users_auth_provider_auth_provider_user_id" in index_names
    assert "ix_users_status" in index_names
    assert "ix_users_created_at" in index_names
    assert "ck_users_status_valid" in constraint_names


def test_user_profile_model_constraints_and_indexes_are_declared() -> None:
    index_names = {index.name for index in UserProfile.__table__.indexes}
    constraint_names = {constraint.name for constraint in UserProfile.__table__.constraints}

    assert "ix_user_profiles_display_name" in index_names
    assert "uq_user_profiles_user_id" in constraint_names
