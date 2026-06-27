from decimal import Decimal

from app.infrastructure.database.models import (
    ApiKey,
    ArchitectureSnapshot,
    AuditLog,
    DependencyEdge,
    IndexingJob,
    Repository,
    RepositoryBranch,
    RepositoryFile,
    User,
)
from sqlalchemy.dialects.postgresql import INET, JSONB


def test_analysis_models_create_relationship_graph() -> None:
    user = User(
        email="architect@example.com",
        auth_provider="github",
        auth_provider_user_id="architect-1",
        status="active",
    )
    repository = Repository(
        provider="github",
        provider_repository_id="repo-1",
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
    indexing_job = IndexingJob(job_type="full_index", status="succeeded")
    source_file = RepositoryFile(path="apps/api/app/main.py", size_bytes=512)
    target_file = RepositoryFile(path="apps/api/app/config/settings.py", size_bytes=768)
    dependency_edge = DependencyEdge(
        source_symbol="create_app",
        target_symbol="Settings",
        dependency_type="import",
        is_external=False,
        confidence=Decimal("0.950000"),
    )
    architecture_snapshot = ArchitectureSnapshot(
        snapshot_type="repository_overview",
        version=1,
        content={"summary": "Backend API and repository intelligence services."},
    )

    user.repositories.append(repository)
    repository.branches.append(branch)
    repository.indexing_jobs.append(indexing_job)
    repository.files.extend([source_file, target_file])
    branch.files.extend([source_file, target_file])
    repository.dependency_edges.append(dependency_edge)
    branch.dependency_edges.append(dependency_edge)
    source_file.source_dependency_edges.append(dependency_edge)
    target_file.target_dependency_edges.append(dependency_edge)
    indexing_job.dependency_edges.append(dependency_edge)
    repository.architecture_snapshots.append(architecture_snapshot)
    branch.architecture_snapshots.append(architecture_snapshot)
    indexing_job.architecture_snapshots.append(architecture_snapshot)

    assert dependency_edge.repository is repository
    assert dependency_edge.branch is branch
    assert dependency_edge.source_file is source_file
    assert dependency_edge.target_file is target_file
    assert dependency_edge.indexing_job is indexing_job
    assert architecture_snapshot.repository is repository
    assert architecture_snapshot.branch is branch
    assert architecture_snapshot.indexing_job is indexing_job


def test_security_models_create_relationship_graph() -> None:
    user = User(
        email="security@example.com",
        auth_provider="github",
        auth_provider_user_id="security-1",
        status="active",
    )
    repository = Repository(
        provider="github",
        provider_repository_id="repo-2",
        owner_name="repomind",
        name="repomind-ai",
        full_name="repomind/repomind-ai",
        default_branch="main",
        visibility="private",
    )
    api_key = ApiKey(
        name="CI automation",
        key_prefix="rmai_live_123",
        key_hash="argon2id:hashed-api-key",
        scopes={"repositories": ["read"], "chat": ["write"]},
        status="active",
    )
    audit_log = AuditLog(
        action="repository.index_requested",
        resource_type="repository",
        request_id="req_123",
        metadata_={"source": "api"},
    )

    user.repositories.append(repository)
    user.api_keys.append(api_key)
    user.audit_logs.append(audit_log)
    repository.audit_logs.append(audit_log)

    assert api_key.user is user
    assert audit_log.user is user
    assert audit_log.repository is repository


def test_analysis_and_security_table_names_match_database_spec() -> None:
    assert DependencyEdge.__tablename__ == "dependency_edges"
    assert ArchitectureSnapshot.__tablename__ == "architecture_snapshots"
    assert ApiKey.__tablename__ == "api_keys"
    assert AuditLog.__tablename__ == "audit_logs"


def test_dependency_edge_indexes_and_constraints_are_declared() -> None:
    index_names = {index.name for index in DependencyEdge.__table__.indexes}
    constraint_names = {constraint.name for constraint in DependencyEdge.__table__.constraints}

    assert "ix_dependency_edges_repository_id_branch_id" in index_names
    assert "ix_dependency_edges_source_file_id" in index_names
    assert "ix_dependency_edges_target_file_id" in index_names
    assert "ix_dependency_edges_dependency_type" in index_names
    assert "ix_dependency_edges_external_package_name" in index_names
    assert "ix_dependency_edges_indexing_job_id" in index_names
    assert "ck_dependency_edges_dependency_type_valid" in constraint_names
    assert "ck_dependency_edges_confidence_between_zero_and_one" in constraint_names


def test_architecture_snapshot_indexes_constraints_and_json_column_are_declared() -> None:
    index_names = {index.name for index in ArchitectureSnapshot.__table__.indexes}
    constraint_names = {
        constraint.name for constraint in ArchitectureSnapshot.__table__.constraints
    }

    assert isinstance(ArchitectureSnapshot.__table__.c.content.type, JSONB)
    assert (
        "ix_arch_snapshots_repo_branch_type_created"
        in index_names
    )
    assert "ix_architecture_snapshots_indexing_job_id" in index_names
    assert "ix_architecture_snapshots_content_gin" in index_names
    assert "ck_architecture_snapshots_snapshot_type_valid" in constraint_names
    assert "ck_architecture_snapshots_version_positive" in constraint_names


def test_api_key_indexes_constraints_and_json_column_are_declared() -> None:
    index_names = {index.name for index in ApiKey.__table__.indexes}
    constraint_names = {constraint.name for constraint in ApiKey.__table__.constraints}

    assert isinstance(ApiKey.__table__.c.scopes.type, JSONB)
    assert "uq_api_keys_key_hash" in index_names
    assert "ix_api_keys_key_prefix" in index_names
    assert "ix_api_keys_user_id_created_at" in index_names
    assert "ix_api_keys_status" in index_names
    assert "ix_api_keys_expires_at" in index_names
    assert "ck_api_keys_status_valid" in constraint_names


def test_audit_log_indexes_and_postgres_columns_are_declared() -> None:
    index_names = {index.name for index in AuditLog.__table__.indexes}

    assert isinstance(AuditLog.__table__.c.ip_address.type, INET)
    assert isinstance(AuditLog.__table__.c.metadata.type, JSONB)
    assert "ix_audit_logs_user_id_created_at" in index_names
    assert "ix_audit_logs_repository_id_created_at" in index_names
    assert "ix_audit_logs_action_created_at" in index_names
    assert "ix_audit_logs_resource_type_resource_id" in index_names
    assert "ix_audit_logs_request_id" in index_names
    assert "ix_audit_logs_metadata_gin" in index_names

