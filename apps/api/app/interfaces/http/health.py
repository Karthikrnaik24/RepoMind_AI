from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    status: str


@router.get("/health", response_model=HealthResponse)
def read_health() -> HealthResponse:
    """Return an unversioned operational health check."""

    return HealthResponse(status="ok")
