"""API v1 router composition."""

from fastapi import APIRouter

from app.interfaces.api.v1.routes.health import router as health_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_router)
