"""Health and status response DTOs."""

from pydantic import BaseModel


class HealthData(BaseModel):
    """Health check payload."""

    status: str


class StatusData(BaseModel):
    """Service status payload."""

    status: str
    database: str
    supabase: str
    service: str
    version: str
