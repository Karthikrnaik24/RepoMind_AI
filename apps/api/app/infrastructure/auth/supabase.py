"""Supabase integration bootstrap.

The backend stores configuration needed for future Supabase calls but does not
call Supabase APIs in Sprint 3.1.
"""

from dataclasses import dataclass

from app.config.settings import Settings


@dataclass(frozen=True)
class SupabaseClient:
    """Configured Supabase backend client metadata.

    The service role key is intentionally retained in memory only and must not
    be logged or serialized.
    """

    url: str
    anon_key: str
    service_role_key: str

    @property
    def is_configured(self) -> bool:
        """Return whether the client has the required Supabase settings."""

        return bool(self.url and self.anon_key and self.service_role_key)


def create_supabase_client(settings: Settings) -> SupabaseClient:
    """Create a configured Supabase client placeholder from settings."""

    return SupabaseClient(
        url=settings.supabase_url,
        anon_key=settings.supabase_anon_key.get_secret_value(),
        service_role_key=settings.supabase_service_role_key.get_secret_value(),
    )
