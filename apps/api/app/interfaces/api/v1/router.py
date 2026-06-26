"""API v1 router composition."""

from fastapi import APIRouter

from app.interfaces.api.v1.routes.admin import router as admin_router
from app.interfaces.api.v1.routes.github import router as github_router
from app.interfaces.api.v1.routes.health import router as health_router
from app.interfaces.api.v1.routes.me import router as me_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_router)
api_v1_router.include_router(github_router)
api_v1_router.include_router(me_router)
api_v1_router.include_router(admin_router)
