"""Authentication infrastructure foundation.

Sprint 3.1 prepares Supabase and JWT utilities only. It does not enforce
authentication, implement login, or introduce RBAC.
"""

from app.infrastructure.auth.jwt import SupabaseJwtVerifier, create_supabase_jwt_verifier
from app.infrastructure.auth.supabase import SupabaseClient, create_supabase_client

__all__ = [
    "SupabaseClient",
    "SupabaseJwtVerifier",
    "create_supabase_client",
    "create_supabase_jwt_verifier",
]
