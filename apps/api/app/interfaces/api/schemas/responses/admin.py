"""Admin response DTOs."""

from pydantic import BaseModel


class AdminPingResponse(BaseModel):
    """Response payload for the ADMIN-only ping endpoint."""

    status: str
