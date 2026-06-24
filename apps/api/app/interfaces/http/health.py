from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str


class StatusResponse(BaseModel):
    status: str
    service: str
    version: str


@router.get("/health", response_model=HealthResponse)
def read_health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/api/status", response_model=StatusResponse)
def read_status() -> StatusResponse:
    return StatusResponse(status="ok", service="repomind-api", version="0.1.0")
