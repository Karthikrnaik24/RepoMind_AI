"""Identity response DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MeResponse(BaseModel):
    """Current synchronized local user response payload."""

    id: UUID
    email: str
    display_name: str | None = None
    avatar_url: str | None = None
    provider: str
    provider_subject: str
    role: str | None = None
    created_at: datetime
    last_login_at: datetime | None = None


MeData = MeResponse
