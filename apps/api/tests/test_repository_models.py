from app.infrastructure.database.models import Repository, RepositoryBranch, User


def test_repository_model_creation_with_owner_and_branch_relationships() -> None:
    owner = User(
        email="engineer@example.com",
        auth_provider="github",
        auth_provider_user_id="12345",
        status="active",
    )
    repository = Repository(
        provider="github",
        provider_repository_id="98765",
        owner_name="repomind",
        name="repomind-ai",
        full_name="repomind/repomind-ai",
        default_branch="main",
        visibility="private",
    )
    branch = RepositoryBranch(
        name="main",
        head_commit_sha="0123456789abcdef0123456789abcdef01234567",
        is_default=True,
    )

    owner.repositories.append(repository)
    repository.branches.append(branch)

    assert repository.owner is owner
    assert owner.repositories == [repository]
    assert branch.repository is repository
    assert repository.branches == [branch]


def test_repository_and_branch_table_names_match_database_spec() -> None:
    assert Repository.__tablename__ == "repositories"
    assert RepositoryBranch.__tablename__ == "repository_branches"


def test_repository_model_constraints_and_indexes_are_declared() -> None:
    index_names = {index.name for index in Repository.__table__.indexes}
    constraint_names = {constraint.name for constraint in Repository.__table__.constraints}

    assert Repository.__table__.primary_key.columns.keys() == ["id"]
    assert "ck_repositories_visibility_valid" in constraint_names
    assert "uq_repositories_provider_provider_repository_id" in index_names
    assert "ix_repositories_owner_user_id" in index_names
    assert "ix_repositories_full_name" in index_names
    assert "ix_repositories_last_indexed_at" in index_names
    assert "ix_repositories_archived_at" in index_names


def test_repository_branch_model_constraints_and_indexes_are_declared() -> None:
    index_names = {index.name for index in RepositoryBranch.__table__.indexes}

    assert RepositoryBranch.__table__.primary_key.columns.keys() == ["id"]
    assert "uq_repository_branches_repository_id_name" in index_names
    assert "uq_repository_branches_repository_id_default" in index_names
    assert "ix_repository_branches_head_commit_sha" in index_names
    assert "ix_repository_branches_last_seen_at" in index_names
