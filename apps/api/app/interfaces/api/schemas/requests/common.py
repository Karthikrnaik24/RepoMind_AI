"""Common request DTO examples for future endpoints."""

from pydantic import BaseModel, Field


class PaginationRequest(BaseModel):
    """Reusable pagination DTO for list endpoints."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=100)
