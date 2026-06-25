"""Identity response DTOs."""

from typing import Any

from pydantic import BaseModel


class MeData(BaseModel):
    """Current authenticated user response payload."""

    id: str
    email: str
    provider: str
    role: str | None = None
    metadata: dict[str, Any]
