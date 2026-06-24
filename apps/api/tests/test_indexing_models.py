from app.infrastructure.database.models import (
    CodeChunk,
    Embedding,
    IndexingJob,
    Repository,
    RepositoryBranch,
    RepositoryFile,
    User,
)
from pgvector.sqlalchemy import Vector


def test_indexing_models_create_relationship_graph() -> None:
    user = User(
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
    job = IndexingJob(job_type="full_index", status="queued")
    repository_file = RepositoryFile(path="apps/api/app/main.py", size_bytes=512)
    code_chunk = CodeChunk(
        chunk_index=0,
        chunk_type="code",
        content="from fastapi import FastAPI",
        content_hash="a" * 64,
    )
    embedding = Embedding(
        model_provider="openai",
        model_name="text-embedding-3-small",
        dimensions=3,
        embedding=[0.1, 0.2, 0.3],
        content_hash="a" * 64,
    )

    user.repositories.append(repository)
    user.requested_indexing_jobs.append(job)
    repository.branches.append(branch)
    repository.indexing_jobs.append(job)
    repository.files.append(repository_file)
    branch.files.append(repository_file)
    job.repository_files.append(repository_file)
    repository_file.code_chunks.append(code_chunk)
    job.code_chunks.append(code_chunk)
    code_chunk.embeddings.append(embedding)
    job.embeddings.append(embedding)

    assert job.repository is repository
    assert job.branch is None
    assert job.requested_by is user
    assert repository_file.repository is repository
    assert repository_file.branch is branch
    assert repository_file.indexing_job is job
    assert code_chunk.repository_file is repository_file
    assert code_chunk.indexing_job is job
    assert embedding.code_chunk is code_chunk
    assert embedding.indexing_job is job


def test_indexing_table_names_match_database_spec() -> None:
    assert RepositoryFile.__tablename__ == "repository_files"
    assert CodeChunk.__tablename__ == "code_chunks"
    assert Embedding.__tablename__ == "embeddings"
    assert IndexingJob.__tablename__ == "indexing_jobs"


def test_repository_file_indexes_and_constraints_are_declared() -> None:
    index_names = {index.name for index in RepositoryFile.__table__.indexes}
    constraint_names = {constraint.name for constraint in RepositoryFile.__table__.constraints}

    assert "uq_repository_files_repository_id_branch_id_path_active" in index_names
    assert "ix_repository_files_repository_id_branch_id" in index_names
    assert "ix_repository_files_indexing_job_id" in index_names
    assert "ix_repository_files_language" in index_names
    assert "ix_repository_files_content_hash" in index_names
    assert "ck_repository_files_size_bytes_non_negative" in constraint_names
    assert "ck_repository_files_line_count_non_negative" in constraint_names


def test_code_chunk_indexes_and_constraints_are_declared() -> None:
    index_names = {index.name for index in CodeChunk.__table__.indexes}
    constraint_names = {constraint.name for constraint in CodeChunk.__table__.constraints}

    assert "uq_code_chunks_repository_file_id_chunk_index" in index_names
    assert "ix_code_chunks_indexing_job_id" in index_names
    assert "ix_code_chunks_content_hash" in index_names
    assert "ix_code_chunks_chunk_type" in index_names
    assert "ix_code_chunks_symbol_name" in index_names
    assert "ck_code_chunks_start_line_positive" in constraint_names
    assert "ck_code_chunks_end_line_not_before_start_line" in constraint_names
    assert "ck_code_chunks_token_count_non_negative" in constraint_names


def test_embedding_pgvector_column_indexes_and_constraints_are_declared() -> None:
    index_names = {index.name for index in Embedding.__table__.indexes}
    constraint_names = {constraint.name for constraint in Embedding.__table__.constraints}

    assert isinstance(Embedding.__table__.c.embedding.type, Vector)
    assert "uq_embeddings_code_chunk_id_model_provider_model_name_content_hash" in index_names
    assert "ix_embeddings_model_provider_model_name" in index_names
    assert "ix_embeddings_indexing_job_id" in index_names
    assert "ix_embeddings_content_hash" in index_names
    assert "ix_embeddings_embedding_hnsw" in index_names
    assert "ck_embeddings_dimensions_positive" in constraint_names


def test_indexing_job_indexes_and_constraints_are_declared() -> None:
    index_names = {index.name for index in IndexingJob.__table__.indexes}
    constraint_names = {constraint.name for constraint in IndexingJob.__table__.constraints}

    assert "ix_indexing_jobs_repository_id_branch_id_created_at" in index_names
    assert "ix_indexing_jobs_status_created_at" in index_names
    assert "ix_indexing_jobs_requested_by_user_id" in index_names
    assert "ix_indexing_jobs_provider_commit_sha" in index_names
    assert "ck_indexing_jobs_job_type_valid" in constraint_names
    assert "ck_indexing_jobs_status_valid" in constraint_names
    assert "ck_indexing_jobs_progress_total_non_negative" in constraint_names
    assert "ck_indexing_jobs_progress_completed_non_negative" in constraint_names
    assert "ck_indexing_jobs_progress_completed_not_greater_than_total" in constraint_names
